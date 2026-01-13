"""
CLI command to concatenate HTML files from a directory into a single HTML file for Ambulon.
Utilizes core logic from app.processing.core.html_concatenator.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_concatenator import concatenate_html_files_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'processing': {
        'concat_html': {
            'include_headers': True,
            'title': "Concatenated HTML",
        }
    }
}

@app.command(
    help=f"""
    Concatenates multiple HTML files from a specified directory into a single HTML file.
    Files are sorted in natural (numeric) order.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/processing.yaml`)
    3. Environment variables
    4. Default values
    """,
)
def main(
    directory: Path = typer.Argument(..., help="Directory containing HTML files.", exists=True, file_okay=False, dir_okay=True, readable=True),
    output: Path = typer.Option(..., "--output", "-o", help="Output HTML file path."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/processing.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Concatenation specific options
    include_headers: Optional[bool] = typer.Option(None, "--include-headers", help="Add headers showing source file names. Set with --no-headers to disable."),
    no_headers: bool = typer.Option(False, "--no-headers", help="Do not add headers showing source file names."),
    title: Optional[str] = typer.Option(None, "--title", help="Title for the concatenated document."),
):
    """
    CLI for concatenating HTML files.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="concat_html")
    logger.info("[START] Starting concat-html module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    concat_html_config = config['processing']['concat_html']

    # Apply CLI overrides (highest priority) and resolve config
    final_include_headers = include_headers if include_headers is not None else concat_html_config.get('include_headers', DEFAULT_CONFIG['processing']['concat_html']['include_headers'])
    if no_headers:
        final_include_headers = False
    
    final_title = title if title is not None else concat_html_config.get('title', DEFAULT_CONFIG['processing']['concat_html']['title'])

    # Execute core logic
    exit_code, generated_path = concatenate_html_files_logic(
        directory=directory,
        output_file=output,
        include_headers=final_include_headers,
        title=final_title
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ Concatenation successful!\nFile produced: {relative_path}")
        else:
            print("\n✓ Concatenation successful, but no specific output file generated (e.g., no HTML files found).")
        raise typer.Exit(code=0)
    else:
        logger.error("Failed to concatenate HTML files.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()