#!/usr/bin/env python3
"""
Restaure les balises <figcaption> autour des légendes
"""
from pathlib import Path
import re

file_path = Path(r'G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\doc\guidelines-illustrated.md')

# Lire le fichier
content = file_path.read_text(encoding='utf-8')
lines = content.split('\n')

# Corriger les lignes qui commencent par "Figure X.Y" mais n'ont pas de balise <figcaption>
modifications = 0
for i, line in enumerate(lines):
    # Chercher les lignes qui ressemblent à "Figure X.Y – ..."
    if re.match(r'^Figure \d+\.\d+ –', line) and '<figcaption>' not in line:
        # Ajouter les balises
        lines[i] = f"<figcaption>{line}</figcaption>"
        modifications += 1
        print(f"Ligne {i+1}: Ajoute balises figcaption")

# Écrire le résultat
new_content = '\n'.join(lines)
file_path.write_text(new_content, encoding='utf-8')

print(f"\nFichier mis a jour")
print(f"Total de modifications : {modifications}")
