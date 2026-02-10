"""
CLI command to add a Table of Contents (TOC) to HTML files for Ambulon.
Utilizes core logic from app.processing.core.html_toc_generator.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_toc_generator import add_toc_to_html_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'processing': {
        'add_toc_html': {
            # No specific config options for now
        }
    }
}


def main(argv=None):
    """
    Entry point for add-toc-html command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Adds a table of contents to an HTML file based on its headings.
        The TOC includes anchor links for navigation, and CSS is injected for styling.

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/processing.yaml)
        3. Environment variables
        4. Default values
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input HTML file.")
    parser.add_argument("--output", "-o", type=Path, help="Output HTML file path (default: <input>-tocced.html).")
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/processing.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output messages.")
    parser.add_argument("--min-level", type=int, default=1, help="Minimum heading level to include in TOC (1-6).")
    parser.add_argument("--max-level", type=int, default=6, help="Maximum heading level to include in TOC (1-6).")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="add_toc4html")
    logger.info("[START] Starting add-toc4html module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    # add_toc_html_config = config['processing']['add_toc_html'] # Not directly used for now

    # Determine output path
    if args.output is None:
        args.output = args.input_file.parent / f"{args.input_file.stem}-tocced{args.input_file.suffix}"

    # Execute core logic
    exit_code, generated_path = add_toc_to_html_logic(
        input_file=args.input_file,
        output_file=args.output
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ TOC added successfully!\nFile produced: {relative_path}")
        else:
            print("\n✓ TOC operation successful, but no specific output file generated (e.g., no headings found).")
        return 0
    else:
        logger.error("Failed to add TOC to HTML file.")
        return 1


if __name__ == '__main__':
    sys.exit(main())