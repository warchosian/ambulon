#!/usr/bin/env python3
"""
Vérifie que chaque diagramme est dans le bon chapitre
"""
from pathlib import Path

file_path = Path(r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\doc\guidelines-illustrated.md')

# Lire le fichier
content = file_path.read_text(encoding='utf-8')
lines = content.split('\n')

# Trouver tous les chapitres (##)
chapters = []
for i, line in enumerate(lines):
    if line.startswith('## ') and not line.startswith('### '):
        chapter_title = line.replace('## ', '').strip()
        chapters.append({'line': i + 1, 'title': chapter_title})

# Ajouter une "fin" pour le dernier chapitre
chapters.append({'line': len(lines), 'title': 'FIN'})

# Trouver tous les blocs PlantUML
plantuml_blocks = []
in_block = False
for i, line in enumerate(lines):
    if '```plantuml' in line:
        in_block = True
        start = i
        title = ""
    elif in_block:
        if line.strip().startswith('title '):
            title = line.strip().replace('title ', '')
        elif line.strip() == '```':
            # Trouver la figcaption
            figcaption = ""
            if i + 1 < len(lines) and '<figcaption>' in lines[i + 1]:
                figcaption = lines[i + 1].replace('<figcaption>', '').replace('</figcaption>', '').strip()

            plantuml_blocks.append({
                'start': start + 1,
                'end': i + 1,
                'title': title,
                'figcaption': figcaption
            })
            in_block = False

# Pour chaque diagramme, trouver dans quel chapitre il se trouve
print("=" * 80)
print("VERIFICATION DE LA POSITION DES DIAGRAMMES")
print("=" * 80)
print()

for idx, block in enumerate(plantuml_blocks, 1):
    # Trouver le chapitre
    current_chapter = None
    for j in range(len(chapters) - 1):
        if chapters[j]['line'] <= block['start'] < chapters[j + 1]['line']:
            current_chapter = chapters[j]['title']
            break

    print(f"Diagramme #{idx} (ligne {block['start']})")
    print(f"  Chapitre: {current_chapter}")
    print(f"  Titre diagramme: {block['title']}")
    print(f"  Legende actuelle: {block['figcaption']}")
    print()

# Résumé par chapitre
print("=" * 80)
print("RESUME PAR CHAPITRE")
print("=" * 80)
print()

for j in range(len(chapters) - 1):
    chapter = chapters[j]
    # Compter les diagrammes dans ce chapitre
    diagrams_in_chapter = []
    for idx, block in enumerate(plantuml_blocks, 1):
        if chapter['line'] <= block['start'] < chapters[j + 1]['line']:
            diagrams_in_chapter.append(f"  - Diagramme #{idx}: {block['title']}")

    if diagrams_in_chapter:
        print(f"{chapter['title']} (ligne {chapter['line']})")
        for diag in diagrams_in_chapter:
            print(diag)
        print()
