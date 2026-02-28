"""
Core logic for adding back-to-TOC links to Markdown headings in Ambulon.
Parses Markdown, finds headings, and adds navigation links (↑) after each heading.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .markdown_itoc_checker import detect_itoc_links

logger = logging.getLogger(__name__)


def remove_existing_backlinks(md_content: str, link_pattern: str = r'\[↑\]\(#[^\)]+\)') -> str:
    """
    Remove existing iTOC (back-to-TOC) links from markdown content.
    
    Args:
        md_content: Markdown content that may contain backlink links
        link_pattern: Regex pattern for iTOC links to remove
        
    Returns:
        Content with backlinks removed
    """
    # Remove backlink patterns from headings
    content = re.sub(r'\s*' + link_pattern, '', md_content)
    
    # Clean up excessive empty lines left behind
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content


def is_toc_heading(text: str) -> bool:
    """Check if a heading is the TOC title itself (should be excluded from backlinks)."""
    toc_patterns = [
        r'table\s+(?:des\s+)?mati[èe]res',  # Table des matières
        r'table\s+of\s+contents',           # Table of Contents
        r'sommaire',                         # Sommaire
    ]
    text_lower = text.lower()
    for pattern in toc_patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def extract_headings_with_positions(md_content: str) -> List[Dict[str, Any]]:
    """
    Extract headings from Markdown content with their positions.

    Args:
        md_content: Markdown content as string

    Returns:
        List of heading dictionaries with level, text, line number, and position
    """
    headings = []
    lines = md_content.split('\n')

    # Pattern to match markdown headings: # Heading, ## Heading, etc.
    # Optionally captures custom IDs in {#id} format
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*\{#[a-zA-Z0-9\-_]+\})?$')

    for line_num, line in enumerate(lines):
        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))  # Count number of #
            text = match.group(2).strip()

            # Skip TOC headings (don't add backlinks to the TOC title itself)
            if is_toc_heading(text):
                continue

            headings.append({
                'level': level,
                'text': text,
                'line': line_num,
                'original_line': line
            })

    return headings


def add_backlinks_to_headings(
    md_content: str,
    headings: List[Dict[str, Any]],
    toc_id: str = "table-of-contents",
    link_text: str = "↑"
) -> str:
    """
    Add back-to-TOC links after Markdown headings.

    Links point to the SPECIFIC LINE in the TOC (toc-{heading-id}), not just
    the TOC in general. This allows users to return to the exact TOC entry.

    Properly handles custom IDs {#id} by inserting the link BEFORE the ID.
    Skips headings that already have a backlink to prevent duplicates.

    Args:
        md_content: Original Markdown content
        headings: List of headings with line numbers
        toc_id: Base ID for TOC (unused, kept for compatibility)
        link_text: Text for the back link (default: "↑")

    Returns:
        Modified Markdown content with back-to-TOC links
    """
    import re
    lines = md_content.split('\n')

    # Process headings in reverse order to avoid line number shifts
    for heading in reversed(headings):
        line_num = heading['line']
        original_line = lines[line_num]
        heading_text = heading['text']

        # Skip if backlink already exists (check for [↑](#toc-...) pattern)
        if re.search(r'\[↑\]\(#toc-[^)]+\)', original_line):
            continue

        # Extract or generate the heading ID to build the TOC line ID
        custom_id_pattern = r'\s*\{#([a-zA-Z0-9\-_]+)\}\s*$'
        match = re.search(custom_id_pattern, original_line)

        if match:
            # Use the custom ID
            heading_id = match.group(1)
        else:
            # Generate ID from heading text (same logic as TOC generation)
            heading_id = re.sub(r'[^\w\s-]', '', heading_text.lower())
            heading_id = re.sub(r'[\s_]+', '-', heading_id).strip('-')

        # Build the TOC line ID: toc-{heading-id}
        toc_line_id = f"toc-{heading_id}"

        # Insert the backlink
        if match:
            # Insert link before the custom ID
            # Format: ## Heading [↑](#toc-heading-id) {#heading-id}
            insert_pos = match.start()
            modified_line = original_line[:insert_pos] + f" [{link_text}](#{toc_line_id})" + original_line[insert_pos:]
        else:
            # No custom ID, append at the end
            # Format: ## Heading [↑](#toc-heading-id)
            modified_line = f"{original_line} [{link_text}](#{toc_line_id})"

        lines[line_num] = modified_line

    return '\n'.join(lines)


def add_toc_backlinks_logic(
    input_file: Path,
    output_file: Path,
    toc_id: str = "table-of-contents",
    link_text: str = "↑",
    min_level: int = 1,
    max_level: int = 6,
    force: bool = False,
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to add back-to-TOC links to a Markdown file.

    Args:
        input_file: Path to input Markdown file
        output_file: Path to output file
        toc_id: ID of the table of contents anchor
        link_text: Text for the back link
        min_level: Minimum heading level to add backlinks (1-6)
        max_level: Maximum heading level to add backlinks (1-6)
        force: If True, add links even if some already exist; if False, skip if links exist

    Returns:
        A tuple: (exit_code: int, generated_path: Optional[Path])
    """
    if not input_file.exists():
        logger.error(f"Error: Input file '{input_file}' does not exist.")
        return 1, None

    if not input_file.is_file():
        logger.error(f"Error: '{input_file}' is not a file.")
        return 1, None

    logger.info(f"Processing: {input_file}")
    logger.info(f"Output: {output_file}")

    try:
        # Read Markdown content
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Check if iTOC links already exist
        itoc_check = detect_itoc_links(md_content)
        if itoc_check['has_itoc_links'] and not force:
            logger.info(f"iTOC links already exist: {itoc_check['itoc_count']}/{itoc_check['total_headings']} headings (use --force to add anyway)")
            # Copy file as-is
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"File copied without changes: {output_file}")
            return 0, output_file

        # Remove existing backlinks if force mode
        if force and itoc_check['has_itoc_links']:
            logger.info(f"Removing {itoc_check['itoc_count']} existing backlinks (force mode)")
            md_content = remove_existing_backlinks(md_content)

        # Extract headings
        all_headings = extract_headings_with_positions(md_content)

        logger.info(f"Found {len(all_headings)} headings.")

        if not all_headings:
            logger.warning("No headings found in Markdown file. No backlinks will be added.")
            # Still write the file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"File copied without backlinks: {output_file}")
            return 0, output_file

        # Filter headings by level
        filtered_headings = [h for h in all_headings if min_level <= h['level'] <= max_level]

        logger.info(f"Adding backlinks to {len(filtered_headings)} headings (levels {min_level}-{max_level}).")

        # Add backlinks to filtered headings
        md_with_backlinks = add_backlinks_to_headings(md_content, filtered_headings, toc_id, link_text)

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_with_backlinks)

        logger.info(f"Markdown with backlinks created: {output_file}")
        logger.info(f"Total headings found:     {len(all_headings)}")
        logger.info(f"Backlinks added:          {len(filtered_headings)}")
        logger.info(f"TOC anchor ID:            #{toc_id}")
        logger.info(f"Link text:                {link_text}")

        file_size = output_file.stat().st_size
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        elif file_size > 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size} bytes"
        logger.info(f"Output file size:         {size_str}")

        return 0, output_file

    except Exception as e:
        logger.error(f"Error: Failed to add backlinks: {e}", exc_info=True)
        return 1, None
