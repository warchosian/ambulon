"""
CLI command to check if a Table of Contents exists in Markdown files for Ambulon.
Utilizes core logic from app.toc.core.markdown_toc_checker.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.markdown_toc_checker import check_toc_exists_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'toc': {
        'check_toc_md': {
            'strict': False,
        }
    }
}


def main(argv=None):
    """
    Entry point for check-toc-md command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code:
        - 0: TOC exists
        - 1: No TOC found
        - 2: Error (file not found, read error, etc.)
    """
    parser = argparse.ArgumentParser(
        description="""
        Checks if a Table of Contents (TOC) exists in a Markdown file.
        Detects [TOC] markers, HTML nav elements, and Markdown TOC sections.

        Exit codes:
        - 0: TOC exists in the file
        - 1: No TOC found in the file
        - 2: Error (file not found, read error, etc.)

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/toc.yaml)
        3. Environment variables
        4. Default values
        """,
        epilog="""
        Examples:
          ambulon check-toc4md document.md
          ambulon check-toc4md document.md --strict
          ambulon check-toc4md document.md --verbose
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input Markdown file.")
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/toc.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging with detection details.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress all output messages (only exit code).")
    parser.add_argument("--strict", "-s", action="store_true", help="Strict mode: only accept [TOC] marker or HTML nav (not Markdown sections).")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.ERROR if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="check_toc4md")
    logger.info("[START] Starting check-toc4md module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    check_toc_md_config = config['toc']['check_toc_md']

    # Apply CLI overrides (highest priority)
    final_strict = args.strict if args.strict else check_toc_md_config.get('strict', DEFAULT_CONFIG['toc']['check_toc_md']['strict'])

    # Execute core logic
    exit_code, results = check_toc_exists_logic(
        input_file=args.input_file,
        verbose=args.verbose,
        strict=final_strict
    )

    # Display user-friendly message (unless --quiet)
    if not args.quiet:
        if exit_code == 0:
            print(f"✓ TOC exists in: {args.input_file}")
            if args.verbose and results:
                print("\nDetected TOC types:")
                if results.get('toc_marker'):
                    print("  - [TOC] marker")
                if results.get('html_nav'):
                    print("  - HTML <nav> element")
                if results.get('markdown_toc_section'):
                    print("  - Markdown TOC section heading")
        elif exit_code == 1:
            print(f"✗ No TOC found in: {args.input_file}")
            if args.verbose:
                print("\nNo TOC markers detected.")
                print("Hint: Add [TOC] marker or use 'ambulon add-toc-md' to generate a TOC.")
        else:  # exit_code == 2
            print(f"Error: Could not check file '{args.input_file}'")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
