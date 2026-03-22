#!/usr/bin/env python
"""Trouver tous les gitlab.yaml"""
import os
from pathlib import Path

print("=== Recherche de tous les gitlab.yaml ===")
print(f"AMBULON_HOME: {os.getenv('AMBULON_HOME', 'non defini')}")
print(f"AMBULON_CONFIG_DIR: {os.getenv('AMBULON_CONFIG_DIR', 'non defini')}")
print(f"Repertoire courant: {Path.cwd()}")
print()

# Chercher tous les gitlab.yaml
for root in [Path.cwd(), Path.home()]:
    if root.exists():
        for yaml_file in root.rglob("gitlab.yaml"):
            print(f"TROUVE: {yaml_file}")
            # Lire les 20 premieres lignes
            try:
                with open(yaml_file, 'r') as f:
                    lines = f.readlines()[:20]
                    for i, line in enumerate(lines, 1):
                        if 'repository' in line.lower() or 'mobilehoop' in line.lower():
                            print(f"  Ligne {i}: {line.rstrip()}")
            except Exception as e:
                print(f"  Erreur lecture: {e}")
            print()

# Verifier le fichier attendu
expected = Path("config/gitlab.yaml")
print(f"\n=== Fichier attendu ===")
print(f"Chemin: {expected.absolute()}")
print(f"Existe: {expected.exists()}")
if expected.exists():
    with open(expected, 'r') as f:
        content = f.read()
        if 'mobilehoop' in content:
            print("✓ Contient 'mobilehoop'")
        else:
            print("✗ Ne contient PAS 'mobilehoop'")
