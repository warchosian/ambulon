"""
Command to convert Markdown files to HTML with diagram support.

This module handles the complete conversion pipeline:
1. Detect and convert diagrams (PlantUML, Mermaid, Graphviz) to SVG
2. Convert Markdown to HTML
3. Wrap in standalone HTML document with proper CSS
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.logging_config import setup_logging
from app.core.output_paths import format_output_path
from ..core import (
    extract_diagram_blocks,
    extract_diagram_blocks_from_file,
    get_diagram_stats,
    convert_diagram,
    clean_svg_content,
    ConversionMethod,
)
from ..core.markdown_to_html import (
    markdown_to_html_basic,
    wrap_html_document,
)
from ..core.base import DiagramType

logger = logging.getLogger(__name__)


def process_markdown_to_html(
    markdown_path: str,
    output_path: Optional[str] = None,
    verbose: bool = False,
    standalone: bool = True,
    plantuml_method: str = 'kroki',
    plantuml_jar: Optional[str] = None,
    page_orientation: Optional[str] = None,
    add_toc_backlinks: bool = False,
    no_diagrams: bool = False,
) -> int:
    """
    Convert a Markdown file with diagrams to HTML with embedded SVG.

    Args:
        markdown_path: Path to the input Markdown file
        output_path: Optional output HTML path. If None, uses same name with .html extension
        verbose: Print verbose output
        standalone: Generate standalone HTML with CSS and full page structure
        plantuml_method: Method to convert PlantUML ('auto', 'jar', or 'kroki')
        plantuml_jar: Path to PlantUML JAR file (overrides PLANTUML_JAR env var)
        page_orientation: Page orientation for PDF optimization:
                         - None: Natural SVG size (default)
                         - 'portrait': 700px max width for A4 portrait
                         - 'landscape': 900px max width for A4 landscape
        add_toc_backlinks: Add back-to-TOC links (↑) after each heading
        no_diagrams: Skip diagram conversion (convert markdown only)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    md_path = Path(markdown_path).resolve()

    # Check if markdown file exists
    if not md_path.exists():
        logger.error(f"Markdown file '{markdown_path}' does not exist.")
        return 1

    if not md_path.is_file():
        logger.error(f"'{markdown_path}' is not a file.")
        return 1

    # Determine output path
    if output_path is None:
        output_path = md_path.parent / (md_path.stem + ".html")
    else:
        output_path = Path(output_path)

    output_path = output_path.resolve()

    logger.info(f"Processing: {md_path}")
    logger.info(f"Output: {output_path}")

    try:
        # Read markdown content with encoding detection
        content = _read_file_with_encoding(md_path, verbose)
        if content is None:
            return 1

        # Convert diagrams to SVG if not disabled
        if not no_diagrams:
            content = _convert_diagrams_in_content(
                content, plantuml_method, plantuml_jar, verbose
            )

        # Convert remaining markdown to HTML
        html_content = markdown_to_html_basic(content, add_toc_backlinks=add_toc_backlinks)

        # Wrap in full HTML if standalone
        if standalone:
            # Check if content has excalidraw diagrams
            has_excalidraw = '___EXCALIDRAW_BLOCK_' in html_content or '.excalidraw-container' in html_content
            html_content = wrap_html_document(html_content, md_path.stem, page_orientation, has_excalidraw=has_excalidraw)

        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        rel_path = format_output_path(output_path)
        logger.info("✓ Conversion md2html reussie !")
        logger.info("Fichier produit : %s", rel_path)

        return 0

    except Exception as e:
        logger.error(f"Failed to convert markdown: {e}", exc_info=verbose)
        return 1


def _read_file_with_encoding(file_path: Path, verbose: bool = False) -> Optional[str]:
    """Read file trying multiple encodings."""
    encodings_to_try = ['utf-8', 'cp1252', 'latin-1', 'iso-8859-1']

    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            if verbose and encoding != 'utf-8':
                logger.info(f"File was read with {encoding} encoding (not UTF-8)")
            return content
        except UnicodeDecodeError:
            continue

    logger.error(f"Could not decode file with any supported encoding: {', '.join(encodings_to_try)}")
    return None


