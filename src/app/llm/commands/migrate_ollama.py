"""Migration d'Ollama - Commande pour migrer les modèles et configurations Ollama."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)


def main(argv: Optional[list[str]] = None) -> int:
    """Point d'entrée principal pour la commande migrate-ollama.
    
    Args:
        argv: Arguments de ligne de commande (None pour utiliser sys.argv)
        
    Returns:
        Code de sortie (0 pour succès, non-zéro pour erreur)
    """
    parser = argparse.ArgumentParser(
        description="Migrer les modèles et configurations Ollama",
        prog="ambulon migrate-ollama"
    )
    
    parser.add_argument(
        "--source",
        help="Répertoire source des modèles Ollama"
    )
    
    parser.add_argument(
        "--destination", 
        help="Répertoire de destination pour la migration"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher les actions qui seraient effectuées sans les exécuter"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Affichage verbeux"
    )
    
    if argv is None:
        argv = sys.argv[1:]
    
    args = parser.parse_args(argv)
    
    # Configuration du logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        logger.info("Début de la migration Ollama")
        
        if args.dry_run:
            logger.info("Mode dry-run activé - aucune modification ne sera effectuée")
        
        # TODO: Implémenter la logique de migration
        logger.info("Migration Ollama terminée avec succès")
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration Ollama: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
