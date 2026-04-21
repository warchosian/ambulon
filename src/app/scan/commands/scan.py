"""
CLI command for TWAIN scanning with DPI profiles for Ambulon.
Handles configuration hierarchy, logging, and displays generated file paths.
"""

import argparse
import logging
import os
import re
import sys
import subprocess # Needed for Popen for NAPS2 GUI
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from app.scan.core.scanning import scan_document
from app.scan.core.ocr import process_existing_files

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'scan': {
        'resolution': 100,
        'profile': 'TWAIN-100ppp',
        'device': None,
        'source': 'flatbed',
        'color_mode': 'color',
        'paper_size': 'A4',
        'orientation': 'portrait',
        'brightness': 0,
        'contrast': 0,
        'gamma': 1.0,
        'format': 'jpg',
        'quality': 90,
        'naming': 'date',
        'increment': False,
        'ocr': False,
        'lang': 'fra',
        'deskew': False,
        'despeckle': False,
        'crop': False,
        'number': 1,
        'pages': 1,
        'batch': False,
        'separator': False,
        'auto_feed': False,
        'preview': False,
        'calibrate': False,
        'test_pattern': False,
        'timeout': 60 # For NAPS2
    },
    'tools': {
        # NAPS2 paths must come from environment or YAML config (no hardcoded personal path)
        'naps2_console_command': os.getenv('AMBULON_NAPS2_CONSOLE_COMMAND', os.getenv('NAPS2_CONSOLE_COMMAND', 'NAPS2.Console.exe')),
        'naps2_gui_command': os.getenv('AMBULON_NAPS2_GUI_COMMAND', os.getenv('NAPS2_GUI_COMMAND', 'NAPS2.exe')),
        'tesseract_command': os.getenv('TESSERACT_COMMAND', 'tesseract'),
        'tesseract_enabled': os.getenv('TESSERACT_ENABLED', 'True').lower() == 'true',
        'tesseract_python_alternative': os.getenv('TESSERACT_PYTHON_ALTERNATIVE', 'False').lower() == 'true',
        'tesseract_fallback_enabled': os.getenv('TESSERACT_FALLBACK_ENABLED', 'False').lower() == 'true',
        'tesseract_timeout': os.getenv('TESSERACT_TIMEOUT', 60)
    }
}

