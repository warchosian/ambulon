#!/usr/bin/env python3
"""
Outil de copie de fichiers avec pattern.
Usage: python copy_files.py <source_dir> <dest_dir> [--pattern "*.md"]
"""

import os
import sys
import shutil
from pathlib import Path


def copy_files(source_dir: str, dest_dir: str, pattern: str = "*", dry_run: bool = False):
    """
    Copie les fichiers d'un répertoire vers un autre.
    
    Args:
        source_dir: Répertoire source
        dest_dir: Répertoire destination
        pattern: Pattern de fichiers
        dry_run: Simulation sans copie
    """
    src_path = Path(source_dir)
    dst_path = Path(dest_dir)
    
    if not src_path.exists():
        print(f"ERREUR: Le répertoire source {source_dir} n'existe pas")
        return 1
    
    if not dst_path.exists():
        print(f"Création du répertoire {dest_dir}")
        if not dry_run:
            dst_path.mkdir(parents=True, exist_ok=True)
    
    copied = []
    
    for f in src_path.glob(pattern):
        if f.is_file():
            dest_file = dst_path / f.name
            if dry_run:
                print(f"[DRY-RUN] Copie: {f} -> {dest_file}")
            else:
                print(f"Copie: {f} -> {dest_file}")
                shutil.copy2(f, dest_file)
            copied.append(f)
    
    print(f"\n{len(copied)} fichier(s) copié(s)")
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Copie des fichiers")
    parser.add_argument("source_dir", help="Répertoire source")
    parser.add_argument("dest_dir", help="Répertoire destination")
    parser.add_argument("--pattern", default="*", help="Pattern de fichiers")
    parser.add_argument("--dry-run", action="store_true", help="Simulation")
    
    args = parser.parse_args()
    sys.exit(copy_files(args.source_dir, args.dest_dir, args.pattern, args.dry_run))
