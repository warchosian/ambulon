#!/usr/bin/env python3
"""
Outil de listage de fichiers avec filtrage.
Usage: python list_files.py <directory> [--pattern "*.md"] [--recursive]
"""

import os
import sys
from pathlib import Path


def list_files(directory: str, pattern: str = "*", recursive: bool = False):
    """Liste les fichiers d'un répertoire."""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"ERREUR: Le répertoire {directory} n'existe pas")
        return 1
    
    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))
    
    files = [f for f in files if f.is_file()]
    
    for f in sorted(files):
        size = f.stat().st_size
        print(f"{f} ({size} bytes)")
    
    print(f"\n{len(files)} fichier(s) trouvé(s)")
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Liste les fichiers")
    parser.add_argument("directory", help="Répertoire cible")
    parser.add_argument("--pattern", default="*", help="Pattern de filtrage")
    parser.add_argument("--recursive", "-r", action="store_true", help="Récursif")
    
    args = parser.parse_args()
    sys.exit(list_files(args.directory, args.pattern, args.recursive))
