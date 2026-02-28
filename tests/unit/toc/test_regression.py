"""
Tests de régression pour le module TOC
Ces tests vérifient que des bugs passés ne se reproduisent pas
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from app.toc.core.markdown_toc_generator import (
    add_toc_to_markdown_logic,
    remove_existing_toc,
)
from app.toc.core.markdown_itoc import (
    add_toc_backlinks_logic,
    remove_existing_backlinks,
)


class TestRegressionTocDuplication:
    """Régressions: duplication de TOC"""
    
    def test_no_toc_duplication_when_rerun_add_toc4md(self, tmp_path):
        """
        REGRESSION: Lancer add-toc4md sur un fichier ayant déjà une TOC HTML
        ne doit pas créer une deuxième TOC
        """
        source = tmp_path / "source.md"
        step1 = tmp_path / "step1.md"
        step2 = tmp_path / "step2.md"
        
        # Fichier avec une vraie TOC HTML (pas juste [TOC])
        source.write_text("""# Document
## Table des matières
<ul><li><a href="#section-1">Section 1</a></li></ul>
---
## Section 1
""", encoding='utf-8')
        
        # Premier passage - doit skipper car TOC HTML existe
        result = add_toc_to_markdown_logic(source, step1, min_level=2, max_level=6)
        content1 = step1.read_text(encoding='utf-8')
        assert content1.count("## Table des matières") == 1
        
        # Second passage sans --force (doit aussi skipper)
        result = add_toc_to_markdown_logic(step1, step2, min_level=2, max_level=6, force=False)
        content2 = step2.read_text(encoding='utf-8')
        
        # Pas de duplication
        assert content2.count("## Table des matières") == 1
    
    def test_toc_marker_gets_replaced_not_skipped(self, tmp_path):
        """
        REGRESSION: [TOC] doit être remplacé par la vraie TOC, pas skip
        """
        source = tmp_path / "source.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Document

[TOC]

## Section 1
""", encoding='utf-8')
        
        result = add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        content = output.read_text(encoding='utf-8')
        
        # [TOC] doit être remplacé
        assert "[TOC]" not in content
        assert "## Table des matières" in content
        assert '<a id="toc-section-1"></a>' in content
        assert '<a href="#section-1">Section 1</a>' in content
    
    def test_toc_heading_not_in_toc(self, tmp_path):
        """
        REGRESSION: Le titre "Table des matières" ne doit pas apparaître
        dans la TOC elle-même
        """
        source = tmp_path / "source.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Document
## Table des matières
### Section 1
## Sommaire
### Section 2
## Vraie Section
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        
        content = output.read_text(encoding='utf-8')
        # La TOC ne doit pas contenir de liens vers les titres de TOC
        assert 'href="#table-des-matieres"' not in content.lower()
        assert 'href="#sommaire"' not in content.lower()
        # Mais doit contenir la vraie section
        assert 'href="#vraie-section"' in content.lower()


class TestRegressionBacklinkDuplication:
    """Régressions: duplication des backlinks"""
    
    def test_no_backlink_duplication_when_rerun_add_itoc4md(self, tmp_path):
        """
        REGRESSION: Relancer add-itoc4md ne doit pas doubler les backlinks
        """
        source = tmp_path / "source.md"
        step1 = tmp_path / "step1.md"
        step2 = tmp_path / "step2.md"
        step3 = tmp_path / "step3.md"
        
        source.write_text("""# Document
## Section 1
""", encoding='utf-8')
        
        # add-toc4md
        add_toc_to_markdown_logic(source, step1, min_level=2, max_level=6)
        
        # Premier add-itoc4md
        add_toc_backlinks_logic(step1, step2, min_level=2, max_level=6)
        content2 = step2.read_text(encoding='utf-8')
        backlink_count_2 = content2.count("[↑](#toc-")
        assert backlink_count_2 == 1  # Un seul backlink
        
        # Second add-itoc4md sans --force
        add_toc_backlinks_logic(step2, step3, min_level=2, max_level=6, force=False)
        content3 = step3.read_text(encoding='utf-8')
        backlink_count_3 = content3.count("[↑](#toc-")
        
        # Pas de duplication
        assert backlink_count_3 == backlink_count_2
    
    def test_no_backlink_on_toc_heading(self, tmp_path):
        """
        REGRESSION: Le titre "Table des matières" ne doit pas avoir
        de backlink [↑]
        """
        source = tmp_path / "source.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        source.write_text("""# Document
## Section 1
## Section 2
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, toc_file, min_level=2, max_level=6)
        add_toc_backlinks_logic(toc_file, itoc_file, min_level=2, max_level=6)
        
        content = itoc_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Trouver la ligne "Table des matières"
        for line in lines:
            if '## Table des matières' in line:
                # Pas de backlink sur cette ligne
                assert '[↑]' not in line
                break
    
    def test_backlink_added_to_correct_headings(self, tmp_path):
        """
        REGRESSION: Les backlinks doivent être ajoutés à tous les titres
        concernés, pas seulement au premier
        """
        source = tmp_path / "source.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        source.write_text("""# Document
## Section 1
## Section 2
## Section 3
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, toc_file, min_level=2, max_level=6)
        add_toc_backlinks_logic(toc_file, itoc_file, min_level=2, max_level=6)
        
        content = itoc_file.read_text(encoding='utf-8')
        
        # Tous les titres doivent avoir leur backlink
        assert "[↑](#toc-section-1)" in content
        assert "[↑](#toc-section-2)" in content
        assert "[↑](#toc-section-3)" in content


