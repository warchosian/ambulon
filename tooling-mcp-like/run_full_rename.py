#!/usr/bin/env python3
"""
Script complet pour renommer les prompts et mettre à jour les références.
Usage: python tooling-mcp-like/run_full_rename.py
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from rename_files import rename_files
from find_replace import find_replace


def main():
    print("=" * 60)
    print("Renommage des fichiers prompts")
    print("=" * 60)
    print()
    
    # Étape 1: Dry-run
    print("[1/3] Dry-run pour vérification...")
    result = rename_files(".claude/prompts", "_prompt_", "prompt.", dry_run=True)
    if result != 0:
        return result
    
    print()
    response = input("Continuer avec le renommage réel ? (o/N): ")
    if response.lower() not in ('o', 'oui', 'y', 'yes'):
        print("Annulé.")
        return 0
    
    # Étape 2: Renommage réel
    print()
    print("[2/3] Renommage réel...")
    result = rename_files(".claude/prompts", "_prompt_", "prompt.", dry_run=False)
    if result != 0:
        return result
    
    # Étape 3: Mise à jour des références
    print()
    print("[3/3] Mise à jour des références dans doc/...")
    result = find_replace("doc", "_prompt_", "prompt.", glob_pattern="*.md", dry_run=False)
    
    print()
    print("=" * 60)
    print("SUCCESS !")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
