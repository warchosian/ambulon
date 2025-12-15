"""Module CLI pour Ambulon."""
import sys

from . import hello
from .scan import main as scan_main


def main():
    """Fonction principale appelée par la commande `ambulon`."""
    if len(sys.argv) > 1 and sys.argv[1] == 'scan':
        # Retirer 'scan' des arguments et lancer le module scan
        original_argv = sys.argv
        sys.argv = [sys.argv[0]] + sys.argv[2:]  # Garder le nom du programme et les arguments après 'scan'
        try:
            return scan_main()
        finally:
            sys.argv = original_argv
    else:
        print(hello())
        return 0
