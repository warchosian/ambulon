"""
Core logic for concatenating HTML files from a directory into a single HTML file in Ambulon.
Handles file collection, natural sorting, internal link replacement, and HTML wrapping.
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


class FirstHeadingExtractor(HTMLParser):
    """HTML Parser to extract the first H1 heading ID and text from HTML content."""

    def __init__(self):
        super().__init__()
        self.first_h1_id = None
        self.first_h1_text = None
        self.found = False
        self.in_h1 = False
        self.h1_text_parts = []
        self.reset() # Call reset to properly initialize HTMLParser internal state

    def reset(self):
        super().reset()
        self.first_h1_id = None
        self.first_h1_text = None
        self.found = False
        self.in_h1 = False
        self.h1_text_parts = []

    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        if not self.found and tag == 'h1':
            attrs_dict = dict(attrs)
            self.first_h1_id = attrs_dict.get('id', None)
            self.in_h1 = True
            self.h1_text_parts = []

    def handle_endtag(self, tag):
        """Handle closing tags."""
        if tag == 'h1' and self.in_h1:
            self.first_h1_text = ''.join(self.h1_text_parts).strip()
            self.in_h1 = False
            self.found = True

    def handle_data(self, data):
        """Handle text data."""
        if self.in_h1:
            self.h1_text_parts.append(data)


def generate_id_from_text(text: str) -> str:
    """
    Generate an ID from heading text (same algorithm as add_toc).

    Args:
        text: Heading text

    Returns:
        Generated ID string
    """
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    base_id = re.sub(r'[^\w\s-]', '', text.lower())
    base_id = re.sub(r'[-\s]+', '-', base_id).strip('-')
    return base_id


def extract_first_heading_id(html_content: str) -> Optional[str]:
    """
    Extract or generate the ID of the first H1 heading from HTML content.

    Args:
        html_content: HTML content as string

    Returns:
        ID of first H1 heading (existing or generated), or None if no H1 found
    """
    parser = FirstHeadingExtractor()
    try:
        parser.feed(html_content)
        parser.close() # Important to close parser

        # If we found an H1
        if parser.found:
            # Use existing ID if present, otherwise generate from text
            if parser.first_h1_id:
                return parser.first_h1_id
            elif parser.first_h1_text:
                return generate_id_from_text(parser.first_h1_text)

        return None
    except Exception as e:
        logger.debug(f"Error extracting first heading ID: {e}")
        return None


def build_filename_to_id_map(html_files: List[Path]) -> Dict[str, str]:
    """
    Build a mapping of filename to first heading ID.

    Args:
        html_files: List of HTML file paths

    Returns:
        Dictionary mapping filename (with and without .html) to heading ID
    """
    filename_map = {}

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            heading_id = extract_first_heading_id(content)
            if heading_id:
                # Map both "page1.html" and "page1" to the heading ID
                filename_map[html_file.name] = heading_id
                filename_map[html_file.stem] = heading_id  # stem = filename without extension
        except Exception as e:
            logger.warning(f"Could not process {html_file.name} for ID map: {e}")
            continue

    return filename_map

def replace_internal_links(html_content: str, filename_map: Dict[str, str]) -> str:
    """
    Replace inter-page links with internal section links.

    Converts href="page2.html" to href="#big-data-pipelines" based on filename_map.

    Args:
        html_content: HTML content with inter-page links
        filename_map: Mapping of filenames to heading IDs

    Returns:
        HTML content with internal links
    """
    def replace_link(match):
        href = match.group(1)

        # Check if this is a link to one of the concatenated files
        for filename, heading_id in filename_map.items():
            if href == filename or href == f"./{filename}":
                # Replace with internal anchor link
                return f'href="#{heading_id}"'

        # Not a match, keep original
        return match.group(0)

    # Pattern to match href="..." or href='...'
    pattern = r'href=["\']([^"\']+)["\']'
    return re.sub(pattern, replace_link, html_content)

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

def collect_html_files(directory: Path, output_file: Path, verbose: bool = False) -> List[Path]:
    """
    Collect HTML files from directory, excluding the output file.

    Args:
        directory: Directory to scan
        output_file: Output file to exclude
        verbose: Print progress

    Returns:
        List of HTML file paths sorted in natural order
    """
    html_files = []

    # Get all HTML files
    for file_path in directory.glob('*.html'):
        # Skip the output file if it exists in the same directory
        if file_path.resolve() == output_file.resolve():
            logger.debug(f"Excluding output file: {file_path.name}")
            continue

        html_files.append(file_path)

    # Sort using natural sort
    html_files.sort(key=lambda f: natural_sort_key(f.name))

    logger.info(f"Found {len(html_files)} HTML files to concatenate.")
    if verbose:
        for i, f in enumerate(html_files, 1):
            logger.debug(f"  {i}. {f.name}")

    return html_files

def extract_body_content(html_content: str) -> str:
    """
    Extract content from HTML body tag, or return full content if no body tag.

    Args:
        html_content: HTML content as string

    Returns:
        Body content or full content
    """
    # Try to extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)

    if body_match:
        return body_match.group(1)
    else:
        # No body tag, return content without html/head tags
        # Remove DOCTYPE
        content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
        # Remove html tags
        content = re.sub(r'</?html[^>]*>', '', content, flags=re.IGNORECASE)
        # Remove head section
        content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
        return content.strip()


def create_html_wrapper(title: str = "Concatenated HTML") -> Tuple[str, str]:
    """
    Create HTML document wrapper (header and footer).

    Args:
        title: Document title

    Returns:
        Tuple of (header, footer) strings
    """
    header = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }}

        .html-file-section {{
            background: white;
            margin: 2rem 0;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .html-file-header {{
            background: #2196F3;
            color: white;
            padding: 1rem 1.5rem;
            margin: -2rem -2rem 2rem -2rem;
            border-radius: 8px 8px 0 0;
            font-size: 1.2rem;
            font-weight: bold;
        }}

        .html-file-separator {{
            border: none;
            border-top: 3px solid #e0e0e0;
            margin: 3rem 0;
        }}
    </style>
</head>
<body>
"""

    footer = """
</body>
</html>
"""

    return header, footer

