"""
CLI command to convert a project directory to a single Markdown file for AI analysis for Ambulon.
Utilizes core logic from app.processing.core.project_to_md_converter.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Set

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.project_to_md_converter import project_to_markdown_logic

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'processing': {
        'project2md': {
            'output_name': "{project_name}_project.md",
            'max_file_size': 1024 * 1024, # 1 MB
            'exclude_dirs': [],
            'use_gitignore': True,
        }
    }
}

def main(argv=None):
    """
    Entry point with argv parameter for testability.

    Scans a project directory and generates a single Markdown file containing:
    - A clickable file tree (table of contents).
    - All non-binary files as collapsible code blocks.
    - Relative file paths and syntax highlighting.
    Perfect for AI code analysis.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (--config, e.g., config/processing.yaml)
    3. Environment variables
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="Scans a project directory and generates a single Markdown file for AI analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
  1. Command-line arguments
  2. YAML configuration file (--config, e.g., config/processing.yaml)
  3. Environment variables
  4. Default values

Examples:
  # Basic conversion (output to <directory_name>_project.md)
  ambulon project2md /path/to/project

  # With custom output file
  ambulon project2md /path/to/project --output ./my_analysis.md

  # Exclude additional directories
  ambulon project2md /path/to/project --exclude logs --exclude temp

  # Ignore .gitignore patterns
  ambulon project2md /path/to/project --no-gitignore

  # Custom max file size (2MB)
  ambulon project2md /path/to/project --max-size 2097152
        """
    )

    # Positional arguments
    parser.add_argument(
        "directory",
        type=Path,
        help="Path to the project directory to scan."
    )

    # Options
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output Markdown file path (default: <directory_name>_project.md)."
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

    # Conversion specific options
    parser.add_argument(
        "--exclude",
        type=str,
        action="append",
        dest="exclude_dirs",
        help="Additional directory names to exclude (e.g., 'logs', 'temp'). Can be specified multiple times."
    )
    parser.add_argument(
        "--max-size",
        type=int,
        dest="max_file_size",
        help="Maximum file size in bytes to include (default: 1MB)."
    )
    parser.add_argument(
        "--use-gitignore",
        action="store_true",
        dest="use_gitignore",
        help="Respect .gitignore patterns (default)."
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        dest="no_gitignore",
        help="Do not respect .gitignore patterns."
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
    setup_logging(level=log_level, log_file_prefix="project2md")
    logger.info("[START] Starting project2md module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config_path) if args.config_path else None, DEFAULT_CONFIG)
    project2md_config = config['processing']['project2md']

    # Apply CLI overrides (highest priority) and resolve config
    final_exclude_dirs = set(args.exclude_dirs) if args.exclude_dirs else set()
    final_exclude_dirs.update(project2md_config.get('exclude_dirs', DEFAULT_CONFIG['processing']['project2md']['exclude_dirs']))

    final_max_file_size = args.max_file_size if args.max_file_size is not None else project2md_config.get('max_file_size', DEFAULT_CONFIG['processing']['project2md']['max_file_size'])

    if args.no_gitignore:
        final_use_gitignore = False
    elif args.use_gitignore:
        final_use_gitignore = True
    else:
        final_use_gitignore = project2md_config.get('use_gitignore', DEFAULT_CONFIG['processing']['project2md']['use_gitignore'])

    # Determine final output path
    if args.output is None:
        project_name = args.directory.name
        final_output_name = project2md_config.get('output_name', DEFAULT_CONFIG['processing']['project2md']['output_name'])
        final_output_file = args.directory.parent / Path(final_output_name.replace("{project_name}", project_name))
    else:
        final_output_file = args.output

    # Execute core logic
    try:
        exit_code, generated_path = project_to_markdown_logic(
            directory=args.directory,
            output_file=final_output_file,
            exclude_dirs=final_exclude_dirs,
            max_file_size=final_max_file_size,
            use_gitignore=final_use_gitignore,
        )

        if exit_code == 0:
            if generated_path:
                try:
                    relative_path = generated_path.relative_to(Path.cwd())
                except ValueError:
                    relative_path = generated_path.resolve()
                print(f"\n✓ Project to Markdown conversion successful!\nFile produced: {relative_path}")
                logger.info("\nTIP: Use this file for AI analysis (ChatGPT, DeepSeek, Qwen).")
            else:
                print("\n✓ Project to Markdown conversion successful, but no specific output file generated (e.g., no non-binary files found).")
            return 0
        else:
            logger.error("Failed to convert project to Markdown file.")
            return 1
    except Exception as e:
        logger.error(f"Error during project to Markdown conversion: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
