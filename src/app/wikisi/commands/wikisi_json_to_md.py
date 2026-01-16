"""
CLI command to convert JSON data to optimal Markdown format for Ambulon.
Utilizes core logic from app.core.json_to_md_converter.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.json_to_md_converter import process_parkjson2md_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'wikisi': {
        'json_to_md': {
            'min_confidence': 0.7, # Example config, might not be used here directly
        }
    }
}


def main(argv=None):
    """
    Entry point for wikisi-md command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Converts JSON data (e.g., application park data) to an optimized Markdown format.
        Supports filtering by range, name, or ID.

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/wikisi.yaml)
        3. Environment variables (e.g., WIKISI_JSON_TO_MD_MIN_CONFIDENCE)
        4. Default values
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input JSON file.")
    parser.add_argument("--output", "-o", type=Path, help="Output Markdown file path (default: input_FILTER.md, or input.md without filter).")
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/wikisi.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output messages.")
    parser.add_argument("--range", "-r", help='Select range of applications (e.g., "1-3", "-5" for last 5, "10-" from 10 to end).')
    parser.add_argument("--name", "-n", help="Filter applications by name (case-insensitive substring match).")
    parser.add_argument("--id", "-i", help="Filter applications by ID (case-insensitive substring match).")
    parser.add_argument("--split-dir", type=Path, help="Directory to generate separate Markdown files for each application.")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="wikisi_json_to_md")
    logger.info("[START] Starting wikisi-json-to-md module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    # json_to_md_config = config['wikisi']['json_to_md'] # Not directly used in this command for now

    # Execute conversion logic
    exit_code, generated_path = process_parkjson2md_logic(
        input_file=args.input_file,
        output_file=args.output,
        range_spec=getattr(args, 'range'),
        name_filter=args.name,
        id_filter=args.id,
        split_dir=args.split_dir
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ Conversion successful!\nFile produced: {relative_path}")
        else:
            print("\n✓ Conversion successful, no specific output file generated (e.g., no matching apps for filter).")
        return 0
    else:
        logger.error("JSON to Markdown conversion failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
