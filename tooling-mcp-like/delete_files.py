#!/usr/bin/env python3
"""
Outil de suppression de fichiers avec pattern.
Usage: python delete_files.py <directory> [--pattern "*.tmp"] [--recursive]
"""

import os
import sys
from pathlib import Path


def delete_files(directory: str, pattern: str = "*", recursive: bool = False, dry_run: bool = False):
    """
    Supprime les fichiers correspondant à un pattern.
    
    Args:
        directory: Répertoire cible
        pattern: Pattern de fichiers
        recursive: Récursif
        dry_run: Simulation sans suppression
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"ERREUR: Le répertoire {directory} n'existe pas")
        return 1
    
    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))
    
    files = [f for f in files if f.is_file()]
    
    for f in files:
        if dry_run:
            print(f"[DRY-RUN] Suppression: {f}")
        else:
            print(f"Suppression: {f}")
            f.unlink()
    
    print(f"\n{len(files)} fichier(s) supprimé(s)")
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Supprime des fichiers")
    parser.add_argument("directory", help="Répertoire cible")
    parser.add_argument("--pattern", default="*", help="Pattern de fichiers")
    parser.add_argument("--recursive", "-r", action="store_true", help="Récursif")
    parser.add_argument("--dry-run", action="store_true", help="Simulation")
    
    args = parser.parse_args()
    sys.exit(delete_files(args.directory, args.pattern, args.recursive, args.dry_run))
