"""
CLI command to merge/fusion multiple HTML files into a single document for Ambulon.
Utilizes core logic from app.processing.core.html_merger.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_merger import fusion_html_files_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'processing': {
        'merge_html': {
            'include_headers': True,
            'title': 'Merged HTML Document',
        }
    }
}

def main(argv=None):
    """
    Entry point with argv parameter for testability.

    Merges multiple HTML files from a directory into a single fused document.
    Creates a table of contents, section identifiers, and adapts internal links.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (--config, e.g., config/processing.yaml)
    3. Environment variables
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="Merges multiple HTML files from a directory into a single fused document.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
  1. Command-line arguments
  2. YAML configuration file (--config, e.g., config/processing.yaml)
  3. Environment variables
  4. Default values

Examples:
  # Basic merge
  ambulon merge-html /path/to/html-dir output.html

  # With custom title
  ambulon merge-html /path/to/html-dir output.html --title "My Merged Doc"

  # Without headers
  ambulon merge-html /path/to/html-dir output.html --no-headers

  # With configuration file
  ambulon merge-html /path/to/html-dir output.html --config config/processing.yaml
        """
    )

    # Positional arguments
    parser.add_argument(
        "source_dir",
        type=Path,
        help="Source directory with .html files to merge."
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Output HTML file path for the merged document."
    )

    # Configuration
    parser.add_argument(
        "-c", "--config",
        type=Path,
        dest="config_path",
        help="Path to a YAML configuration file (e.g., config/processing.yaml)."
    )

    # Global options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress most output messages."
    )

    # Merge specific options
    parser.add_argument(
        "--include-headers",
        action="store_true",
        dest="include_headers",
        help="Add headers showing source file names (default)."
    )
    parser.add_argument(
        "--no-headers",
        action="store_true",
        dest="no_headers",
        help="Do not add headers showing source file names."
    )
    parser.add_argument(
        "-t", "--title",
        type=str,
        help="Title for the merged document."
    )

    args = parser.parse_args(argv)

    # Validate directory exists
    if not args.source_dir.exists():
        print(f"Error: Source directory does not exist: {args.source_dir}", file=sys.stderr)
        return 1
    if not args.source_dir.is_dir():
        print(f"Error: Path is not a directory: {args.source_dir}", file=sys.stderr)
        return 1

    # Setup logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="merge_html")
    logger.info("[START] Starting merge-html module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config_path) if args.config_path else None, DEFAULT_CONFIG)
    merge_html_config = config['processing']['merge_html']

    # Apply CLI overrides (highest priority) and resolve config
    if args.include_headers:
        final_include_headers = True
    elif args.no_headers:
        final_include_headers = False
    else:
        final_include_headers = merge_html_config.get('include_headers', DEFAULT_CONFIG['processing']['merge_html']['include_headers'])

    final_title = args.title if args.title is not None else merge_html_config.get('title', DEFAULT_CONFIG['processing']['merge_html']['title'])

    # Execute core logic
    try:
        exit_code, generated_path = fusion_html_files_logic(
            source_dir=args.source_dir,
            output_file=args.output,
            include_headers=final_include_headers,
            title=final_title,
        )

        if exit_code == 0:
            if generated_path:
                try:
                    relative_path = generated_path.relative_to(Path.cwd())
                except ValueError:
                    relative_path = generated_path.resolve()
                print(f"\n✓ HTML merging successful!\nOutput file: {relative_path}")
            else:
                print("\n✓ HTML merging successful, but no specific output generated.")
            return 0
        else:
            logger.error("Failed to merge HTML files.")
            return 1
    except Exception as e:
        logger.error(f"Error during HTML merging: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
