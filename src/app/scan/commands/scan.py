"""
CLI command for TWAIN scanning with DPI profiles for Ambulon.
Handles configuration hierarchy, logging, and displays generated file paths.
"""

import typer
import logging
import os
import sys
import subprocess # Needed for Popen for NAPS2 GUI
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from app.scan.core.scanning import scan_document
from app.scan.core.ocr import process_existing_files

logger = logging.getLogger(__name__)

app = typer.Typer()

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
        'naps2_console_command': os.getenv('NAPS2_CONSOLE_COMMAND', r'G:\WarchoLife\WarchoPortable\PortableCommon\Naps2\NAPS2.Console.exe'),
        'naps2_gui_command': os.getenv('NAPS2_GUI_COMMAND', r'G:\WarchoLife\WarchoPortable\PortableCommon\Naps2\NAPS2.exe'),
        'tesseract_command': os.getenv('TESSERACT_COMMAND', 'tesseract'),
        'tesseract_enabled': os.getenv('TESSERACT_ENABLED', 'True').lower() == 'true',
        'tesseract_python_alternative': os.getenv('TESSERACT_PYTHON_ALTERNATIVE', 'False').lower() == 'true',
        'tesseract_fallback_enabled': os.getenv('TESSERACT_FALLBACK_ENABLED', 'False').lower() == 'true',
        'tesseract_timeout': os.getenv('TESSERACT_TIMEOUT', 60)
    }
}

