"""
CLI command to add Table of Contents to files (Markdown or HTML).
Automatically detects file type and calls the appropriate core logic.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List

from app.core.logging_config import setup_logging

logger = logging.getLogger(__name__)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Entry point for add-toc command.

    Automatically detects file type (.md or .html) and calls the appropriate core logic.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Add a Table of Contents (TOC) to a Markdown or HTML file.

        The command automatically detects the file type based on extension:
        - .md, .markdown: uses Markdown TOC generator
        - .html, .htm: uses HTML TOC inserter

        For Markdown files, generates a hierarchical TOC with anchor links.
        For HTML files, inserts TOC after <body> tag or at specified position.
        """,
        epilog="""
        Examples:
          ambulon add-toc document.md
          ambulon add-toc document.html
          ambulon add-toc doc.md -o output.md --min-level 2 --max-level 4
          ambulon add-toc doc.html -o output.html --position after-title
        """
    )

    parser.add_argument("input_file", type=Path, help="Input file (Markdown or HTML)")
    parser.add_argument("--output", "-o", type=Path, help="Output file path (default: auto-generated)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    # Common options for both formats
    parser.add_argument("--min-level", type=int, default=1, choices=range(1, 7),
                        help="Minimum heading level to include in TOC (1-6, default: 1)")
    parser.add_argument("--max-level", type=int, default=6, choices=range(1, 7),
                        help="Maximum heading level to include in TOC (1-6, default: 6)")

    # HTML-specific options
    parser.add_argument("--position", type=str, choices=['after-body', 'after-title', 'before-content'],
                        default='after-body',
                        help="Position to insert TOC in HTML (default: after-body). Only used for HTML files.")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="add-toc")
    logger.info("[START] Starting add-toc module.")

    # Validate input file
    if not args.input_file.exists():
        logger.error(f"Input file not found: {args.input_file}")
        print(f"✗ Error: Input file not found: {args.input_file}")
        return 1

    if not args.input_file.is_file():
        logger.error(f"Input path is not a file: {args.input_file}")
        print(f"✗ Error: Input path is not a file: {args.input_file}")
        return 1

    # Detect file type
    file_extension = args.input_file.suffix.lower()

    if file_extension in ['.md', '.markdown']:
        # Markdown file - use Markdown TOC generator
        logger.info(f"Detected Markdown file: {args.input_file}")

        from ..core.markdown_toc_generator import add_toc_to_markdown_logic

        # Determine output file
        if args.output is None:
            output_file = args.input_file.parent / f"{args.input_file.stem}-toced.md"
        else:
            output_file = args.output

        exit_code, result_path = add_toc_to_markdown_logic(
            input_file=args.input_file,
            output_file=output_file,
            min_level=args.min_level,
            max_level=args.max_level
        )

        if exit_code == 0 and result_path:
            print(f"\n✓ TOC added successfully!")
            print(f"File produced: {result_path}")
        else:
            print(f"\n✗ Failed to add TOC")

        return exit_code

    elif file_extension in ['.html', '.htm']:
        # HTML file - use HTML TOC adder
        logger.info(f"Detected HTML file: {args.input_file}")

        from ..core.html_toc_adder import add_toc_to_html_logic

        # Determine output file
        if args.output is None:
            output_file = args.input_file.parent / f"{args.input_file.stem}-toced.html"
        else:
            output_file = args.output

        exit_code, result_path = add_toc_to_html_logic(
            input_file=args.input_file,
            output_file=output_file,
            min_level=args.min_level,
            max_level=args.max_level,
            position=args.position
        )

        if exit_code == 0 and result_path:
            print(f"\n✓ TOC added successfully!")
            print(f"File produced: {result_path}")
        else:
            print(f"\n✗ Failed to add TOC")

        return exit_code

    else:
        # Unsupported file type
        logger.error(f"Unsupported file type: {file_extension}")
        print(f"\n✗ Error: Unsupported file type '{file_extension}'")
        print(f"Supported types: .md, .markdown, .html, .htm")
        return 1


if __name__ == '__main__':
    sys.exit(main())
