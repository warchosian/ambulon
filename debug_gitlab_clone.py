#!/usr/bin/env python
"""Diagnostic complet du parsing gitlab.yaml"""
import yaml
import sys
from pathlib import Path

config_path = Path("config/gitlab.yaml")
print(f"=== Fichier: {config_path.absolute()} ===")
print(f"Existe: {config_path.exists()}")
print()

# Lecture brute
with open(config_path, 'r', encoding='utf-8') as f:
    raw_content = f.read()
    lines = raw_content.split('\n')
    
print("=== Lignes 60-68 (repr) ===")
for i, line in enumerate(lines[59:68], start=60):
    print(f"{i}: {repr(line)}")

print()
print("=== Parsing YAML ===")
try:
    config = yaml.safe_load(raw_content)
    gitlab_config = config.get('gitlab', {})
    repos = gitlab_config.get('repositories', [])
    
    print(f"Config gitlab trouvée: {bool(gitlab_config)}")
    print(f"Nombre de repositories: {len(repos)}")
    print()
    
    print("=== Repos actifs (non commentés) ===")
    for i, r in enumerate(repos, 1):
        marker = " <-- MOBILEHOOP" if 'mobilehoop' in str(r) else ""
        print(f"{i}. {r}{marker}")
    
    print()
    # Vérifie mobilehoop spécifiquement
    mobilehoop_repos = [r for r in repos if 'mobilehoop' in str(r)]
    if mobilehoop_repos:
        print(f"✓ mobilehoop trouvé: {mobilehoop_repos}")
    else:
        print("✗ mobilehoop NON trouvé dans la liste!")
        
except Exception as e:
    print(f"ERREUR YAML: {e}")
    import traceback
    traceback.print_exc()
