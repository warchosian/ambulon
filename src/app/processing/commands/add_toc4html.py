"""
CLI command to add a Table of Contents (TOC) to HTML files for Ambulon.
Utilizes core logic from app.processing.core.html_toc_generator.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_toc_generator import add_toc_to_html_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'processing': {
        'add_toc_html': {
            # No specific config options for now
        }
    }
}

@app.command(
    help="""
    Adds a table of contents to an HTML file based on its headings.
    The TOC includes anchor links for navigation, and CSS is injected for styling.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/processing.yaml`)
    3. Environment variables
    4. Default values
    """
)
def main(
    input_file: Path = typer.Argument(..., help="Path to input HTML file.", exists=True, file_okay=True, dir_okay=False, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output HTML file path (default: <input>-tocced.html)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/processing.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # TOC specific options (min-level, max-level are not yet implemented in core logic)
    min_level: int = typer.Option(1, "--min-level", help="Minimum heading level to include in TOC (1-6)."),
    max_level: int = typer.Option(6, "--max-level", help="Maximum heading level to include in TOC (1-6)."),
):
    """
    CLI for adding a table of contents to HTML files.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="add_toc4html")
    logger.info("[START] Starting add-toc4html module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    # add_toc_html_config = config['processing']['add_toc_html'] # Not directly used for now

    # Determine output path
    if output is None:
        output = input_file.parent / f"{input_file.stem}-tocced{input_file.suffix}"

    # Execute core logic
    exit_code, generated_path = add_toc_to_html_logic(
        input_file=input_file,
        output_file=output
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ TOC added successfully!\nFile produced: {relative_path}")
        else:
            print("\n✓ TOC operation successful, but no specific output file generated (e.g., no headings found).")
        raise typer.Exit(code=0)
    else:
        logger.error("Failed to add TOC to HTML file.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()