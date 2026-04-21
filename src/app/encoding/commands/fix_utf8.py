"""
CLI command to fix UTF-8 encoding and content issues in Markdown files for Ambulon.
Utilizes the core fixing logic from app.encoding.core.fixer.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
import os
from pathlib import Path
from typing import List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.fixer import fix_markdown_files

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'encoding': {
        'fix_utf8': {
            'backup': False,
        }
    }
}

def main(argv=None):
    """
    CLI for fixing UTF-8 encoding and content issues in Markdown files.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/encoding.yaml`)
    3. Environment variables (e.g., FIX_UTF8_BACKUP)
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="""
Fixes UTF-8 encoding and common content issues in Markdown files.

Configuration Hierarchy (from highest to lowest priority):
1. Command-line arguments
2. YAML configuration file (--config, e.g., config/encoding.yaml)
3. Environment variables (e.g., FIX_UTF8_BACKUP)
4. Default values
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "patterns",
        nargs='+',
        help="Glob pattern(s) for Markdown files (e.g., 'si/**/*.md', 'docs/*.md')."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Not used for this command, but kept for compatibility."
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to a YAML configuration file (e.g., config/encoding.yaml)."
    )
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
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Simulate changes without modifying files."
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a .bak file before modification. Overrides config/env."
    )

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="fix_utf8")
    logger.info("[START] Starting fix-utf8 module.")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    fix_config = config['encoding']['fix_utf8']

    # Apply CLI overrides (highest priority) and resolve config
    final_backup = args.backup if args.backup else fix_config.get('backup', DEFAULT_CONFIG['encoding']['fix_utf8']['backup'])

    # Execute fixing logic
    results = fix_markdown_files(
        patterns=args.patterns,
        dry_run=args.dry_run,
        backup=final_backup
    )

    has_errors = False
    for r in results:
        status = "✅" if r.get('success', False) else "❌"
        msg = r.get('message', 'No message')
        try:
            from app.core.output_paths import format_output_path
            path_str = format_output_path(r['path']) if 'path' in r else 'Unknown Path'
        except KeyError:
            path_str = 'Unknown Path'
        logger.log(logging.INFO if r.get('success', False) else logging.ERROR, f"{status} {path_str} → {msg}")
        if not r.get('success', False):
            has_errors = True

    if has_errors:
        logger.error("\nCompleted with errors.")
        return 1
    else:
        logger.info("\nAll specified Markdown files processed successfully.")
        return 0

if __name__ == '__main__':
    sys.exit(main())