@app.command(
    help="""
    Scans documents using TWAIN compatible scanners (via NAPS2 Console).
    Supports various scan options, OCR, and file processing.

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
)
def main(
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory or base file name (e.g., scans/ or scans/document). Required for scanning.", show_default=False),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file (e.g., config/scan.yaml)."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),
    
    # Scan options
    resolution: Optional[int] = typer.Option(None, "-r", "--resolution", min=100, max=1200, help="Scan resolution in DPI."),
    profile: Optional[str] = typer.Option(None, "-p", "--profile", help="Predefined TWAIN profile (e.g., TWAIN-300ppp)."),
    device: Optional[str] = typer.Option(None, "--device", help="Scanner device to use."),
    source: Optional[str] = typer.Option(None, "--source", help="Scanner source (flatbed, adf, duplex)."),
    color_mode: Optional[str] = typer.Option(None, "--color-mode", help="Color mode (color, grayscale, bw)."),
    paper_size: Optional[str] = typer.Option(None, "--paper-size", help="Paper size (A4, A3, Letter, Legal, Custom)."),
    orientation: Optional[str] = typer.Option(None, "--orientation", help="Orientation (portrait, landscape)."),
    brightness: Optional[int] = typer.Option(None, "--brightness", min=-100, max=100, help="Brightness (-100 to 100)."),
    contrast: Optional[int] = typer.Option(None, "--contrast", min=-100, max=100, help="Contrast (-100 to 100)."),
    gamma: Optional[float] = typer.Option(None, "--gamma", min=0.1, max=3.0, help="Gamma correction (0.1 to 3.0)."),
    
    # Output options
    format: Optional[str] = typer.Option(None, "-f", "--format", help="Output format (pdf, png, jpg, jpeg, tiff, svg)."),
    quality: Optional[int] = typer.Option(None, "--quality", min=1, max=100, help="Compression quality (1-100)."),
    naming: Optional[str] = typer.Option(None, "--naming", help="Naming convention (date, sequence, custom)."),
    increment: Optional[bool] = typer.Option(None, "--increment", help="Enable auto-incrementation of filename."),
    no_increment: bool = typer.Option(False, "--no-increment", help="Disable auto-incrementation (use filename as-is). Overrides --increment if set."),

    # Post-scan processing options
    ocr: Optional[bool] = typer.Option(None, "--ocr", help="Enable OCR after scan."),
    lang: Optional[str] = typer.Option(None, "--lang", help="Language for OCR (e.g., fra, eng, fra+eng)."),
    deskew: Optional[bool] = typer.Option(None, "--deskew", help="Automatic deskewing."),
    despeckle: Optional[bool] = typer.Option(None, "--despeckle", help="Despeckle images."),
    crop: Optional[bool] = typer.Option(None, "--crop", help="Automatic cropping."),
    
    # Batch options
    number: Optional[int] = typer.Option(None, "-n", "--number", min=1, help="Number of scans to perform."),
    pages: Optional[int] = typer.Option(None, "--pages", min=1, help="Number of pages to scan (for ADF)."),
    batch: Optional[bool] = typer.Option(None, "--batch", help="Batch mode for multiple documents."),
    separator: Optional[bool] = typer.Option(None, "--separator", help="Separator page between documents."),
    auto_feed: Optional[bool] = typer.Option(None, "--auto-feed", help="Automatic document feeder (ADF)."),
    
    # Advanced options
    calibrate: Optional[bool] = typer.Option(None, "--calibrate", help="Calibrate scanner."),
    test_pattern: Optional[bool] = typer.Option(None, "--test-pattern", help="Scan a test pattern."),
    manual: Optional[bool] = typer.Option(False, "--manual", help="Open NAPS2 GUI for manual configuration."),
    timeout: Optional[int] = typer.Option(None, "--timeout", min=1, help="Timeout for scan operations in seconds."),
):
    """
    CLI for TWAIN scanning.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="scan")
    logger.info("[START] Starting scan module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    # Load configuration
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    scan_config = config['scan']
    tool_config = config['tools']

    # Handle manual NAPS2 GUI option (special case, bypasses scanning)
    if manual:
        try:
            naps2_gui_executable = tool_config.get('naps2_gui_command', DEFAULT_CONFIG['tools']['naps2_gui_command'])
            if not Path(naps2_gui_executable).exists():
                logger.error(f"NAPS2 GUI not found: {naps2_gui_executable}")
                raise typer.Exit(code=1)
            
            logger.info(f"Opening NAPS2 GUI: {naps2_gui_executable}")
            subprocess.Popen([naps2_gui_executable])
            logger.info("NAPS2 GUI opened.")
            raise typer.Exit(code=0)
        except Exception as e:
            logger.error(f"Error opening NAPS2 GUI: {e}")
            raise typer.Exit(code=1)

    # Validate output path
    if output is None:
        logger.error("Error: --output/-o is required.")
        raise typer.Exit(code=1)
    
    output_str = str(output)
    has_wildcards = '*' in output_str or '?' in output_str
    has_extension = '.' in Path(output_str).name
    
    # Apply CLI overrides (highest priority) and resolve config
    final_resolution = resolution if resolution is not None else scan_config.get('resolution', DEFAULT_CONFIG['scan']['resolution'])
    final_profile = profile if profile is not None else scan_config.get('profile', DEFAULT_CONFIG['scan']['profile'])
    final_device = device if device is not None else scan_config.get('device', DEFAULT_CONFIG['scan']['device'])
    final_source = source if source is not None else scan_config.get('source', DEFAULT_CONFIG['scan']['source'])
    final_color_mode = color_mode if color_mode is not None else scan_config.get('color_mode', DEFAULT_CONFIG['scan']['color_mode'])
    final_paper_size = paper_size if paper_size is not None else scan_config.get('paper_size', DEFAULT_CONFIG['scan']['paper_size'])
    final_orientation = orientation if orientation is not None else scan_config.get('orientation', DEFAULT_CONFIG['scan']['orientation'])
    final_brightness = brightness if brightness is not None else scan_config.get('brightness', DEFAULT_CONFIG['scan']['brightness'])
    final_contrast = contrast if contrast is not None else scan_config.get('contrast', DEFAULT_CONFIG['scan']['contrast'])
    final_gamma = gamma if gamma is not None else scan_config.get('gamma', DEFAULT_CONFIG['scan']['gamma'])
    final_format = format if format is not None else scan_config.get('format', DEFAULT_CONFIG['scan']['format'])
    final_quality = quality if quality is not None else scan_config.get('quality', DEFAULT_CONFIG['scan']['quality'])
    final_naming = naming if naming is not None else scan_config.get('naming', DEFAULT_CONFIG['scan']['naming'])
    final_increment = increment if increment is not None else scan_config.get('increment', DEFAULT_CONFIG['scan']['increment'])
    
    # Override increment based on no_increment (CLI has highest priority)
    if no_increment:
        final_increment = False

    final_ocr = ocr if ocr is not None else scan_config.get('ocr', DEFAULT_CONFIG['scan']['ocr'])
    final_lang = lang if lang is not None else scan_config.get('lang', DEFAULT_CONFIG['scan']['lang'])
    final_deskew = deskew if deskew is not None else scan_config.get('deskew', DEFAULT_CONFIG['scan']['deskew'])
    final_despeckle = despeckle if despeckle is not None else scan_config.get('despeckle', DEFAULT_CONFIG['scan']['despeckle'])
    final_crop = crop if crop is not None else scan_config.get('crop', DEFAULT_CONFIG['scan']['crop'])
    final_number = number if number is not None else scan_config.get('number', DEFAULT_CONFIG['scan']['number'])
    final_pages = pages if pages is not None else scan_config.get('pages', DEFAULT_CONFIG['scan']['pages'])
    final_batch = batch if batch is not None else scan_config.get('batch', DEFAULT_CONFIG['scan']['batch'])
    final_separator = separator if separator is not None else scan_config.get('separator', DEFAULT_CONFIG['scan']['separator'])
    final_auto_feed = auto_feed if auto_feed is not None else scan_config.get('auto_feed', DEFAULT_CONFIG['scan']['auto_feed'])
    final_preview = preview if preview is not None else scan_config.get('preview', DEFAULT_CONFIG['scan']['preview'])
    final_calibrate = calibrate if calibrate is not None else scan_config.get('calibrate', DEFAULT_CONFIG['scan']['calibrate'])
    final_test_pattern = test_pattern if test_pattern is not None else scan_config.get('test_pattern', DEFAULT_CONFIG['scan']['test_pattern'])
    final_timeout = timeout if timeout is not None else scan_config.get('timeout', DEFAULT_CONFIG['scan']['timeout'])


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
                raise typer.Exit(code=0)
            else:
                logger.error("No files were processed successfully.")
                raise typer.Exit(code=1)
        except Exception as e:
            logger.error(f"Error processing existing files: {e}", exc_info=True)
            raise typer.Exit(code=1)
    else:
        # Mode: normal scan
        logger.info(f"Mode: Normal scan to: {output_str}")
        try:
            generated_files = scan_document(
                dpi=dpi_to_use,
                output_location=output,
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
                raise typer.Exit(code=0)
            else:
                logger.error("Scan operation failed.")
                raise typer.Exit(code=1)
        except Exception as e:
            logger.error(f"Unexpected error during scan operation: {e}", exc_info=True)
            raise typer.Exit(code=1)

if __name__ == '__main__':
    app()