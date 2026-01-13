"""
CLI command to fix UTF-8 encoding and content issues in Markdown files for Ambulon.
Utilizes the core fixing logic from app.encoding.core.fixer.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.fixer import fix_markdown_files

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'encoding': {
        'fix_utf8': {
            'backup': False,
        }
    }
}

@app.command(
    help="""
    Fixes UTF-8 encoding and common content issues in Markdown files.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/encoding.yaml`)
    3. Environment variables (e.g., FIX_UTF8_BACKUP)
    4. Default values
    """
)
def main(
    patterns: List[str] = typer.Argument(..., help="Glob pattern(s) for Markdown files (e.g., 'si/**/*.md', 'docs/*.md')."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Not used for this command, but kept for compatibility."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/encoding.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Fix specific options
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Simulate changes without modifying files."),
    backup: Optional[bool] = typer.Option(None, "--backup", help="Create a .bak file before modification. Overrides config/env."),
):
    """
    CLI for fixing UTF-8 encoding and content issues in Markdown files.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="fix_utf8")
    logger.info("[START] Starting fix-utf8 module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    fix_config = config['encoding']['fix_utf8']

    # Apply CLI overrides (highest priority) and resolve config
    final_backup = backup if backup is not None else fix_config.get('backup', DEFAULT_CONFIG['encoding']['fix_utf8']['backup'])

    # Execute fixing logic
    results = fix_markdown_files(
        patterns=patterns,
        dry_run=dry_run,
        backup=final_backup
    )

    has_errors = False
    for r in results:
        status = "✅" if r.get('success', False) else "❌"
        msg = r.get('message', 'No message')
        path_str = Path(r['path']).relative_to(Path.cwd()) if 'path' in r else 'Unknown Path'
        logger.log(logging.INFO if r.get('success', False) else logging.ERROR, f"{status} {path_str} → {msg}")
        if not r.get('success', False):
            has_errors = True
    
    if has_errors:
        logger.error("\nCompleted with errors.")
        raise typer.Exit(code=1)
    else:
        logger.info("\nAll specified Markdown files processed successfully.")
        raise typer.Exit(code=0)

if __name__ == '__main__':
    app()