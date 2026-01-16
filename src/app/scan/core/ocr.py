"""
Core OCR logic for Ambulon.
Handles Tesseract OCR integration and processing of existing files.
"""

import logging
import re
import sys
import subprocess
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Conditional imports
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None

try:
    from PIL import Image
except ImportError:
    Image = None


# Configure logger for this module
logger = logging.getLogger(__name__)


def _load_tool_config(tool_name: str, config: Dict[str, Any], default_path: str) -> str:
    """Helper to load tool executable path from config."""
    # This should ultimately come from the global config loader, not a hardcoded dk.config
    # For now, it reflects the original scan_main.py behavior but will be replaced
    return config.get('tools', {}).get(tool_name, {}).get('command', default_path)


def _perform_ocr_python(image_file: Path, language: str = 'fra') -> Optional[Path]:
    """
    Performs OCR using pytesseract (Python alternative).

    Returns:
        Optional[Path]: Path to the generated OCR text file on success, None otherwise.
    """
    if not TESSERACT_AVAILABLE:
        logger.error("pytesseract is not available. Ensure it's installed: pip install pytesseract Pillow")
        return None
    
    if Image is None:
        logger.error("Pillow is not available. Ensure it's installed: pip install Pillow")
        return None

    ocr_output_file = image_file.with_suffix('.txt')
    
    logger.info(f"Starting OCR with pytesseract for '{image_file}' (Language: {language})")
    
    try:
        with Image.open(image_file) as img:
            text = pytesseract.image_to_string(img, lang=language)
        
        with open(ocr_output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        if ocr_output_file.exists():
            ocr_size = ocr_output_file.stat().st_size
            logger.info(f"OCR successful with pytesseract: {ocr_output_file} ({ocr_size} bytes)")
            return ocr_output_file
        else:
            logger.error(f"OCR file was not created by pytesseract: {ocr_output_file}")
            return None
        
    except Exception as e:
        logger.error(f"Error during pytesseract OCR: {str(e)}", exc_info=True)
        return None


def _perform_ocr(image_file: Path, ocr_config: Dict[str, Any], language: str = 'fra') -> Optional[Path]:
    """
    Performs OCR on an image file using Tesseract or its Python alternative.

    Args:
        image_file: Path to the image file to process.
        ocr_config: Dictionary containing Tesseract configuration (executable path, enabled status).
        language: Language for OCR.

    Returns:
        Optional[Path]: Path to the generated OCR text file on success, None otherwise.
    """
    tesseract_enabled = ocr_config.get('enabled', True)
    tesseract_executable = ocr_config.get('command', 'tesseract')
    
    if not tesseract_enabled:
        logger.warning("Tesseract is disabled in configuration.")
        python_alt = ocr_config.get('python_alternative', False)
        fallback_enabled = ocr_config.get('fallback_enabled', False)
        
        if python_alt and fallback_enabled:
            logger.info(f"Falling back to Python OCR alternative: {python_alt}")
            return _perform_ocr_python(image_file, language)
        else:
            logger.error("Tesseract disabled and no Python alternative configured or enabled.")
            return None

    ocr_output_file = image_file.with_suffix('.txt')
    
    logger.info(f"Starting OCR with Tesseract for '{image_file}' (Language: {language})")
    logger.info(f"Tesseract executable: {tesseract_executable}")
    
    output_base = str(ocr_output_file.with_suffix(''))
    
    cmd = [
        tesseract_executable,
        str(image_file),
        output_base,
        '-l', language,
        '--psm', '3',
        '--oem', '3'
    ]
    
    logger.info(f"Tesseract command: {' '.join(cmd)}")
    
    try:
        subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=ocr_config.get('timeout', 60)
        )
        
        if ocr_output_file.exists():
            ocr_size = ocr_output_file.stat().st_size
            logger.info(f"OCR successful with Tesseract: {ocr_output_file} ({ocr_size} bytes)")
            return ocr_output_file
        else:
            logger.error(f"OCR file was not created by Tesseract: {ocr_output_file}")
            return None
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Tesseract error (code {e.returncode}): {e.stderr if e.stderr else 'Unknown error'}")
        return None
    except subprocess.TimeoutExpired:
        logger.error("Timeout during Tesseract OCR.")
        return None
    except FileNotFoundError:
        logger.error(f"Tesseract executable not found: {tesseract_executable}")
        return None
    except Exception as e:
        logger.error(f"General Tesseract OCR error: {str(e)}", exc_info=True)
        return None


def process_existing_files(
    file_pattern: str, 
    ocr_enabled: bool, 
    ocr_lang: str,
    ocr_tool_config: Dict[str, Any]
) -> Optional[List[Path]]:
    """
    Processes existing files (e.g., adds OCR).

    Returns:
        Optional[List[Path]]: List of generated OCR file paths on success, None otherwise.
    """
    logger.info(f"Processing existing files matching pattern: {file_pattern}")
    
    matching_files = [Path(p) for p in glob.glob(file_pattern)] # glob needs to be imported
    
    if not matching_files:
        logger.warning(f"No files found for pattern: {file_pattern}")
        return None
    
    logger.info(f"{len(matching_files)} file(s) found.")
    
    generated_ocr_files = []
    for file_path in matching_files:
        logger.info(f"Processing: {file_path}")
        
        try:
            if ocr_enabled:
                ocr_output_file = _perform_ocr(file_path, ocr_tool_config, ocr_lang)
                if ocr_output_file:
                    generated_ocr_files.append(ocr_output_file)
                    logger.info(f"OCR successful for: {file_path}. Output: {ocr_output_file}")
                else:
                    logger.error(f"OCR failed for: {file_path}")
            else:
                logger.info(f"File processed (no OCR): {file_path}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
            
    return generated_ocr_files if generated_ocr_files else None