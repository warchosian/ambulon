"""
Tests d'intégration pour le workflow complet TOC
Teste les scénarios réels d'utilisation
"""

import pytest
import tempfile
import shutil
from pathlib import Path

# Import des modules à tester
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from app.toc.core.markdown_toc_generator import add_toc_to_markdown_logic
from app.toc.core.markdown_itoc import add_toc_backlinks_logic


class TestFullWorkflow:
    """Tests du workflow complet: add-toc4md -> add-itoc4md"""
    
    def test_workflow_simple_document(self, tmp_path):
        """Workflow sur un document simple"""
        # Arrange
        source = tmp_path / "source.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        source.write_text("""# Mon Document

**Version**: 1.0

## Introduction

Voici l'introduction.

## Partie 1

Contenu de la partie 1.

### Détails

Détails importants.

## Conclusion

C'est fini.
""", encoding='utf-8')
        
        # Act - Étape 1: add-toc4md
        result1 = add_toc_to_markdown_logic(
            input_file=source,
            output_file=toc_file,
            min_level=2,
            max_level=6,
            force=False
        )
        
        # Assert - Étape 1
        assert result1[0] == 0
        toc_content = toc_file.read_text(encoding='utf-8')
        assert "## Table des matières" in toc_content
        assert '<a id="toc-introduction"></a>' in toc_content
        assert '<a href="#introduction">Introduction</a>' in toc_content
        
        # Act - Étape 2: add-itoc4md
        result2 = add_toc_backlinks_logic(
            input_file=toc_file,
            output_file=itoc_file,
            min_level=2,
            max_level=6,
            force=False
        )
        
        # Assert - Étape 2
        assert result2[0] == 0
        final_content = itoc_file.read_text(encoding='utf-8')
        
        # Vérifications finales
        assert final_content.count("## Table des matières") == 1
        assert "[↑](#toc-introduction)" in final_content
        assert "[↑](#toc-partie-1)" in final_content
        assert "[↑](#toc-details)" in final_content
        assert "[↑](#toc-conclusion)" in final_content
        # Pas de backlink sur le titre TOC lui-même
        assert "## Table des matières [↑]" not in final_content
    
    def test_workflow_with_toc_marker(self, tmp_path):
        """Workflow avec marqueur [TOC]"""
        source = tmp_path / "source.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        source.write_text("""# Document avec TOC

**Date**: 2024-01-15

[TOC]

## Section A

Texte A.

## Section B

Texte B.
""", encoding='utf-8')
        
        # add-toc4md
        add_toc_to_markdown_logic(source, toc_file, min_level=2, max_level=6)
        
        toc_content = toc_file.read_text(encoding='utf-8')
        assert "[TOC]" not in toc_content  # Marqueur remplacé
        assert "## Table des matières" in toc_content
        # La TOC doit être à la place du marqueur
        assert toc_content.find("## Table des matières") < toc_content.find("## Section A")
        
        # add-itoc4md
        add_toc_backlinks_logic(toc_file, itoc_file, min_level=2, max_level=6)
        
        final_content = itoc_file.read_text(encoding='utf-8')
        assert "[↑](#toc-section-a)" in final_content
        assert "[↑](#toc-section-b)" in final_content
    
    def test_no_duplication_on_multiple_runs(self, tmp_path):
        """Pas de duplication si on relance plusieurs fois"""
        source = tmp_path / "source.md"
        step1 = tmp_path / "step1.md"
        step2 = tmp_path / "step2.md"
        step3 = tmp_path / "step3.md"
        step4 = tmp_path / "step4.md"
        
        source.write_text("""# Document
## Section 1
## Section 2
""", encoding='utf-8')
        
        # Premier passage
        add_toc_to_markdown_logic(source, step1, min_level=2, max_level=6)
        add_toc_backlinks_logic(step1, step2, min_level=2, max_level=6)
        
        content2 = step2.read_text(encoding='utf-8')
        toc_count_2 = content2.count("## Table des matières")
        backlink_count_2 = content2.count("[↑](#toc-")
        
        # Second passage (doit skipper)
        add_toc_to_markdown_logic(step2, step3, min_level=2, max_level=6, force=False)
        add_toc_backlinks_logic(step2, step4, min_level=2, max_level=6, force=False)
        
        content3 = step3.read_text(encoding='utf-8')
        content4 = step4.read_text(encoding='utf-8')
        
        # Pas de duplication
        assert content3.count("## Table des matières") == toc_count_2
        assert content4.count("[↑](#toc-") == backlink_count_2
    
    def test_force_option(self, tmp_path):
        """Option --force pour forcer le remplacement"""
        source = tmp_path / "source.md"
        toc1 = tmp_path / "toc1.md"
        toc2 = tmp_path / "toc2.md"
        
        source.write_text("""# Document
