"""
Command to add a Table of Contents (TOC) to Markdown files.

This module parses Markdown files, extracts headings (# to ######), and generates
a hierarchical table of contents with anchor links.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def extract_headings(md_content: str) -> List[Dict[str, any]]:
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
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*\{#([a-zA-Z0-9\-_]+)\})?$')

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


def generate_id(text: str, existing_ids: set) -> str:
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


def generate_toc_markdown(headings: List[dict], min_level: int = 1, max_level: int = 6) -> str:
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


def add_anchors_to_headings(md_content: str, headings: List[dict]) -> str:
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

    # Create a mapping of line numbers to heading IDs
    line_to_id = {h['line']: h['id'] for h in headings}

    # Insert anchors (process in reverse to maintain line numbers)
    offset = 0
    for heading in sorted(headings, key=lambda h: h['line']):
        line_num = heading['line'] + offset
        heading_id = heading['id']

        # Add anchor before the heading
        anchor = f'<a id="{heading_id}"></a>'

        # If the heading already has a custom ID, we don't need to add an anchor
        if heading.get('custom_id'):
            continue

        # Insert anchor on the line before the heading
        if line_num > 0 and lines[line_num - 1].strip() == '':
            # If previous line is empty, replace it with anchor
            lines[line_num - 1] = anchor
        else:
            # Otherwise insert a new line with anchor
            lines.insert(line_num, anchor)
            offset += 1

    return '\n'.join(lines)


def add_toc_to_markdown(
    input_path: str,
    output_path: Optional[str] = None,
    min_level: int = 1,
    max_level: int = 6,
    verbose: bool = False
) -> int:
    """
    Add a table of contents to a Markdown file.

    Args:
        input_path: Path to input Markdown file
        output_path: Optional path to output file. If None, uses <name>-tocced.md
        min_level: Minimum heading level to include in TOC (1-6)
        max_level: Maximum heading level to include in TOC (1-6)
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_file = Path(input_path).resolve()

    # Check if input file exists
    if not input_file.exists():
        print(f"[ERROR] Input file '{input_path}' does not exist.", file=sys.stderr)
        return 1

    if not input_file.is_file():
        print(f"[ERROR] '{input_path}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        output_file = input_file.parent / f"{input_file.stem}-tocced.md"
    else:
        output_file = Path(output_path).resolve()

    if verbose:
        print(f"[INFO] Processing: {input_file}")
        print(f"[INFO] Output: {output_file}")

    try:
        # Read Markdown content
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Extract headings
        headings = extract_headings(md_content)

        if verbose:
            print(f"\n[INFO] Found {len(headings)} headings")

        if not headings:
            print("[WARNING] No headings found in Markdown file. No TOC will be added.", file=sys.stderr)
            # Still write the file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"\n[INFO] File copied without TOC: {output_file}")
            return 0

        # Generate IDs for headings
        existing_ids = set(h['custom_id'] for h in headings if h.get('custom_id'))
        for heading in headings:
            if heading.get('custom_id'):
                heading['id'] = heading['custom_id']
            else:
                heading['id'] = generate_id(heading['text'], existing_ids)

            if verbose:
                try:
                    level_str = '#' * heading['level']
                    print(f"  {level_str} {heading['text']} (#{heading['id']})")
                except UnicodeEncodeError:
                    # Fallback for Windows console
                    safe_text = heading['text'].encode('ascii', 'replace').decode('ascii')
                    level_str = '#' * heading['level']
                    print(f"  {level_str} {safe_text} (#{heading['id']})")

        # Generate TOC
        toc_md = generate_toc_markdown(headings, min_level, max_level)

        # Add anchors to headings
        md_with_anchors = add_anchors_to_headings(md_content, headings)

        # Combine TOC + content
        final_content = toc_md + '\n' + md_with_anchors

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)

        filtered_count = len([h for h in headings if min_level <= h['level'] <= max_level])

        print(f"\n{'='*70}")
        print(f"[SUCCESS] Markdown with TOC created: {output_file}")
        print(f"{'='*70}")
        print(f"Total headings found:     {len(headings)}")
        print(f"Headings in TOC:          {filtered_count}")
        print(f"Heading level range:      {min_level} - {max_level}")

        # Calculate file size
        file_size = output_file.stat().st_size
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        elif file_size > 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size} bytes"

        print(f"Output file size:         {size_str}")
        print(f"{'='*70}\n")

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to add TOC: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def register_add_toc4md_command(subparsers):
    """
    Register the add-toc4md command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'add-toc4md',
        help='Add a table of contents to a Markdown file',
        description='Parse Markdown file, extract headings (# to ######), and add a hierarchical table of contents with anchor links.'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Markdown file to process'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output Markdown file path (default: <input>-tocced.md)'
    )

    parser.add_argument(
        '--min-level',
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5, 6],
        help='Minimum heading level to include in TOC (default: 1)'
    )

    parser.add_argument(
        '--max-level',
        type=int,
        default=6,
        choices=[1, 2, 3, 4, 5, 6],
        help='Maximum heading level to include in TOC (default: 6)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: add_toc_to_markdown(
        args.input,
        args.output,
        args.min_level,
        args.max_level,
        args.verbose
    ))


if __name__ == '__main__':
    # Allow running as standalone script
    import argparse
    parser = argparse.ArgumentParser(
        description="Add a table of contents to a Markdown file"
    )
    parser.add_argument('input', help='Markdown file to process')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--min-level', type=int, default=1, choices=[1, 2, 3, 4, 5, 6])
    parser.add_argument('--max-level', type=int, default=6, choices=[1, 2, 3, 4, 5, 6])
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    sys.exit(add_toc_to_markdown(
        args.input,
        args.output,
        args.min_level,
        args.max_level,
        args.verbose
    ))
