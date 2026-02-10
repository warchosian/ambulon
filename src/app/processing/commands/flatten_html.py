"""
CLI command to flatten an HTML directory structure for Ambulon.
Utilizes core logic from app.processing.core.html_flattener.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_flattener import flatten_html_directory_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'processing': {
        'flatten_html': {
            # No specific config options for now
        }
    }
}

def main(argv=None):
    """
    Entry point with argv parameter for testability.

    Flattens a nested HTML directory structure into a single directory.
    All .html files are copied, and their internal links are adapted to
    work in the flattened structure.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (--config, e.g., config/processing.yaml)
    3. Environment variables
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="Flattens a nested HTML directory structure into a single directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
  1. Command-line arguments
  2. YAML configuration file (--config, e.g., config/processing.yaml)
  3. Environment variables
  4. Default values

Examples:
  # Basic flattening (output to <source_dir>-flattened)
  ambulon flatten-html /path/to/nested-html

  # With custom output directory
  ambulon flatten-html /path/to/nested-html --output /path/to/flat-html

  # With configuration file
  ambulon flatten-html /path/to/nested-html -o output-dir --config config/processing.yaml
        """
    )

    # Positional arguments
    parser.add_argument(
        "source_dir",
        type=Path,
        help="Source directory with nested HTML files."
    )

    # Options
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory (default: <source_dir>-flattened)."
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
    setup_logging(level=log_level, log_file_prefix="flatten_html")
    logger.info("[START] Starting flatten-html module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config_path) if args.config_path else None, DEFAULT_CONFIG)
    # flatten_html_config = config['processing']['flatten_html'] # Not directly used for now

    # Execute core logic
    try:
        exit_code, generated_path = flatten_html_directory_logic(
            source_dir=args.source_dir,
            output_dir=args.output,
        )

        if exit_code == 0:
            if generated_path:
                try:
                    relative_path = generated_path.relative_to(Path.cwd())
                except ValueError:
                    relative_path = generated_path.resolve()
                print(f"\n✓ HTML flattening successful!\nOutput directory: {relative_path}")
            else:
                print("\n✓ HTML flattening successful, but no specific output generated (e.g., no HTML files found).")
            return 0
        else:
            logger.error("Failed to flatten HTML directory.")
            return 1
    except Exception as e:
        logger.error(f"Error during HTML flattening: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