class TestRegressionTocPosition:
    """Régressions: position de la TOC"""
    
    def test_toc_after_h1_and_metadata(self, tmp_path):
        """
        REGRESSION: La TOC doit être positionnée après le H1 et les
        métadonnées (Version, Date, etc.), pas au début du fichier
        """
        source = tmp_path / "source.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Titre Principal

**Version**: 1.0
**Date**: 2024-01-15
**Auteur**: Test

## Section 1
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        
        content = output.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        h1_idx = None
        toc_idx = None
        section_idx = None
        
        for i, line in enumerate(lines):
            if line.startswith('# Titre Principal'):
                h1_idx = i
            elif '## Table des matières' in line:
                toc_idx = i
            elif line.startswith('## Section 1'):
                section_idx = i
        
        assert h1_idx is not None
        assert toc_idx is not None
        assert section_idx is not None
        assert h1_idx < toc_idx < section_idx
    
    def test_toc_marker_replaced_in_place(self, tmp_path):
        """
        REGRESSION: Le marqueur [TOC] doit être remplacé à sa position
        exacte, pas déplacé
        """
        source = tmp_path / "source.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Titre

Texte avant.

[TOC]

Texte après.

## Section 1
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        
        content = output.read_text(encoding='utf-8')
        
        assert "[TOC]" not in content
        assert "## Table des matières" in content
        
        # La TOC doit être entre les deux textes
        assert content.find("Texte avant.") < content.find("## Table des matières")
        assert content.find("## Table des matières") < content.find("Texte après.")


class TestRegressionRemoveExisting:
    """Régressions: suppression du contenu existant"""
    
    def test_remove_toc_preserves_content(self, tmp_path):
        """
        REGRESSION: remove_existing_toc ne doit pas supprimer
        le contenu du document
        """
        content = """# Document

## Table des matières
<ul><li>Item</li></ul>
---

## Section 1

Important content here.

### Subsection

More content.
"""
        result = remove_existing_toc(content)
        
        assert "## Table des matières" not in result
        assert "<ul>" not in result
        assert "## Section 1" in result
        assert "Important content here." in result
        assert "### Subsection" in result
        assert "More content." in result
    
    def test_remove_backlinks_preserves_content(self, tmp_path):
        """
        REGRESSION: remove_existing_backlinks ne doit pas supprimer
        le contenu du document
        """
        content = """# Titre [↑](#toc-titre)

## Section 1 [↑](#toc-section-1)

Important content.

### Subsection [↑](#toc-subsection)

More content.
"""
        result = remove_existing_backlinks(content)
        
        assert "[↑]" not in result
        assert "# Titre" in result
        assert "## Section 1" in result
        assert "Important content." in result
        assert "### Subsection" in result
        assert "More content." in result


class TestRegressionCustomIds:
    """Régressions: gestion des IDs personnalisés"""
    
    def test_custom_id_preserved_in_toc(self, tmp_path):
        """
        REGRESSION: Les IDs personnalisés {#id} doivent être préservés
        dans les liens de la TOC
        """
        source = tmp_path / "source.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Document
## Section A {#ma-section}
## Section B {#autre-section}
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        
        content = output.read_text(encoding='utf-8')
        
        # Les liens doivent utiliser les IDs personnalisés
        assert 'href="#ma-section"' in content
        assert 'href="#autre-section"' in content
    
    def test_toc_id_generated_from_custom_id(self, tmp_path):
        """
        REGRESSION: Les liens toc-xxx doivent utiliser les IDs personnalisés
        """
        source = tmp_path / "source.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        source.write_text("""# Document
## Section A {#ma-section}
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, toc_file, min_level=2, max_level=6)
        add_toc_backlinks_logic(toc_file, itoc_file, min_level=2, max_level=6)
        
        content = itoc_file.read_text(encoding='utf-8')
        
        # Le backlink doit pointer vers toc-ma-section
        assert "[↑](#toc-ma-section)" in content


class TestRegressionEmptyAndEdgeCases:
    """Régressions: cas vides et limites"""
    
    def test_empty_document_no_crash(self, tmp_path):
        """
        REGRESSION: Document vide ne doit pas causer de crash
        """
        source = tmp_path / "empty.md"
        output = tmp_path / "output.md"
        
        source.write_text("", encoding='utf-8')
        
        result = add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        assert result[0] == 0
        assert output.exists()
    
    def test_no_headings_no_crash(self, tmp_path):
        """
        REGRESSION: Document sans titres ne doit pas causer de crash
        """
        source = tmp_path / "no_headings.md"
        output = tmp_path / "output.md"
        
        source.write_text("Juste du texte sans titres.", encoding='utf-8')
        
        result = add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        assert result[0] == 0
    
    def test_only_h1_no_toc(self, tmp_path):
        """
        REGRESSION: Document avec uniquement H1 ne doit pas avoir de TOC
        (car min_level=2 par défaut)
        """
        source = tmp_path / "only_h1.md"
        output = tmp_path / "output.md"
        
        source.write_text("""# Titre 1
# Titre 2
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(source, output, min_level=2, max_level=6)
        
        content = output.read_text(encoding='utf-8')
        # Pas de TOC car pas de H2+
        assert "## Table des matières" not in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
