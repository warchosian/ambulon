import re

# Test sur le fichier
with open('applications/formation-ecologie.rag/formation-ecologie.c4model-toced.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Ma regex
toc_exists_pattern = r'^##\s+(Table des matières|Table of Contents|Sommaire)'
has_existing_toc = re.search(toc_exists_pattern, content, re.MULTILINE | re.IGNORECASE)

print(f"TOC détectée: {has_existing_toc is not None}")
if has_existing_toc:
    print(f"Match: {has_existing_toc.group()}")
else:
    # Debug - chercher manuellement
    for i, line in enumerate(content.split('\n')[:20], 1):
        if 'Table' in line or 'matière' in line.lower():
            print(f"Ligne {i}: {repr(line)}")
