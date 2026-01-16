"""
CLI command to check UTF-8 encoding of Markdown files for Ambulon.
Utilizes the core checking logic from app.encoding.core.checker.
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
from ..core.checker import check_markdown_files

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'encoding': {
        'check_utf8': {
            'min_confidence': 0.7,
        }
    }
}

def main(argv=None):
    """
    CLI for checking UTF-8 encoding of Markdown files.

    Checks UTF-8 encoding of Markdown files.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/encoding.yaml`)
    3. Environment variables (e.g., CHECK_UTF8_MIN_CONFIDENCE)
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="Checks UTF-8 encoding of Markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
  1. Command-line arguments
  2. YAML configuration file (--config)
  3. Environment variables
  4. Default values
        """
    )

    parser.add_argument("patterns", nargs='+', help="Glob pattern(s) for Markdown files (e.g., 'docs/**/*.md').")
    parser.add_argument("-o", "--output", type=Path, help="Not used for this command, but kept for compatibility.")
    parser.add_argument("-c", "--config", type=Path, dest="config_path", help="Path to a YAML configuration file (e.g., config/encoding.yaml).")

    # Global options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress most output messages.")

    # Check specific options
    parser.add_argument("--min-confidence", type=float, help="Minimum confidence for encoding detection (0.0 to 1.0). Overrides config/env.")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="check_utf8")
    logger.info("[START] Starting check-utf8 module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config_path) if args.config_path else None, DEFAULT_CONFIG)
    check_config = config['encoding']['check_utf8']

    # Apply CLI overrides (highest priority) and resolve config
    final_min_confidence = args.min_confidence if args.min_confidence is not None else check_config.get('min_confidence', DEFAULT_CONFIG['encoding']['check_utf8']['min_confidence'])

    # Execute checking logic
    results = check_markdown_files(
        patterns=args.patterns,
        min_confidence=final_min_confidence
    )

    has_issue = False
    for res in results:
        encoding = res.get('encoding') or 'inconnu'
        confidence = res.get('confidence', 0.0)
        error = res.get('error')
        path_str = Path(res['path']).relative_to(Path.cwd()) if 'path' in res else 'Unknown Path'

        if error:
            logger.error(f"[ERREUR] {path_str}: {error}")
            has_issue = True
        elif encoding != 'utf-8':
            logger.warning(f"[WARN] {path_str}: encodage {encoding.upper()} (confiance {confidence:.2%})")
            has_issue = True
        else:
            logger.info(f"[OK] {path_str}: UTF-8 (confiance {confidence:.2%})")

    if has_issue:
        logger.warning(f"\nVérification terminée avec des problèmes d'encodage. Voir les logs ci-dessus.")
        return 1
    else:
        logger.info(f"\nTous les fichiers vérifiés sont correctement encodés en UTF-8.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
