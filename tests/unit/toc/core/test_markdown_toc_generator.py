"""
Tests unitaires pour markdown_toc_generator.py
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from app.toc.core.markdown_toc_generator import (
    extract_headings,
    generate_id,
    generate_toc_markdown,
    add_anchors_to_headings,
    add_toc_to_markdown_logic
)


class TestExtractHeadings:
    """Tests pour extract_headings()"""

    def test_extract_simple_headings(self):
        """Test extraction de titres simples"""
        content = """# Titre 1
## Titre 2
### Titre 3
"""
        headings = extract_headings(content)
        assert len(headings) == 3
        assert headings[0]['level'] == 1
        assert headings[0]['text'] == 'Titre 1'
        assert headings[1]['level'] == 2
        assert headings[1]['text'] == 'Titre 2'
        assert headings[2]['level'] == 3
        assert headings[2]['text'] == 'Titre 3'

    def test_extract_headings_with_custom_id(self):
        """Test extraction avec ID personnalisés"""
        content = """# Titre Principal {#main-title}
## Section A {#section-a}
"""
        headings = extract_headings(content)
        assert len(headings) == 2
        assert headings[0]['custom_id'] == 'main-title'
        assert headings[1]['custom_id'] == 'section-a'

    def test_extract_no_headings(self):
        """Test extraction sans titres"""
        content = "Juste du texte sans titres."
        headings = extract_headings(content)
        assert len(headings) == 0

    def test_extract_headings_mixed_levels(self):
        """Test extraction avec niveaux mixtes"""
        content = """# H1
#### H4
## H2
"""
        headings = extract_headings(content)
        assert len(headings) == 3
        assert headings[0]['level'] == 1
        assert headings[1]['level'] == 4
        assert headings[2]['level'] == 2


class TestGenerateId:
    """Tests pour generate_id()"""

    def test_generate_simple_id(self):
        """Test génération ID simple"""
        existing_ids = set()
        id_result = generate_id("My Title", existing_ids)
        assert id_result == "my-title"
        assert "my-title" in existing_ids

    def test_generate_id_with_special_chars(self):
        """Test génération ID avec caractères spéciaux"""
        existing_ids = set()
        id_result = generate_id("Title: With (Special) Chars!", existing_ids)
        assert id_result == "title-with-special-chars"

    def test_generate_id_uniqueness(self):
        """Test unicité des IDs générés"""
        existing_ids = set()
        id1 = generate_id("Same Title", existing_ids)
        id2 = generate_id("Same Title", existing_ids)
        assert id1 == "same-title"
        assert id2 == "same-title-1"
        assert len(existing_ids) == 2

    def test_generate_id_multiple_duplicates(self):
        """Test génération avec multiples doublons"""
        existing_ids = set()
        id1 = generate_id("Test", existing_ids)
        id2 = generate_id("Test", existing_ids)
        id3 = generate_id("Test", existing_ids)
        assert id1 == "test"
        assert id2 == "test-1"
        assert id3 == "test-2"


class TestGenerateTocMarkdown:
    """Tests pour generate_toc_markdown()"""

    def test_generate_simple_toc(self):
        """Test génération TOC simple"""
        headings = [
            {'level': 1, 'text': 'Title 1', 'id': 'title-1'},
            {'level': 2, 'text': 'Title 2', 'id': 'title-2'},
        ]
        toc = generate_toc_markdown(headings)
        assert '## Table des matières' in toc
        assert '[Title 1](#title-1)' in toc
        assert '[Title 2](#title-2)' in toc

    def test_generate_toc_with_level_filtering(self):
        """Test génération TOC avec filtrage de niveaux"""
        headings = [
            {'level': 1, 'text': 'H1', 'id': 'h1'},
            {'level': 2, 'text': 'H2', 'id': 'h2'},
            {'level': 3, 'text': 'H3', 'id': 'h3'},
        ]
        toc = generate_toc_markdown(headings, min_level=2, max_level=2)
        assert '[H1](#h1)' not in toc
        assert '[H2](#h2)' in toc
        assert '[H3](#h3)' not in toc

    def test_generate_empty_toc(self):
        """Test génération TOC vide"""
        toc = generate_toc_markdown([])
        assert toc == ""

    def test_generate_toc_with_indentation(self):
        """Test indentation correcte dans la TOC"""
        headings = [
            {'level': 1, 'text': 'H1', 'id': 'h1'},
            {'level': 2, 'text': 'H2', 'id': 'h2'},
            {'level': 3, 'text': 'H3', 'id': 'h3'},
        ]
        toc = generate_toc_markdown(headings)
        lines = toc.split('\n')
        # Vérifier l'indentation (H2 et H3 doivent être indentés)
        h2_line = [l for l in lines if 'H2' in l][0]
        h3_line = [l for l in lines if 'H3' in l][0]
        assert h2_line.startswith('  ')  # 2 espaces pour level 2
        assert h3_line.startswith('    ')  # 4 espaces pour level 3


class TestAddAnchorsToHeadings:
    """Tests pour add_anchors_to_headings()"""

    def test_add_anchors_simple(self):
        """Test ajout d'ancres simples"""
        content = """# Titre 1
Du texte
## Titre 2
"""
        headings = [
            {'level': 1, 'text': 'Titre 1', 'id': 'titre-1', 'line': 0},
            {'level': 2, 'text': 'Titre 2', 'id': 'titre-2', 'line': 2},
        ]
        result = add_anchors_to_headings(content, headings)
        assert '<a id="titre-1"></a>' in result
        assert '<a id="titre-2"></a>' in result

    def test_add_anchors_skip_custom_ids(self):
        """Test que les ancres ne sont pas ajoutées pour les IDs personnalisés"""
        content = "# Titre {#custom}"
        headings = [
            {'level': 1, 'text': 'Titre', 'id': 'custom', 'line': 0, 'custom_id': 'custom'},
        ]
        result = add_anchors_to_headings(content, headings)
        # L'ancre ne devrait pas être ajoutée car l'ID est personnalisé
        assert '<a id="custom"></a>' not in result


