"""
Markdown to HTML conversion utilities.

Core functions for converting Markdown content to HTML,
separated from the CLI command for reusability.
"""

import re
from typing import Optional


def markdown_to_html_basic(content: str, add_toc_backlinks: bool = False) -> str:
    """
    Basic markdown to HTML conversion for common elements.

    Supports:
    - Headers (# to ####) with anchor IDs
    - Bold (**text**) and italic (*text*)
    - Inline code (`code`)
    - Code blocks (```lang...```)
    - Links ([text](url))
    - Tables
    - Lists (unordered)
    - Blockquotes
    - Horizontal rules
    - TOC generation with [TOC]

    Args:
        content: Markdown content
        add_toc_backlinks: Add back-to-TOC links (↑) after each heading

    Returns:
        HTML content
    """
    # Clean anchor tags with empty href attributes
    content = re.sub(r'<a\s+id="([^"]+)"\s+href=""\s*></a>', r'<a id="\1"></a>', content)

    # Convert markdown links BEFORE protecting HTML
    def convert_md_link(match):
        text = match.group(1)
        url = match.group(2)
        if url.endswith('.md'):
            url = url[:-3] + '.html'
        return f'<a href="{url}">{text}</a>'

    content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', convert_md_link, content)

    # Protect HTML tags
    html_tags = {}
    def save_html_tag(match):
        placeholder = f'___HTML_TAG_{len(html_tags)}___'
        html_tags[placeholder] = match.group(0)
        return placeholder

    content = re.sub(r'<a\s+id="[^"]+"\s*></a>', save_html_tag, content)
    content = re.sub(r'<a\s+href="[^"]+">.*?</a>', save_html_tag, content)
    content = re.sub(r'<details[^>]*>.*?</details>', save_html_tag, content, flags=re.DOTALL)
    content = re.sub(r'</?(?:summary|div)[^>]*>', save_html_tag, content)

    # Protect code blocks (including excalidraw blocks which need special handling)
    code_block_pattern = r'(`{3,})([^\n`]*)\n(.*?)\1(?:\n|$)'
    code_blocks = {}
    excalidraw_blocks = {}
    
    def save_code_block(match):
        lang = match.group(2).strip() or ''
        code = match.group(3)
        
        # Handle excalidraw blocks specially
        if lang.lower() == 'excalidraw':
            placeholder = f'___EXCALIDRAW_BLOCK_{len(excalidraw_blocks)}___'
            excalidraw_blocks[placeholder] = code.strip()
            return placeholder
        
        placeholder = f'___CODE_BLOCK_{len(code_blocks)}___'
        code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        code_blocks[placeholder] = f'<pre><code class="language-{lang}">{code_escaped}</code></pre>'
        return placeholder

    content = re.sub(code_block_pattern, save_code_block, content, flags=re.DOTALL)

    # Convert tables
    table_pattern = r'(\|.+\|[\r\n]+\|[\s\-:|]+\|[\r\n]+(?:\|.+\|[\r\n]+)*)'
    tables = re.findall(table_pattern, content, re.MULTILINE)
    table_placeholders = {}

    for i, table in enumerate(tables):
        placeholder = f'___TABLE_PLACEHOLDER_{i}___'
        table_placeholders[placeholder] = convert_markdown_table(table)
        content = content.replace(table, placeholder, 1)

    # Generate TOC
    # 1. If [TOC] marker present, replace it (and surrounding formatting like **)
    # 2. If TOC already exists (## Table des matières), don't generate another one
    # 3. Otherwise, auto-insert after first H1 (to keep title/version/date before TOC)
    toc_html = ''
    has_toc_marker = '[TOC]' in content
    
    # Check if TOC already exists in the markdown (from add-toc4md)
    # Pattern to match ## Table des matieres/matieres (with or without accent)
    toc_exists_pattern = r'^##\s+Table des mati'
    has_existing_toc = re.search(toc_exists_pattern, content, re.MULTILINE | re.IGNORECASE)
    
    if has_existing_toc:
        # TOC already exists in markdown (from add-toc4md), don't generate another one
        # But still remove [TOC] marker if present
        if has_toc_marker:
            content = re.sub(r'\*\*\[TOC\]\*\*', '', content)
            content = re.sub(r'\*\[TOC\]\*', '', content)
            content = re.sub(r'\[TOC\]', '', content)
        toc_html = ''
    elif has_toc_marker:
        toc_html = generate_toc(content)
        # Replace [TOC] even if surrounded by formatting (**, *, __, _)
        content = re.sub(r'\*?\*?\[TOC\]\*?\*?', '___TOC_PLACEHOLDER___', content)
        content = re.sub(r'_?\_?\[TOC\]_?\_?', '___TOC_PLACEHOLDER___', content)
    else:
        # Auto-insert TOC after first H1
        toc_html = generate_toc(content)
        if toc_html:
            # Find first H1 and insert TOC after it
            h1_pattern = r'^(# .+)$'
            h1_match = re.search(h1_pattern, content, re.MULTILINE)
            if h1_match:
                h1_end = h1_match.end()
                # Find the end of the line (including following metadata lines)
                lines = content.split('\n')
                h1_line_idx = content[:h1_end].count('\n')
                insert_idx = h1_line_idx + 1
                
                # Skip empty lines and metadata lines after H1
                while insert_idx < len(lines):
                    line = lines[insert_idx].strip()
                    if not line:
                        insert_idx += 1
                        break  # Keep one empty line as separator
                    if any(line.startswith(prefix) for prefix in ['Version', 'Date', 'Auteur', 'Author', 'Mise à jour', 'Updated']):
                        insert_idx += 1
                    else:
                        break
                
                # Insert TOC placeholder at the calculated position
                lines.insert(insert_idx, '___TOC_PLACEHOLDER___')
                content = '\n'.join(lines)

    # Convert headings
    def convert_heading(match, level):
        text = match.group(1).strip()
        
        # Extract existing backlink [↑](#toc-xxx) if present
        # Use Unicode escape sequence to avoid encoding issues
        import unicodedata
        up_arrow = '\u2191'  # ↑ character
        backlink_pattern = r'\s*\[' + up_arrow + r'\]\(#toc-[^)]+\)\s*'
        backlink_match = re.search(backlink_pattern, text)
        existing_backlink = backlink_match.group(0) if backlink_match else None
        if backlink_match:
            text = text[:backlink_match.start()] + text[backlink_match.end():]
            text = text.strip()
        
        # Extract custom ID {#id} if present
        id_match = re.search(r'\s*\{#([a-z0-9\-_]+)\}\s*$', text, re.IGNORECASE)
        if id_match:
            heading_id = id_match.group(1)
            text = text[:id_match.start()].strip()
        else:
            heading_id = re.sub(r'[^\w\s-]', '', text.lower())
            heading_id = re.sub(r'[\s_]+', '-', heading_id).strip('-')

        # Build HTML
        if add_toc_backlinks:
            backlink_html = f' <a href="#table-of-contents" class="back-to-toc" title="Retour à la table des matières">&uarr;</a>'
            return f'<h{level} id="{heading_id}">{text}{backlink_html}</h{level}>'
        else:
            # Preserve existing backlink from markdown if not adding new ones
            if existing_backlink:
                # Convert markdown backlink to HTML
                backlink_url = re.search(r'\(#([^)]+)\)', existing_backlink).group(1)
                backlink_html = f' <a href="#{backlink_url}">&uarr;</a>'
                return f'<h{level} id="{heading_id}">{text}{backlink_html}</h{level}>'
            else:
                return f'<h{level} id="{heading_id}">{text}</h{level}>'

    content = re.sub(r'^# (.+)$', lambda m: convert_heading(m, 1), content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', lambda m: convert_heading(m, 2), content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', lambda m: convert_heading(m, 3), content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', lambda m: convert_heading(m, 4), content, flags=re.MULTILINE)

    # TOC placeholder will be replaced after paragraph conversion

    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)

    # Convert blockquotes and lists
    lines = content.split('\n')
    result_lines = []
    in_blockquote = False
    blockquote_lines = []
    in_list = False

    for line in lines:
        if line.startswith('> '):
            if not in_blockquote:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                in_blockquote = True
            blockquote_lines.append(line[2:])
        elif re.match(r'^[-*+] ', line):
            if in_blockquote:
                result_lines.append('<blockquote>')
                result_lines.extend(blockquote_lines)
                result_lines.append('</blockquote>')
                blockquote_lines = []
                in_blockquote = False
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            item = re.sub(r'^[-*+] ', '', line)
            result_lines.append(f'<li>{item}</li>')
        else:
            if in_blockquote:
                result_lines.append('<blockquote>')
                result_lines.extend(blockquote_lines)
                result_lines.append('</blockquote>')
                blockquote_lines = []
                in_blockquote = False
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)

    if in_blockquote:
        result_lines.append('<blockquote>')
        result_lines.extend(blockquote_lines)
        result_lines.append('</blockquote>')
    if in_list:
        result_lines.append('</ul>')

    content = '\n'.join(result_lines)

    # Convert horizontal rules
    content = re.sub(r'^---$', r'<hr>', content, flags=re.MULTILINE)

    # Convert paragraphs
    paragraphs = content.split('\n\n')
    new_paragraphs = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Skip if already HTML block
        if para.startswith('___'):
            new_paragraphs.append(para)
            continue
        if re.match(r'^<(table|ul|ol|blockquote|pre|h[1-6]|nav|div|figure)', para):
            new_paragraphs.append(para)
            continue
        if para.startswith('</'):
            new_paragraphs.append(para)
            continue

        # Replace single newlines with <br>
        para = para.replace('\n', '<br>\n')
        new_paragraphs.append(f'<p>{para}</p>')

    content = '\n\n'.join(new_paragraphs)

    # Restore protected blocks
    for placeholder, code_html in code_blocks.items():
        content = content.replace(placeholder, code_html)

    for placeholder, table_html in table_placeholders.items():
        content = content.replace(placeholder, table_html)

    for placeholder, tag in html_tags.items():
        content = content.replace(placeholder, tag)
    
    # Restore excalidraw blocks as interactive components
    for placeholder, excalidraw_json in excalidraw_blocks.items():
        # Escape the JSON for use in data attribute
        json_escaped = excalidraw_json.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        container_id = f'excalidraw-container-{hash(placeholder) & 0xFFFFFFFF}'
        excalidraw_html = f'''<div class="excalidraw-wrapper">
    <div id="{container_id}" class="excalidraw-container" data-scene="{json_escaped}"></div>
</div>'''
        content = content.replace(placeholder, excalidraw_html)

    # Insert TOC HTML at the end (after all markdown conversions)
    if toc_html:
        content = content.replace('___TOC_PLACEHOLDER___', toc_html)

    return content


