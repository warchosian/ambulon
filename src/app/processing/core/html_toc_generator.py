"""
Core logic for adding a Table of Contents (TOC) to HTML files in Ambulon.
Parses HTML, extracts headings, generates hierarchical TOC with anchor links,
and injects CSS for styling.
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Set, Dict, Any
from html.parser import HTMLParser
import urllib.parse

logger = logging.getLogger(__name__)


class HeadingExtractor(HTMLParser):
    """HTML Parser to extract headings and their content."""

    def __init__(self):
        super().__init__()
        self.headings = []
        self.current_heading: Optional[Dict[str, Any]] = None
        self.current_level: Optional[int] = None
        self.capture_data = False
        self.reset() # Call reset to properly initialize HTMLParser internal state

    def reset(self):
        super().reset()
        self.headings = []
        self.current_heading = None
        self.current_level = None
        self.capture_data = False

    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_level = int(tag[1])
            # Get existing id if present
            attrs_dict = dict(attrs)
            heading_id = attrs_dict.get('id', '')
            self.current_heading = {
                'level': self.current_level,
                'text': '',
                'id': heading_id,
                'tag': tag
            }
            self.capture_data = True

    def handle_endtag(self, tag):
        """Handle closing tags."""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and self.current_heading:
            self.headings.append(self.current_heading)
            self.current_heading = None
            self.capture_data = False

    def handle_data(self, data):
        """Handle text data."""
        if self.capture_data and self.current_heading is not None:
            self.current_heading['text'] += data.strip()


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


def generate_toc_html(headings: List[Dict[str, Any]]) -> str:
    """
    Generate HTML for table of contents.

    Args:
        headings: List of heading dictionaries

    Returns:
        HTML string for TOC
    """
    if not headings:
        return ""

    toc_html = ['<nav id="table-of-contents" class="table-of-contents">', '<h2>Table des matières</h2>']

    # Build hierarchical structure
    current_level = 0
    # Add a sentinel to ensure all lists are closed
    processed_headings = headings + [{'level': 0, 'text': '', 'id': ''}]

    for heading in processed_headings:
        level = heading['level']
        text = heading['text']
        heading_id = heading['id']

        # Skip if no text and not a sentinel
        if not text and level != 0:
            continue

        if level > current_level:
            for _ in range(level - current_level):
                toc_html.append('<ul>')
        elif level < current_level:
            for _ in range(current_level - level):
                toc_html.append('</li>')
                toc_html.append('</ul>')
        elif level == current_level and current_level > 0:
            toc_html.append('</li>')

        if level != 0: # Only add list item for real headings
            # Add TOC item with anchor for back-navigation (works in both HTML and Markdown)
            toc_id = f'toc-{heading_id}'
            # Check if heading_id is valid for an href
            safe_heading_id = urllib.parse.quote(heading_id) if heading_id else ""
            toc_html.append(f'<li><a id="{toc_id}"></a><a href="#{safe_heading_id}">{text}</a>')

        current_level = level

    toc_html.append('</nav>')

    return '\n'.join(toc_html)


def add_ids_to_headings(html_content: str, headings: List[Dict[str, Any]]) -> str:
    """
    Add IDs to headings in HTML content and add back-to-TOC links.

    Args:
        html_content: Original HTML content
        headings: List of headings with generated IDs

    Returns:
        Modified HTML content with IDs and back-links added
    """
    # Create a list of (tag, original_text, id, toc_id) tuples for easy lookup
    heading_replacements: List[Tuple[str, str, str, str]] = []
    for heading in headings:
        if heading['id'] and not heading.get('had_id', False):  # Only process headings that got new IDs
            # Use original text to match, so we need to rebuild original HTML
            # This approach is less error-prone than regex with non-unique text
            heading_replacements.append((
                heading['tag'],
                heading['text'],
                heading['id'],
                f'toc-{heading["id"]}'
            ))
    
    # Process from deepest headings to shallowest to avoid conflicts with outer tags
    # Or, a simpler approach for unique IDs: just iterate and replace
    modified_html_content = html_content
    for heading_data in reversed(heading_replacements): # Reversed to avoid index shifting if not careful
        tag, original_text, heading_id, toc_id = heading_data
        
        # Regex to find the *first* occurrence of this specific heading without an ID
        # This is a bit tricky, might need more robust HTML parsing for complex cases.
        # For simple cases, replace <hX>Content</hX> with <hX id="Y">Content</hX>
        # Pattern must be careful not to match headings *already* having an ID
        # Also need to handle cases where the text might contain regex special chars
        
        # Escape original_text for regex
        escaped_text = re.escape(original_text)
        
        # Pattern: <hX>(TEXT)</hX> without an existing ID on the hX tag
        # Use a negative lookahead to ensure no 'id="..."' in the opening tag
        pattern = re.compile(rf'(<{tag}(?![^>]*\bid\s*=))(>{escaped_text}</{tag}>)', re.IGNORECASE)

        # Replace only the first non-ID'd occurrence found in a robust manner
        def repl(match):
            # This ensures we only add the ID once
            back_link = f' <a href="#{toc_id}" class="back-to-toc" title="Retour à la table des matières">&#8617;</a></{tag}>'
            closing_tag = f'</{tag}>'
            return f'{match.group(1)} id="{heading_id}"{match.group(2).replace(closing_tag, back_link)}'

        # Only replace if this heading doesn't already have an ID.
        # This is a basic approach and could be improved with a proper HTML tree modification.
        # For simplicity here, we assume if the heading_id is in the HTML, it's already processed.
        if f'id="{heading_id}"' not in modified_html_content:
            modified_html_content = pattern.sub(repl, modified_html_content, count=1)
        
    return modified_html_content


def get_toc_css() -> str:
    """
    Get CSS styles for table of contents with back-navigation.

    Returns:
        CSS string
    """
    return """
    /* Table of Contents Styles */
    .table-of-contents {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        margin: 30px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .table-of-contents h2 {
        margin-top: 0;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }

    .table-of-contents ul {
        list-style-type: none;
        padding-left: 0;
        margin: 10px 0;
    }

    .table-of-contents ul ul {
        padding-left: 20px;
        margin-top: 5px;
    }

    .table-of-contents li {
        margin: 8px 0;
        line-height: 1.6;
    }

    .table-of-contents a {
        color: #3498db;
        text-decoration: none;
        transition: color 0.2s;
    }

    .table-of-contents a:hover {
        color: #2980b9;
        text-decoration: underline;
    }

    /* Back-to-TOC links next to headings */
    .back-to-toc {
        font-size: 0.7em;
        color: #95a5a6;
        text-decoration: none;
        margin-left: 10px;
        opacity: 0.6;
        transition: opacity 0.2s, color 0.2s;
        vertical-align: super;
    }

    .back-to-toc:hover {
        opacity: 1;
        color: #3498db;
        text-decoration: none;
    }

    h1:hover .back-to-toc,
    h2:hover .back-to-toc,
    h3:hover .back-to-toc,
    h4:hover .back-to-toc,
    h5:hover .back-to-toc,
    h6:hover .back-to-toc {
        opacity: 1;
    }

    /* Floating TOC button */
    .floating-toc-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: #3498db;
        color: white;
        padding: 12px 18px;
        border-radius: 50px;
        text-decoration: none;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: background 0.3s, transform 0.2s;
        z-index: 1000;
    }

    .floating-toc-btn:hover {
        background: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        text-decoration: none;
    }

    /* Smooth scrolling for anchor links */
    html {
        scroll-behavior: smooth;
    }

    /* Highlight target when navigating */
    .table-of-contents li:target {
        background: #fff3cd;
        border-radius: 4px;
        transition: background 0.5s;
    }
    """


def add_toc_to_html_logic(
    input_file: Path,
    output_file: Path,
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to add a table of contents to an HTML file.

    Args:
        input_file: Path to input HTML file
        output_file: Path to output HTML file

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
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        logger.debug(f"HTML file size: {len(html_content):,} bytes")

        # Extract headings
        parser = HeadingExtractor()
        parser.feed(html_content)
        headings = parser.headings
        parser.close() # Important to call close for some parsers to finalize processing

        logger.info(f"Found {len(headings)} headings")

        if not headings:
            logger.warning("No headings found in HTML file. No TOC will be added.")
            # Still write the file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"File copied without TOC: {output_file}")
            return 0, output_file

        # Generate IDs for headings that don't have them
        existing_ids = set(h['id'] for h in headings if h['id'])
        for heading in headings:
            if heading['id']:
                heading['had_id'] = True  # Mark that this heading already had an ID
            else:
                heading['id'] = generate_id(heading['text'], existing_ids)
                heading['had_id'] = False  # Mark that we generated this ID
            logger.debug(f"  {heading['tag'].upper()}: {heading['text']} (#{heading['id']})")

        # Add IDs to headings in HTML
        html_content = add_ids_to_headings(html_content, headings)

        # Generate TOC HTML
        toc_html = generate_toc_html(headings)

        # Add TOC CSS if not already present
        if '<style>' in html_content and '.table-of-contents' not in html_content:
            # Insert CSS before </style>
            toc_css = get_toc_css()
            html_content = html_content.replace('</style>', f'{toc_css}\n    </style>')
            logger.debug("TOC CSS injected into existing style block.")
        elif '<head>' in html_content and '<style>' not in html_content:
            # Add style section in head
            toc_css = get_toc_css()
            style_section = f'<style>{toc_css}</style>\n</head>'
            html_content = html_content.replace('</head>', style_section)
            logger.debug("TOC CSS injected as a new style block in head.")
        else:
            logger.warning("No </head> or <style> tag found for CSS injection. CSS will be added at the beginning of the body.")
            # Prepend CSS to the head or body if head/style are missing
            if '<head>' in html_content:
                html_content = html_content.replace('<head>', f'<head>\n<style>{get_toc_css()}</style>')
            elif '<body>' in html_content:
                html_content = html_content.replace('<body>', f'<body>\n<style>{get_toc_css()}</style>')
            else:
                html_content = f'<style>{get_toc_css()}</style>\n' + html_content


        # Insert TOC after <body> tag or at the beginning of body content
        if '<body>' in html_content:
            html_content = html_content.replace('<body>', f'<body>\n{toc_html}\n', 1)
            logger.debug("TOC HTML injected after <body> tag.")
        elif '<body' in html_content:
            # Handle <body> with attributes
            body_pattern = r'(<body[^>]*>)'
            html_content = re.sub(body_pattern, f'\g<1>\n{toc_html}\n', html_content, count=1)
            logger.debug("TOC HTML injected after <body> tag (with attributes).")
        else:
            # No body tag, just prepend
            html_content = toc_html + '\n' + html_content
            logger.warning("No <body> tag found. TOC HTML prepended to content.")

        # Add floating TOC button before </body>
        floating_btn = '<a href="#table-of-contents" class="floating-toc-btn" title="Retour à la table des matières">↑ TOC</a>'
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{floating_btn}\n</body>', 1)
            logger.debug("Floating TOC button injected before </body> tag.")
        else:
            # No body tag, add at the end
            html_content = html_content + '\n' + floating_btn
            logger.warning("No <body> tag found. Floating TOC button appended to content.")

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML with TOC created: {output_file}")
        logger.info(f"Added table of contents with {len(headings)} entries.")

        return 0, output_file

    except Exception as e:
        logger.error(f"Error: Failed to add TOC: {e}", exc_info=True)
        return 1, None
