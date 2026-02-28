"""
Tests unitaires pour markdown_itoc.py
Couvre: add_itoc4md, add_backlinks_to_headings, detect_itoc_links, etc.
"""

import pytest
from pathlib import Path
from src.app.toc.core.markdown_itoc import (
    extract_headings_with_positions,
    add_backlinks_to_headings,
    remove_existing_backlinks,
    is_toc_heading,
    add_toc_backlinks_logic,
)
from src.app.toc.core.markdown_itoc_checker import detect_itoc_links


class TestExtractHeadingsWithPositions:
    """Tests pour extract_headings_with_positions()"""
    
    def test_extract_basic(self):
        """Extraction basique avec positions"""
        content = """# Titre 1
Ligne 2
## Section 1
Ligne 4
### Subsection
"""
        headings = extract_headings_with_positions(content)
        assert len(headings) == 3
        assert headings[0] == {'level': 1, 'text': 'Titre 1', 'line': 0, 'original_line': '# Titre 1'}
        assert headings[1] == {'level': 2, 'text': 'Section 1', 'line': 2, 'original_line': '## Section 1'}
        assert headings[2] == {'level': 3, 'text': 'Subsection', 'line': 4, 'original_line': '### Subsection'}
    
    def test_extract_with_custom_ids(self):
        """Extraction avec IDs personnalisés"""
        content = """# Titre {#mon-id}
## Section {#section-id}
"""
        headings = extract_headings_with_positions(content)
        assert len(headings) == 2
        assert headings[0]['text'] == "Titre"
        assert headings[1]['text'] == "Section"
    
    def test_exclude_toc_headings(self):
        """Les titres de TOC doivent être exclus"""
        content = """# Document
## Table des matières
## Section 1
## Sommaire
## Section 2
"""
        headings = extract_headings_with_positions(content)
        assert len(headings) == 3  # Document, Section 1, Section 2
        assert headings[0]['text'] == "Document"
        assert headings[1]['text'] == "Section 1"
        assert headings[2]['text'] == "Section 2"
    
    def test_empty_content(self):
        """Contenu vide"""
        assert extract_headings_with_positions("") == []


class TestIsTocHeading:
    """Tests pour is_toc_heading()"""
    
    @pytest.mark.parametrize("text", [
        "Table des matières",
        "Table of Contents",
        "SOMMAIRE",
        "Sommaire",
    ])
    def test_toc_variants(self, text):
        """Variantes reconnues comme TOC"""
        assert is_toc_heading(text) is True
    
    @pytest.mark.parametrize("text", [
        "Introduction",
        "Tableau récapitulatif",
        "Matières premières",
    ])
    def test_not_toc(self, text):
        """Non-TOC"""
        assert is_toc_heading(text) is False


class TestRemoveExistingBacklinks:
    """Tests pour remove_existing_backlinks()"""
    
    def test_remove_backlinks(self):
        """Suppression des backlinks"""
        content = """# Titre
## Section 1 [↑](#toc-section-1)
### Subsection [↑](#toc-subsection)
"""
        result = remove_existing_backlinks(content)
        assert "[↑](#toc-section-1)" not in result
        assert "[↑](#toc-subsection)" not in result
        assert "## Section 1" in result
        assert "### Subsection" in result
    
    def test_no_backlinks_to_remove(self):
        """Pas de backlinks à supprimer"""
        content = """# Titre
## Section 1
### Subsection
"""
        result = remove_existing_backlinks(content)
        assert result == content


class TestDetectItocLinks:
    """Tests pour detect_itoc_links()"""
    
    def test_detect_no_links(self):
        """Aucun lien détecté"""
        content = """# Titre
## Section 1
### Subsection
"""
        result = detect_itoc_links(content)
        assert result['has_itoc_links'] is False
        assert result['itoc_count'] == 0
        assert result['total_headings'] == 3
    
    def test_detect_links(self):
        """Liens détectés"""
        content = """# Titre [↑](#toc-titre)
## Section 1 [↑](#toc-section-1)
### Subsection
"""
        result = detect_itoc_links(content)
        assert result['has_itoc_links'] is True
        assert result['itoc_count'] == 2
        assert result['total_headings'] == 3
        assert len(result['headings_with_itoc']) == 2
        assert len(result['headings_without_itoc']) == 1
    
    def test_detect_all_headings_have_links(self):
        """Tous les titres ont des liens"""
        content = """# Titre [↑](#toc-titre)
## Section 1 [↑](#toc-section-1)
"""
        result = detect_itoc_links(content)
        assert result['has_itoc_links'] is True
        assert result['itoc_count'] == result['total_headings']
        assert len(result['headings_without_itoc']) == 0


