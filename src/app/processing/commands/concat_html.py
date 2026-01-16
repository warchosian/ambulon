"""
CLI command to concatenate HTML files from a directory into a single HTML file for Ambulon.
Utilizes core logic from app.processing.core.html_concatenator.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_concatenator import concatenate_html_files_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'processing': {
        'concat_html': {
            'include_headers': True,
            'title': "Concatenated HTML",
        }
    }
}

def main(argv=None):
    """
    Entry point with argv parameter for testability.

    Concatenates multiple HTML files from a specified directory into a single HTML file.
    Files are sorted in natural (numeric) order.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (--config, e.g., config/processing.yaml)
    3. Environment variables
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="Concatenates multiple HTML files from a specified directory into a single HTML file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
  1. Command-line arguments
  2. YAML configuration file (--config, e.g., config/processing.yaml)
  3. Environment variables
  4. Default values

Examples:
  # Basic concatenation
  ambulon concat-html /path/to/html-dir --output output.html

  # With configuration file
  ambulon concat-html /path/to/html-dir -o output.html --config config/processing.yaml

  # Without headers and custom title
  ambulon concat-html /path/to/html-dir -o output.html --no-headers --title "My Document"
        """
    )

    # Positional arguments
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing HTML files."
    )

    # Required options
    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Output HTML file path."
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

    # Concatenation specific options
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
        "--title",
        type=str,
        help="Title for the concatenated document."
    )

    args = parser.parse_args(argv)

    # Validate directory exists
    if not args.directory.exists():
        print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
        return 1
    if not args.directory.is_dir():
        print(f"Error: Path is not a directory: {args.directory}", file=sys.stderr)
        return 1

    # Setup logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="concat_html")
    logger.info("[START] Starting concat-html module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config_path) if args.config_path else None, DEFAULT_CONFIG)
    concat_html_config = config['processing']['concat_html']

    # Apply CLI overrides (highest priority) and resolve config
    if args.include_headers:
        final_include_headers = True
    elif args.no_headers:
        final_include_headers = False
    else:
        final_include_headers = concat_html_config.get('include_headers', DEFAULT_CONFIG['processing']['concat_html']['include_headers'])

    final_title = args.title if args.title is not None else concat_html_config.get('title', DEFAULT_CONFIG['processing']['concat_html']['title'])

    # Execute core logic
    try:
        exit_code, generated_path = concatenate_html_files_logic(
            directory=args.directory,
            output_file=args.output,
            include_headers=final_include_headers,
            title=final_title
        )

        if exit_code == 0:
            if generated_path:
                try:
                    relative_path = generated_path.relative_to(Path.cwd())
                except ValueError:
                    relative_path = generated_path.resolve()
                print(f"\n✓ Concatenation successful!\nFile produced: {relative_path}")
            else:
                print("\n✓ Concatenation successful, but no specific output file generated (e.g., no HTML files found).")
            return 0
        else:
            logger.error("Failed to concatenate HTML files.")
            return 1
    except Exception as e:
        logger.error(f"Error during concatenation: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
