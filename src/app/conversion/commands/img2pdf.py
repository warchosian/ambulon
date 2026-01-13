"""
Module de conversion d'images en PDF pour Ambulon.
Utilise PyMuPDF (fitz) et Pillow pour la conversion et la compression.
Suit la hiérarchie de configuration standard et les pratiques de logging.
"""

import os
import sys
import logging
from pathlib import Path
from io import BytesIO
from typing import List, Dict, Any, Optional

import typer
from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

# Setup logger for this module
logger = logging.getLogger(__name__)

app = typer.Typer()

DEFAULT_CONFIG = {
    "conversion": {
        "img2pdf": {
            "compress": False,
            "quality": 85
        }
    }
}

# Extensions d'images supportées
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

def get_image_files(directory: Path) -> List[Path]:
    """
    Récupère tous les fichiers image d'un répertoire, triés alphabétiquement.
    """
    image_files = []
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_files.append(file_path)
    image_files.sort(key=lambda x: x.name)
    return image_files

def images_to_pdf(
    directory: Path,
    output_path: Path,
    compress: bool,
    quality: int,
    verbose: bool = False
) -> Optional[Path]:
    """
    Convertit toutes les images d'un répertoire en un seul fichier PDF.
    """
    if not PIL_AVAILABLE:
        logger.error("The Pillow library is not installed. Install with: pip install Pillow")
        return None

    if not directory.exists():
        logger.error(f"Directory '{directory}' does not exist.")
        return None
    if not directory.is_dir():
        logger.error(f"'{directory}' is not a directory.")
        return None

    image_files = get_image_files(directory)
    if not image_files:
        logger.warning(f"No image files found in '{directory}'. Supported formats: {', '.join(sorted(IMAGE_EXTENSIONS))}")
        return None

    logger.info(f"Found {len(image_files)} image(s) in '{directory.name}'")
    for img_file in image_files:
        logger.debug(f"  - {img_file.name}")
    logger.info(f"Converting to PDF: {output_path}")
    if compress:
        logger.info(f"Compression enabled (quality: {quality})")

    try:
        images = []
        first_image = None

        for i, img_path in enumerate(image_files):
            try:
                img = Image.open(img_path)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P': img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'): background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                if compress:
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    buffer.seek(0)
                    img = Image.open(buffer)

                if i == 0: first_image = img
                else: images.append(img)
                logger.debug(f"Processed: {img_path.name}")
            except Exception as e:
                logger.warning(f"Could not process {img_path.name}: {e}")
                continue

        if first_image is None:
            logger.error("No images could be processed.")
            return None

        first_image.save(output_path, "PDF", save_all=True, append_images=images, resolution=100.0)
        logger.info(f"PDF created successfully: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to create PDF: {e}", exc_info=True)
        return None

@app.command(
    help="""
    Converts all images in a directory to a single PDF file.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments (e.g., --output)
    2. YAML configuration file (`--config`)
    3. Environment variables (e.g., IMG2PDF_COMPRESS, IMG2PDF_QUALITY)
    4. Default values
    """
)
def main(
    directory: Path = typer.Argument(..., help="Directory containing images to convert.", exists=True, file_okay=False, dir_okay=True, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Path to the output PDF file (default: <directory_name>.pdf in the source directory)."),
    compress: Optional[bool] = typer.Option(None, "--compress", "-c", help="Enable compression to reduce PDF size. Overrides config/env."),
    quality: Optional[int] = typer.Option(None, "--quality", "-q", min=1, max=100, help="JPEG quality for compression (1-100, default: 85). Lower values = smaller file but lower quality. Overrides config/env."),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to a YAML configuration file."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging.")
):
    """
    CLI for converting images in a directory to a single PDF file.
    """
    # Setup logging
    central_setup_logging(verbose)

    # Determine default config file path
    default_config_file = Path("config/img2pdf.yaml")
    if config_path is None and default_config_file.exists():
        config_path = default_config_file

    # Load config from YAML, substituting env vars, merged over defaults
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)
    
    # Extract values with hierarchy: CLI > Config > Env > Default
    final_compress = compress if compress is not None else config['conversion']['img2pdf'].get('compress', DEFAULT_CONFIG['conversion']['img2pdf']['compress'])
    final_quality = quality if quality is not None else config['conversion']['img2pdf'].get('quality', DEFAULT_CONFIG['conversion']['img2pdf']['quality'])

    # Determine output path if not provided
    if output is None:
        output = directory / (directory.name + ".pdf")

    # Execute conversion
    result_path = images_to_pdf(
        directory=directory,
        output_path=output,
        compress=final_compress,
        quality=final_quality,
        verbose=verbose
    )

    if result_path:
        relative_path = os.path.relpath(result_path)
        print(f"\n✓ Conversion réussie !\nFichier produit : {relative_path}")
        raise typer.Exit(code=0)
    else:
        logger.error("Image to PDF conversion failed.")
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()