class TestAddBacklinksToHeadings:
    """Tests pour add_backlinks_to_headings()"""
    
    def test_add_basic_backlinks(self):
        """Ajout basique de backlinks"""
        content = """# Titre Principal
## Section 1
### Subsection
"""
        headings = [
            {'level': 1, 'text': 'Titre Principal', 'line': 0, 'original_line': '# Titre Principal'},
            {'level': 2, 'text': 'Section 1', 'line': 1, 'original_line': '## Section 1'},
            {'level': 3, 'text': 'Subsection', 'line': 2, 'original_line': '### Subsection'},
        ]
        result = add_backlinks_to_headings(content, headings)
        
        assert "[↑](#toc-titre-principal)" in result
        assert "[↑](#toc-section-1)" in result
        assert "[↑](#toc-subsection)" in result
    
    def test_add_with_custom_ids(self):
        """Ajout avec IDs personnalisés"""
        content = """# Titre {#mon-titre}
## Section {#ma-section}
"""
        headings = [
            {'level': 1, 'text': 'Titre', 'line': 0, 'original_line': '# Titre {#mon-titre}'},
            {'level': 2, 'text': 'Section', 'line': 1, 'original_line': '## Section {#ma-section}'},
        ]
        result = add_backlinks_to_headings(content, headings)
        
        # Les backlinks utilisent l'ID personnalisé
        assert "[↑](#toc-mon-titre)" in result
        assert "[↑](#toc-ma-section)" in result
        # Le lien est inséré AVANT l'ID personnalisé
        assert "[↑](#toc-mon-titre) {#mon-titre}" in result
    
    def test_skip_existing_backlinks(self):
        """Pas de duplication des backlinks existants"""
        content = """# Titre [↑](#toc-titre)
## Section 1
"""
        headings = [
            {'level': 1, 'text': 'Titre', 'line': 0, 'original_line': '# Titre [↑](#toc-titre)'},
            {'level': 2, 'text': 'Section 1', 'line': 1, 'original_line': '## Section 1'},
        ]
        result = add_backlinks_to_headings(content, headings)
        
        # Un seul backlink sur le titre (pas de duplication)
        assert result.count("[↑](#toc-titre)") == 1
        # Section 1 a son backlink
        assert "[↑](#toc-section-1)" in result


class TestAddTocBacklinksLogic:
    """Tests d'intégration pour add_toc_backlinks_logic()"""
    
    def test_add_backlinks_to_new_file(self, tmp_path):
        """Ajout de backlinks à un nouveau fichier"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Mon Document

## Section 1
Texte

## Section 2
Texte
""", encoding='utf-8')
        
        exit_code, path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6,
            force=False
        )
        
        assert exit_code == 0
        assert path == output_file
        
        content = output_file.read_text(encoding='utf-8')
        assert "[↑](#toc-section-1)" in content
        assert "[↑](#toc-section-2)" in content
    
    def test_skip_existing_backlinks(self, tmp_path):
        """Skip si backlinks existent déjà"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document
## Section 1 [↑](#toc-section-1)
""", encoding='utf-8')
        
        exit_code, path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6,
            force=False
        )
        
        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')
        assert content.count("[↑](#toc-section-1)") == 1
    
    def test_force_replace_backlinks(self, tmp_path):
        """Remplacer avec --force"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document
## Section 1 [↑](#toc-old-id)
""", encoding='utf-8')
        
        exit_code, path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6,
            force=True
        )
        
        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')
        # Ancien ID remplacé
        assert "[↑](#toc-old-id)" not in content
        assert "[↑](#toc-section-1)" in content
    
    def test_respects_min_max_level(self, tmp_path):
        """Respect des niveaux min/max"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document
## Section 1
### Subsection
#### Detail
""", encoding='utf-8')
        
        add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=3,
            force=False
        )
        
        content = output_file.read_text(encoding='utf-8')
        assert "[↑](#toc-section-1)" in content  # Niveau 2
        assert "[↑](#toc-subsection)" in content  # Niveau 3
        assert "[↑](#toc-detail)" not in content  # Niveau 4 exclu
    
    def test_no_backlinks_on_toc_heading(self, tmp_path):
        """Pas de backlink sur le titre de TOC"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document
## Table des matières
<ul><li>Item</li></ul>
## Section 1
""", encoding='utf-8')
        
        add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6,
            force=False
        )
        
        content = output_file.read_text(encoding='utf-8')
        # Pas de backlink sur "Table des matières"
        assert "## Table des matières [↑]" not in content
        assert "## Table des matières\n" in content or "## Table des matières\r\n" in content
        # Backlink sur Section 1
        assert "[↑](#toc-section-1)" in content


class TestTocWorkflowIntegration:
    """Tests d'intégration du workflow complet"""
    
    def test_no_duplicate_backlinks_on_rerun(self, tmp_path):
        """Pas de duplication des backlinks si on relance"""
        step1 = tmp_path / "step1.md"
        step2 = tmp_path / "step2.md"
        step3 = tmp_path / "step3.md"
        
        step1.write_text("""# Document
## Section 1
""", encoding='utf-8')
        
        # Premier passage
        add_toc_backlinks_logic(step1, step2, min_level=2, max_level=6, force=False)
        
        # Second passage
        add_toc_backlinks_logic(step2, step3, min_level=2, max_level=6, force=False)
        
        content2 = step2.read_text(encoding='utf-8')
        content3 = step3.read_text(encoding='utf-8')
        
        # Même nombre de backlinks
        assert content2.count("[↑](#toc-") == content3.count("[↑](#toc-")
    
    def test_filter_by_level(self, tmp_path):
        """Filtrage par niveau de titre"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document
## H2
### H3
#### H4
##### H5
""", encoding='utf-8')
        
        add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=3,
            max_level=4,
            force=False
        )
        
        content = output_file.read_text(encoding='utf-8')
        assert "[↑](#toc-h2)" not in content  # Niveau 2 exclu
        assert "[↑](#toc-h3)" in content     # Niveau 3 inclus
        assert "[↑](#toc-h4)" in content     # Niveau 4 inclus
        assert "[↑](#toc-h5)" not in content  # Niveau 5 exclu


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
