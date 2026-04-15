"""
CLI command to merge multiple Markdown files into a single document for Ambulon.
Utilizes core logic from app.processing.core.markdown_merger.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.markdown_merger import fusion_markdown_files_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'processing': {
        'merge_md': {
            'output_name': "merged.md",
            'title': "Merged Markdown Document",
        }
    }
}

def main(argv=None):
    """
    Entry point with argv parameter for testability.

    Merges multiple Markdown files from a directory into a single Markdown document.
    Files are merged in alphabetical order, with a generated Table of Contents
    and adapted internal links. Includes validation for balanced code blocks.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (--config, e.g., config/processing.yaml)
    3. Environment variables
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="Merges multiple Markdown files from a directory into a single Markdown document.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
  1. Command-line arguments
  2. YAML configuration file (--config, e.g., config/processing.yaml)
  3. Environment variables
  4. Default values

Examples:
  # Basic merge (output to <source_dir>-merged/merged.md)
  ambulon merge-md /path/to/markdown-dir

  # With custom output directory
  ambulon merge-md /path/to/markdown-dir --output ./merged-output

  # With custom filename and title
  ambulon merge-md /path/to/markdown-dir -o ./output --name "combined.md" --title "My Combined Doc"

  # With configuration file
  ambulon merge-md /path/to/markdown-dir --config config/processing.yaml
        """
    )

    # Positional arguments
    parser.add_argument(
        "source_dir",
        type=Path,
        help="Source directory with Markdown files to merge."
    )

    # Options
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory for the merged Markdown file (default: <source_dir>-merged)."
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
        "-n", "--name",
        type=str,
        dest="output_name",
        help="Name of the output merged Markdown file (default: merged.md)."
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Title for the merged Markdown document."
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force overwrite if output file already exists."
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
    setup_logging(level=log_level, log_file_prefix="merge_md")
    logger.info("[START] Starting merge-md module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config_path) if args.config_path else None, DEFAULT_CONFIG)
    merge_md_config = config['processing']['merge_md']

    # Apply CLI overrides (highest priority) and resolve config
    final_output_name = args.output_name if args.output_name is not None else merge_md_config.get('output_name', DEFAULT_CONFIG['processing']['merge_md']['output_name'])
    final_title = args.title if args.title is not None else merge_md_config.get('title', DEFAULT_CONFIG['processing']['merge_md']['title'])

    # Determine final output path
    if args.output is None:
        # No output specified: create directory next to source
        output_dir_resolved = args.source_dir.parent / f"{args.source_dir.name}-merged"
        final_output_file = output_dir_resolved / final_output_name
    else:
        # Output specified: check if it's a file or directory
        if args.output.suffix == '.md':
            # User provided a file path (e.g., output.md)
            final_output_file = args.output
        else:
            # User provided a directory path
            output_dir_resolved = args.output
            final_output_file = output_dir_resolved / final_output_name

    # Execute core logic
    try:
        exit_code, generated_path = fusion_markdown_files_logic(
            source_dir=args.source_dir,
            output_file=final_output_file,
            output_name=final_output_name,
            title=final_title,
            force=args.force
        )

        if exit_code == 0:
            if generated_path:
                try:
                    relative_path = generated_path.relative_to(Path.cwd())
                except ValueError:
                    relative_path = generated_path.resolve()
                print(f"\n✓ Markdown merging successful!\nFile produced: {relative_path}")
            else:
                print("\n✓ Markdown merging successful, but no specific output file generated (e.g., no Markdown files found).")
            return 0
        else:
            logger.error("Failed to merge Markdown files.")
            return 1
    except Exception as e:
        logger.error(f"Error during Markdown merging: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
