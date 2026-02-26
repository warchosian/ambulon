"""
Core logic for adding back-to-TOC links to Markdown headings in Ambulon.
Parses Markdown, finds headings, and adds navigation links (↑) after each heading.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


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

    Properly handles custom IDs {#id} by inserting the link BEFORE the ID.

    Args:
        md_content: Original Markdown content
        headings: List of headings with line numbers
        toc_id: ID of the table of contents anchor (default: "table-of-contents")
        link_text: Text for the back link (default: "↑")

    Returns:
        Modified Markdown content with back-to-TOC links
    """
    lines = md_content.split('\n')

    # Process headings in reverse order to avoid line number shifts
    for heading in reversed(headings):
        line_num = heading['line']
        original_line = lines[line_num]

        # Check if the heading has a custom ID {#custom-id}
        # If yes, insert the link BEFORE the ID
        # If no, insert at the end
        import re
        custom_id_pattern = r'\s*\{#([a-zA-Z0-9\-_]+)\}\s*$'
        match = re.search(custom_id_pattern, original_line)

        if match:
            # Insert link before the custom ID
            # Format: ## Heading [↑](#toc) {#custom-id}
            insert_pos = match.start()
            modified_line = original_line[:insert_pos] + f" [{link_text}](#{toc_id})" + original_line[insert_pos:]
        else:
            # No custom ID, append at the end
            # Format: ## Heading [↑](#toc)
            modified_line = f"{original_line} [{link_text}](#{toc_id})"

        lines[line_num] = modified_line

    return '\n'.join(lines)


def add_toc_backlinks_logic(
    input_file: Path,
    output_file: Path,
    toc_id: str = "table-of-contents",
    link_text: str = "↑",
    min_level: int = 1,
    max_level: int = 6,
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
