"""
Tests unitaires pour markdown_toc_generator.py
Couvre: add_toc4md, generate_toc_markdown, extract_headings, etc.
"""

import pytest
from pathlib import Path
from src.app.toc.core.markdown_toc_generator import (
    extract_headings,
    generate_id,
    generate_toc_markdown,
    add_anchors_to_headings,
    remove_existing_toc,
    is_toc_heading,
    add_toc_to_markdown_logic,
)


class TestExtractHeadings:
    """Tests pour extract_headings()"""
    
    def test_extract_basic_headings(self):
        """Extraction basique des titres"""
        content = """# Titre 1
## Section 1.1
### Section 1.1.1
## Section 1.2
# Titre 2
"""
        headings = extract_headings(content)
        assert len(headings) == 5
        assert headings[0]['text'] == "Titre 1"
        assert headings[0]['level'] == 1
        assert headings[1]['text'] == "Section 1.1"
        assert headings[1]['level'] == 2
    
    def test_extract_with_custom_ids(self):
        """Extraction avec IDs personnalisés {#id}"""
        content = """# Titre Principal {#mon-titre}
## Section A {#section-a}
"""
        headings = extract_headings(content)
        assert len(headings) == 2
        assert headings[0]['custom_id'] == "mon-titre"
        assert headings[1]['custom_id'] == "section-a"
    
    def test_exclude_toc_headings(self):
        """Les titres 'Table des matières' doivent être exclus"""
        content = """# Document
## Table des matières
### Section 1
## Table of Contents
### Section 2
## Sommaire
### Section 3
## Vrai Section
"""
        headings = extract_headings(content)
        assert len(headings) == 2  # Seulement "Document" et "Vrai Section"
        assert headings[0]['text'] == "Document"
        assert headings[1]['text'] == "Vrai Section"
    
    def test_empty_content(self):
        """Contenu vide"""
        assert extract_headings("") == []
    
    def test_no_headings(self):
        """Pas de titres"""
        content = "Juste du texte\nsans titres"
        assert extract_headings(content) == []


class TestGenerateId:
    """Tests pour generate_id()"""
    
    def test_basic_id_generation(self):
        """Génération basique d'ID"""
        existing = set()
        assert generate_id("Hello World", existing) == "hello-world"
        assert "hello-world" in existing
    
    def test_id_with_special_chars(self):
        """ID avec caractères spéciaux"""
        existing = set()
        assert generate_id("Café & Thé 100%", existing) == "caf-th-100"
    
    def test_unique_id_collision(self):
        """Gestion des collisions d'ID"""
        existing = {"hello-world"}
        assert generate_id("Hello World", existing) == "hello-world-1"
        assert "hello-world-1" in existing
        
        # Troisième collision
        assert generate_id("Hello World", existing) == "hello-world-2"


class TestIsTocHeading:
    """Tests pour is_toc_heading()"""
    
    @pytest.mark.parametrize("text", [
        "Table des matières",
        "Table des matieres",
        "Table of Contents",
        "SOMMAIRE",
        "sommaire",
        "  Table des matières  ",
    ])
    def test_toc_headings(self, text):
        """Détection des titres de TOC"""
        assert is_toc_heading(text) is True
    
    @pytest.mark.parametrize("text", [
        "Introduction",
        "Conclusion",
        "Tableau des données",
        "Matières premières",
    ])
    def test_non_toc_headings(self, text):
        """Rejet des faux positifs"""
        assert is_toc_heading(text) is False


class TestRemoveExistingToc:
    """Tests pour remove_existing_toc()"""
    
    def test_remove_toc_marker(self):
        """Suppression du marqueur [TOC]"""
        content = """# Titre
[TOC]
## Section
"""
        result = remove_existing_toc(content, keep_toc_marker=False)
        assert "[TOC]" not in result
        assert "# Titre" in result
        assert "## Section" in result
    
    def test_keep_toc_marker(self):
        """Préservation du marqueur [TOC]"""
        content = """# Titre
[TOC]
## Section
"""
        result = remove_existing_toc(content, keep_toc_marker=True)
        assert "[TOC]" in result
    
    def test_remove_html_toc(self):
        """Suppression de la TOC HTML"""
        content = """# Titre
## Table des matières
<ul>
<li><a href="#section">Section</a></li>
</ul>
---
## Section
"""
        result = remove_existing_toc(content)
        assert "## Table des matières" not in result
        assert "<ul>" not in result
        assert "## Section" in result
    
    def test_remove_toc_anchors(self):
        """Suppression des ancres toc-xxx"""
        content = """# Titre
<a id="toc-section"></a>
## Section
<a id="section"></a>
"""
        result = remove_existing_toc(content)
        assert '<a id="toc-section"></a>' not in result
        assert '<a id="section"></a>' in result  # Ancre normale préservée


