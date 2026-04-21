"""
Module de conversion d'images en PDF pour Ambulon.
Utilise PyMuPDF (fitz) et Pillow pour la conversion et la compression.
Suit la hiérarchie de configuration standard et les pratiques de logging.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from io import BytesIO
from typing import List, Dict, Any, Optional

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

def main(argv=None):
    """
    CLI for converting images in a directory to a single PDF file.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments (e.g., --output)
    2. YAML configuration file (`--config`)
    3. Environment variables (e.g., AMBULON_IMG2PDF_COMPRESS, AMBULON_IMG2PDF_QUALITY)
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="""
Converts all images in a directory to a single PDF file.

Configuration Hierarchy (from highest to lowest priority):
1. Command-line arguments (e.g., --output)
2. YAML configuration file (--config)
3. Environment variables (e.g., AMBULON_IMG2PDF_COMPRESS, AMBULON_IMG2PDF_QUALITY)
4. Default values
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing images to convert."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Path to the output PDF file (default: <directory_name>.pdf in the source directory)."
    )
    parser.add_argument(
        "-c", "--compress",
        action="store_true",
        help="Enable compression to reduce PDF size. Overrides config/env."
    )
    parser.add_argument(
        "-q", "--quality",
        type=int,
        help="JPEG quality for compression (1-100, default: 85). Lower values = smaller file but lower quality. Overrides config/env."
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to a YAML configuration file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )

    args = parser.parse_args(argv)

    # Setup logging
    setup_logging(logging.DEBUG if args.verbose else logging.INFO, log_file_prefix="img2pdf")

    # Check if directory exists
    if not args.directory.exists():
        logger.error(f"Directory does not exist: {args.directory}")
        return 1
    if not args.directory.is_dir():
        logger.error(f"Path is not a directory: {args.directory}")
        return 1

    # Determine default config file path
    config_path = args.config
    default_config_file = Path("config/img2pdf.yaml")
    if config_path is None and default_config_file.exists():
        config_path = default_config_file

    # Load config from YAML, substituting env vars, merged over defaults
    config = load_app_config(str(config_path) if config_path else None, DEFAULT_CONFIG)

    # Extract values with hierarchy: CLI > Config > Env > Default
    final_compress = args.compress if args.compress else config['conversion']['img2pdf'].get('compress', DEFAULT_CONFIG['conversion']['img2pdf']['compress'])
    final_quality = args.quality if args.quality is not None else config['conversion']['img2pdf'].get('quality', DEFAULT_CONFIG['conversion']['img2pdf']['quality'])

    # Validate quality range
    if not 1 <= final_quality <= 100:
        logger.error(f"Quality must be between 1 and 100, got: {final_quality}")
        return 1

    # Determine output path if not provided
    output = args.output
    if output is None:
        output = args.directory / (args.directory.name + ".pdf")

    # Execute conversion
    result_path = images_to_pdf(
        directory=args.directory,
        output_path=output,
        compress=final_compress,
        quality=final_quality,
        verbose=args.verbose
    )

    if result_path:
        try:
            relative_path = os.path.relpath(result_path)
        except ValueError:
            relative_path = result_path
        print(f"\n✓ Conversion réussie !\nFichier produit : {relative_path}")
        return 0
    else:
        logger.error("Image to PDF conversion failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())