## Section Ancienne
""", encoding='utf-8')
        
        # Première passe
        add_toc_to_markdown_logic(source, toc1, min_level=2, max_level=6)
        
        # Modification du document source
        source.write_text("""# Document
## Section Nouvelle
### Sous-section
""", encoding='utf-8')
        
        # Force avec nouveau contenu
        add_toc_to_markdown_logic(source, toc2, min_level=2, max_level=6, force=True)
        
        content2 = toc2.read_text(encoding='utf-8')
        assert "## Section Nouvelle" in content2
        assert "### Sous-section" in content2
        assert "## Table des matières" in content2
    
    def test_with_existing_custom_ids(self, tmp_path):
        """Gestion des IDs personnalisés existants"""
        source = tmp_path / "source.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        source.write_text("""# Titre {#mon-titre}

## Section A {#section-a}

Texte.

## Section B {#section-b}

Texte.
""", encoding='utf-8')
        
        # add-toc4md
        add_toc_to_markdown_logic(source, toc_file, min_level=2, max_level=6)
        
        toc_content = toc_file.read_text(encoding='utf-8')
        # La TOC doit utiliser les IDs personnalisés
        assert '<a href="#section-a">Section A</a>' in toc_content
        assert '<a href="#section-b">Section B</a>' in toc_content
        
        # add-itoc4md
        add_toc_backlinks_logic(toc_file, itoc_file, min_level=2, max_level=6)
        
        final_content = itoc_file.read_text(encoding='utf-8')
        # Les backlinks doivent pointer vers les IDs toc-xxx
        assert "[↑](#toc-section-a)" in final_content
        assert "[↑](#toc-section-b)" in final_content
    
    def test_level_filtering(self, tmp_path):
        """Filtrage par niveau de titre"""
        source = tmp_path / "source.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        source.write_text("""# Document
## Niveau 2
### Niveau 3
#### Niveau 4
##### Niveau 5
""", encoding='utf-8')
        
        # Niveaux 2-4 uniquement
        add_toc_to_markdown_logic(source, toc_file, min_level=2, max_level=4)
        
        toc_content = toc_file.read_text(encoding='utf-8')
        assert "Niveau 2" in toc_content
        assert "Niveau 3" in toc_content
        assert "Niveau 4" in toc_content
        assert "Niveau 5" not in toc_content  # Exclu
        
        add_toc_backlinks_logic(toc_file, itoc_file, min_level=2, max_level=4)
        
        final_content = itoc_file.read_text(encoding='utf-8')
        assert "[↑](#toc-niveau-2)" in final_content
        assert "[↑](#toc-niveau-3)" in final_content
        assert "[↑](#toc-niveau-4)" in final_content
        assert "[↑](#toc-niveau-5)" not in final_content


class TestEdgeCases:
    """Cas limites et erreurs"""
    
    def test_empty_file(self, tmp_path):
        """Fichier vide"""
        source = tmp_path / "empty.md"
        output = tmp_path / "output.md"
        
        source.write_text("", encoding='utf-8')
        
        result = add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        assert result[0] == 0
        assert output.exists()
    
    def test_no_headings(self, tmp_path):
        """Fichier sans titres"""
        source = tmp_path / "no_headings.md"
        output = tmp_path / "output.md"
        
        source.write_text("Juste du texte sans titres.", encoding='utf-8')
        
        result = add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        assert result[0] == 0
        
        content = output.read_text(encoding='utf-8')
        assert "## Table des matières" not in content
    
    def test_only_h1_headings(self, tmp_path):
        """Uniquement des titres H1"""
        source = tmp_path / "only_h1.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Titre 1
# Titre 2
""", encoding='utf-8')
        
        result = add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        assert result[0] == 0
        
        content = output.read_text(encoding='utf-8')
        # Pas de TOC car pas de H2+
        assert "## Table des matières" not in content
    
    def test_special_characters_in_headings(self, tmp_path):
        """Caractères spéciaux dans les titres"""
        source = tmp_path / "special.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Document
## Café & Thé 100%
## Code: `variable`
## Emoji 🎉
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        
        content = output.read_text(encoding='utf-8')
        assert "## Table des matières" in content
        # Les titres doivent être présents
        assert "Café &amp; Thé 100%" in content or "Café" in content
    
    def test_very_long_document(self, tmp_path):
        """Document très long (performance)"""
        source = tmp_path / "long.md"
        output = tmp_path / "output.md"
        
        # Créer un document avec 100 sections
        lines = ["# Document Principal", ""]
        for i in range(100):
            lines.append(f"## Section {i}")
            lines.append("")
            lines.append(f"Contenu de la section {i}.")
            lines.append("")
        
        source.write_text("\n".join(lines), encoding='utf-8')
        
        import time
        start = time.time()
        
        add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        
        elapsed = time.time() - start
        
        # Doit se terminer en moins de 5 secondes
        assert elapsed < 5.0
        
        content = output.read_text(encoding='utf-8')
        assert content.count("<li>") >= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
