"""Module CLI pour Ambulon."""
import sys
import argparse

from . import hello
from .scan import main as scan_main
from .ocr import main as ocr_main


def show_help():
    """Affiche l'aide principale avec les modules disponibles."""
    print(hello())
    print()
    print("Usage: ambulon [MODULE] [OPTIONS]")
    print()
    print("Modules disponibles:")
    print("  scan    Module de scan TWAIN avec profils DPI")
    print("  ocr     Module OCR - Reconnaissance optique de caractères")
    print()
    print("Options générales:")
    print("  -h, --help    Afficher cette aide")
    print("  --version     Afficher la version")
    print()
    print("Exemples:")
    print("  ambulon scan --help          Aide du module scan")
    print("  ambulon scan -r 300 -o scans/")
    print("  ambulon ocr --help           Aide du module OCR")
    print("  ambulon ocr -i image.jpg -l fra")
    print()
    print("Pour plus d'informations sur un module spécifique:")
    print("  ambulon [MODULE] --help")


def main():
    """Fonction principale appelée par la commande `ambulon`."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Gérer les options d'aide globales
        if command in ['-h', '--help']:
            show_help()
            return 0
        elif command == '--version':
            from . import __version__
            print(f"Ambulon version {__version__}")
            return 0
        elif command == 'scan':
            # Retirer 'scan' des arguments et lancer le module scan
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]  # Garder le nom du programme et les arguments après 'scan'
            try:
                return scan_main()
            finally:
                sys.argv = original_argv
        elif command == 'ocr':
            # Retirer 'ocr' des arguments et lancer le module ocr
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]  # Garder le nom du programme et les arguments après 'ocr'
            try:
                return ocr_main()
            finally:
                sys.argv = original_argv
        else:
            print(f"Module inconnu: {command}")
            print("Utilisez 'ambulon --help' pour voir les modules disponibles.")
            return 1
    else:
        show_help()
        return 0
