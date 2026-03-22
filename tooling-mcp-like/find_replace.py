#!/usr/bin/env python3
"""
Outil de recherche et remplacement dans des fichiers.
Usage: python find_replace.py <pattern> <replacement> <directory> [--glob "*.md"]
"""

import os
import sys
import re
from pathlib import Path


def find_replace(directory: str, pattern: str, replacement: str, glob_pattern: str = "*", 
                 dry_run: bool = False, case_sensitive: bool = True):
    """
    Recherche et remplace du texte dans les fichiers.
    
    Args:
        directory: Répertoire à scanner
        pattern: Texte/pattern à rechercher
        replacement: Texte de remplacement
        glob_pattern: Pattern de fichiers (ex: "*.md")
        dry_run: Simulation sans modification
        case_sensitive: Respect de la casse
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"ERREUR: Le répertoire {directory} n'existe pas")
        return 1
    
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(re.escape(pattern), flags)
    
    modified_files = []
    
    for f in dir_path.rglob(glob_pattern):
        if not f.is_file():
            continue
            
        try:
            content = f.read_text(encoding='utf-8')
            new_content = regex.sub(replacement, content)
            
            if new_content != content:
                count = len(regex.findall(content))
                if dry_run:
                    print(f"[DRY-RUN] {f}: {count} remplacement(s)")
                else:
                    print(f"Modification: {f} ({count} remplacement(s))")
                    f.write_text(new_content, encoding='utf-8')
                modified_files.append((f, count))
        except Exception as e:
            print(f"ERREUR sur {f}: {e}")
    
    print(f"\n{len(modified_files)} fichiers modifiés")
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Recherche et remplace dans des fichiers")
    parser.add_argument("pattern", help="Texte à rechercher")
    parser.add_argument("replacement", help="Texte de remplacement")
    parser.add_argument("directory", help="Répertoire cible")
    parser.add_argument("--glob", default="*", help="Pattern de fichiers (défaut: *)")
    parser.add_argument("--dry-run", action="store_true", help="Simulation")
    parser.add_argument("--case-insensitive", action="store_true", help="Ignorer la casse")
    
    args = parser.parse_args()
    sys.exit(find_replace(args.directory, args.pattern, args.replacement, 
                          args.glob, args.dry_run, not args.case_insensitive))
