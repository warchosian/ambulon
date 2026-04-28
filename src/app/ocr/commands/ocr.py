"""
CLI command for OCR (Optical Character Recognition) for Ambulon.
Handles configuration hierarchy, logging, and displays generated file paths.
"""

import argparse
import logging
import os
import sys
import subprocess # Needed for NAPS2 GUI
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from app.ocr.core.ocr_logic import perform_ocr_single_file, process_multiple_files, _process_pdf_ocr

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'ocr': {
        'language': 'fra',
        'psm': '3', # Page Segmentation Mode
        'oem': '3'  # OCR Engine Mode
    },
    'tools': {
        # Prefer AMBULON_TESSERACT_* but keep legacy TESSERACT_* for retrocompat.
        'tesseract_command': os.getenv('AMBULON_TESSERACT_COMMAND', os.getenv('TESSERACT_COMMAND', 'tesseract')),
        'tesseract_enabled': os.getenv('AMBULON_TESSERACT_ENABLED', os.getenv('TESSERACT_ENABLED', 'True')).lower() == 'true',
        'tesseract_python_alternative': os.getenv('AMBULON_TESSERACT_PYTHON_ALTERNATIVE', os.getenv('TESSERACT_PYTHON_ALTERNATIVE', 'False')).lower() == 'true',
        'tesseract_fallback_enabled': os.getenv('AMBULON_TESSERACT_FALLBACK_ENABLED', os.getenv('TESSERACT_FALLBACK_ENABLED', 'False')).lower() == 'true',
        'tesseract_timeout': os.getenv('AMBULON_TESSERACT_TIMEOUT', os.getenv('TESSERACT_TIMEOUT', '60'))
    }
}

def main(argv=None):
    """
    CLI for Optical Character Recognition.

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
    parser = argparse.ArgumentParser(
        description="Performs Optical Character Recognition (OCR) on image or PDF files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
1. Command-line arguments
2. YAML configuration file (--config)
3. Environment variables (OCR_*, TESSERACT_*)
4. Default values

Environment variables:
  OCR_LANGUAGE          Default OCR language
  TESSERACT_COMMAND     Path to tesseract executable
  TESSERACT_ENABLED     Enable Tesseract (True/False)
        """
    )

    parser.add_argument("input", type=str, help="Input file, directory, or glob pattern (e.g., image.jpg, folder/, \"*.png\").")
    parser.add_argument("-o", "--output", type=Path, help="Output file or directory (default: same folder as input, .txt extension).")
    parser.add_argument("-c", "--config", type=Path, help="Path to a YAML configuration file (e.g., config/ocr.yaml).")

    # Global options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress most output messages.")

    # OCR specific options
    parser.add_argument("-l", "--lang", type=str, help="Language for OCR (e.g., fra, eng, fra+eng).")
    parser.add_argument("--psm", type=str, help="Page Segmentation Mode (0-13).")
    parser.add_argument("--oem", type=str, help="OCR Engine Mode (0-3).")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="ocr")
    logger.info("[START] Starting OCR module.")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    ocr_config = config['ocr']
    tool_config = config['tools']

    # Apply CLI overrides (highest priority) and resolve config
    final_language = args.lang if args.lang is not None else ocr_config.get('language', DEFAULT_CONFIG['ocr']['language'])
    final_psm = args.psm if args.psm is not None else ocr_config.get('psm', DEFAULT_CONFIG['ocr']['psm'])
    final_oem = args.oem if args.oem is not None else ocr_config.get('oem', DEFAULT_CONFIG['ocr']['oem'])

    # Determine input type
    input_path = Path(args.input)
    has_wildcards = '*' in args.input or '?' in args.input

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
        logger.info(f"Mode: Processing multiple files from pattern/directory: {args.input}")
        generated_files = process_multiple_files(
            file_pattern=args.input,
            ocr_lang=final_language,
            ocr_tool_config=ocr_tool_config,
            output_dir=args.output # This handles both file and dir output
        )
    elif input_path.is_file():
        # Mode: single file
        logger.info(f"Mode: Processing single file: {args.input}")
        if input_path.suffix.lower() == '.pdf':
            # Determine output: same path/name as input, extension .md
            if args.output:
                output_file = Path(args.output)
            else:
                output_file = input_path.with_suffix('.md')
            result = _process_pdf_ocr(input_path, final_language, output_file)
            if result.get('success') and result.get('output_file'):
                generated_files = [Path(result['output_file'])]
        else:
            result_file = perform_ocr_single_file(
                image_file=input_path,
                language=final_language,
                output_file=args.output
            )
            if result_file:
                generated_files = [result_file]
    else:
        logger.error(f"Input '{args.input}' is not a valid file, directory or glob pattern.")
        return 1

    if generated_files:
        logger.info(f"OCR operation successful. Generated {len(generated_files)} file(s).")
        for f in generated_files:
            try:
                relative_path = os.path.relpath(f)
            except ValueError:
                relative_path = str(f)
            print(f"\n✓ OCR réussi !\nFichier produit : {relative_path}")
        return 0
    else:
        logger.error("OCR operation failed or no files were generated.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