def convert_markdown_table(table_text: str) -> str:
    """Convert a markdown table to HTML table."""
    lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]

    if len(lines) < 2:
        return table_text

    header_cells = [cell.strip() for cell in lines[0].split('|')[1:-1]]
    data_rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if cells:
            data_rows.append(cells)

    html = '<table>\n<thead>\n<tr>\n'
    for cell in header_cells:
        html += f'<th>{convert_inline_markdown(cell)}</th>\n'
    html += '</tr>\n</thead>\n<tbody>\n'

    for row in data_rows:
        html += '<tr>\n'
        for cell in row:
            html += f'<td>{convert_inline_markdown(cell)}</td>\n'
        html += '</tr>\n'

    html += '</tbody>\n</table>'
    return html


def convert_inline_markdown(text: str) -> str:
    """Convert inline markdown (bold, italic, code) to HTML."""
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


def generate_toc(content: str, skip_h1: bool = True) -> str:
    """Generate a Table of Contents from markdown headers."""
    toc_items = []
    header_pattern = r'^(#{1,4})\s+(.+?)(?:\s*\{#([a-z0-9\-_]+)\})?\s*$'

    for match in re.finditer(header_pattern, content, re.MULTILINE | re.IGNORECASE):
        level = len(match.group(1))
        text = match.group(2).strip()
        explicit_id = match.group(3)

        # Skip H1 if requested (main title should not be in TOC)
        if skip_h1 and level == 1:
            continue

        if explicit_id:
            heading_id = explicit_id
        else:
            heading_id = re.sub(r'[^\w\s-]', '', text.lower())
            heading_id = re.sub(r'[\s_]+', '-', heading_id).strip('-')

        toc_items.append({'level': level, 'text': text, 'id': heading_id})

    if not toc_items:
        return ''
    
    # Normalize levels if H1 was skipped (H2 becomes level 1, H3 becomes level 2, etc.)
    if skip_h1 and toc_items:
        min_level = min(item['level'] for item in toc_items)
        if min_level > 1:
            for item in toc_items:
                item['level'] = item['level'] - min_level + 1
    
    # Build nested TOC HTML using stack-based approach
    result = ['<nav class="table-of-contents" id="table-of-contents">']
    result.append('<h2>Table des matières</h2>')
    
    # Stack tracks (level, lines) for each open list
    stack = []
    
    for item in toc_items:
        level = item['level']
        
        # Close lists that are at same or deeper level
        while stack and stack[-1][0] >= level:
            closed_level, closed_lines = stack.pop()
            closed_lines.append('</ul>')
            if stack:
                # Add closed list to parent and close parent's li
                stack[-1][1].extend(closed_lines)
                stack[-1][1].append('</li>')
            else:
                # Root level closed - add to result
                result.extend(closed_lines)
        
        # Start new list if needed
        if not stack:
            # Start root list
            stack.append((level, ['<ul>']))
        elif stack[-1][0] < level:
            # Start nested list - remove </li> from parent, add <ul>
            stack[-1][1].pop()  # Remove </li>
            stack[-1][1].append('<ul>')
            stack.append((level, []))
        
        # Add item to current level with anchor for backlink
        toc_line_id = f"toc-{item['id']}"
        stack[-1][1].append(f'<li><a id="{toc_line_id}"></a><a href="#{item["id"]}">{item["text"]}</a></li>')
    
    # Close remaining lists
    while stack:
        closed_level, closed_lines = stack.pop()
        closed_lines.append('</ul>')
        if stack:
            stack[-1][1].extend(closed_lines)
            stack[-1][1].append('</li>')
        else:
            result.extend(closed_lines)
    
    result.append('</nav>')
    return '\n'.join(result)


