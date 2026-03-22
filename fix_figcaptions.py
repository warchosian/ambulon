#!/usr/bin/env python3
"""
Script pour corriger les figcaptions en analysant le contexte réel de chaque diagramme
"""
import re
from pathlib import Path

file_path = Path(r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\doc\guidelines-illustrated.md')

# Lire le fichier
content = file_path.read_text(encoding='utf-8')
lines = content.split('\n')

# Trouver tous les blocs PlantUML avec leur contexte
plantuml_blocks = []
in_block = False
current_section = ""
current_subsection = ""

for i, line in enumerate(lines):
    # Détecter les sections
    if line.startswith('## '):
        current_section = line.replace('## ', '').strip()
    elif line.startswith('### '):
        current_subsection = line.replace('### ', '').strip()

    # Détecter les blocs PlantUML
    if '```plantuml' in line:
        in_block = True
        start = i
        title = ""
    elif in_block:
        # Chercher le titre dans le bloc
        if line.strip().startswith('title '):
            title = line.strip().replace('title ', '')
        elif line.strip() == '```':
            plantuml_blocks.append({
                'start': start,
                'end': i,
                'section': current_section,
                'subsection': current_subsection,
                'title': title
            })
            in_block = False

print(f"Trouvé {len(plantuml_blocks)} blocs PlantUML\n")

# Afficher le contexte de chaque bloc
for idx, block in enumerate(plantuml_blocks, 1):
    print(f"Bloc {idx} (ligne {block['start']}):")
    print(f"  Section: {block['section']}")
    print(f"  Sous-section: {block['subsection']}")
    print(f"  Titre: {block['title']}")

    # Lire la figcaption actuelle si elle existe
    next_line_idx = block['end'] + 1
    if next_line_idx < len(lines) and '<figcaption>' in lines[next_line_idx]:
        current_caption = lines[next_line_idx].replace('<figcaption>', '').replace('</figcaption>', '').strip()
        print(f"  Caption actuelle: {current_caption}")
    print()
