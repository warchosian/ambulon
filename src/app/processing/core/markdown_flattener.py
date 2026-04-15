"""
Core logic for flattening a Markdown directory structure in Ambulon.
Copies .md files from a nested structure to a flat directory,
adapting internal Markdown links to work in the flattened structure.
"""

import sys
import shutil
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use in filenames.

    Args:
        name: String to sanitize

    Returns:
        Sanitized string safe for filenames
    """
    # Replace invalid filename characters
    invalid_chars = '<>:\"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name


def flatten_md_path(relative_path: Path) -> str:
    """
    Convert a relative path to a flattened filename using dots as separators.

    Examples:
        Getting-Started/Quick-Start.md → Getting-Started.Quick-Start.md
        RAG-System/Chunking/Algorithm.md → RAG-System.Chunking.Algorithm.md
        README.md → README.md

    Args:
        relative_path: Path relative to source root

    Returns:
        Flattened filename
    """
    parts = list(relative_path.parts)

    # Get filename without extension
    filename = parts[-1]
    # stem = Path(filename).stem # Path().stem already gives "index" for "index.html"
    # suffix = Path(filename).suffix # Path().suffix gives ".html" for "index.html"

    # Get directory path (all parts except the last one)
    dir_parts = parts[:-1]

    if not dir_parts:
        # File at root level
        return filename

    # Sanitize each directory part
    sanitized_dirs = [sanitize_filename(part) for part in dir_parts]

    # Join directory parts with double underscores and add filename
    flattened = '__'.join(sanitized_dirs) + '__' + filename

    return flattened


def natural_sort_key(filename: str) -> List[Any]:
    """
    Generate a sort key for natural (numeric) sorting.

    Converts 'file10.html' to ['file', 10, '.html'] for proper numeric comparison.

    Args:
        filename: Filename to generate key for

    Returns:
        List of strings and integers for sorting
    """
    def try_int(s):
        try:
            return int(s)
        except ValueError:
            return s.lower()

    return [try_int(part) for part in re.split(r'(\d+)', filename)]


def collect_md_files_for_flattening(
    source_dir: Path,
) -> List[Tuple[Path, str, Path]]:
    """
    Collect all .md files and their flattened names.

    Args:
        source_dir: Root source directory

    Returns:
        List of (source_path, flattened_name, relative_path) tuples
    """
    files = []

    # Find all .md files recursively
    md_files = list(source_dir.rglob('*.md'))

    logger.info(f"Found {len(md_files)} Markdown files in '{source_dir}'.")

    for file_path in md_files:
        # Get relative path from source_dir
        relative_path = file_path.relative_to(source_dir)

        # Generate flattened name
        flattened_name = flatten_md_path(relative_path)

        files.append((file_path, flattened_name, relative_path))

    return files


def build_link_mapping(files: List[Tuple[Path, str, Path]]) -> Dict[Path, str]:
    """
    Build a mapping from relative paths to flattened names.

    Args:
        files: List of (source_path, flattened_name, relative_path) tuples

    Returns:
        Dictionary mapping relative_path → flattened_name
    """
    mapping = {}
    for source_path, flattened_name, relative_path in files:
        mapping[relative_path] = flattened_name
    return mapping


def adapt_markdown_links(
    content: str,
    current_relative_path: Path,
    link_mapping: Dict[Path, str],
    source_dir: Path,
) -> str:
    """
    Adapt Markdown links in content to work in flattened structure.

    Args:
        content: Markdown content
        current_relative_path: Relative path of current file
        link_mapping: Mapping of relative paths to flattened names
        source_dir: Source directory root

    Returns:
        Content with adapted links
    """
    # Pattern to match Markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

    adapted_count = 0
    external_count = 0
    preserved_count = 0

    def replace_link(match):
        nonlocal adapted_count, external_count, preserved_count

        link_text = match.group(1)
        link_url = match.group(2)

        # Skip if it's an absolute URL (http://, https://, etc.) or anchor-only link
        if '://' in link_url or link_url.startswith('#'):
            preserved_count += 1
            return match.group(0)

        # Parse the link (might have anchor)
        if '#' in link_url:
            link_path, anchor = link_url.split('#', 1)
            has_anchor = True
        else:
            link_path = link_url
            anchor = ''
            has_anchor = False

        # Skip empty links
        if not link_path:
            preserved_count += 1
            return match.group(0)

        # Resolve the link relative to current file
        current_dir = current_relative_path.parent

        try:
            # Resolve relative path
            if link_path.startswith('./'):
                link_path = link_path[2:]
            elif link_path.startswith('../'):
                pass  # Will be handled by resolve()

            # Calculate absolute path within source_dir
            absolute_link = (source_dir / current_dir / link_path).resolve()

            # Check if link is within source_dir
            try:
                link_relative = absolute_link.relative_to(source_dir)

                # Check if this file is in our mapping
                matched_path = None

                # Try 1: Direct match
                if link_relative in link_mapping:
                    matched_path = link_relative

                # Try 2: Add .md extension (for GitLab wiki links without extension)
                if not matched_path and not str(link_relative).endswith('.md'):
                    link_with_md = Path(str(link_relative) + '.md')
                    if link_with_md in link_mapping:
                        matched_path = link_with_md
                        logger.debug(f"Wiki link without .md extension found: '{link_url}' → '{link_with_md}'")

                # Try 3: Transform path with slashes to flattened name (e.g., "configuration/detail_gitlab" → "configuration__detail_gitlab.md")
                if not matched_path and '/' in str(link_relative):
                    # Replace / with __ and ensure .md extension
                    flattened_name = str(link_relative).replace('/', '__')
                    if not flattened_name.endswith('.md'):
                        flattened_name += '.md'
                    flattened_path = Path(flattened_name)
                    if flattened_path in link_mapping:
                        matched_path = flattened_path
                        logger.debug(f"Wiki path transformed to flattened name: '{link_url}' → '{flattened_path}'")

                if matched_path:
                    # Internal link - adapt it
                    new_link = link_mapping[matched_path]
                    if has_anchor:
                        new_link = f"{new_link}#{anchor}"

                    adapted_count += 1
                    logger.debug(f"Adapted link in {current_relative_path}: '{link_url}' → '{new_link}'")
                    return f"[{link_text}]({new_link})"
                else:
                    # File exists but not in mapping (e.g., a file not included by filters)
                    # Keep original link
                    external_count += 1
                    return match.group(0)

            except ValueError:
                # Link points outside source_dir - keep as is
                external_count += 1
                return match.group(0)

        except Exception as e:
            logger.warning(f"Could not adapt link '{link_url}' in '{current_relative_path}': {e}")
            return match.group(0)

    # Replace all links
    adapted_content = re.sub(link_pattern, replace_link, content)

    logger.debug(f"Links in {current_relative_path}: {adapted_count} adapted, {external_count} external/preserved.")

    return adapted_content


def flatten_markdown_directory_logic(
    source_dir: Path,
    output_dir: Optional[Path] = None,
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to flatten a Markdown directory structure.

    Args:
        source_dir: Source directory with nested .md files
        output_dir: Output directory (default: {source_dir}-flattened)

    Returns:
        A tuple: (exit_code: int, generated_path: Optional[Path])
    """
    # Fix encoding for Windows console (moved from CLI to here as it's a core concern)
    if sys.platform == 'win32':
        import codecs
        stdout_buffer = getattr(sys.stdout, "buffer", None)
        stderr_buffer = getattr(sys.stderr, "buffer", None)
        if stdout_buffer is not None:
            sys.stdout = codecs.getwriter('utf-8')(stdout_buffer, 'strict')
        if stderr_buffer is not None:
            sys.stderr = codecs.getwriter('utf-8')(stderr_buffer, 'strict')

    source_path = source_dir.resolve()

    if not source_path.exists():
        logger.error(f"Error: Source directory does not exist: {source_dir}.")
        return 1, None

    if not source_path.is_dir():
        logger.error(f"Error: '{source_dir}' is not a directory.")
        return 1, None

    # Determine output directory
    if output_dir:
        output_path = output_dir.resolve()
    else:
        output_path = source_path.parent / f"{source_path.name}-flattened"

    logger.info(f"Source directory: {source_path}")
    logger.info(f"Output directory: {output_path}")

    # Collect all .md files
    files = collect_md_files_for_flattening(source_path)

    if not files:
        logger.warning(f"No Markdown files found in '{source_dir}'. Nothing to flatten.")
        return 1, None

    # Build link mapping
    logger.info(f"Building internal link map for {len(files)} files...")
    link_mapping = build_link_mapping(files)
    logger.debug(f"Generated link map with {len(link_mapping)} entries.")

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory created/ensured: {output_path}")

    logger.info(f"Flattening {len(files)} files...")

    # Copy and adapt files
    success_count = 0
    error_count = 0

    for source_file, flattened_name, relative_path in files:
        try:
            # Read source file
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Adapt links
            adapted_content = adapt_markdown_links(
                content,
                relative_path,
                link_mapping,
                source_path,
            )

            # Write to output
            final_output_file = output_path / flattened_name
            with open(final_output_file, 'w', encoding='utf-8') as f:
                f.write(adapted_content)

            success_count += 1
            logger.info(f"Processed: {relative_path} → {flattened_name}")

        except Exception as e:
            error_count += 1
            logger.error(f"Failed to process {relative_path}: {e}", exc_info=True)

    # Summary
    logger.info("="*70)
    logger.info("Markdown Flattening complete")
    logger.info("="*70)
    logger.info(f"Files processed:  {success_count}/{len(files)}")
    if error_count > 0:
        logger.error(f"Errors:          {error_count}")
        return 1, None
    
    logger.info(f"Output directory: {output_path}")
    logger.info("="*70)

    return 0, output_path