def _convert_diagrams_in_content(
    content: str,
    plantuml_method: str,
    plantuml_jar: Optional[str],
    verbose: bool
) -> str:
    """Convert all diagrams in content to SVG."""
    # Detect diagrams using the core module
    diagrams = extract_diagram_blocks(content)

    if not diagrams:
        if verbose:
            logger.info("No diagrams found in content")
        return content

    if verbose:
        stats = get_diagram_stats(diagrams)
        logger.info(f"Found {stats['total']} diagram(s):")
        if stats.get('plantuml', 0) > 0:
            logger.info(f"  - PlantUML: {stats['plantuml']}")
        if stats.get('mermaid', 0) > 0:
            logger.info(f"  - Mermaid: {stats['mermaid']}")
        if stats.get('graphviz', 0) > 0:
            logger.info(f"  - Graphviz: {stats['graphviz']}")
        if stats.get('excalidraw', 0) > 0:
            logger.info(f"  - Excalidraw: {stats['excalidraw']}")

    result_content = content

    # Parse method
    try:
        method = ConversionMethod(plantuml_method.lower())
    except ValueError:
        method = ConversionMethod.KROKI

    # Convert each diagram
    for diagram in diagrams:
        diagram_type = diagram.diagram_type
        diagram_code = diagram.content
        full_block = diagram.full_block

        # Skip Excalidraw diagrams - they are handled specially in markdown_to_html_basic
        if diagram_type == DiagramType.EXCALIDRAW:
            if verbose:
                logger.info(f"Skipping {diagram_type.value} diagram at line {diagram.start_line} (handled by React)")
            continue

        if verbose:
            logger.info(f"Converting {diagram_type.value} diagram at line {diagram.start_line}...")

        result = convert_diagram(
            diagram_type=diagram_type,
            diagram_code=diagram_code,
            method=method,
            plantuml_jar=plantuml_jar,
            timeout=30
        )

        if result.success and result.svg_content:
            svg_content = clean_svg_content(result.svg_content)
            replacement = f'<div class="diagram diagram-{diagram_type.value}">\n{svg_content}\n</div>'
            result_content = result_content.replace(full_block, replacement, 1)

            if verbose:
                logger.info(f"  [OK] Converted successfully using {result.method_used}")
        else:
            if verbose:
                logger.warning(f"  [FAILED] {result.error_message or 'Unknown error'}")

    return result_content


def main(argv=None):
    """
    Entry point for md2html command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Convert Markdown to HTML with diagram support.

        This command converts Markdown files to HTML while:
        - Converting PlantUML, Mermaid, and Graphviz diagrams to SVG
        - Generating a table of contents from headers
        - Preserving formatting (tables, lists, code blocks)
        - Creating standalone HTML documents with CSS styling
        """,
        epilog="""
        Examples:
          ambulon md2html document.md
          ambulon md2html document.md -o result.html
          ambulon md2html document.md -p landscape --plantuml-method jar
          ambulon md2html document.md --no-standalone --toc-backlinks

        Environment Variables:
          PLANTUML_JAR    Path to PlantUML JAR file (for jar method)
          GRAPHVIZ_EXE    Path to Graphviz dot executable
        """
    )

    parser.add_argument("input", type=str, help="Input Markdown file")
    parser.add_argument("-o", "--output", type=str, help="Output HTML file (default: <input>.html)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-standalone", action="store_true", help="Output HTML fragment only (no CSS)")
    parser.add_argument("--no-diagrams", action="store_true", help="Skip diagram conversion")
    parser.add_argument("--plantuml-method", type=str, default='kroki',
                        choices=['auto', 'jar', 'kroki'],
                        help="PlantUML conversion method (default: kroki)")
    parser.add_argument("--plantuml-jar", type=str, help="Path to PlantUML JAR file")
    parser.add_argument("-p", "--page-orientation", type=str,
                        choices=['portrait', 'landscape'],
                        help="Optimize SVG size for PDF generation")
    parser.add_argument("--toc-backlinks", action="store_true",
                        help="Add back-to-TOC links after headings")

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="diagrams-md2html")
    logger.info("[START] Starting diagrams md2html conversion.")

    return process_markdown_to_html(
        markdown_path=args.input,
        output_path=args.output,
        verbose=args.verbose,
        standalone=not args.no_standalone,
        plantuml_method=args.plantuml_method,
        plantuml_jar=args.plantuml_jar,
        page_orientation=args.page_orientation,
        add_toc_backlinks=args.toc_backlinks,
        no_diagrams=args.no_diagrams,
    )


if __name__ == '__main__':
    sys.exit(main())
