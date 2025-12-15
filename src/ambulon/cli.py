"""Module CLI pour Ambulon."""
import sys

from . import hello
from .scan import scan


def main():
    """Fonction principale appelée par la commande `ambulon`."""
    if len(sys.argv) > 1 and sys.argv[1] == 'scan':
        # Passer les arguments restants à la fonction scan
        scan(*sys.argv[2:])
    else:
        print(hello())
