"""
Core logic for merging multiple Markdown files into a single document in Ambulon.
Handles file collection, natural sorting, internal link adaptation, TOC generation,
and validation of code blocks.
"""

import sys
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any

logger = logging.getLogger(__name__)


def sanitize_anchor(text: str) -> str:
    """
    Convert text to a valid HTML anchor ID.

    Args:
        text: Text to convert

    Returns:
        Sanitized anchor ID
    """
    # Convert to lowercase
    anchor = text.lower()

    # Replace spaces and dots with hyphens
    anchor = anchor.replace(' ', '-').replace('.', '-')

    # Remove invalid characters
    anchor = re.sub(r'[^a-z0-9\-_]', '', anchor)

    # Remove multiple consecutive hyphens
    anchor = re.sub(r'-+', '-', anchor)

    # Remove leading/trailing hyphens
    anchor = anchor.strip('-')

    return anchor


def create_file_anchor(filename: str) -> str:
    """
    Create an anchor ID from a filename.

    Args:
        filename: Original filename (e.g., "Getting-Started.Quick-Start.md")

    Returns:
        Anchor ID (e.g., "getting-started-quick-start")
    """
    stem = Path(filename).stem
    return sanitize_anchor(stem)


def check_code_blocks_balanced(file_path: Path) -> Tuple[bool, int]:
    """
    Check if a markdown file has balanced code blocks.

    Args:
        file_path: Path to markdown file

    Returns:
        Tuple of (is_balanced, backtick_count)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    backtick_count = content.count('```')
    is_balanced = backtick_count % 2 == 0

    return is_balanced, backtick_count


def collect_markdown_files_for_merging(
    source_dir: Path,
) -> List[Tuple[Path, str]]:
    """
    Collect all .md files and sort them alphabetically.

    Args:
        source_dir: Source directory with .md files

    Returns:
        List of (file_path, filename) tuples sorted alphabetically
    """
    md_files = []

    for md_file in source_dir.glob('*.md'):
        md_files.append((md_file, md_file.name))

    # Sort alphabetically by filename
    md_files.sort(key=lambda x: natural_sort_key(x[1]))

    logger.info(f"Found {len(md_files)} Markdown files to merge.")

    return md_files


def validate_markdown_files(
    files: List[Tuple[Path, str]],
) -> Tuple[List[Tuple[Path, str]], List[str]]:
    """
    Validate markdown files for balanced code blocks.

    Args:
        files: List of (file_path, filename) tuples

    Returns:
        Tuple of (valid_files, unbalanced_filenames)
    """
    valid_files = []
    unbalanced_files = []

    for file_path, filename in files:
        is_balanced, backtick_count = check_code_blocks_balanced(file_path)

        if is_balanced:
            valid_files.append((file_path, filename))
        else:
            unbalanced_files.append(filename)
            logger.warning(f"{filename}: {backtick_count} backticks (unbalanced - excluded from merge)")

    return valid_files, unbalanced_files


def adapt_links_for_fusion(
    content: str,
    current_file: str,
    file_anchors: Dict[str, str],
) -> str:
    """
    Adapt Markdown links in content to work in fused document.

    Internal links to other .md files are converted to anchor links.
    External links and anchor-only links are preserved.

    Args:
        content: Markdown content
        current_file: Current filename
        file_anchors: Mapping of filename → anchor ID

    Returns:
        Content with adapted links
    """
    # Pattern to match Markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

    adapted_count = 0
    preserved_count = 0 # for external/unmatched links

    def replace_link(match):
        nonlocal adapted_count, preserved_count

        link_text = match.group(1)
        link_url = match.group(2)

        # Skip if it's an absolute URL (http://, https://, etc.)
        if '://' in link_url:
            preserved_count += 1
            return match.group(0)

        # Check if it's an anchor-only link
        if link_url.startswith('#'):
            preserved_count += 1
            return match.group(0)

        # Parse the link (might have anchor)
        if '#' in link_url:
            link_file, anchor = link_url.split('#', 1)
            has_anchor = True
        else:
            link_file = link_url
            anchor = ''
            has_anchor = False

        # Skip empty links
        if not link_file:
            preserved_count += 1
            return match.group(0)

        # Check if this is a link to another .md file
        if link_file.endswith('.md'):
            # Get the target anchor
            if link_file in file_anchors:
                target_anchor = file_anchors[link_file]

                # If there's an additional anchor, append it
                if anchor:
                    new_link = f"#{target_anchor}-{anchor}"
                else:
                    new_link = f"#{target_anchor}"

                adapted_count += 1
                logger.debug(f"Adapted link in {current_file}: '{link_url}' -> '{new_link}'")
                return f"[{link_text}]({new_link})"
            else:
                # File exists but not in mapping (not a .md file we're processing for merge)
                preserved_count += 1
                return match.group(0)
        else:
            # Not a Markdown file link, preserve as-is
            preserved_count += 1
            return match.group(0)


    adapted_content = re.sub(link_pattern, replace_link, content)

    if adapted_count > 0:
        logger.debug(f"File {current_file}: {adapted_count} links adapted, {preserved_count} external/preserved.")

    return adapted_content


def generate_table_of_contents(
    files: List[Tuple[Path, str]],
    file_anchors: Dict[str, str]
) -> str:
    """
    Generate table of contents for the fused document.

    Args:
        files: List of (file_path, filename) tuples
        file_anchors: Mapping of filename → anchor ID

    Returns:
        Table of contents as Markdown
    """
    toc_lines = [
        "# 📚 Table des matières",
        "",
        "> Document fusionné généré automatiquement",
        "",
    ]

    for file_path, filename in files:
        anchor = file_anchors[filename]
        stem = Path(filename).stem

        # Create a readable title from the filename
        title = stem.replace('.', ' › ')

        toc_lines.append(f"- [{title}](#{anchor})")

    toc_lines.append("")
    toc_lines.append("---")
    toc_lines.append("")

    return '\n'.join(toc_lines)


def create_section_separator(filename: str, anchor: str) -> str:
    """
    Create a section separator with file identification.

    Args:
        filename: Original filename
        anchor: Anchor ID for this section

    Returns:
        Section separator as Markdown
    """
    stem = Path(filename).stem
    title = stem.replace('.', ' › ')

    separator = [
        "",
        "---",
        "",
        f'<a id="{anchor}"></a>',
        "",
        f"# 📄 {title}",
        "",
        f"> **Source :** `{filename}`",
        "",
    ]

    return '\n'.join(separator)


def fusion_markdown_files_logic(
    source_dir: Path,
    output_file: Path,
    output_name: str = "merged.md",
    title: str = "Merged Markdown Document", # New title for Markdown
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to merge multiple Markdown files into a single fused document.

    Args:
        source_dir: Source directory with .md files
        output_file: Output file path
        output_name: Name of output file (default: merged.md)
        title: Title for the merged Markdown document

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

    logger.info(f"Source directory: {source_path}")
    logger.info(f"Output file: {output_file}")

    # Collect all .md files
    all_files = collect_markdown_files_for_merging(source_path)

    if not all_files:
        logger.warning(f"No Markdown files found in '{source_dir}'. Nothing to merge.")
        return 1, None

    # Validate files for balanced code blocks
    files, unbalanced_files = validate_markdown_files(all_files)

    if unbalanced_files:
        logger.warning(f"{len(unbalanced_files)} file(s) excluded from merge due to unbalanced code blocks:")
        for filename in unbalanced_files:
            logger.warning(f"  - {filename}")
        logger.warning("Fix unbalanced backticks (```) in these files before merging.")

    if not files:
        logger.error(f"No valid Markdown files to merge (all files have unbalanced code blocks).")
        return 1, None

    # Create anchor mapping
    file_anchors = {}
    for file_path, filename in files:
        anchor = create_file_anchor(filename)
        file_anchors[filename] = anchor
    logger.debug(f"Generated file anchors for {len(file_anchors)} files.")

    # Generate table of contents
    logger.info("Generating Table of Contents...")
    toc = generate_table_of_contents(files, file_anchors)

    # Merge all files
    merged_content_parts = [toc]
    success_count = 0
    error_count = 0

    for file_path, filename in files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Adapt links
            adapted_content = adapt_links_for_fusion(
                content,
                filename,
                file_anchors,
            )

            # Create section separator
            anchor = file_anchors[filename]
            separator = create_section_separator(filename, anchor)

            # Add to merged content
            merged_content_parts.append(separator)
            merged_content_parts.append(adapted_content)

            success_count += 1
            logger.info(f"Processed: {filename}")

        except Exception as e:
            error_count += 1
            logger.error(f"Failed to process {filename}: {e}", exc_info=True)

    final_markdown_content = '\n'.join(merged_content_parts)

    if not final_markdown_content.strip():
        logger.warning("Merged content is empty. No output file will be written.")
        return 1, None

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write merged file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_markdown_content)

        logger.info(f"Merged content written to {output_file}.")

    except Exception as e:
        logger.error(f"Failed to write output file: {e}", exc_info=True)
        return 1, None

    # Summary
    logger.info("="*70)
    logger.info("Markdown Merging complete")
    logger.info("="*70)
    logger.info(f"Files merged:     {success_count}/{len(files)}")
    if len(unbalanced_files) > 0:
        logger.warning(f"Files excluded:   {len(unbalanced_files)} (unbalanced code blocks)")
    if error_count > 0:
        logger.error(f"Errors:          {error_count}")
        return 1, None
    
    logger.info(f"Output file:     {output_file}")

    # Calculate file size
    file_size = output_file.stat().st_size
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.2f} MB"
    elif file_size > 1024:
        size_str = f"{file_size / 1024:.2f} KB"
    else:
        size_str = f"{file_size} bytes"
    logger.info(f"File size:       {size_str}")
    logger.info("="*70)

    return 0, output_file
