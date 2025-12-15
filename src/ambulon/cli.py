"""Module CLI pour Ambulon."""
import sys

from . import hello


def scan(*args):
    """Fonction scan temporaire."""
    print(f"Commande scan appelée avec les arguments: {args}")


def main():
    """Fonction principale appelée par la commande `ambulon`."""
    if len(sys.argv) > 1 and sys.argv[1] == 'scan':
        # Passer les arguments restants à la fonction scan
        scan(*sys.argv[2:])
    else:
        print(hello())
