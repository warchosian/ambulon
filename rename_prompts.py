#!/usr/bin/env python3
"""Script pour renommer les fichiers _prompt_*.md en prompt.*.md"""

from pathlib import Path
import sys

def main():
    directory = Path('.claude/prompts')
    
    if not directory.exists():
        print(f"Erreur: Le répertoire {directory} n'existe pas.", file=sys.stderr)
        return 1
    
    files = sorted(directory.glob('_prompt_*.md'))
    
    if not files:
        print("Aucun fichier trouvé avec le pattern '_prompt_*.md'")
        return 0
    
    print(f"Fichiers trouvés: {len(files)}\n")
    
    count = 0
    for old_path in files:
        new_name = old_path.name.replace('_prompt_', 'prompt.', 1)
        new_path = old_path.parent / new_name
        
        old_path.rename(new_path)
        print(f'  ✓ {old_path.name} -> {new_name}')
        count += 1
    
    print(f'\n═══════════════════════════════════════')
    print(f'  Total de fichiers renommés: {count}')
    print(f'═══════════════════════════════════════')
    return 0

if __name__ == '__main__':
    sys.exit(main())
