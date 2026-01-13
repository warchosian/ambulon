"""
CLI command to convert a project directory to a single Markdown file for AI analysis for Ambulon.
Utilizes core logic from app.processing.core.project_to_md_converter.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import List, Optional, Set

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.project_to_md_converter import project_to_markdown_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

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

@app.command(
    help="""
    Scans a project directory and generates a single Markdown file containing:
    - A clickable file tree (table of contents).
    - All non-binary files as collapsible code blocks.
    - Relative file paths and syntax highlighting.
    Perfect for AI code analysis.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/processing.yaml`)
    3. Environment variables
    4. Default values
    """
)
def main(
    directory: Path = typer.Argument(..., help="Path to the project directory to scan.", exists=True, file_okay=False, dir_okay=True, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output Markdown file path (default: <directory_name>_project.md)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/processing.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Conversion specific options
    exclude_dirs: Optional[List[str]] = typer.Option(None, "--exclude", help="Additional directory names to exclude (e.g., 'logs', 'temp')."),
    max_file_size: Optional[int] = typer.Option(None, "--max-size", help="Maximum file size in bytes to include (default: 1MB)."),
    use_gitignore: Optional[bool] = typer.Option(None, "--use-gitignore", help="Respect .gitignore patterns. Set with --no-gitignore to disable."),
    no_gitignore: bool = typer.Option(False, "--no-gitignore", help="Do not respect .gitignore patterns."),
):
    """
    CLI for converting project directories to Markdown.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="project2md")
    logger.info("[START] Starting project2md module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    project2md_config = config['processing']['project2md']

    # Apply CLI overrides (highest priority) and resolve config
    final_exclude_dirs = set(exclude_dirs) if exclude_dirs else set()
    final_exclude_dirs.update(project2md_config.get('exclude_dirs', DEFAULT_CONFIG['processing']['project2md']['exclude_dirs']))

    final_max_file_size = max_file_size if max_file_size is not None else project2md_config.get('max_file_size', DEFAULT_CONFIG['processing']['project2md']['max_file_size'])

    final_use_gitignore = use_gitignore if use_gitignore is not None else project2md_config.get('use_gitignore', DEFAULT_CONFIG['processing']['project2md']['use_gitignore'])
    if no_gitignore:
        final_use_gitignore = False
    
    # Determine final output path
    if output is None:
        project_name = directory.name
        final_output_name = project2md_config.get('output_name', DEFAULT_CONFIG['processing']['project2md']['output_name'])
        final_output_file = directory.parent / Path(final_output_name.replace("{project_name}", project_name))
    else:
        final_output_file = output

    # Execute core logic
    exit_code, generated_path = project_to_markdown_logic(
        directory=directory,
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
        raise typer.Exit(code=0)
    else:
        logger.error("Failed to convert project to Markdown file.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()