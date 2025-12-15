"""
Module de conversion d'images en PDF pour Ambulon.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None


# Extensions d'images supportées
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}


def get_image_files(directory: Path) -> List[Path]:
    """
    Récupère tous les fichiers image d'un répertoire, triés alphabétiquement.

    Args:
        directory: Chemin vers le répertoire contenant les images

    Returns:
        Liste des objets Path pour les fichiers image, triés alphabétiquement
    """
    image_files = []

    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_files.append(file_path)

    # Trier alphabétiquement par nom
    image_files.sort(key=lambda x: x.name)

    return image_files


def images_to_pdf(directory: str, output_path: str = None, verbose: bool = False, 
                  compress: bool = False, quality: int = 85) -> Dict[str, Any]:
    """
    Convertit toutes les images d'un répertoire en un seul fichier PDF.

    Args:
        directory: Chemin vers le répertoire contenant les images
        output_path: Chemin de sortie PDF optionnel. Si None, utilise le nom du répertoire
        verbose: Affichage verbeux
        compress: Activer la compression pour réduire la taille du PDF
        quality: Qualité JPEG pour la compression (1-100, défaut 85)

    Returns:
        Dict contenant les résultats de la conversion
    """
    if not PIL_AVAILABLE:
        error_msg = "La bibliothèque Pillow n'est pas installée. Installez-la avec: pip install Pillow"
        logging.error(f"[IMG2PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    dir_path = Path(directory).resolve()

    # Vérifier si le répertoire existe
    if not dir_path.exists():
        error_msg = f"Le répertoire '{directory}' n'existe pas."
        logging.error(f"[IMG2PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    if not dir_path.is_dir():
        error_msg = f"'{directory}' n'est pas un répertoire."
        logging.error(f"[IMG2PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    # Récupérer tous les fichiers image
    image_files = get_image_files(dir_path)

    if not image_files:
        error_msg = f"Aucun fichier image trouvé dans '{directory}'. Formats supportés: {', '.join(sorted(IMAGE_EXTENSIONS))}"
        logging.error(f"[IMG2PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    # Déterminer le chemin de sortie
    if output_path is None:
        # Créer le PDF dans le répertoire source avec le nom du répertoire
        output_path = dir_path / (dir_path.name + ".pdf")
    else:
        output_path = Path(output_path)

    output_path = output_path.resolve()

    if verbose:
        logging.info(f"[IMG2PDF] {len(image_files)} image(s) trouvée(s) dans '{dir_path.name}'")
        for img_file in image_files:
            logging.info(f"[IMG2PDF]   - {img_file.name}")
        logging.info(f"[IMG2PDF] Conversion vers PDF: {output_path}")
        if compress:
            logging.info(f"[IMG2PDF] Compression activée (qualité: {quality})")

    try:
        # Ouvrir toutes les images et les convertir en RGB
        images = []
        first_image = None

        for i, img_path in enumerate(image_files):
            try:
                img = Image.open(img_path)

                # Convertir en RGB (PDF nécessite le mode RGB)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Créer un arrière-plan blanc pour les images transparentes
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Appliquer la compression si demandée
                if compress:
                    from io import BytesIO
                    # Compresser en sauvegardant vers BytesIO et en rechargeant
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    buffer.seek(0)
                    img = Image.open(buffer)

                if i == 0:
                    first_image = img
                else:
                    images.append(img)

                if verbose:
                    logging.info(f"[IMG2PDF] Traité: {img_path.name}")

            except Exception as e:
                warning_msg = f"Impossible de traiter {img_path.name}: {e}"
                logging.warning(f"[IMG2PDF] {warning_msg}")
                continue

        if first_image is None:
            error_msg = "Aucune image n'a pu être traitée."
            logging.error(f"[IMG2PDF] {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }

        # Sauvegarder en PDF
        first_image.save(
            output_path,
            "PDF",
            save_all=True,
            append_images=images,
            resolution=100.0
        )

        file_size = output_path.stat().st_size
        logging.info(f"[IMG2PDF] PDF créé avec succès: {output_path} ({file_size} octets)")

        return {
            "success": True,
            "output_file": output_path,
            "total_pages": len(image_files),
            "file_size": file_size,
            "compressed": compress,
            "quality": quality if compress else None
        }

    except Exception as e:
        error_msg = f"Échec de la création du PDF: {e}"
        logging.error(f"[IMG2PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


def main():
    """Point d'entrée principal pour le module img2pdf."""
    import argparse
    from .cli import setup_logging
    
    parser = argparse.ArgumentParser(
        description='Convertir les images d\'un répertoire en fichier PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s scans/
  %(prog)s scans/ -o documents/rapport.pdf
  %(prog)s images/ --compress --quality 75
  %(prog)s photos/ -o album.pdf --verbose
        """
    )

    parser.add_argument(
        'directory',
        type=str,
        help='Répertoire contenant les images à convertir'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Chemin du fichier PDF de sortie (défaut: <répertoire>/<nom_répertoire>.pdf)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Afficher le progrès détaillé de la conversion'
    )

    parser.add_argument(
        '-c', '--compress',
        action='store_true',
        help='Activer la compression pour réduire la taille du PDF'
    )

    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        choices=range(1, 101),
        metavar='QUALITE',
        help='Qualité JPEG pour la compression (1-100, défaut: 85). Valeurs plus faibles = fichier plus petit mais qualité moindre'
    )

    args = parser.parse_args()
    
    # Configuration du logging
    setup_logging(args.verbose)
    
    logging.info(f"[DÉMARRAGE] Démarrage du module img2pdf")
    logging.info(f"   Répertoire source: {args.directory}")
    if args.output:
        logging.info(f"   Fichier de sortie: {args.output}")
    
    try:
        result = images_to_pdf(
            args.directory,
            args.output,
            args.verbose,
            args.compress,
            args.quality
        )
        
        if result['success']:
            print(f"Succès ! PDF créé: {result['output_file']}")
            print(f"Total de pages: {result['total_pages']}")
            print(f"Taille du fichier: {result['file_size'] / (1024*1024):.2f} MB")
            if result['compressed']:
                print(f"Compression appliquée (qualité: {result['quality']})")
            return 0
        else:
            print(f"Erreur: {result['error']}")
            return 1
            
    except Exception as e:
        error_msg = f"Erreur inattendue: {e}"
        logging.error(f"[ERREUR] {error_msg}")
        print(f"Erreur: {error_msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
