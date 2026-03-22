#!/usr/bin/env python3
"""Script temporaire pour renommer les fichiers."""

import os
from pathlib import Path

def rename_files(directory: str, old_pattern: str, new_pattern: str):
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"ERREUR: Le répertoire {directory} n'existe pas")
        return 1
    
    renamed = []
    
    for f in dir_path.iterdir():
        if f.is_file() and old_pattern in f.name:
            new_name = f.name.replace(old_pattern, new_pattern)
            new_path = f.parent / new_name
            
            print(f"Renommage: {f.name} -> {new_name}")
            f.rename(new_path)
            
            renamed.append((f.name, new_name))
    
    print(f"\n{len(renamed)} fichiers renommés")
    return renamed

if __name__ == "__main__":
    result = rename_files('.claude/prompts', '_prompt_', 'prompt.')