def concatenate_html_files_logic(
    directory: Path,
    output_file: Path,
    include_headers: bool = True,
    title: str = "Concatenated HTML",
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to concatenate HTML files from a directory into a single file.

    Args:
        directory: Directory containing HTML files
        output_file: Output file path
        include_headers: Add headers showing source file names
        title: Title for the concatenated document

    Returns:
        A tuple: (exit_code: int, generated_path: Optional[Path])
    """
    # Validate directory
    if not directory.exists():
        logger.error(f"Error: Directory '{directory}' does not exist.")
        return 1, None

    if not directory.is_dir():
        logger.error(f"Error: '{directory}' is not a directory.")
        return 1, None

    logger.info(f"Scanning directory: {directory}")
    logger.info(f"Output file: {output_file}")

    try:
        # Collect HTML files
        html_files = collect_html_files(directory, output_file)

        if not html_files:
            logger.warning(f"No HTML files found in {directory}. Nothing to concatenate.")
            return 1, None

        # Build filename to heading ID mapping for internal link conversion
        logger.info(f"Building internal link map...")
        filename_map = build_filename_to_id_map(html_files)
        logger.debug(f"Found {len(filename_map) // 2 if filename_map else 0} file-to-section mappings.")

        # Create output
        header, footer = create_html_wrapper(title)

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as out_file:
            # Write header
            out_file.write(header)

            # Concatenate files
            for i, html_file in enumerate(html_files, 1):
                logger.info(f"Processing {i}/{len(html_files)}: {html_file.name}")

                try:
                    # Read file
                    with open(html_file, 'r', encoding='utf-8') as in_file:
                        content = in_file.read()

                    # Extract body content
                    body_content = extract_body_content(content)

                    # Replace inter-page links with internal section links
                    body_content = replace_internal_links(body_content, filename_map)

                    # Add section wrapper
                    out_file.write(f'\n<!-- Source: {html_file.name} -->\n')
                    out_file.write('<div class="html-file-section">\n')

                    if include_headers:
                        out_file.write(f'<div class="html-file-header">📄 {html_file.name}</div>\n')

                    out_file.write(body_content)
                    out_file.write('\n</div>\n')

                    # Add separator except for last file
                    if i < len(html_files):
                        out_file.write('<hr class="html-file-separator">\n')

                except Exception as e:
                    logger.error(f"Failed to process {html_file.name}: {e}")
                    continue

            # Write footer
            out_file.write(footer)

        logger.info(f"Concatenated {len(html_files)} files into: {output_file}.")

        # Show file size
        output_size = output_file.stat().st_size
        logger.info(f"Output file size: {output_size:,} bytes ({output_size / 1024:.1f} KB).")

        return 0, output_file

    except Exception as e:
        logger.error(f"Error: Concatenation failed: {e}", exc_info=True)
        return 1, None
