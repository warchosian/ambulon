"""
Core logic for adding a Table of Contents (TOC) to Markdown files in Ambulon.
Parses Markdown, extracts headings, generates hierarchical TOC with anchor links.
"""

import re
import sys
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Set

logger = logging.getLogger(__name__)


def extract_headings(md_content: str) -> List[Dict[str, Any]]:
    """
    Extract headings from Markdown content.

    Args:
        md_content: Markdown content as string

    Returns:
        List of heading dictionaries with level, text, and line number
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
            custom_id = match.group(3)  # Custom ID if specified

            headings.append({
                'level': level,
                'text': text,
                'line': line_num,
                'custom_id': custom_id,
                'id': None  # Will be generated later
            })

    return headings


def generate_id(text: str, existing_ids: Set[str]) -> str:
    """
    Generate a unique ID from heading text.

    Args:
        text: Heading text
        existing_ids: Set of already used IDs

    Returns:
        Unique ID string
    """
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    base_id = re.sub(r'[^\w\s-]', '', text.lower())
    base_id = re.sub(r'[-\s]+', '-', base_id).strip('-')

    # Ensure uniqueness
    unique_id = base_id
    counter = 1
    while unique_id in existing_ids:
        unique_id = f"{base_id}-{counter}"
        counter += 1

    existing_ids.add(unique_id)
    return unique_id


def generate_toc_markdown(headings: List[Dict[str, Any]], min_level: int = 1, max_level: int = 6) -> str:
    """
    Generate Markdown table of contents.

    Args:
        headings: List of heading dictionaries
        min_level: Minimum heading level to include (default: 1)
        max_level: Maximum heading level to include (default: 6)

    Returns:
        Markdown string for TOC
    """
    if not headings:
        return ""

    toc_lines = ['## Table des matières', '']

    # Filter headings by level
    filtered_headings = [h for h in headings if min_level <= h['level'] <= max_level]

    if not filtered_headings:
        return ""

    # Find the minimum level to use as base for indentation
    base_level = min(h['level'] for h in filtered_headings)

    for heading in filtered_headings:
        level = heading['level']
        text = heading['text']
        heading_id = heading['id']

        # Calculate indentation (2 spaces per level)
        indent = '  ' * (level - base_level)

        # Create TOC entry
        toc_lines.append(f'{indent}- [{text}](#{heading_id})')

    toc_lines.append('')  # Empty line after TOC
    toc_lines.append('---')  # Separator
    toc_lines.append('')

    return '\n'.join(toc_lines)


def add_anchors_to_headings(md_content: str, headings: List[Dict[str, Any]]) -> str:
    """
    Add HTML anchor IDs to Markdown headings.

    Since Markdown doesn't have native ID support, we add HTML anchors
    before each heading for navigation.

    Args:
        md_content: Original Markdown content
        headings: List of headings with generated IDs

    Returns:
        Modified Markdown content with anchors
    """
    lines = md_content.split('\n')
    
    # Store replacements to apply them in reverse order of line numbers
    # This prevents issues with changing line indices when inserting new lines
    replacements: List[Tuple[int, str]] = []

    for heading in headings:
        line_num = heading['line']
        heading_id = heading['id']

        # If the heading already has a custom ID, it's assumed to have an anchor, so skip
        if heading.get('custom_id'):
            continue
        
        # Add anchor before the heading (HTML anchor on a separate line)
        anchor = f'<a id="{heading_id}"></a>'

        # Insert anchor on the line before the heading
        # This will be applied in reverse later
        replacements.append((line_num, anchor))
    
    # Apply replacements in reverse order of line number
    # This correctly handles inserting new lines without messing up subsequent indices
    for line_num, anchor in sorted(replacements, key=lambda x: x[0], reverse=True):
        lines.insert(line_num, anchor)

    return '\n'.join(lines)


def add_toc_to_markdown_logic(
    input_file: Path,
    output_file: Path,
    min_level: int = 1,
    max_level: int = 6,
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to add a table of contents to a Markdown file.

    Args:
        input_file: Path to input Markdown file
        output_file: Path to output file
        min_level: Minimum heading level to include in TOC (1-6)
        max_level: Maximum heading level to include in TOC (1-6)

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
        headings = extract_headings(md_content)

        logger.info(f"Found {len(headings)} headings.")

        if not headings:
            logger.warning("No headings found in Markdown file. No TOC will be added.")
            # Still write the file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"File copied without TOC: {output_file}")
            return 0, output_file

        # Generate IDs for headings
        existing_ids: Set[str] = set()
        for heading in headings:
            if heading.get('custom_id'):
                heading['id'] = heading['custom_id']
                existing_ids.add(heading['id']) # Add custom IDs to ensure uniqueness check works
            else:
                heading['id'] = generate_id(heading['text'], existing_ids)

            logger.debug(f"  {'#' * heading['level']} {heading['text']} (#{heading['id']})")

        # Generate TOC Markdown
        toc_md = generate_toc_markdown(headings, min_level, max_level)

        # Add anchors to headings in the content
        md_with_anchors = add_anchors_to_headings(md_content, headings)

        # Combine TOC + content
        final_content = toc_md + '\n' + md_with_anchors

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)

        filtered_count = len([h for h in headings if min_level <= h['level'] <= max_level])

        logger.info(f"Markdown with TOC created: {output_file}")
        logger.info(f"Total headings found:     {len(headings)}")
        logger.info(f"Headings in TOC:          {filtered_count}")
        logger.info(f"Heading level range:      {min_level} - {max_level}")
        
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
        logger.error(f"Error: Failed to add TOC: {e}", exc_info=True)
        return 1, None
