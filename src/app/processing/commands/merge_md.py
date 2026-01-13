"""
CLI command to merge multiple Markdown files into a single document for Ambulon.
Utilizes core logic from app.processing.core.markdown_merger.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.markdown_merger import fusion_markdown_files_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'processing': {
        'merge_md': {
            'output_name': "merged.md",
            'title': "Merged Markdown Document",
        }
    }
}

@app.command(
    help="""
    Merges multiple Markdown files from a directory into a single Markdown document.
    Files are merged in alphabetical order, with a generated Table of Contents
    and adapted internal links. Includes validation for balanced code blocks.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/processing.yaml`)
    3. Environment variables
    4. Default values
    """
)
def main(
    source_dir: Path = typer.Argument(..., help="Source directory with Markdown files to merge.", exists=True, file_okay=False, dir_okay=True, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for the merged Markdown file (default: <source_dir>-merged)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/processing.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Merge specific options
    output_name: Optional[str] = typer.Option(None, "--name", "-n", help="Name of the output merged Markdown file (default: merged.md)."),
    title: Optional[str] = typer.Option(None, "--title", help="Title for the merged Markdown document."),
):
    """
    CLI for merging Markdown files.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="merge_md")
    logger.info("[START] Starting merge-md module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    merge_md_config = config['processing']['merge_md']

    # Apply CLI overrides (highest priority) and resolve config
    final_output_name = output_name if output_name is not None else merge_md_config.get('output_name', DEFAULT_CONFIG['processing']['merge_md']['output_name'])
    final_title = title if title is not None else merge_md_config.get('title', DEFAULT_CONFIG['processing']['merge_md']['title'])

    # Determine final output path
    if output is None:
        output_dir_resolved = source_dir.parent / f"{source_dir.name}-merged"
    else:
        output_dir_resolved = output
    final_output_file = output_dir_resolved / final_output_name

    # Execute core logic
    exit_code, generated_path = fusion_markdown_files_logic(
        source_dir=source_dir,
        output_file=final_output_file,
        output_name=final_output_name,
        title=final_title
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
        raise typer.Exit(code=0)
    else:
        logger.error("Failed to merge Markdown files.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()