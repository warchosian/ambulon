#!/usr/bin/env python3
"""
Vérifie l'ordre et la position des diagrammes dans SISS-DAT.md
"""
from pathlib import Path

file_path = Path(r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\doc\SISS-DAT.md')

# Lire le fichier
content = file_path.read_text(encoding='utf-8')
lines = content.split('\n')

# Trouver tous les chapitres et diagrammes
chapters = []
diagrams = []

current_chapter = None
in_plantuml = False
diagram_start = 0
diagram_title = ""

for i, line in enumerate(lines, 1):
    # Détecter les chapitres (### ou ##)
    if line.startswith('### ') or line.startswith('## '):
        chapter_title = line.replace('###', '').replace('##', '').strip()
        current_chapter = chapter_title
        chapters.append({'line': i, 'title': chapter_title})

    # Détecter les blocs PlantUML
    if '```plantuml' in line:
        in_plantuml = True
        diagram_start = i
        diagram_title = ""
    elif in_plantuml:
        if line.strip().startswith('title '):
            diagram_title = line.strip().replace('title ', '')
        elif line.strip() == '```':
            diagrams.append({
                'line': diagram_start,
                'end': i,
                'chapter': current_chapter,
                'title': diagram_title
            })
            in_plantuml = False

print("="*80)
print("STRUCTURE DES DIAGRAMMES DANS SISS-DAT.md")
print("="*80)
print()

for idx, diag in enumerate(diagrams, 1):
    print(f"Diagramme #{idx} (lignes {diag['line']}-{diag['end']})")
    print(f"  Chapitre: {diag['chapter']}")
    print(f"  Titre diagramme: {diag['title']}")
    print()

print("="*80)
print("PROBLEMES POTENTIELS")
print("="*80)
print()

# Vérifier l'ordre logique
expected_order = [
    "Cas d'usage",
    "Composants Techniques",
    "Flux de Données",
    "Diagramme de Déploiement",
    "Diagramme de Composants",
    "Authentification en Mode TEST",
    "Cycle de Vie d'un Utilisateur",
    "Modèle Relationnel Simplifié"
]

for idx, (diag, expected) in enumerate(zip(diagrams, expected_order), 1):
    if diag['title'] != expected:
        print(f"! Diagramme #{idx} : Attendu '{expected}', trouve '{diag['title']}'")

# Vérifier les doublons
diagram_titles = [d['title'] for d in diagrams]
seen = set()
for title in diagram_titles:
    if title in seen:
        print(f"! DOUBLON detecte : '{title}'")
    seen.add(title)

print()
print("Total diagrammes : ", len(diagrams))
