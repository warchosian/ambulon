"""
CLI command to convert JSON data to optimal Markdown format for Ambulon.
Utilizes core logic from app.core.json_to_md_converter.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.json_to_md_converter import process_parkjson2md_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'wikisi': {
        'json_to_md': {
            'min_confidence': 0.7, # Example config, might not be used here directly
        }
    }
}

@app.command(
    help="""
    Converts JSON data (e.g., application park data) to an optimized Markdown format.
    Supports filtering by range, name, or ID.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/wikisi.yaml`)
    3. Environment variables (e.g., WIKISI_JSON_TO_MD_MIN_CONFIDENCE)
    4. Default values
    """
)
def main(
    input_file: Path = typer.Argument(..., help="Path to input JSON file.", exists=True, file_okay=True, dir_okay=False, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output Markdown file path (default: input_FILTER.md, or input.md without filter)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/wikisi.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Filter options
    range_spec: Optional[str] = typer.Option(None, "--range", "-r", help='Select range of applications (e.g., "1-3", "-5" for last 5, "10-" from 10 to end).'),
    name_filter: Optional[str] = typer.Option(None, "--name", "-n", help="Filter applications by name (case-insensitive substring match)."),
    id_filter: Optional[str] = typer.Option(None, "--id", "-i", help="Filter applications by ID (case-insensitive substring match)."),

    # Output options
    split_dir: Optional[Path] = typer.Option(None, "--split-dir", help="Directory to generate separate Markdown files for each application."),
):
    """
    CLI for converting JSON to Markdown.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="wikisi_json_to_md")
    logger.info("[START] Starting wikisi-json-to-md module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    # json_to_md_config = config['wikisi']['json_to_md'] # Not directly used in this command for now

    # Execute conversion logic
    exit_code, generated_path = process_parkjson2md_logic(
        input_file=input_file,
        output_file=output,
        range_spec=range_spec,
        name_filter=name_filter,
        id_filter=id_filter,
        split_dir=split_dir
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ Conversion successful!\nFile produced: {relative_path}")
        else:
            print("\n✓ Conversion successful, no specific output file generated (e.g., no matching apps for filter).")
        raise typer.Exit(code=0)
    else:
        logger.error("JSON to Markdown conversion failed.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()