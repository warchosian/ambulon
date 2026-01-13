"""
CLI command to add a Table of Contents (TOC) to Markdown files for Ambulon.
Utilizes core logic from app.processing.core.markdown_toc_generator.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.markdown_toc_generator import add_toc_to_markdown_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'processing': {
        'add_toc_md': {
            'min_level': 1,
            'max_level': 6,
        }
    }
}

@app.command(
    help="""
    Adds a table of contents to a Markdown file based on its headings.
    The TOC includes anchor links for navigation.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/processing.yaml`)
    3. Environment variables
    4. Default values
    """
)
def main(
    input_file: Path = typer.Argument(..., help="Path to input Markdown file.", exists=True, file_okay=True, dir_okay=False, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output Markdown file path (default: <input>-tocced.md)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/processing.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # TOC specific options
    min_level: Optional[int] = typer.Option(None, "--min-level", help="Minimum heading level to include in TOC (1-6). Overrides config/env."),
    max_level: Optional[int] = typer.Option(None, "--max-level", help="Maximum heading level to include in TOC (1-6). Overrides config/env."),
):
    """
    CLI for adding a table of contents to Markdown files.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="add_toc4md")
    logger.info("[START] Starting add-toc4md module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    add_toc_md_config = config['processing']['add_toc_md']

    # Determine output path
    if output is None:
        output = input_file.parent / f"{input_file.stem}-tocced.md"

    # Apply CLI overrides (highest priority) and resolve config
    final_min_level = min_level if min_level is not None else add_toc_md_config.get('min_level', DEFAULT_CONFIG['processing']['add_toc_md']['min_level'])
    final_max_level = max_level if max_level is not None else add_toc_md_config.get('max_level', DEFAULT_CONFIG['processing']['add_toc_md']['max_level'])

    # Execute core logic
    exit_code, generated_path = add_toc_to_markdown_logic(
        input_file=input_file,
        output_file=output,
        min_level=final_min_level,
        max_level=final_max_level
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
        logger.error("Failed to add TOC to Markdown file.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()