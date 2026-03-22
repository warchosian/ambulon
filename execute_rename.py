#!/usr/bin/env python3
"""Exécute le renommage des fichiers."""

from pathlib import Path

dir_path = Path('.claude/prompts')
old_pattern = '_prompt_'
new_pattern = 'prompt.'

renamed_files = []

for f in dir_path.iterdir():
    if f.is_file() and old_pattern in f.name:
        new_name = f.name.replace(old_pattern, new_pattern)
        new_path = f.parent / new_name
        
        print(f"Renommage: {f.name} -> {new_name}")
        f.rename(new_path)
        
        renamed_files.append((f.name, new_name))

print(f"\n{len(renamed_files)} fichiers renommés")

# Écrit la liste des fichiers renommés dans un fichier
with open('renamed_files_list.txt', 'w', encoding='utf-8') as out:
    for old, new in renamed_files:
        out.write(f"{old} -> {new}\n")
