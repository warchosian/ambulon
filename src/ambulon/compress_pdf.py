"""
Module de compression PDF pour Ambulon.
"""

import sys
from pathlib import Path
from io import BytesIO
from typing import Dict, Any
import logging

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


def compress_pdf(input_path: str, output_path: str = None, quality: int = 85, 
                verbose: bool = False) -> Dict[str, Any]:
    """
    Compresse un fichier PDF existant en retraitant ses images.

    Args:
        input_path: Chemin vers le fichier PDF d'entrée
        output_path: Chemin de sortie PDF optionnel. Si None, ajoute le suffixe '_compressed'
        quality: Qualité JPEG pour la compression (1-100, défaut 85)
        verbose: Affichage verbeux

    Returns:
        Dict contenant les résultats de la compression
    """
    if not PIL_AVAILABLE or not PYMUPDF_AVAILABLE:
        missing_libs = []
        if not PIL_AVAILABLE:
            missing_libs.append("Pillow")
        if not PYMUPDF_AVAILABLE:
            missing_libs.append("PyMuPDF")
        
        error_msg = f"Bibliothèques requises non installées: {', '.join(missing_libs)}. Installez avec: pip install {' '.join(missing_libs)}"
        logging.error(f"[COMPRESS_PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    pdf_path = Path(input_path).resolve()

    # Vérifier si le PDF existe
    if not pdf_path.exists():
        error_msg = f"Le fichier PDF '{input_path}' n'existe pas."
        logging.error(f"[COMPRESS_PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    if not pdf_path.is_file():
        error_msg = f"'{input_path}' n'est pas un fichier."
        logging.error(f"[COMPRESS_PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    if pdf_path.suffix.lower() != '.pdf':
        error_msg = f"'{input_path}' n'est pas un fichier PDF."
        logging.error(f"[COMPRESS_PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

    # Déterminer le chemin de sortie
    if output_path is None:
        # Ajouter '_compressed' avant l'extension
        output_path = pdf_path.parent / f"{pdf_path.stem}_compressed{pdf_path.suffix}"
    else:
        output_path = Path(output_path)

    output_path = output_path.resolve()

    if verbose:
        logging.info(f"[COMPRESS_PDF] PDF d'entrée: {pdf_path}")
        logging.info(f"[COMPRESS_PDF] PDF de sortie: {output_path}")
        logging.info(f"[COMPRESS_PDF] Qualité de compression: {quality}")

    try:
        # Ouvrir le PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        if verbose:
            logging.info(f"[COMPRESS_PDF] Traitement de {total_pages} pages...")

        # Créer un nouveau PDF
        new_doc = fitz.open()

        for page_num in range(total_pages):
            page = doc[page_num]

            # Rendre la page en image à 72 DPI (résolution PDF standard)
            # Utiliser un zoom de 1.0 pour garder la taille originale
            mat = fitz.Matrix(1.0, 1.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convertir en image PIL
            img_data = pix.tobytes("jpeg")
            img = Image.open(BytesIO(img_data))

            # S'assurer du mode RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Compresser l'image avec optimisation
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
            buffer.seek(0)

            # Créer une nouvelle page avec l'image compressée
            rect = page.rect
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(rect, stream=buffer.getvalue())

            if verbose:
                logging.info(f"[COMPRESS_PDF] Page compressée {page_num + 1}/{total_pages}")

        # Sauvegarder le PDF compressé
        new_doc.save(output_path, garbage=4, deflate=True, clean=True)
        new_doc.close()
        doc.close()

        # Obtenir les tailles de fichier
        original_size = pdf_path.stat().st_size
        compressed_size = output_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100

        logging.info(f"[COMPRESS_PDF] PDF compressé créé avec succès: {output_path}")
        logging.info(f"[COMPRESS_PDF] Taille originale: {original_size / (1024*1024):.2f} MB")
        logging.info(f"[COMPRESS_PDF] Taille compressée: {compressed_size / (1024*1024):.2f} MB")
        logging.info(f"[COMPRESS_PDF] Réduction de taille: {reduction:.1f}%")

        return {
            "success": True,
            "input_file": pdf_path,
            "output_file": output_path,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "reduction_percent": reduction,
            "total_pages": total_pages,
            "quality": quality
        }

    except Exception as e:
        error_msg = f"Échec de la compression du PDF: {e}"
        logging.error(f"[COMPRESS_PDF] {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


def main():
    """Point d'entrée principal pour le module compress_pdf."""
    import argparse
    from .cli import setup_logging
    
    parser = argparse.ArgumentParser(
        description='Compresser un fichier PDF existant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s document.pdf
  %(prog)s document.pdf -o document_petit.pdf
  %(prog)s gros_fichier.pdf --quality 60 --verbose
        """
    )

    parser.add_argument(
        'input',
        type=str,
        help='Fichier PDF d\'entrée à compresser'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Chemin du fichier PDF de sortie (défaut: <entrée>_compressed.pdf)'
    )

    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        choices=range(1, 101),
        metavar='QUALITE',
        help='Qualité JPEG pour la compression (1-100, défaut: 85). Valeurs plus faibles = fichier plus petit mais qualité moindre'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Afficher le progrès détaillé de la compression'
    )

    args = parser.parse_args()
    
    # Configuration du logging
    setup_logging(args.verbose)
    
    logging.info(f"[DÉMARRAGE] Démarrage du module compress_pdf")
    logging.info(f"   Fichier d'entrée: {args.input}")
    if args.output:
        logging.info(f"   Fichier de sortie: {args.output}")
    
    try:
        result = compress_pdf(
            args.input,
            args.output,
            args.quality,
            args.verbose
        )
        
        if result['success']:
            print(f"Succès ! PDF compressé créé: {result['output_file']}")
            print(f"Taille originale: {result['original_size'] / (1024*1024):.2f} MB")
            print(f"Taille compressée: {result['compressed_size'] / (1024*1024):.2f} MB")
            print(f"Réduction de taille: {result['reduction_percent']:.1f}%")
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
