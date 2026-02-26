"""
CLI command to check if inverse TOC (iTOC) links exist in Markdown files for Ambulon.
Utilizes core logic from app.toc.core.markdown_itoc_checker.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.markdown_itoc_checker import check_itoc_exists_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'toc': {
        'check_itoc_md': {
            'min_coverage': 0.0,  # 0% minimum par défaut
            'link_pattern': r'\[↑\]\(#[^\)]+\)',
        }
    }
}


def main(argv=None):
    """
    Entry point for check-itoc-md command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code:
        - 0: iTOC links exist and meet coverage requirement
        - 1: No iTOC links found or coverage too low
        - 2: Error (file not found, read error, etc.)
    """
    parser = argparse.ArgumentParser(
        description="""
        Checks if inverse TOC (iTOC) links exist in a Markdown file.
        Detects back-to-TOC navigation links (↑) after headings.

        Exit codes:
        - 0: iTOC links exist and coverage >= min-coverage
        - 1: No iTOC links found or coverage < min-coverage
        - 2: Error (file not found, read error, etc.)

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/toc.yaml)
        3. Environment variables
        4. Default values
        """,
        epilog="""
        Examples:
          ambulon check-itoc4md document.md
          ambulon check-itoc4md document.md --min-coverage 0.8
          ambulon check-itoc4md document.md --verbose
          ambulon check-itoc4md document.md --link-pattern '\[⬆\]\(#[^\)]+\)'
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input Markdown file.")
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/toc.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging with detection details.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress all output messages (only exit code).")
    parser.add_argument("--min-coverage", type=float, help="Minimum coverage required (0.0-1.0). Default: 0.0 (any iTOC link).")
    parser.add_argument("--link-pattern", type=str, help="Regex pattern for iTOC links. Default: \\[↑\\]\\(#[^\\)]+\\)")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.ERROR if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="check_itoc4md")
    logger.info("[START] Starting check-itoc4md module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    check_itoc_md_config = config['toc']['check_itoc_md']

    # Apply CLI overrides (highest priority)
    final_min_coverage = args.min_coverage if args.min_coverage is not None else check_itoc_md_config.get('min_coverage', DEFAULT_CONFIG['toc']['check_itoc_md']['min_coverage'])
    final_link_pattern = args.link_pattern if args.link_pattern is not None else check_itoc_md_config.get('link_pattern', DEFAULT_CONFIG['toc']['check_itoc_md']['link_pattern'])

    # Validate min_coverage
    if not (0.0 <= final_min_coverage <= 1.0):
        logger.error("Error: --min-coverage must be between 0.0 and 1.0")
        return 2

    # Execute core logic
    exit_code, results = check_itoc_exists_logic(
        input_file=args.input_file,
        verbose=args.verbose,
        min_coverage=final_min_coverage,
        link_pattern=final_link_pattern
    )

    # Display user-friendly message (unless --quiet)
    if not args.quiet:
        if exit_code == 0:
            coverage = results.get('coverage', 0.0) * 100
            print(f"✓ iTOC links found in: {args.input_file}")
            print(f"  Coverage: {results['itoc_count']}/{results['total_headings']} headings ({coverage:.1f}%)")

            if args.verbose and results.get('headings_without_itoc'):
                print(f"\n  Headings without iTOC links:")
                for heading in results['headings_without_itoc'][:5]:  # Limit to first 5
                    print(f"    - Line {heading['line']+1}: {'#' * heading['level']} {heading['text']}")
                if len(results['headings_without_itoc']) > 5:
                    print(f"    ... and {len(results['headings_without_itoc']) - 5} more")

        elif exit_code == 1:
            if results and results.get('total_headings', 0) > 0:
                coverage = results.get('coverage', 0.0) * 100
                print(f"✗ iTOC coverage insufficient in: {args.input_file}")
                print(f"  Found: {results['itoc_count']}/{results['total_headings']} headings ({coverage:.1f}%)")
                print(f"  Required: {final_min_coverage*100:.1f}%")

                if args.verbose:
                    print(f"\n  Hint: Use 'ambulon add-itoc4md {args.input_file}' to add iTOC links")
            else:
                print(f"✗ No iTOC links found in: {args.input_file}")
                if args.verbose:
                    if results and results.get('total_headings', 0) == 0:
                        print("  No headings found in file")
                    else:
                        print(f"  Hint: Use 'ambulon add-itoc4md {args.input_file}' to add iTOC links")
        else:  # exit_code == 2
            print(f"Error: Could not check file '{args.input_file}'")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