class TestGenerateTocMarkdown:
    """Tests pour generate_toc_markdown()"""
    
    def test_basic_toc_generation(self):
        """Génération basique de TOC"""
        headings = [
            {'level': 2, 'text': 'Section 1', 'id': 'section-1'},
            {'level': 3, 'text': 'Subsection', 'id': 'subsection'},
            {'level': 2, 'text': 'Section 2', 'id': 'section-2'},
        ]
        toc = generate_toc_markdown(headings, min_level=2, max_level=6)
        
        assert "## Table des matières" in toc
        assert '<a id="toc-section-1"></a>' in toc
        assert '<a href="#section-1">Section 1</a>' in toc
        assert "<ul>" in toc
        assert "</ul>" in toc
    
    def test_toc_respects_min_max_level(self):
        """Respect des niveaux min/max"""
        headings = [
            {'level': 1, 'text': 'H1', 'id': 'h1'},
            {'level': 2, 'text': 'H2', 'id': 'h2'},
            {'level': 3, 'text': 'H3', 'id': 'h3'},
            {'level': 4, 'text': 'H4', 'id': 'h4'},
        ]
        toc = generate_toc_markdown(headings, min_level=2, max_level=3)
        
        assert 'h1' not in toc  # Exclu par min_level
        assert 'h2' in toc
        assert 'h3' in toc
        assert 'h4' not in toc  # Exclu par max_level
    
    def test_empty_headings(self):
        """Liste de titres vide"""
        assert generate_toc_markdown([]) == ""


class TestAddAnchorsToHeadings:
    """Tests pour add_anchors_to_headings()"""
    
    def test_add_anchors(self):
        """Ajout d'ancres aux titres"""
        content = """# Titre Principal
## Section 1
### Subsection
"""
        headings = [
            {'level': 1, 'text': 'Titre Principal', 'id': 'titre-principal'},
            {'level': 2, 'text': 'Section 1', 'id': 'section-1'},
            {'level': 3, 'text': 'Subsection', 'id': 'subsection'},
        ]
        result = add_anchors_to_headings(content, headings)
        
        assert '<a id="titre-principal"></a>' in result
        assert '<a id="section-1"></a>' in result
        assert '<a id="subsection"></a>' in result
    
    def test_skip_custom_ids(self):
        """Pas d'ancres pour les titres avec ID personnalisé"""
        content = """# Titre {#mon-id}
## Section
"""
        headings = [
            {'level': 1, 'text': 'Titre', 'id': 'mon-id', 'custom_id': 'mon-id'},
            {'level': 2, 'text': 'Section', 'id': 'section'},
        ]
        result = add_anchors_to_headings(content, headings)
        
        # Pas d'ancre ajoutée avant le titre avec custom_id
        lines = result.split('\n')
        titre_idx = [i for i, l in enumerate(lines) if '# Titre' in l][0]
        assert '<a id="mon-id"></a>' not in result


