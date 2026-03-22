#!/usr/bin/env python
"""Diagnostic complet du chargement de config par gitlab_clone"""
import sys
import os
from pathlib import Path

# Simuler l'environnement
os.chdir(r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon')

# Importer comme le fait gitlab_clone
sys.path.insert(0, 'src')

from app.core.config_loader import load_config as load_app_config, find_config_file

DEFAULT_CONFIG = {
    'gitlab': {
        'token': os.getenv('GITLAB_PRIVATE_TOKEN', ''),
        'username': os.getenv('GITLAB_USERNAME', 'oauth2'),
        'base_clone_dir': './gitlab_clones',
        'repositories': []
    }
}

config_path = "config/gitlab.yaml"
print(f"=== Chargement de la config ===")
print(f"Chemin demande: {config_path}")
print(f"Repertoire courant: {Path.cwd()}")
print()

# Verifier si le fichier existe
full_path = Path(config_path)
print(f"Fichier existe (relatif): {full_path.exists()}")
print(f"Fichier existe (absolu): {full_path.absolute().exists()}")
print(f"Chemin absolu: {full_path.absolute()}")
print()

# Charger la config comme le fait gitlab_clone
config = load_app_config(config_path, DEFAULT_CONFIG)

print("=== Config chargee ===")
gitlab_config = config.get("gitlab", {})
print(f"Sections: {list(config.keys())}")
print(f"Gitlab sections: {list(gitlab_config.keys())}")
print()

repositories = gitlab_config.get("repositories", [])
print(f"Type des repositories: {type(repositories)}")
print(f"Nombre de repositories: {len(repositories)}")
print()

if isinstance(repositories, str):
    print("ATTENTION: repositories est une string, pas une liste!")
    print(f"Contenu: {repr(repositories[:200])}")
else:
    print("=== Repositories ===")
    for i, r in enumerate(repositories, 1):
        marker = " <-- MOBILEHOOP" if 'mobilehoop' in str(r) else ""
        print(f"{i}. {r}{marker}")
