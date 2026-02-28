"""
CLI command to convert diagrams to SVG in Markdown files for Ambulon.

Supports: PlantUML, Mermaid, Graphviz
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.logging_config import setup_logging
from app.core.output_paths import format_output_path
from ..core import (
    extract_diagram_blocks_from_file,
    get_diagram_stats,
    convert_diagram,
    clean_svg_content,
    ConversionMethod,
    DiagramType,
)

logger = logging.getLogger(__name__)


def process_diagram2svg(
    input_file: Path,
    output_file: Optional[Path] = None,
    plantuml_method: str = 'kroki',
    plantuml_jar: Optional[str] = None,
    verbose: bool = False
) -> tuple[int, Optional[Path]]:
    """
    Convert diagrams in Markdown to embedded SVG.

    Args:
        input_file: Path to input Markdown file
        output_file: Optional output path (default: {input}-svg.md)
        plantuml_method: PlantUML conversion method ('kroki', 'jar', 'auto')
        plantuml_jar: Path to PlantUML JAR (for 'jar' method)
        verbose: Enable verbose logging

    Returns:
        Tuple of (exit_code, output_path)
    """
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return 1, None

    if not input_file.is_file():
        logger.error(f"Input path is not a file: {input_file}")
        return 1, None

    # Determine output path
    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}-svg.md"

    logger.info(f"Processing: {input_file}")
    logger.info(f"Output: {output_file}")

    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Detect diagrams
        diagrams = extract_diagram_blocks_from_file(input_file)
        stats = get_diagram_stats(diagrams)

        logger.info(f"Found {stats['total']} diagram(s):")
        if stats['plantuml'] > 0:
            logger.info(f"  - PlantUML: {stats['plantuml']}")
        if stats['mermaid'] > 0:
            logger.info(f"  - Mermaid: {stats['mermaid']}")
        if stats['graphviz'] > 0:
            logger.info(f"  - Graphviz: {stats['graphviz']}")

        if stats['total'] == 0:
            logger.warning("No diagrams found in file")
            # Copy file as-is
            output_file.write_text(content, encoding='utf-8')
            return 0, output_file

        # Convert diagrams to SVG
        result_content = content
        converted_count = 0
        failed_count = 0

        # Parse method
        try:
            method = ConversionMethod(plantuml_method.lower())
        except ValueError:
            method = ConversionMethod.KROKI

        for diagram in diagrams:
            diagram_type = diagram.diagram_type
            diagram_content = diagram.content
            full_block = diagram.full_block

            logger.debug(f"Converting {diagram_type.value} diagram at line {diagram.start_line}")

            # Convert based on type
            result = convert_diagram(
                diagram_type=diagram_type,
                diagram_code=diagram_content,
                method=method,
                plantuml_jar=plantuml_jar,
                timeout=30
            )

            if result.success and result.svg_content:
                # Clean SVG
                svg_content = clean_svg_content(result.svg_content)

                # Replace code block with SVG
                replacement = f'<div class="diagram diagram-{diagram_type.value}">\n{svg_content}\n</div>'
                result_content = result_content.replace(full_block, replacement, 1)
                converted_count += 1
                logger.debug(f"  [OK] Converted successfully using {result.method_used}")
            else:
                failed_count += 1
                logger.warning(f"  [FAILED] {result.error_message or 'Unknown error'}")

        # Write output file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result_content)

        logger.info(f"Conversion complete:")
        logger.info(f"  - Converted: {converted_count}/{stats['total']}")
        if failed_count > 0:
            logger.info(f"  - Failed: {failed_count}")

        rel_path = format_output_path(output_file)
        logger.info(f"✓ Conversion reussie ! Fichier produit : {rel_path}")

        return 0, output_file

    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=verbose)
        return 1, None


def main(argv=None):
    """
    Entry point for diagram2svg4md command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Convert diagrams in Markdown files to embedded SVG.

        Supported:
        - PlantUML (```plantuml or ```puml)
        - Mermaid (```mermaid)
        - Graphviz/DOT (```graphviz or ```dot)

        The output file will have diagrams replaced with inline SVG,
        making the Markdown self-contained and portable.
        """,
        epilog="""
        Examples:
          ambulon diagram2svg4md document.md
          ambulon diagram2svg4md doc.md -o doc-converted.md
          ambulon diagram2svg4md doc.md --plantuml-method jar --plantuml-jar /path/to/plantuml.jar
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input Markdown file with diagrams.")
    parser.add_argument("--output", "-o", type=Path, help="Output Markdown file path (default: <input>-svg.md).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--plantuml-method", type=str, default='kroki',
                        choices=['kroki', 'jar', 'auto'],
                        help="PlantUML conversion method (default: kroki).")
    parser.add_argument("--plantuml-jar", type=str, help="Path to PlantUML JAR file (for 'jar' method).")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="diagram2svg4md")
    logger.info("[START] Starting diagram2svg4md module.")

    # Execute conversion
    exit_code, result_path = process_diagram2svg(
        input_file=args.input_file,
        output_file=args.output,
        plantuml_method=args.plantuml_method,
        plantuml_jar=args.plantuml_jar,
        verbose=args.verbose
    )

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
