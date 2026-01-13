"""
CLI command to merge/fusion multiple HTML files into a single document for Ambulon.
Utilizes core logic from app.processing.core.html_merger.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.html_merger import fusion_html_files_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'processing': {
        'merge_html': {
            'include_headers': True,
            'title': 'Merged HTML Document',
        }
    }
}

@app.command(
    help="""
    Merges multiple HTML files from a directory into a single fused document.
    Creates a table of contents, section identifiers, and adapts internal links.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/processing.yaml`)
    3. Environment variables
    4. Default values
    """
)
def main(
    source_dir: Path = typer.Argument(..., help="Source directory with .html files to merge.", exists=True, file_okay=False, dir_okay=True, readable=True),
    output: Path = typer.Argument(..., help="Output HTML file path for the merged document."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/processing.yaml)."),

    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Merge specific options
    include_headers: Optional[bool] = typer.Option(None, "--include-headers/--no-headers", help="Add headers showing source file names."),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Title for the merged document."),
):
    """
    CLI for merging HTML files into a single document.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="merge_html")
    logger.info("[START] Starting merge-html module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    merge_html_config = config['processing']['merge_html']

    # Apply CLI overrides (highest priority) and resolve config
    final_include_headers = include_headers if include_headers is not None else merge_html_config.get('include_headers', DEFAULT_CONFIG['processing']['merge_html']['include_headers'])
    final_title = title if title is not None else merge_html_config.get('title', DEFAULT_CONFIG['processing']['merge_html']['title'])

    # Execute core logic
    exit_code, generated_path = fusion_html_files_logic(
        source_dir=source_dir,
        output_file=output,
        include_headers=final_include_headers,
        title=final_title,
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ HTML merging successful!\nOutput file: {relative_path}")
        else:
            print("\n✓ HTML merging successful, but no specific output generated.")
        raise typer.Exit(code=0)
    else:
        logger.error("Failed to merge HTML files.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()
