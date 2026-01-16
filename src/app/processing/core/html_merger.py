"""
Core logic for merging multiple HTML files into a single document in Ambulon.
Handles file collection, natural sorting, internal link adaptation, TOC generation,
and HTML wrapping.
"""

import sys
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any
from html.parser import HTMLParser

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
        filename: Original filename (e.g., "section.page.html")

    Returns:
        Anchor ID (e.g., "section-page")
    """
    stem = Path(filename).stem
    return sanitize_anchor(stem)


def extract_body_content(html_content: str) -> str:
    """
    Extract content from <body> tag of HTML.

    Args:
        html_content: Full HTML content

    Returns:
        Content inside <body> tags, or full content if no body tags found
    """
    # Try to extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)

    if body_match:
        return body_match.group(1).strip()

    # If no body tag found, return content without html/head tags
    # Remove DOCTYPE
    content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
    # Remove html tags
    content = re.sub(r'</?html[^>]*>', '', content, flags=re.IGNORECASE)
    # Remove head section
    content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
    return content.strip()


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


def collect_html_files_for_merging(
    source_dir: Path,
) -> List[Tuple[Path, str]]:
    """
    Collect all .html files and sort them alphabetically.

    Args:
        source_dir: Source directory with .html files

    Returns:
        List of (file_path, filename) tuples sorted alphabetically
    """
    html_files = []

    for html_file in source_dir.glob('*.html'):
        html_files.append((html_file, html_file.name))

    # Sort alphabetically by filename
    html_files.sort(key=lambda x: natural_sort_key(x[1]))

    logger.info(f"Found {len(html_files)} HTML files to merge.")

    return html_files


def adapt_links_for_fusion(
    content: str,
    current_file: str,
    file_anchors: Dict[str, str],
) -> str:
    """
    Adapt HTML links to work in fused document.

    Internal links to other .html files are converted to anchor links.
    External links and anchor-only links are preserved.

    Args:
        content: HTML content
        current_file: Current filename
        file_anchors: Mapping of filename → anchor ID

    Returns:
        Content with adapted links
    """
    # Pattern to match href attributes in HTML
    link_pattern = r'href=["\']([^"\\]+)["\\]'

    adapted_count = 0

    def replace_link(match):
        nonlocal adapted_count

        href = match.group(1)

        # Skip absolute URLs (http://, https://, etc.)
        if '://' in href or href.startswith('//'):
            return match.group(0)

        # Check if it's an anchor-only link
        if href.startswith('#'):
            return match.group(0)

        # Parse the link (might have anchor)
        if '#' in href:
            link_file, anchor = href.split('#', 1)
        else:
            link_file = href
            anchor = ''

        # Skip empty links
        if not link_file:
            return match.group(0)

        # Check if this is a link to another .html file
        if link_file.endswith('.html') or link_file.endswith('.htm'):
            # Get the target anchor
            if link_file in file_anchors:
                target_anchor = file_anchors[link_file]

                # If there's an additional anchor, append it
                if anchor:
                    new_link = f"#{target_anchor}-{anchor}"
                else:
                    new_link = f"#{target_anchor}"

                adapted_count += 1
                logger.debug(f"Adapted link in {current_file}: '{href}' -> '{new_link}'")
                return f'href="{new_link}"'

        # Keep link as is (external or other)
        return match.group(0)

    adapted_content = re.sub(link_pattern, replace_link, content)

    if adapted_count > 0:
        logger.debug(f"File {current_file}: {adapted_count} links adapted.")

    return adapted_content


def generate_table_of_contents(
    files: List[Tuple[Path, str]],
    file_anchors: Dict[str, str]
) -> str:
    """
    Generate HTML table of contents for the fused document.

    Args:
        files: List of (file_path, filename) tuples
        file_anchors: Mapping of filename → anchor ID

    Returns:
        Table of contents as HTML
    """
    toc_lines = [
        '<div class="toc">',
        '<h1>📚 Table des matières</h1>',
        '<p><em>Document fusionné généré automatiquement</em></p>',
        '<ul>',
    ]

    for file_path, filename in files:
        anchor = file_anchors[filename]
        stem = Path(filename).stem

        # Create a readable title from the filename
        title = stem.replace('.', ' › ')

        toc_lines.append(f'  <li><a href="#{anchor}">{title}</a></li>')

    toc_lines.append('</ul>')
    toc_lines.append('</div>')
    toc_lines.append('<hr>')

    return '\n'.join(toc_lines)


def create_section_separator(filename: str, anchor: str) -> str:
    """
    Create a section separator with file identification.

    Args:
        filename: Original filename
        anchor: Anchor ID for this section

    Returns:
        Section separator as HTML
    """
    stem = Path(filename).stem
    title = stem.replace('.', ' › ')

    separator = [
        '<hr>',
        f'<div id="{anchor}" class="section">',
        f'  <h2>📄 {title}</h2>',
        f'  <p class="source"><strong>Source :</strong> <code>{filename}</code></p>',
        '</div>',
    ]

    return '\n'.join(separator)


def create_html_document(content: str, title: str = "Merged Document") -> str:
    """
    Wrap content in a complete HTML document structure.

    Args:
        content: HTML content to wrap
        title: Document title

    Returns:
        Complete HTML document
    """
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        .toc {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .toc h1 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 8px 0;
        }}
        .toc a {{
            color: #3498db;
            text-decoration: none;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
        .section {{
            margin-top: 40px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .source {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: -10px;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 40px 0;
        }}
        code {{
            background: #f8f8f8;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""


def fusion_html_files_logic(
    source_dir: Path,
    output_file: Path,
    include_headers: bool = True,
    title: str = "Concatenated HTML",
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to merge multiple HTML files into a single fused document.

    Args:
        source_dir: Source directory with .html files
        output_file: Output file path
        include_headers: Add headers showing source file names
        title: Title for the concatenated document

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

    # Collect all .html files
    files = collect_html_files_for_merging(source_path)

    if not files:
        logger.warning(f"No HTML files found in '{source_dir}'. Nothing to merge.")
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
    merged_sections = [toc]
    success_count = 0
    error_count = 0

    for file_path, filename in files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract body content
            body_content = extract_body_content(content)

            # Adapt links
            adapted_content = adapt_links_for_fusion(
                body_content,
                filename,
                file_anchors,
            )

            # Create section separator
            anchor = file_anchors[filename]
            separator = create_section_separator(filename, anchor)

            # Add to merged content
            merged_sections.append(separator)
            merged_sections.append(adapted_content)

            success_count += 1
            logger.info(f"Processed: {filename}")

        except Exception as e:
            error_count += 1
            logger.error(f"Failed to process {filename}: {e}", exc_info=True)

    # Create complete HTML document
    merged_content = '\n'.join(merged_sections)
    full_html = create_html_document(merged_content, title=title)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write merged file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)

        logger.info(f"Merged content written to {output_file}.")

    except Exception as e:
        logger.error(f"Failed to write output file: {e}", exc_info=True)
        return 1, None

    # Summary
    logger.info("="*70)
    logger.info("HTML Merging complete")
    logger.info("="*70)
    logger.info(f"Files merged:     {success_count}/{len(files)}")
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
