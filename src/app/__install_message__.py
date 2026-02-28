"""
Message affiché après installation de la wheel.
"""

INSTALL_MESSAGE = """
╔════════════════════════════════════════════════════════════════╗
║  Installation d'Ambulon terminée !                             ║
╚════════════════════════════════════════════════════════════════╝

Pour utiliser la conversion HTML → PDF avec support SVG optimal :

    python -m playwright install chromium

Ou si vous utilisez Poetry :

    poetry run playwright install chromium

Cette étape installe le navigateur Chromium (~100 MB) nécessaire
pour le rendu des diagrammes PlantUML/Mermaid en PDF.

Alternative : Utilisez wkhtmltopdf (moins bon pour SVG) :

    ambulon html2pdf document.html --method wkhtmltopdf

"""

def print_install_message():
    """Print the installation message."""
    print(INSTALL_MESSAGE)

if __name__ == "__main__":
    print_install_message()
