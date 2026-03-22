#!/usr/bin/env python3
"""
Script pour ajouter automatiquement des <figcaption> aux diagrammes PlantUML
dans guidelines-illustrated.md
"""
import re
from pathlib import Path

file_path = Path(r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\doc\guidelines-illustrated.md')

# Lire le fichier
content = file_path.read_text(encoding='utf-8')
lines = content.split('\n')

# Définir manuellement les légendes pour chaque diagramme
# Basé sur l'analyse du contexte de chaque section
captions = [
    "Figure 1.1 – Comparaison CLI : Typer vs Argparse",  # Ligne ~26
    "Figure 2.1 – Pattern argparse obligatoire",  # Ligne ~76
    "Figure 2.2 – Gestion des sous-commandes",  # Ligne ~141
    "Figure 3.1 – Pattern de logging obligatoire",  # Ligne ~205
    "Figure 3.2 – Pattern de configuration obligatoire",  # Ligne ~279
    "Figure 4.1 – Workflow de validation et rebuild",  # Ligne ~357
    "Figure 5.1 – Gestion des secrets et fichiers sensibles",  # Ligne ~421
    "Figure 6.1 – Structure des types de commits conventionnels",  # Ligne ~493
    "Figure 6.2 – Workflow de gestion des commits",  # Ligne ~568
    "Figure 6.3 – Classification par impact des commits",  # Ligne ~612
    "Figure 6.4 – Détection et correction des commits non conformes",  # Ligne ~658
    "Figure 7.1 – Workflow Git avec branches de développement",  # Ligne ~722
    "Figure 7.2 – Pattern de pre-commit hooks",  # Ligne ~776
    "Figure 7.3 – Workflow de release complète",  # Ligne ~827
    "Figure 8.1 – Workflow de développement d'une fonctionnalité",  # Ligne ~890
    "Figure 8.2 – Workflow de release avec validation",  # Ligne ~946
    "Figure 9.1 – Pattern de création de branches",  # Ligne ~1016
    "Figure 10.1 – Architecture des principes clés",  # Ligne ~1109
]

# Trouver tous les blocs PlantUML
plantuml_blocks = []
in_block = False
for i, line in enumerate(lines):
    if '```plantuml' in line:
        in_block = True
        start = i
    elif in_block and line.strip() == '```':
        plantuml_blocks.append({'start': start, 'end': i})
        in_block = False

print(f"Trouvé {len(plantuml_blocks)} blocs PlantUML")
print(f"Légendes préparées : {len(captions)}")

# Ajouter les figcaptions
new_lines = lines.copy()
offset = 0

for idx, block in enumerate(plantuml_blocks):
    if idx >= len(captions):
        print(f"Warning: Pas assez de légendes pour le bloc {idx + 1}")
        continue

    # Position après le ```
    insert_pos = block['end'] + 1 + offset

    # Vérifier si une figcaption existe déjà
    if insert_pos < len(new_lines) and '<figcaption>' in new_lines[insert_pos]:
        print(f"Bloc {idx + 1}: Légende déjà présente, skip")
        continue

    # Insérer la figcaption
    caption_line = f"<figcaption>{captions[idx]}</figcaption>"
    new_lines.insert(insert_pos, caption_line)
    offset += 1

    print(f"Bloc {idx + 1} (ligne {block['end']}): Ajouté '{captions[idx]}'")

# Écrire le résultat
new_content = '\n'.join(new_lines)
file_path.write_text(new_content, encoding='utf-8')

print(f"\nFichier mis à jour : {file_path}")
print(f"Total de légendes ajoutées : {offset}")
