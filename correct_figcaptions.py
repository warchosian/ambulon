#!/usr/bin/env python3
"""
Script pour corriger les figcaptions basé sur les titres réels des diagrammes
"""
import re
from pathlib import Path

file_path = Path(r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\doc\guidelines-illustrated.md')

# Lire le fichier
content = file_path.read_text(encoding='utf-8')
lines = content.split('\n')

# Mapping correct basé sur l'analyse précédente
# Format: titre du diagramme -> légende correcte
correct_captions = {
    "Typer vs argparse - Comparaison": "Figure 1.1 – Comparaison CLI : Typer vs Argparse",
    "Pattern CLI Obligatoire avec argparse": "Figure 2.1 – Pattern argparse obligatoire",
    "Flux d'Exécution Standard d'une Commande CLI": "Figure 2.2 – Flux d'exécution CLI standard",
    "Architecture des Branches Git - Ambulon": "Figure 3.1 – Architecture des branches Git",
    "Processus de Release avec SemVer": "Figure 4.1 – Processus de release avec SemVer",
    "Impact des Types de Commits sur la Version": "Figure 4.2 – Impact des types de commits",
    "Hiérarchie de Configuration - Priority Order": "Figure 5.1 – Hiérarchie de configuration",
    "Flux de Résolution de Configuration": "Figure 5.2 – Flux de résolution de configuration",
    "Pattern des Modules de Conversion": "Figure 6.1 – Pattern des modules de conversion",
    "Conventions de Nommage des Modules de Conversion": "Figure 6.2 – Conventions de nommage",
    "Interface CLI Standard pour Conversions": "Figure 6.3 – Interface CLI standard",
    "Gestion des Secrets - Workflow de Sécurité": "Figure 7.1 – Workflow de gestion des secrets",
    "Checklist de Sécurité Avant Push": "Figure 7.2 – Checklist de sécurité pré-push",
    "Structure du Projet Ambulon": "Figure 8.1 – Structure du projet Ambulon",
    "Séparation Commands / Core - Responsabilités": "Figure 8.2 – Séparation Commands/Core",
    "Cycle de Vie Complet d'une Fonctionnalité": "Figure 9.1 – Cycle de vie d'une fonctionnalité",
    "Matrice de Décision - Type de Commit": "Figure 9.2 – Matrice de décision des commits",
    "Principes Clés du Projet Ambulon": "Figure 10.1 – Résumé des principes clés",
}

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
            plantuml_blocks.append({
                'start': start,
                'end': i,
                'title': title
            })
            in_block = False

print(f"Trouvé {len(plantuml_blocks)} blocs PlantUML\n")

# Corriger les figcaptions
modifications = 0
for idx, block in enumerate(plantuml_blocks):
    next_line_idx = block['end'] + 1

    if next_line_idx >= len(lines):
        continue

    # Vérifier si une figcaption existe
    if '<figcaption>' in lines[next_line_idx]:
        # Trouver la légende correcte
        title = block['title']
        if title in correct_captions:
            correct_caption = f"<figcaption>{correct_captions[title]}</figcaption>"

            if lines[next_line_idx] != correct_caption:
                old_caption = lines[next_line_idx]
                lines[next_line_idx] = correct_caption
                modifications += 1

                print(f"OK Bloc {idx + 1} (ligne {block['end'] + 1}):")
                print(f"  Titre: {title}")
                print(f"  Avant: {old_caption}")
                print(f"  Apres: {correct_caption}\n")
        else:
            print(f"WARNING Bloc {idx + 1}: Titre non trouve dans le mapping: '{title}'")

# Écrire le résultat
new_content = '\n'.join(lines)
file_path.write_text(new_content, encoding='utf-8')

print(f"\nFichier mis à jour : {file_path}")
print(f"Total de modifications : {modifications}/18")
