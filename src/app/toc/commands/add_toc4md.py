"""
CLI command to add a Table of Contents (TOC) to Markdown files for Ambulon.
Utilizes core logic from app.toc.core.markdown_toc_generator.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.markdown_toc_generator import add_toc_to_markdown_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'toc': {
        'add_toc_md': {
            'min_level': 1,
            'max_level': 6,
        }
    }
}


def main(argv=None):
    """
    Entry point for add-toc-md command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Adds a table of contents to a Markdown file based on its headings.
        The TOC includes anchor links for navigation.

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/toc.yaml)
        3. Environment variables
        4. Default values
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input Markdown file.")
    parser.add_argument("--output", "-o", type=Path, help="Output Markdown file path (default: <input>-toced.md).")
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/toc.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output messages.")
    parser.add_argument("--min-level", type=int, help="Minimum heading level to include in TOC (1-6). Overrides config/env.")
    parser.add_argument("--max-level", type=int, help="Maximum heading level to include in TOC (1-6). Overrides config/env.")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="add_toc4md")
    logger.info("[START] Starting add-toc4md module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    add_toc_md_config = config['toc']['add_toc_md']

    # Determine output path
    if args.output is None:
        args.output = args.input_file.parent / f"{args.input_file.stem}-toced.md"

    # Apply CLI overrides (highest priority) and resolve config
    final_min_level = args.min_level if args.min_level is not None else add_toc_md_config.get('min_level', DEFAULT_CONFIG['toc']['add_toc_md']['min_level'])
    final_max_level = args.max_level if args.max_level is not None else add_toc_md_config.get('max_level', DEFAULT_CONFIG['toc']['add_toc_md']['max_level'])

    # Execute core logic
    exit_code, generated_path = add_toc_to_markdown_logic(
        input_file=args.input_file,
        output_file=args.output,
        min_level=final_min_level,
        max_level=final_max_level
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
        logger.error("Failed to add TOC to Markdown file.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