class TestAddTocToMarkdownLogic:
    """Tests d'intégration pour add_toc_to_markdown_logic()"""

    def setup_method(self):
        """Setup temporaire pour chaque test"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup après chaque test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_add_toc_success(self):
        """Test ajout TOC réussi"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-toced.md"

        input_file.write_text("""# Introduction
Du contenu
## Section A
Plus de contenu
""", encoding='utf-8')

        exit_code, result_path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=1,
            max_level=6
        )

        assert exit_code == 0
        assert result_path == output_file
        assert output_file.exists()

        content = output_file.read_text(encoding='utf-8')
        assert '## Table des matières' in content
        assert '[Introduction](#introduction)' in content
        assert '[Section A](#section-a)' in content

    def test_add_toc_file_not_found(self):
        """Test fichier non trouvé"""
        input_file = self.temp_dir / "nonexistent.md"
        output_file = self.temp_dir / "output.md"

        exit_code, result_path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file
        )

        assert exit_code == 1
        assert result_path is None

    def test_add_toc_no_headings(self):
        """Test fichier sans titres"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-toced.md"

        input_file.write_text("Juste du texte sans titres.", encoding='utf-8')

        exit_code, result_path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file
        )

        assert exit_code == 0
        assert result_path == output_file
        assert output_file.exists()

    def test_add_toc_with_level_filtering(self):
        """Test avec filtrage de niveaux"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-toced.md"

        input_file.write_text("""# H1
## H2
### H3
#### H4
""", encoding='utf-8')

        exit_code, result_path = add_toc_to_markdown_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=3
        )

        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')
        assert '[H1](#h1)' not in content  # Exclu (level 1)
        assert '[H2](#h2)' in content       # Inclus (level 2)
        assert '[H3](#h3)' in content       # Inclus (level 3)
        assert '[H4](#h4)' not in content   # Exclu (level 4)
