"""
Module de compression PDF pour Ambulon.
Utilise PyMuPDF (fitz) et Pillow pour la compression.
Suit la hiérarchie de configuration standard et les pratiques de logging.
"""

import os
import sys
import logging
from pathlib import Path
from io import BytesIO
from typing import Dict, Any, Optional

import typer
from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

# Setup logger for this module
logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    "conversion": {
        "compress_pdf": {
            "quality": 85
        }
    }
}

def compress_pdf(
    input_path: Path,
    output_path: Path,
    quality: int,
    verbose: bool = False
) -> Optional[Path]:
    """
    Compresse un fichier PDF existant en retraitant ses images.
    """
    if not PIL_AVAILABLE or not PYMUPDF_AVAILABLE:
        missing_libs = []
        if not PIL_AVAILABLE: missing_libs.append("Pillow")
        if not PYMUPDF_AVAILABLE: missing_libs.append("PyMuPDF")
        logger.error(f"Missing required libraries: {', '.join(missing_libs)}. Install with: pip install {' '.join(missing_libs)}")
        return None

    if not input_path.exists():
        logger.error(f"PDF file '{input_path}' does not exist.")
        return None
    if not input_path.is_file():
        logger.error(f"'{input_path}' is not a file.")
        return None
    if input_path.suffix.lower() != '.pdf':
        logger.error(f"'{input_path}' is not a PDF file.")
        return None

    logger.info(f"Input PDF: {input_path}")
    logger.info(f"Output PDF: {output_path}")
    logger.info(f"Compression quality: {quality}")

    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        logger.info(f"Processing {total_pages} pages...")

        new_doc = fitz.open()

        for page_num in range(total_pages):
            page = doc[page_num]
            mat = fitz.Matrix(1.0, 1.0) # Standard PDF resolution
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img_data = pix.tobytes("jpeg")
            img = Image.open(BytesIO(img_data))
            if img.mode != 'RGB': img = img.convert('RGB')

            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
            buffer.seek(0)

            rect = page.rect
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(rect, stream=buffer.getvalue())
            logger.debug(f"Page compressed {page_num + 1}/{total_pages}")

        new_doc.save(output_path, garbage=4, deflate=True, clean=True)
        new_doc.close()
        doc.close()

        original_size = input_path.stat().st_size
        compressed_size = output_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100

        logger.info(f"Compressed PDF created successfully: {output_path}")
        logger.info(f"Original size: {original_size / (1024*1024):.2f} MB")
        logger.info(f"Compressed size: {compressed_size / (1024*1024):.2f} MB")
        logger.info(f"Size reduction: {reduction:.1f}%")
        
        return output_path

    except Exception as e:
        logger.error(f"Failed to compress PDF: {e}", exc_info=True)
        return None

@app.command(
    help="""
    Compresses an existing PDF file to reduce its size.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments (e.g., --output)
    2. YAML configuration file (`--config`)
    3. Environment variables (e.g., COMPRESSPDF_QUALITY)
    4. Default values
    """
)
def main(
    input_file: Path = typer.Argument(..., help="Input PDF file to compress.", exists=True, file_okay=True, dir_okay=False, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Path to the output compressed PDF file (default: <input>_compressed.pdf)."),
    quality: Optional[int] = typer.Option(None, "--quality", "-q", min=1, max=100, help="JPEG quality for compression (1-100, default: 85). Lower values = smaller file but lower quality. Overrides config/env."),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to a YAML configuration file."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging.")
):
    """
    CLI for compressing PDF files.
    """
    # Setup logging
    central_setup_logging(verbose)

    # Determine default config file path
    default_config_file = Path("config/compress_pdf.yaml")
    if config_path is None and default_config_file.exists():
        config_path = default_config_file

    # Load config from YAML, substituting env vars, merged over defaults
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    
    # Extract values with hierarchy: CLI > Config > Env > Default
    final_quality = quality if quality is not None else config['conversion']['compress_pdf'].get('quality', DEFAULT_CONFIG['conversion']['compress_pdf']['quality'])

    # Determine output path if not provided
    if output is None:
        output = input_file.parent / f"{input_file.stem}_compressed{input_file.suffix}"

    # Execute compression
    result_path = compress_pdf(
        input_path=input_file,
        output_path=output,
        quality=final_quality,
        verbose=verbose
    )

    if result_path:
        relative_path = os.path.relpath(result_path)
        print(f"\n✓ Compression réussie !\nFichier produit : {relative_path}")
        raise typer.Exit(code=0)
    else:
        logger.error("PDF compression failed.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()