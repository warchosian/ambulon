"""
CLI command for OCR (Optical Character Recognition) for Ambulon.
Handles configuration hierarchy, logging, and displays generated file paths.
"""

import typer
import logging
import os
import sys
import subprocess # Needed for NAPS2 GUI
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from app.ocr.core.ocr_logic import perform_ocr_single_file, process_multiple_files

logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    'ocr': {
        'language': 'fra',
        'psm': '3', # Page Segmentation Mode
        'oem': '3'  # OCR Engine Mode
    },
    'tools': {
        'tesseract_command': os.getenv('TESSERACT_COMMAND', 'tesseract'),
        'tesseract_enabled': os.getenv('TESSERACT_ENABLED', 'True').lower() == 'true',
        'tesseract_python_alternative': os.getenv('TESSERACT_PYTHON_ALTERNATIVE', 'False').lower() == 'true',
        'tesseract_fallback_enabled': os.getenv('TESSERACT_FALLBACK_ENABLED', 'False').lower() == 'true',
        'tesseract_timeout': os.getenv('TESSERACT_TIMEOUT', 60)
    }
}

@app.command(
    help="""
    Performs Optical Character Recognition (OCR) on image or PDF files.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/ocr.yaml`)
    3. Environment variables (e.g., OCR_LANGUAGE, TESSERACT_COMMAND)
    4. Default values

    Environment variables:
      OCR_LANGUAGE          Default OCR language
      TESSERACT_COMMAND     Path to tesseract executable
      TESSERACT_ENABLED     Enable Tesseract (True/False)
    """
)
def main(
    input: str = typer.Argument(..., help="Input file, directory, or glob pattern (e.g., image.jpg, folder/, \"*.png\")."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file or directory (default: same folder as input, .txt extension)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/ocr.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # OCR specific options
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Language for OCR (e.g., fra, eng, fra+eng)."),
    psm: Optional[str] = typer.Option(None, "--psm", help="Page Segmentation Mode (0-13)."),
    oem: Optional[str] = typer.Option(None, "--oem", help="OCR Engine Mode (0-3)."),
):
    """
    CLI for Optical Character Recognition.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout # Ensure output goes to console
    )
    logger.info("[START] Starting OCR module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    ocr_config = config['ocr']
    tool_config = config['tools']

    # Apply CLI overrides (highest priority) and resolve config
    final_language = language if language is not None else ocr_config.get('language', DEFAULT_CONFIG['ocr']['language'])
    final_psm = psm if psm is not None else ocr_config.get('psm', DEFAULT_CONFIG['ocr']['psm'])
    final_oem = oem if oem is not None else ocr_config.get('oem', DEFAULT_CONFIG['ocr']['oem'])

    # Determine input type
    input_path = Path(input)
    has_wildcards = '*' in input or '?' in input

    ocr_tool_config = {
        'enabled': tool_config['tesseract_enabled'],
        'command': tool_config['tesseract_command'],
        'python_alternative': tool_config['tesseract_python_alternative'],
        'fallback_enabled': tool_config['tesseract_fallback_enabled'],
        'timeout': tool_config['tesseract_timeout'],
        'psm': final_psm,
        'oem': final_oem
    }

    generated_files: Optional[List[Path]] = None

    if input_path.is_dir() or has_wildcards:
        # Mode: process multiple files (directory or glob pattern)
        logger.info(f"Mode: Processing multiple files from pattern/directory: {input}")
        generated_files = process_multiple_files(
            file_pattern=input,
            ocr_lang=final_language,
            ocr_tool_config=ocr_tool_config,
            output_dir=output # This handles both file and dir output
        )
    elif input_path.is_file():
        # Mode: single file
        logger.info(f"Mode: Processing single file: {input}")
        result_file = perform_ocr_single_file(
            image_file=input_path,
            ocr_config=ocr_tool_config,
            language=final_language,
            output_file=output
        )
        if result_file:
            generated_files = [result_file]
    else:
        logger.error(f"Input '{input}' is not a valid file, directory or glob pattern.")
        raise typer.Exit(code=1)

    if generated_files:
        logger.info(f"OCR operation successful. Generated {len(generated_files)} file(s).")
        for f in generated_files:
            try:
                relative_path = os.path.relpath(f)
            except ValueError:
                relative_path = f.resolve()
            print(f"\n✓ OCR réussi !\nFichier produit : {relative_path}")
        raise typer.Exit(code=0)
    else:
        logger.error("OCR operation failed or no files were generated.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()