def main(argv=None):
    """
    CLI for TWAIN scanning.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`, e.g., `config/scan.yaml`)
    3. Environment variables (e.g., SCAN_RESOLUTION, SCAN_OCR_LANG, NAPS2_CONSOLE_COMMAND)
    4. Default values

    Environment variables:
      SCAN_RESOLUTION       Default scan resolution (DPI)
      SCAN_PROFILE          Default TWAIN profile
      SCAN_OUTPUT_DIR       Default output directory
      SCAN_FORMAT           Default output format
      SCAN_OCR              Enable OCR by default (True/False)
      SCAN_OCR_LANG         Default OCR language
      NAPS2_CONSOLE_COMMAND Path to NAPS2.Console.exe
      TESSERACT_COMMAND     Path to tesseract executable
    """
    parser = argparse.ArgumentParser(
        description="Scans documents using TWAIN compatible scanners (via NAPS2 Console).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
1. Command-line arguments
2. YAML configuration file (--config)
3. Environment variables (SCAN_*, NAPS2_*, TESSERACT_*)
4. Default values

Environment variables:
  SCAN_RESOLUTION       Default scan resolution (DPI)
  SCAN_PROFILE          Default TWAIN profile
  SCAN_FORMAT           Default output format
  SCAN_OCR              Enable OCR by default (True/False)
  SCAN_OCR_LANG         Default OCR language
  NAPS2_CONSOLE_COMMAND Path to NAPS2.Console.exe
  TESSERACT_COMMAND     Path to tesseract executable
        """
    )

    # Main options
    parser.add_argument("-o", "--output", type=Path, help="Output directory or base file name (e.g., scans/ or scans/document). Required for scanning.")
    parser.add_argument("-c", "--config", type=Path, help="Path to a YAML configuration file (e.g., config/scan.yaml).")

    # Global options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress most output messages.")

    # Scan options
    parser.add_argument("-r", "--resolution", type=int, help="Scan resolution in DPI (100-1200).")
    parser.add_argument("-p", "--profile", type=str, help="Predefined TWAIN profile (e.g., TWAIN-300ppp).")
    parser.add_argument("--device", type=str, help="Scanner device to use.")
    parser.add_argument("--source", type=str, help="Scanner source (flatbed, adf, duplex).")
    parser.add_argument("--color-mode", type=str, help="Color mode (color, grayscale, bw).")
    parser.add_argument("--paper-size", type=str, help="Paper size (A4, A3, Letter, Legal, Custom).")
    parser.add_argument("--orientation", type=str, help="Orientation (portrait, landscape).")
    parser.add_argument("--brightness", type=int, help="Brightness (-100 to 100).")
    parser.add_argument("--contrast", type=int, help="Contrast (-100 to 100).")
    parser.add_argument("--gamma", type=float, help="Gamma correction (0.1 to 3.0).")

    # Output options
    parser.add_argument("-f", "--format", type=str, help="Output format (pdf, png, jpg, jpeg, tiff, svg).")
    parser.add_argument("--quality", type=int, help="Compression quality (1-100).")
    parser.add_argument("--naming", type=str, help="Naming convention (date, sequence, custom).")
    parser.add_argument("--increment", action="store_true", help="Enable auto-incrementation of filename.")
    parser.add_argument("--no-increment", action="store_true", help="Disable auto-incrementation (use filename as-is).")

    # Post-scan processing options
    parser.add_argument("--ocr", action="store_true", help="Enable OCR after scan.")
    parser.add_argument("--lang", type=str, help="Language for OCR (e.g., fra, eng, fra+eng).")
    parser.add_argument("--deskew", action="store_true", help="Automatic deskewing.")
    parser.add_argument("--despeckle", action="store_true", help="Despeckle images.")
    parser.add_argument("--crop", action="store_true", help="Automatic cropping.")

    # Batch options
    parser.add_argument("-n", "--number", type=int, help="Number of scans to perform.")
    parser.add_argument("--pages", type=int, help="Number of pages to scan (for ADF).")
    parser.add_argument("--batch", action="store_true", help="Batch mode for multiple documents.")
    parser.add_argument("--separator", action="store_true", help="Separator page between documents.")
    parser.add_argument("--auto-feed", action="store_true", help="Automatic document feeder (ADF).")

    # Advanced options
    parser.add_argument("--calibrate", action="store_true", help="Calibrate scanner.")
    parser.add_argument("--test-pattern", action="store_true", help="Scan a test pattern.")
    parser.add_argument("--manual", action="store_true", help="Open NAPS2 GUI for manual configuration.")
    parser.add_argument("--timeout", type=int, help="Timeout for scan operations in seconds.")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="scan")
    logger.info("[START] Starting scan module.")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    scan_config = config['scan']
    tool_config = config['tools']

    # Handle manual NAPS2 GUI option (special case, bypasses scanning)
    if args.manual:
        try:
            naps2_gui_executable = tool_config.get('naps2_gui_command', DEFAULT_CONFIG['tools']['naps2_gui_command'])
            if not Path(naps2_gui_executable).exists():
                logger.error(f"NAPS2 GUI not found: {naps2_gui_executable}")
                return 1

            logger.info(f"Opening NAPS2 GUI: {naps2_gui_executable}")
            subprocess.Popen([naps2_gui_executable])
            logger.info("NAPS2 GUI opened.")
            return 0
        except Exception as e:
            logger.error(f"Error opening NAPS2 GUI: {e}")
            return 1

    # Validate output path
    if args.output is None:
        logger.error("Error: --output/-o is required.")
        return 1

    output_str = str(args.output)
    has_wildcards = '*' in output_str or '?' in output_str
    has_extension = '.' in Path(output_str).name

    # Apply CLI overrides (highest priority) and resolve config
    final_resolution = args.resolution if args.resolution is not None else scan_config.get('resolution', DEFAULT_CONFIG['scan']['resolution'])
    final_profile = args.profile if args.profile is not None else scan_config.get('profile', DEFAULT_CONFIG['scan']['profile'])
    final_device = args.device if args.device is not None else scan_config.get('device', DEFAULT_CONFIG['scan']['device'])
    final_source = args.source if args.source is not None else scan_config.get('source', DEFAULT_CONFIG['scan']['source'])
    final_color_mode = getattr(args, 'color_mode', None) if getattr(args, 'color_mode', None) is not None else scan_config.get('color_mode', DEFAULT_CONFIG['scan']['color_mode'])
    final_paper_size = getattr(args, 'paper_size', None) if getattr(args, 'paper_size', None) is not None else scan_config.get('paper_size', DEFAULT_CONFIG['scan']['paper_size'])
    final_orientation = args.orientation if args.orientation is not None else scan_config.get('orientation', DEFAULT_CONFIG['scan']['orientation'])
    final_brightness = args.brightness if args.brightness is not None else scan_config.get('brightness', DEFAULT_CONFIG['scan']['brightness'])
    final_contrast = args.contrast if args.contrast is not None else scan_config.get('contrast', DEFAULT_CONFIG['scan']['contrast'])
    final_gamma = args.gamma if args.gamma is not None else scan_config.get('gamma', DEFAULT_CONFIG['scan']['gamma'])
    final_format = args.format if args.format is not None else scan_config.get('format', DEFAULT_CONFIG['scan']['format'])
    final_quality = args.quality if args.quality is not None else scan_config.get('quality', DEFAULT_CONFIG['scan']['quality'])
    final_naming = args.naming if args.naming is not None else scan_config.get('naming', DEFAULT_CONFIG['scan']['naming'])
    final_increment = args.increment if args.increment else scan_config.get('increment', DEFAULT_CONFIG['scan']['increment'])

    # Override increment based on no_increment (CLI has highest priority)
    if args.no_increment:
        final_increment = False

    final_ocr = args.ocr if args.ocr else scan_config.get('ocr', DEFAULT_CONFIG['scan']['ocr'])
    final_lang = args.lang if args.lang is not None else scan_config.get('lang', DEFAULT_CONFIG['scan']['lang'])
    final_deskew = args.deskew if args.deskew else scan_config.get('deskew', DEFAULT_CONFIG['scan']['deskew'])
    final_despeckle = args.despeckle if args.despeckle else scan_config.get('despeckle', DEFAULT_CONFIG['scan']['despeckle'])
    final_crop = args.crop if args.crop else scan_config.get('crop', DEFAULT_CONFIG['scan']['crop'])
    final_number = args.number if args.number is not None else scan_config.get('number', DEFAULT_CONFIG['scan']['number'])
    final_pages = args.pages if args.pages is not None else scan_config.get('pages', DEFAULT_CONFIG['scan']['pages'])
    final_batch = args.batch if args.batch else scan_config.get('batch', DEFAULT_CONFIG['scan']['batch'])
    final_separator = args.separator if args.separator else scan_config.get('separator', DEFAULT_CONFIG['scan']['separator'])
    final_auto_feed = getattr(args, 'auto_feed', False) if getattr(args, 'auto_feed', False) else scan_config.get('auto_feed', DEFAULT_CONFIG['scan']['auto_feed'])
    final_preview = scan_config.get('preview', DEFAULT_CONFIG['scan']['preview'])
    final_calibrate = args.calibrate if args.calibrate else scan_config.get('calibrate', DEFAULT_CONFIG['scan']['calibrate'])
    final_test_pattern = getattr(args, 'test_pattern', False) if getattr(args, 'test_pattern', False) else scan_config.get('test_pattern', DEFAULT_CONFIG['scan']['test_pattern'])
    final_timeout = args.timeout if args.timeout is not None else scan_config.get('timeout', DEFAULT_CONFIG['scan']['timeout'])


    # Determine the resolution to use: positional arg (if it existed) > --resolution > config > default
    # Since dpi_profile positional is removed, this simplifies to final_resolution
    dpi_to_use = final_resolution
    
    # Generate TWAIN profile based on resolution if no specific profile is provided
    # or if default profile is used
    if final_profile == 'TWAIN-100ppp' or final_profile is None: # If default or not set, generate based on final_resolution
        final_profile = f"TWAIN-{dpi_to_use}ppp"
    else: # If custom profile is set, extract DPI from it if possible
        profile_match = re.search(r'TWAIN-(\d+)ppp', final_profile)
        if profile_match:
            profile_dpi = int(profile_match.group(1))
            if profile_dpi != dpi_to_use:
                logger.warning(f"Inconsistency detected: requested DPI ({dpi_to_use}) != profile DPI ({profile_dpi}). Using profile DPI ({profile_dpi}).")
                dpi_to_use = profile_dpi
        else:
            logger.warning(f"Custom profile '{final_profile}' does not contain DPI. Using resolution {dpi_to_use} from config/CLI.")

    scan_params = {
        'profile': final_profile,
        'device': final_device,
        'source': final_source,
        'color_mode': final_color_mode,
        'paper_size': final_paper_size,
        'orientation': final_orientation,
        'brightness': final_brightness,
        'contrast': final_contrast,
        'gamma': final_gamma,
        'format': final_format,
        'quality': final_quality,
        'naming': final_naming,
        'increment': final_increment,
        'ocr': final_ocr,
        'lang': final_lang,
        'deskew': final_deskew,
        'despeckle': final_despeckle,
        'crop': final_crop,
        'number': final_number,
        'pages': final_pages,
        'batch': final_batch,
        'separator': final_separator,
        'auto_feed': final_auto_feed,
        'preview': final_preview,
        'calibrate': final_calibrate,
        'test_pattern': final_test_pattern,
        'timeout': final_timeout
    }

    if has_wildcards and has_extension:
        # Mode: process existing files
        logger.info(f"Mode: Processing existing files matching pattern: {output_str}")
        try:
            generated_files = process_existing_files(
                file_pattern=output_str,
                ocr_enabled=scan_params['ocr'],
                ocr_lang=scan_params['lang'],
                ocr_tool_config={
                    'enabled': tool_config['tesseract_enabled'],
                    'command': tool_config['tesseract_command'],
                    'python_alternative': tool_config['tesseract_python_alternative'],
                    'fallback_enabled': tool_config['tesseract_fallback_enabled'],
                    'timeout': tool_config['tesseract_timeout']
                }
            )
            # Display results for processed existing files
            if generated_files:
                logger.info("Processed files:")
                for f in generated_files:
                    try:
                        relative_path = os.path.relpath(f)
                    except ValueError:
                        relative_path = f.resolve()
                    print(f"\n✓ Traitement réussi !\nFichier produit : {relative_path}")
                return 0
            else:
                logger.error("No files were processed successfully.")
                return 1
        except Exception as e:
            logger.error(f"Error processing existing files: {e}", exc_info=True)
            return 1
    else:
        # Mode: normal scan
        logger.info(f"Mode: Normal scan to: {output_str}")
        try:
            generated_files = scan_document(
                dpi=dpi_to_use,
                output_location=args.output,
                tool_config={
                    'naps2_console_command': tool_config['naps2_console_command']
                },
                ocr_config={
                    'enabled': tool_config['tesseract_enabled'],
                    'command': tool_config['tesseract_command'],
                    'python_alternative': tool_config['tesseract_python_alternative'],
                    'fallback_enabled': tool_config['tesseract_fallback_enabled'],
                    'timeout': tool_config['tesseract_timeout']
                },
                number_of_scans=scan_params['number'],
                **scan_params # Pass all other relevant options
            )

            if generated_files:
                logger.info(f"Scan operation successful. Generated {len(generated_files)} file(s).")
                for f in generated_files:
                    try:
                        relative_path = os.path.relpath(f)
                    except ValueError:
                        relative_path = f.resolve()
                    print(f"\n✓ Scan réussi !\nFichier produit : {relative_path}")
                return 0
            else:
                logger.error("Scan operation failed.")
                return 1
        except Exception as e:
            logger.error(f"Unexpected error during scan operation: {e}", exc_info=True)
            return 1

if __name__ == '__main__':
    sys.exit(main())