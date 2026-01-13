"""
CLI command to flatten an HTML directory structure for Ambulon.
Utilizes core logic from app.processing.core.html_flattener.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_flattener import flatten_html_directory_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'processing': {
        'flatten_html': {
            # No specific config options for now
        }
    }
}

@app.command(
    help="""
    Flattens a nested HTML directory structure into a single directory.
    All .html files are copied, and their internal links are adapted to
    work in the flattened structure.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/processing.yaml`)
    3. Environment variables
    4. Default values
    """
)
def main(
    source_dir: Path = typer.Argument(..., help="Source directory with nested HTML files.", exists=True, file_okay=False, dir_okay=True, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory (default: <source_dir>-flattened)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/processing.yaml)."),

    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),
):
    """
    CLI for flattening HTML directory structures.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="flatten_html")
    logger.info("[START] Starting flatten-html module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    # flatten_html_config = config['processing']['flatten_html'] # Not directly used for now

    # Execute core logic
    exit_code, generated_path = flatten_html_directory_logic(
        source_dir=source_dir,
        output_dir=output,
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ HTML flattening successful!\nOutput directory: {relative_path}")
        else:
            print("\n✓ HTML flattening successful, but no specific output generated (e.g., no HTML files found).")
        raise typer.Exit(code=0)
    else:
        logger.error("Failed to flatten HTML directory.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()