def wrap_html_document(content: str, title: str, page_orientation: Optional[str] = None, has_excalidraw: bool = False) -> str:
    """
    Wrap HTML content in a full document with CSS.

    Args:
        content: HTML content body
        title: Page title
        page_orientation: 'portrait', 'landscape' or None for diagram sizing
        has_excalidraw: Whether the document contains excalidraw diagrams

    Returns:
        Complete HTML document
    """
    css_orientation = ""
    if page_orientation == 'portrait':
        css_orientation = """
        .diagram svg {
            max-width: 700px;
            height: auto;
        }
        """
    elif page_orientation == 'landscape':
        css_orientation = """
        .diagram svg {
            max-width: 900px;
            height: auto;
        }
        """
    
    excalidraw_css = """
        .excalidraw-wrapper {
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        .excalidraw-container {
            height: 400px;
            background: #f8f9fa;
            position: relative;
        }
        .excalidraw-container iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        .excalidraw-fallback {
            padding: 20px;
            text-align: center;
            color: #666;
        }
        .excalidraw-fallback a {
            color: #0066cc;
            text-decoration: none;
        }
        .excalidraw-fallback a:hover {
            text-decoration: underline;
        }
    """ if has_excalidraw else ""
    
    excalidraw_scripts = _get_excalidraw_scripts() if has_excalidraw else ""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        .diagram {{
            margin: 20px 0;
            text-align: center;
        }}
        .diagram svg {{
            max-width: 90%;
            height: auto;
            display: inline-block;
        }}
        {css_orientation}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', Consolas, Monaco, 'Lucida Console', monospace;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', Consolas, Monaco, 'Lucida Console', monospace;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background: #f4f4f4;
        }}
        .back-to-toc {{
            text-decoration: none;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        .table-of-contents {{
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px 20px;
            margin: 20px 0;
        }}
        .table-of-contents h2 {{
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        .table-of-contents ul {{
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }}
        .table-of-contents ul ul {{
            padding-left: 20px;
            margin-top: 5px;
        }}
        .table-of-contents li {{
            margin: 8px 0;
            line-height: 1.5;
        }}
        .table-of-contents a {{
            text-decoration: none;
            color: #0066cc;
        }}
        .table-of-contents a:hover {{
            text-decoration: underline;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 0;
            padding-left: 16px;
            color: #666;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
        {excalidraw_css}
    </style>
    {excalidraw_scripts}
</head>
<body>
{content}
</body>
</html>"""


def _get_excalidraw_scripts() -> str:
    """Generate scripts for Excalidraw integration."""
    return '''
    <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/@excalidraw/excalidraw@0.17/dist/excalidraw.production.min.js" crossorigin></script>
    <script>
        // Initialize Excalidraw components
        document.addEventListener('DOMContentLoaded', function() {
            const containers = document.querySelectorAll('.excalidraw-container');
            containers.forEach(function(container) {
                const sceneData = container.getAttribute('data-scene');
                if (!sceneData) return;
                
                // Decode the JSON
                const jsonStr = sceneData.replace(/&quot;/g, '"')
                                         .replace(/&lt;/g, '<')
                                         .replace(/&gt;/g, '>')
                                         .replace(/&amp;/g, '&');
                
                try {
                    const scene = JSON.parse(jsonStr);
                    const root = ReactDOM.createRoot(container);
                    const e = React.createElement;
                    root.render(
                        e(window.ExcalidrawLib.Excalidraw, {
                            initialData: scene,
                            UIOptions: {
                                canvasActions: {
                                    saveToActiveFile: false,
                                    export: false,
                                    loadScene: false,
                                }
                            },
                            viewModeEnabled: true,
                            zenModeEnabled: false,
                            gridModeEnabled: false,
                            theme: 'light'
                        })
                    );
                } catch (err) {
                    console.error('Failed to load Excalidraw:', err);
                    container.innerHTML = '<div class="excalidraw-fallback"><p>⚠️ Unable to load Excalidraw diagram</p><p><a href="https://excalidraw.com" target="_blank">Open in Excalidraw</a></p></div>';
                }
            });
        });
    </script>
    '''
