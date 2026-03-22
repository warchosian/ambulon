#!/usr/bin/env python
import re

# Lire le fichier
with open('applications/formation-ecologie.rag/formation-ecologie.c4model-itoced.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Test la regex
toc_exists_pattern = r'^##\s+(Table des matières|Table of Contents|Sommaire)'
has_existing_toc = re.search(toc_exists_pattern, content, re.MULTILINE | re.IGNORECASE)

print(f"Pattern: {toc_exists_pattern}")
print(f"has_existing_toc: {has_existing_toc is not None}")

if has_existing_toc:
    print(f"Match trouvé: '{has_existing_toc.group()}'")
    print(f"Position: {has_existing_toc.start()}-{has_existing_toc.end()}")
else:
    print("Aucun match trouvé")
    print("\nPremières lignes du fichier:")
    for i, line in enumerate(content.split('\n')[:15], 1):
        if 'Table' in line or 'matière' in line.lower() or line.startswith('##'):
            print(f"  Ligne {i}: {repr(line)}")
