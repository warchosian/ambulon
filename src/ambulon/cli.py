"""Module CLI pour Ambulon."""
import sys

from . import hello
from .scan import main as scan_main
from .ocr import main as ocr_main


def main():
    """Fonction principale appelée par la commande `ambulon`."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'scan':
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
            print(hello())
            return 0
    else:
        print(hello())
        return 0
