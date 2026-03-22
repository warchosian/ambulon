#!/usr/bin/env python3
"""
Outil de renommage de fichiers avec pattern.
Usage: python rename_files.py <directory> <old_pattern> <new_pattern>
Exemple: python rename_files.py .claude/prompts "_prompt_" "prompt."
"""

import os
import sys
import re
from pathlib import Path


def rename_files(directory: str, old_pattern: str, new_pattern: str, dry_run: bool = False):
    """
    Renomme les fichiers en remplaçant un pattern par un autre.
    
    Args:
        directory: Répertoire contenant les fichiers
        old_pattern: Pattern à remplacer dans le nom
        new_pattern: Pattern de remplacement
        dry_run: Si True, affiche seulement sans renommer
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"ERREUR: Le répertoire {directory} n'existe pas")
        return 1
    
    renamed = []
    
    for f in dir_path.iterdir():
        if f.is_file() and old_pattern in f.name:
            new_name = f.name.replace(old_pattern, new_pattern)
            new_path = f.parent / new_name
            
            if dry_run:
                print(f"[DRY-RUN] {f.name} -> {new_name}")
            else:
                print(f"Renommage: {f.name} -> {new_name}")
                f.rename(new_path)
            
            renamed.append((f.name, new_name))
    
    print(f"\n{len(renamed)} fichiers concernés")
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Renomme les fichiers avec pattern")
    parser.add_argument("directory", help="Répertoire cible")
    parser.add_argument("old_pattern", help="Pattern à remplacer")
    parser.add_argument("new_pattern", help="Nouveau pattern")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans renommage")
    
    args = parser.parse_args()
    sys.exit(rename_files(args.directory, args.old_pattern, args.new_pattern, args.dry_run))
