"""Migration d'Ollama - Commande pour migrer les modèles et configurations Ollama."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_default_ollama_paths():
    """Retourne les chemins par défaut d'Ollama selon l'OS et les variables d'environnement."""
    # Vérifier les variables d'environnement Ollama en priorité
    models_path = os.environ.get('OLLAMA_MODELS')
    home_path = os.environ.get('OLLAMA_HOME')
    
    if os.name == 'nt':  # Windows
        # Chemins par défaut Windows
        default_models = Path.home() / '.ollama' / 'models'
        default_config = Path.home() / '.ollama'
        default_data = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / 'Ollama'
        
        # Utiliser les variables d'environnement si définies
        if models_path:
            default_models = Path(models_path)
        if home_path:
            default_config = Path(home_path)
            default_data = Path(home_path)
            
        return {
            'models': default_models,
            'config': default_config,
            'data': default_data
        }
    else:  # Linux/macOS
        # Chemins par défaut Unix
        default_models = Path.home() / '.ollama' / 'models'
        default_config = Path.home() / '.ollama'
        default_data = Path.home() / '.ollama'
        
        # Utiliser les variables d'environnement si définies
        if models_path:
            default_models = Path(models_path)
        if home_path:
            default_config = Path(home_path)
            default_data = Path(home_path)
            
        return {
            'models': default_models,
            'config': default_config,
            'data': default_data
        }


def migrate_ollama_data(source_paths: dict, destination: Path, dry_run: bool = False) -> bool:
    """Migre les données Ollama vers le nouveau répertoire.
    
    Args:
        source_paths: Dictionnaire des chemins source
        destination: Répertoire de destination
        dry_run: Si True, affiche seulement les actions sans les exécuter
        
    Returns:
        True si la migration réussit, False sinon
    """
    try:
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)
        
        for data_type, source_path in source_paths.items():
            if not source_path.exists():
                logger.warning(f"Le répertoire source {data_type} n'existe pas: {source_path}")
                continue
                
            dest_path = destination / data_type
            
            if dry_run:
                logger.info(f"[DRY-RUN] Copierait {source_path} vers {dest_path}")
                continue
            
            logger.info(f"Migration de {data_type}: {source_path} -> {dest_path}")
            
            if dest_path.exists():
                logger.warning(f"Le répertoire de destination existe déjà: {dest_path}")
                response = input(f"Écraser {dest_path}? (o/N): ")
                if response.lower() != 'o':
                    logger.info(f"Migration de {data_type} ignorée")
                    continue
                shutil.rmtree(dest_path)
            
            shutil.copytree(source_path, dest_path)
            logger.info(f"Migration de {data_type} terminée")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        return False


def main(argv: Optional[list[str]] = None) -> int:
    """Point d'entrée principal pour la commande migrate-ollama.
    
    Args:
        argv: Arguments de ligne de commande (None pour utiliser sys.argv)
        
    Returns:
        Code de sortie (0 pour succès, non-zéro pour erreur)
    """
    parser = argparse.ArgumentParser(
        description="Migrer les modèles et configurations Ollama vers Z:\\WarchoLife\\WarchoOllama",
        prog="ambulon migrate-ollama"
    )
    
    parser.add_argument(
        "--source",
        help="Répertoire source des modèles Ollama (détecté automatiquement si non spécifié)"
    )
    
    parser.add_argument(
        "--destination", 
        default=r"Z:\WarchoLife\WarchoOllama",
        help="Répertoire de destination pour la migration (défaut: Z:\\WarchoLife\\WarchoOllama)"
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
        
        # Déterminer les chemins source
        if args.source:
            source_base = Path(args.source)
            source_paths = {
                'models': source_base / 'models',
                'config': source_base,
                'data': source_base
            }
        else:
            logger.info("Détection automatique des chemins Ollama...")
            logger.info("Vérification des variables d'environnement OLLAMA_MODELS et OLLAMA_HOME...")
            
            # Afficher les variables d'environnement détectées
            if os.environ.get('OLLAMA_MODELS'):
                logger.info(f"OLLAMA_MODELS détecté: {os.environ.get('OLLAMA_MODELS')}")
            if os.environ.get('OLLAMA_HOME'):
                logger.info(f"OLLAMA_HOME détecté: {os.environ.get('OLLAMA_HOME')}")
            
            source_paths = get_default_ollama_paths()
        
        destination = Path(args.destination)
        
        logger.info(f"Migration vers: {destination}")
        for data_type, path in source_paths.items():
            logger.info(f"  {data_type}: {path}")
        
        # Vérifier que le lecteur Z: est accessible
        if not args.dry_run and not Path("Z:").exists():
            logger.error("Le lecteur Z: n'est pas accessible. Vérifiez que le réseau est connecté.")
            return 1
        
        # Effectuer la migration
        success = migrate_ollama_data(source_paths, destination, args.dry_run)
        
        if success:
            logger.info("Migration Ollama terminée avec succès")
            if not args.dry_run:
                logger.info(f"Les données Ollama ont été migrées vers: {destination}")
                logger.info("N'oubliez pas de configurer Ollama pour utiliser le nouveau répertoire.")
            return 0
        else:
            logger.error("La migration a échoué")
            return 1
        
    except Exception as e:
        logger.error(f"Erreur lors de la migration Ollama: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