class TestAddTocToMarkdownLogic:
    """Tests d'intégration pour add_toc_to_markdown_logic()"""
    
    def test_add_toc_to_new_file(self, tmp_path):
        """Ajout de TOC à un nouveau fichier"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Mon Document

## Section 1
Texte

## Section 2
Texte
""", encoding='utf-8')
        
        exit_code, path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6
        )
        
        assert exit_code == 0
        assert path == output_file
        assert output_file.exists()
        
        content = output_file.read_text(encoding='utf-8')
        assert "## Table des matières" in content
        assert '<a href="#section-1">Section 1</a>' in content
    
    def test_skip_existing_html_toc(self, tmp_path):
        """Skip si une vraie TOC HTML existe déjà (pas [TOC])"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document
## Table des matières
<ul><li>Item</li></ul>
---
## Section
""", encoding='utf-8')
        
        exit_code, path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6,
            force=False
        )
        
        assert exit_code == 0
        # Ne doit pas doubler la TOC
        content = output_file.read_text(encoding='utf-8')
        assert content.count("## Table des matières") == 1
    
    def test_replace_toc_marker(self, tmp_path):
        """[TOC] doit être remplacé par la vraie TOC (pas skip)"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document

[TOC]

## Section 1
""", encoding='utf-8')
        
        exit_code, path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6,
            force=False
        )
        
        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')
        # [TOC] doit être remplacé
        assert "[TOC]" not in content
        assert "## Table des matières" in content
        assert '<a href="#section-1">Section 1</a>' in content
    
    def test_force_replace_toc(self, tmp_path):
        """Remplacer la TOC existante avec --force"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Document
## Table des matières
<ul><li>Ancienne TOC</li></ul>
---
## Section 1
""", encoding='utf-8')
        
        exit_code, path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6,
            force=True
        )
        
        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')
        assert "## Table des matières" in content
        assert "Ancienne TOC" not in content  # Ancienne TOC remplacée
    
    def test_toc_position_after_h1(self, tmp_path):
        """La TOC doit être positionnée après le H1"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Titre Principal
**Version**: 1.0
**Date**: 2024

## Section 1
Texte
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6
        )
        
        content = output_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        h1_idx = [i for i, l in enumerate(lines) if l.startswith('# Titre Principal')][0]
        toc_idx = [i for i, l in enumerate(lines) if '## Table des matières' in l][0]
        section_idx = [i for i, l in enumerate(lines) if l.startswith('## Section 1')][0]
        
        assert h1_idx < toc_idx < section_idx
    
    def test_toc_replaces_toc_marker(self, tmp_path):
        """Le marqueur [TOC] doit être remplacé"""
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        
        input_file.write_text("""# Titre

[TOC]

## Section 1
""", encoding='utf-8')
        
        add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=6
        )
        
        content = output_file.read_text(encoding='utf-8')
        assert "[TOC]" not in content
        assert "## Table des matières" in content


class TestTocWithAddItoc4md:
    """Tests d'intégration entre add-toc4md et add-itoc4md"""
    
    def test_workflow_toc_then_itoc(self, tmp_path):
        """Workflow complet: add-toc4md puis add-itoc4md"""
        from src.app.toc.core.markdown_itoc import add_toc_backlinks_logic
        
        input_file = tmp_path / "input.md"
        toc_file = tmp_path / "toced.md"
        itoc_file = tmp_path / "itoced.md"
        
        input_file.write_text("""# Document

## Section 1
### Subsection 1.1
## Section 2
""", encoding='utf-8')
        
        # Étape 1: add-toc4md
        result1 = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=toc_file,
            min_level=2,
            max_level=6
        )
        assert result1[0] == 0
        
        # Étape 2: add-itoc4md
        result2 = add_toc_backlinks_logic(
            input_file=toc_file,
            output_file=itoc_file,
            min_level=2,
            max_level=6
        )
        assert result2[0] == 0
        
        content = itoc_file.read_text(encoding='utf-8')
        
        # Vérifications
        assert content.count("## Table des matières") == 1  # Pas de duplication
        assert "[↑](#toc-section-1)" in content  # Backlink présent
        assert "[↑](#toc-table-des-matieres)" not in content  # Pas de backlink sur TOC
    
    def test_no_duplicate_on_rerun(self, tmp_path):
        """Pas de duplication si on relance les commandes"""
        from src.app.toc.core.markdown_itoc import add_toc_backlinks_logic
        
        input_file = tmp_path / "input.md"
        step1 = tmp_path / "step1.md"
        step2 = tmp_path / "step2.md"
        step3 = tmp_path / "step3.md"
        step4 = tmp_path / "step4.md"
        
        input_file.write_text("""# Document
## Section 1
""", encoding='utf-8')
        
        # Premier passage
        add_toc_to_markdown_logic(input_file, step1, min_level=2, max_level=6)
        add_toc_backlinks_logic(step1, step2, min_level=2, max_level=6)
        
        # Second passage (doit skipper)
        add_toc_to_markdown_logic(step2, step3, min_level=2, max_level=6, force=False)
        add_toc_backlinks_logic(step2, step4, min_level=2, max_level=6, force=False)
        
        content3 = step3.read_text(encoding='utf-8')
        content4 = step4.read_text(encoding='utf-8')
        
        assert content3.count("## Table des matières") == 1
        assert content4.count("[↑](#toc-") == content2.count("[↑](#toc-")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
