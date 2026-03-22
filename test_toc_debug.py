#!/usr/bin/env python
import sys
sys.path.insert(0, 'src')

from app.diagrams.core.markdown_to_html import markdown_to_html_basic

# Test
with open('applications/formation-ecologie.rag/formation-ecologie.c4model-toced.md', 'r', encoding='utf-8') as f:
    content = f.read()

print("Premieres lignes du fichier:")
for i, line in enumerate(content.split('\n')[:15], 1):
    print(f"{i}: {repr(line)}")

print("\n" + "="*50)
print("Test detection TOC:")

import re
toc_exists_pattern = r'^##\s+(Table des matières|Table of Contents|Sommaire)'
has_existing_toc = re.search(toc_exists_pattern, content, re.MULTILINE | re.IGNORECASE)
print(f"has_existing_toc: {has_existing_toc}")

# Conversion
html = markdown_to_html_basic(content)

# Compter les TOCs
toc_count = html.count('Table des matières')
print(f"\nNombre de 'Table des matières' dans HTML: {toc_count}")

# Chercher les nav
toc_nav_count = html.count('<nav class="table-of-contents"')
print(f"Nombre de <nav class='table-of-contents'>: {toc_nav_count}")
