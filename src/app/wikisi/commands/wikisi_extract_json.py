"""
CLI command to extract and filter applications from JSON data for Ambulon.
Utilizes core logic from app.wikisi.core.extractor.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.extractor import process_parkjson2json_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'wikisi': {
        'extract_json': {
            'preserve_structure': True,
            'include_metadata': True,
        }
    }
}


def main(argv=None):
    """
    Entry point for wikisi-extract command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Extracts and filters applications from a JSON file, creating a new JSON file
        with only the selected applications. Supports filtering by range, name, or ID.

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/wikisi.yaml)
        3. Environment variables (e.g., WIKISI_EXTRACT_PRESERVE_STRUCTURE)
        4. Default values
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input JSON file.")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file path (default: input_FILTER.json, or input.json without filter).")
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/wikisi.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output messages.")
    parser.add_argument("--range", "-r", help='Select range of applications (e.g., "1-3", "-5" for last 5, "10-" from 10 to end).')
    parser.add_argument("--name", "-n", help="Filter applications by name (case-insensitive substring match).")
    parser.add_argument("--id", "-i", help="Filter applications by ID (case-insensitive substring match).")
    parser.add_argument("--preserve-structure", action="store_true", default=None, help="Preserve original JSON structure (default: True).")
    parser.add_argument("--no-preserve-structure", action="store_true", help="Do not preserve original JSON structure.")
    parser.add_argument("--include-metadata", action="store_true", default=None, help="Include metadata in output JSON (default: True).")
    parser.add_argument("--no-include-metadata", action="store_true", help="Do not include metadata in output JSON.")
    parser.add_argument("--split-dir", type=Path, help="Directory to generate separate files for each application.")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="wikisi_extract_json")
    logger.info("[START] Starting wikisi-extract-json module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    extract_config = config['wikisi']['extract_json']

    # Apply CLI overrides (highest priority) and resolve config
    final_preserve_structure = args.preserve_structure if args.preserve_structure is not None else extract_config.get('preserve_structure', DEFAULT_CONFIG['wikisi']['extract_json']['preserve_structure'])
    if args.no_preserve_structure:
        final_preserve_structure = False

    final_include_metadata = args.include_metadata if args.include_metadata is not None else extract_config.get('include_metadata', DEFAULT_CONFIG['wikisi']['extract_json']['include_metadata'])
    if args.no_include_metadata:
        final_include_metadata = False

    # Execute extraction logic
    exit_code, generated_path = process_parkjson2json_logic(
        input_file=args.input_file,
        output_file=args.output,
        range_spec=getattr(args, 'range'),
        name_filter=args.name,
        id_filter=args.id,
        preserve_structure=final_preserve_structure,
        include_metadata=final_include_metadata,
        split_dir=args.split_dir
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ Extraction successful!\nFile produced: {relative_path}")
        else:
            print("\n✓ Extraction successful, no specific output file generated (e.g., no matching apps for filter).")
        return 0
    else:
        logger.error("JSON extraction failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
