"""
CLI command to extract and filter applications from JSON data for Ambulon.
Utilizes core logic from app.wikisi.core.extractor.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.extractor import process_parkjson2json_logic

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'wikisi': {
        'extract_json': {
            'preserve_structure': True,
            'include_metadata': True,
        }
    }
}

@app.command(
    help="""
    Extracts and filters applications from a JSON file, creating a new JSON file
    with only the selected applications. Supports filtering by range, name, or ID.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/wikisi.yaml`)
    3. Environment variables (e.g., WIKISI_EXTRACT_PRESERVE_STRUCTURE)
    4. Default values
    """
)
def main(
    input_file: Path = typer.Argument(..., help="Path to input JSON file.", exists=True, file_okay=True, dir_okay=False, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file path (default: input_FILTER.json, or input.json without filter)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/wikisi.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Filter options
    range_spec: Optional[str] = typer.Option(None, "--range", "-r", help='Select range of applications (e.g., "1-3", "-5" for last 5, "10-" from 10 to end).'),
    name_filter: Optional[str] = typer.Option(None, "--name", "-n", help="Filter applications by name (case-insensitive substring match)."),
    id_filter: Optional[str] = typer.Option(None, "--id", "-i", help="Filter applications by ID (case-insensitive substring match)."),

    # Output options
    preserve_structure: Optional[bool] = typer.Option(None, "--preserve-structure", help="Preserve original JSON structure (default: True). Set with --no-preserve-structure to disable."),
    no_preserve_structure: bool = typer.Option(False, "--no-preserve-structure", help="Do not preserve original JSON structure."),
    include_metadata: Optional[bool] = typer.Option(None, "--include-metadata", help="Include metadata in output JSON (default: True). Set with --no-include-metadata to disable."),
    no_include_metadata: bool = typer.Option(False, "--no-include-metadata", help="Do not include metadata in output JSON."),
    split_dir: Optional[Path] = typer.Option(None, "--split-dir", help="Directory to generate separate files for each application."),
):
    """
    CLI for extracting and filtering applications from JSON.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="wikisi_extract_json")
    logger.info("[START] Starting wikisi-extract-json module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    extract_config = config['wikisi']['extract_json']

    # Apply CLI overrides (highest priority) and resolve config
    final_preserve_structure = preserve_structure if preserve_structure is not None else extract_config.get('preserve_structure', DEFAULT_CONFIG['wikisi']['extract_json']['preserve_structure'])
    if no_preserve_structure:
        final_preserve_structure = False

    final_include_metadata = include_metadata if include_metadata is not None else extract_config.get('include_metadata', DEFAULT_CONFIG['wikisi']['extract_json']['include_metadata'])
    if no_include_metadata:
        final_include_metadata = False

    # Execute extraction logic
    exit_code, generated_path = process_parkjson2json_logic(
        input_file=input_file,
        output_file=output,
        range_spec=range_spec,
        name_filter=name_filter,
        id_filter=id_filter,
        preserve_structure=final_preserve_structure,
        include_metadata=final_include_metadata,
        split_dir=split_dir
    )

    if exit_code == 0:
        if generated_path:
            try:
                relative_path = generated_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = generated_path.resolve()
            print(f"\n✓ Extraction successful!\nFile produced: {relative_path}")
        else:
            print("\n✓ Extraction successful, no specific output file generated (e.g., no matching apps for filter).")
        raise typer.Exit(code=0)
    else:
        logger.error("JSON extraction failed.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()