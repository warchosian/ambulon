"""
CLI command to add back-to-TOC (inverse TOC) links to Markdown headings for Ambulon.
Utilizes core logic from app.toc.core.markdown_itoc.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.markdown_itoc import add_toc_backlinks_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'toc': {
        'add_itoc_md': {
            'toc_id': 'table-of-contents',
            'link_text': '↑',
            'min_level': 1,
            'max_level': 6,
        }
    }
}


def main(argv=None):
    """
    Entry point for add-itoc-md command (inverse TOC links).

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Adds inverse TOC navigation links (↑) after each heading in a Markdown file.
        These links allow readers to quickly jump back to the table of contents.

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/toc.yaml)
        3. Environment variables
        4. Default values
        """
    )

    parser.add_argument("input_file", type=Path, help="Path to input Markdown file.")
    parser.add_argument("--output", "-o", type=Path, help="Output Markdown file path (default: <input>-itoc.md).")
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/toc.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output messages.")
    parser.add_argument("--toc-id", type=str, help="ID of the TOC anchor to link to (default: table-of-contents).")
    parser.add_argument("--link-text", type=str, help="Text for the back link (default: ↑).")
    parser.add_argument("--min-level", type=int, help="Minimum heading level to add backlinks (1-6). Overrides config/env.")
    parser.add_argument("--max-level", type=int, help="Maximum heading level to add backlinks (1-6). Overrides config/env.")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="add_itoc4md")
    logger.info("[START] Starting add-itoc4md module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    add_itoc_md_config = config['toc']['add_itoc_md']

    # Determine output path
    if args.output is None:
        # Si le fichier contient déjà -toced, remplacer par -itoced
        # Sinon ajouter -itoced
        if args.input_file.stem.endswith('-toced'):
            new_stem = args.input_file.stem.replace('-toced', '-itoced')
        else:
            new_stem = f"{args.input_file.stem}-itoced"
        args.output = args.input_file.parent / f"{new_stem}.md"

    # Apply CLI overrides (highest priority) and resolve config
    final_toc_id = args.toc_id if args.toc_id is not None else add_itoc_md_config.get('toc_id', DEFAULT_CONFIG['toc']['add_itoc_md']['toc_id'])
    final_link_text = args.link_text if args.link_text is not None else add_itoc_md_config.get('link_text', DEFAULT_CONFIG['toc']['add_itoc_md']['link_text'])
    final_min_level = args.min_level if args.min_level is not None else add_itoc_md_config.get('min_level', DEFAULT_CONFIG['toc']['add_itoc_md']['min_level'])
    final_max_level = args.max_level if args.max_level is not None else add_itoc_md_config.get('max_level', DEFAULT_CONFIG['toc']['add_itoc_md']['max_level'])

    # Execute core logic
    exit_code, generated_path = add_toc_backlinks_logic(
        input_file=args.input_file,
        output_file=args.output,
        toc_id=final_toc_id,
        link_text=final_link_text,
        min_level=final_min_level,
        max_level=final_max_level
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ Inverse TOC links added successfully!\nFile produced: {relative_path}")
        else:
            print("\n✓ iTOC operation successful, but no specific output file generated (e.g., no headings found).")
        return 0
    else:
        logger.error("Failed to add inverse TOC links to Markdown file.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
