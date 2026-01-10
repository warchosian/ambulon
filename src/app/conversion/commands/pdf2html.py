"""
PDF to HTML Converter - Ambulon

Convertit des fichiers PDF en HTML en extrayant le texte et la structure.
Utilise PyMuPDF (fitz) pour l'extraction du contenu.

Exemple:
    ambulon pdf2html document.pdf -o document.html
    ambulon pdf2html --input document.pdf --output document.html --verbose
"""

import sys
from pathlib import Path
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def convert_pdf_to_html(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False,
    include_images: bool = False,
    page_numbers: bool = True
) -> int:
    """
    Convertit un PDF en HTML.

    Args:
        input_file: Chemin vers le fichier PDF d'entrée
        output_file: Chemin vers le fichier HTML de sortie (optionnel)
        verbose: Activer les messages détaillés
        include_images: Inclure les images extraites du PDF
        page_numbers: Ajouter les numéros de page dans le HTML

    Returns:
        0 si succès, 1 si erreur
    """
    if fitz is None:
        print("Error: PyMuPDF (fitz) n'est pas installé.", file=sys.stderr)
        print("Installez avec: pip install PyMuPDF", file=sys.stderr)
        return 1

    # Chemins
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Fichier PDF non trouvé: {input_file}", file=sys.stderr)
        return 1

    if output_file is None:
        output_file = str(input_path.with_suffix('.html'))
    output_path = Path(output_file)

    try:
        if verbose:
            print(f"Conversion PDF → HTML")
            print(f"  Entrée: {input_path}")
            print(f"  Sortie: {output_path}")

        # Ouvrir le PDF
        pdf_document = fitz.open(str(input_path))
        total_pages = len(pdf_document)

        if verbose:
            print(f"  Pages: {total_pages}")

        # Générer le HTML
        html_content = []
        html_content.append("<!DOCTYPE html>")
        html_content.append("<html lang='fr'>")
        html_content.append("<head>")
        html_content.append("  <meta charset='UTF-8'>")
        html_content.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_content.append(f"  <title>{input_path.stem}</title>")
        html_content.append("  <style>")
        html_content.append("    body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }")
        html_content.append("    .page { margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; background: #fff; }")
        html_content.append("    .page-number { color: #666; font-style: italic; margin-bottom: 15px; }")
        html_content.append("    p { margin: 10px 0; }")
        html_content.append("    img { max-width: 100%; height: auto; margin: 15px 0; }")
        html_content.append("    h1, h2, h3 { color: #333; }")
        html_content.append("  </style>")
        html_content.append("</head>")
        html_content.append("<body>")
        html_content.append(f"  <h1>{input_path.stem}</h1>")

        # Extraire le contenu de chaque page
        for page_num in range(total_pages):
            page = pdf_document[page_num]

            if verbose and page_num % 10 == 0:
                print(f"  Traitement page {page_num + 1}/{total_pages}...")

            html_content.append("  <div class='page'>")

            if page_numbers:
                html_content.append(f"    <div class='page-number'>Page {page_num + 1}</div>")

            # Extraire le texte
            text = page.get_text()

            # Convertir le texte en paragraphes HTML
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para:
                    # Échapper les caractères HTML
                    para = para.replace('&', '&amp;')
                    para = para.replace('<', '&lt;')
                    para = para.replace('>', '&gt;')
                    para = para.replace('\n', '<br>')

                    html_content.append(f"    <p>{para}</p>")

            # Extraire les images si demandé
            if include_images:
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        # Sauvegarder l'image
                        img_filename = f"{output_path.stem}_p{page_num + 1}_img{img_index + 1}.{image_ext}"
                        img_path = output_path.parent / img_filename

                        with open(img_path, "wb") as img_file:
                            img_file.write(image_bytes)

                        # Ajouter au HTML
                        html_content.append(f"    <img src='{img_filename}' alt='Image page {page_num + 1}'>")

                        if verbose:
                            print(f"    Image extraite: {img_filename}")

                    except Exception as e:
                        if verbose:
                            print(f"    Erreur extraction image: {e}")
                        continue

            html_content.append("  </div>")

        html_content.append("</body>")
        html_content.append("</html>")

        # Écrire le fichier HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))

        pdf_document.close()

        if verbose:
            print(f"✓ Conversion réussie !")
            print(f"  Fichier HTML: {output_path}")
            if include_images:
                print(f"  Images extraites dans: {output_path.parent}")

        return 0

    except Exception as e:
        print(f"Error: Erreur lors de la conversion: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def main():
    """Point d'entrée CLI pour la conversion PDF vers HTML."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Convertir un PDF en HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s document.pdf
  %(prog)s document.pdf -o output.html
  %(prog)s document.pdf --include-images --verbose
        """
    )

    parser.add_argument('input_file', help='Fichier PDF d\'entrée')
    parser.add_argument('-o', '--output', dest='output_file',
                        help='Fichier HTML de sortie (défaut: même nom avec .html)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Mode verbeux')
    parser.add_argument('--include-images', action='store_true',
                        help='Inclure les images extraites du PDF')
    parser.add_argument('--no-page-numbers', action='store_true',
                        help='Ne pas afficher les numéros de page')

    args = parser.parse_args()

    return convert_pdf_to_html(
        input_file=args.input_file,
        output_file=args.output_file,
        verbose=args.verbose,
        include_images=args.include_images,
        page_numbers=not args.no_page_numbers
    )


if __name__ == '__main__':
    sys.exit(main())
