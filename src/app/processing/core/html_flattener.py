"""
Core logic for flattening an HTML directory structure in Ambulon.
Copies .html files from a nested structure to a flat directory,
adapting internal HTML links to work in the flattened structure.
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


def flatten_html_path(relative_path: Path) -> str:
    """
    Convert a relative path to a flattened filename using dots as separators.

    Examples:
        getting-started/index.html → getting-started.index.html
        api/methods/detail.html → api.methods.detail.html
        index.html → index.html

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

    # Join directory parts with dots and add filename
    flattened = '.'.join(sanitized_dirs) + '.' + filename

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


def collect_html_files_for_flattening(
    source_dir: Path,
) -> List[Tuple[Path, str, Path]]:
    """
    Collect all .html files and their flattened names.

    Args:
        source_dir: Root source directory

    Returns:
        List of (source_path, flattened_name, relative_path) tuples
    """
    files = []

    # Find all .html files recursively
    html_files = list(source_dir.rglob('*.html'))

    logger.info(f"Found {len(html_files)} HTML files in '{source_dir}'.")

    for file_path in html_files:
        # Get relative path from source_dir
        relative_path = file_path.relative_to(source_dir)

        # Generate flattened name
        flattened_name = flatten_html_path(relative_path)

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


def adapt_html_links(
    content: str,
    current_relative_path: Path,
    link_mapping: Dict[Path, str],
    source_dir: Path,
) -> str:
    """
    Adapt HTML links in content to work in flattened structure.

    Only adapts href attributes pointing to other HTML files.
    Preserves all asset references (CSS, JS, images, etc.).

    Args:
        content: HTML content
        current_relative_path: Relative path of current file
        link_mapping: Mapping of relative paths to flattened names
        source_dir: Source directory root

    Returns:
        Content with adapted links
    """
    # Asset extensions to always preserve
    ASSET_EXTENSIONS = {
        '.css', '.js',  # Stylesheets and scripts
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.bmp',  # Images
        '.woff', '.woff2', '.ttf', '.eot',  # Fonts
        '.mp4', '.webm', '.ogg', '.mp3', '.wav',  # Media
        '.pdf', '.zip', '.tar', '.gz',  # Documents/Archives
    }

    # Pattern to match href attributes: href="..." or href='...'
    link_pattern = r'href=["\"]([^"\\]+)["\"]'

    adapted_count = 0
    preserved_count = 0

    def replace_link(match):
        nonlocal adapted_count, preserved_count

        href = match.group(1)

        # 1. Skip absolute URLs (http://, https://, //, etc.)
        if '://' in href or href.startswith('//'):
            preserved_count += 1
            return match.group(0)

        # 2. Skip anchor-only links
        if href.startswith('#'):
            preserved_count += 1
            return match.group(0)

        # 3. Parse href (might have anchor or query params)
        # Split on # and ? to get the path part
        path_part_raw = href.split('#')[0].split('?')[0]

        # 4. Skip empty paths
        if not path_part_raw:
            preserved_count += 1
            return match.group(0)

        # 5. Check if this is an asset by extension
        path_lower = path_part_raw.lower()
        if any(path_lower.endswith(ext) for ext in ASSET_EXTENSIONS):
            # This is an asset reference - preserve it
            preserved_count += 1
            return match.group(0)

        # 6. Extract anchor and query parts (if any)
        anchor = ''
        query = ''

        # Extracting parts from original href
        full_path_without_scheme = href
        if '://' in href:
            full_path_without_scheme = href.split('://', 1)[1] # remove http/https
        
        # Split on first # and then first ?
        parts_hash = full_path_without_scheme.split('#', 1)
        path_and_query = parts_hash[0]
        if len(parts_hash) > 1:
            anchor = parts_hash[1]

        parts_query = path_and_query.split('?', 1)
        path_part_clean = parts_query[0]
        if len(parts_query) > 1:
            query = parts_query[1]


        # 7. Check if it's an HTML file (explicitly .html/.htm or no extension)
        is_html = (path_part_clean.lower().endswith('.html') or
                   path_part_clean.lower().endswith('.htm') or
                   ('.' not in Path(path_part_clean).name))  # No extension might imply HTML

        if not is_html:
            # Not HTML and not a known asset - preserve as-is
            preserved_count += 1
            return match.group(0)

        # 8. Resolve the link relative to current file
        current_dir = current_relative_path.parent

        try:
            # Clean up ./ prefix
            if path_part_clean.startswith('./'):
                path_part_clean = path_part_clean[2:]

            # Resolve the path relative to the source_dir
            # This handles '..' and other relative pathing correctly
            resolved_link_path = (source_dir / current_dir / path_part_clean).resolve()

            # Check if resolved_link_path is within source_dir
            try:
                link_relative = resolved_link_path.relative_to(source_dir)

                # Check if this file is in our mapping (it's an HTML file we're flattening)
                if link_relative in link_mapping:
                    # Internal HTML link - adapt it
                    new_link = link_mapping[link_relative]

                    # Rebuild with anchor and query if present
                    final_href = new_link
                    if query:
                        final_href = f"{final_href}?{query}"
                    if anchor:
                        final_href = f"{final_href}#{anchor}"

                    adapted_count += 1
                    logger.debug(f"Adapted link in {current_relative_path}: '{href}' -> '{final_href}'")
                    return f'href="{final_href}"'
                else:
                    # File exists and is HTML but not in mapping (e.g., a file not included by filters)
                    preserved_count += 1
                    return match.group(0)

            except ValueError:
                # Link points outside source_dir - preserve
                preserved_count += 1
                return match.group(0)

        except Exception as e:
            logger.warning(f"Could not adapt link '{href}' in '{current_relative_path}': {e}")
            preserved_count += 1
            return match.group(0)

    # Replace all href attributes
    adapted_content = re.sub(link_pattern, replace_link, content)

    logger.debug(f"Links in {current_relative_path}: {adapted_count} adapted, {preserved_count} preserved.")

    return adapted_content


def flatten_html_directory_logic(
    source_dir: Path,
    output_dir: Optional[Path] = None,
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to flatten an HTML directory structure.

    Args:
        source_dir: Source directory with nested .html files
        output_dir: Output directory (default: {source_dir}-flattened)

    Returns:
        A tuple: (exit_code: int, generated_path: Optional[Path])
    """
    # Fix encoding for Windows console (moved from CLI to here as it's a core concern)
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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

    # Collect all .html files
    files = collect_html_files_for_flattening(source_path)

    if not files:
        logger.warning(f"No HTML files found in '{source_dir}'. Nothing to flatten.")
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
            adapted_content = adapt_html_links(
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
    logger.info("HTML Flattening complete")
    logger.info("="*70)
    logger.info(f"Files processed:  {success_count}/{len(files)}")
    if error_count > 0:
        logger.error(f"Errors:          {error_count}")
        return 1, None
    
    logger.info(f"Output directory: {output_path}")
    logger.info("="*70)

    return 0, output_path
