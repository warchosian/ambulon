#!/usr/bin/env python
"""Test complet du workflow add-toc4md -> add-itoc4md"""

import sys
import tempfile
import shutil
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.toc.core.markdown_toc_generator import add_toc_to_markdown_logic
from app.toc.core.markdown_itoc import add_toc_backlinks_logic

# Fichier de test
source_file = Path("applications/sireines.rag/sireines.dat.md")

if not source_file.exists():
    print(f"Fichier source non trouvé: {source_file}")
    sys.exit(1)

# Créer un répertoire temporaire pour les tests
with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)
    
    # Étape 1: Copier le fichier source
    step1_input = tmp_path / "step0.md"
    shutil.copy(source_file, step1_input)
    print(f"=== ÉTAPE 0: Fichier source copié ===")
    print(f"   Fichier: {step1_input}")
    
    # Étape 2: add-toc4md
    step1_output = tmp_path / "step1-toced.md"
    result = add_toc_to_markdown_logic(
        input_file=step1_input,
        output_file=step1_output,
        min_level=2,
        max_level=6,
        force=False
    )
    if result[0] != 0:
        print(f"ERREUR add-toc4md: {result}")
        sys.exit(1)
    print(f"\n=== ÉTAPE 1: add-toc4md ===")
    print(f"   Fichier: {step1_output}")
    print(f"   Taille: {step1_output.stat().st_size} bytes")
    
    # Étape 3: add-itoc4md
    step2_output = tmp_path / "step2-itoced.md"
    result = add_toc_backlinks_logic(
        input_file=step1_output,
        output_file=step2_output,
        min_level=2,
        max_level=6,
        force=False
    )
    if result[0] != 0:
        print(f"ERREUR add-itoc4md: {result}")
        sys.exit(1)
    print(f"\n=== ÉTAPE 2: add-itoc4md ===")
    print(f"   Fichier: {step2_output}")
    print(f"   Taille: {step2_output.stat().st_size} bytes")
    
    # Étape 4: Vérifier qu'on ne duplique pas en relançant add-toc4md
    step3_output = tmp_path / "step3-retoced.md"
    result = add_toc_to_markdown_logic(
        input_file=step2_output,
        output_file=step3_output,
        min_level=2,
        max_level=6,
        force=False
    )
    print(f"\n=== ÉTAPE 3: Re-add-toc4md (doit skipper) ===")
    print(f"   Résultat: {result}")
    
    # Étape 5: Vérifier qu'on ne duplique pas en relançant add-itoc4md  
    step4_output = tmp_path / "step4-reitoced.md"
    result = add_toc_backlinks_logic(
        input_file=step2_output,
        output_file=step4_output,
        min_level=2,
        max_level=6,
        force=False
    )
    print(f"\n=== ÉTAPE 4: Re-add-itoc4md (doit skipper) ===")
    print(f"   Résultat: {result}")
    
    # Vérifier le contenu
    print(f"\n=== VÉRIFICATIONS ===")
    
    with open(step2_output, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Compter les TOC
    toc_count = content.count("## Table des matières")
    print(f"   Nombre de '## Table des matières': {toc_count}")
    if toc_count > 1:
        print("   ⚠️ ATTENTION: TOC dupliquée!")
    else:
        print("   ✓ Une seule TOC")
    
    # Compter les backlinks
    backlink_count = content.count("[↑](#toc-")
    print(f"   Nombre de backlinks [↑](#toc-...): {backlink_count}")
    
    # Vérifier que les titres ont des backlinks
    lines = content.split('\n')
    h2_with_backlinks = 0
    h2_without_backlinks = 0
    for line in lines:
        if line.startswith('## ') and not 'Table des matières' in line:
            if '[↑](#toc-' in line:
                h2_with_backlinks += 1
            else:
                h2_without_backlinks += 1
    
    print(f"   H2 avec backlinks: {h2_with_backlinks}")
    print(f"   H2 sans backlinks: {h2_without_backlinks}")
    
    # Trouver la position de la TOC
    toc_pos = content.find("## Table des matières")
    h1_pos = content.find("# Dossier d'Architecture")
    intro_pos = content.find("## 1. Introduction")
    
    print(f"\n=== POSITIONS ===")
    print(f"   Position H1: {h1_pos}")
    print(f"   Position TOC: {toc_pos}")
    print(f"   Position Introduction (H2): {intro_pos}")
    
    if toc_pos > h1_pos and toc_pos < intro_pos:
        print("   ✓ TOC est entre H1 et le premier H2")
    else:
        print("   ⚠️ ATTENTION: TOC n'est pas au bon endroit!")
    
    # Copier le résultat final pour inspection
    final_output = Path("test_output_final.md")
    shutil.copy(step2_output, final_output)
    print(f"\n=== FICHIER FINAL ===")
    print(f"   Copié vers: {final_output.absolute()}")
    
    # Afficher les 30 premières lignes
    print(f"\n=== APERÇU (30 premières lignes) ===")
    lines = content.split('\n')[:30]
    for i, line in enumerate(lines, 1):
        print(f"{i:3}: {line}")
