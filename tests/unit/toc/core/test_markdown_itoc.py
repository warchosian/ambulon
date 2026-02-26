"""
Tests unitaires pour markdown_itoc.py (inverse TOC / back-to-TOC links)
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from app.toc.core.markdown_itoc import (
    extract_headings_with_positions,
    add_backlinks_to_headings,
    add_toc_backlinks_logic
)


class TestExtractHeadingsWithPositions:
    """Tests pour extract_headings_with_positions()"""

    def test_extract_simple_headings(self):
        """Test extraction de titres simples avec positions"""
        content = """# Titre 1
Contenu
## Titre 2
Plus de contenu
"""
        headings = extract_headings_with_positions(content)
        assert len(headings) == 2
        assert headings[0]['level'] == 1
        assert headings[0]['text'] == 'Titre 1'
        assert headings[0]['line'] == 0
        assert headings[1]['level'] == 2
        assert headings[1]['text'] == 'Titre 2'
        assert headings[1]['line'] == 2

    def test_extract_headings_with_custom_id(self):
        """Test extraction avec ID personnalisés ignorés"""
        content = """# Titre {#custom-id}
## Section
"""
        headings = extract_headings_with_positions(content)
        assert len(headings) == 2
        # Les IDs personnalisés sont ignorés dans cette fonction
        assert 'custom_id' not in headings[0] or headings[0].get('custom_id') is None

    def test_extract_no_headings(self):
        """Test extraction sans titres"""
        content = "Juste du texte."
        headings = extract_headings_with_positions(content)
        assert len(headings) == 0

    def test_extract_preserves_original_line(self):
        """Test que la ligne originale est préservée"""
        content = """# Titre 1
## Titre 2
"""
        headings = extract_headings_with_positions(content)
        assert headings[0]['original_line'] == '# Titre 1'
        assert headings[1]['original_line'] == '## Titre 2'


class TestAddBacklinksToHeadings:
    """Tests pour add_backlinks_to_headings()"""

    def test_add_simple_backlinks(self):
        """Test ajout de liens retour simples"""
        content = """# Titre 1
Contenu
## Titre 2
"""
        headings = [
            {'level': 1, 'text': 'Titre 1', 'line': 0, 'original_line': '# Titre 1'},
            {'level': 2, 'text': 'Titre 2', 'line': 2, 'original_line': '## Titre 2'},
        ]

        result = add_backlinks_to_headings(content, headings)
        assert '# Titre 1 [↑](#table-of-contents)' in result
        assert '## Titre 2 [↑](#table-of-contents)' in result

    def test_add_backlinks_custom_toc_id(self):
        """Test avec ID TOC personnalisé"""
        content = "# Titre"
        headings = [
            {'level': 1, 'text': 'Titre', 'line': 0, 'original_line': '# Titre'},
        ]

        result = add_backlinks_to_headings(content, headings, toc_id="my-toc")
        assert '[↑](#my-toc)' in result

    def test_add_backlinks_custom_link_text(self):
        """Test avec texte de lien personnalisé"""
        content = "# Titre"
        headings = [
            {'level': 1, 'text': 'Titre', 'line': 0, 'original_line': '# Titre'},
        ]

        result = add_backlinks_to_headings(content, headings, link_text="⬆")
        assert '[⬆](#table-of-contents)' in result

    def test_add_backlinks_preserves_content(self):
        """Test que le contenu non-titre est préservé"""
        content = """# Titre 1
Paragraphe important
## Titre 2
Autre paragraphe
"""
        headings = [
            {'level': 1, 'text': 'Titre 1', 'line': 0, 'original_line': '# Titre 1'},
            {'level': 2, 'text': 'Titre 2', 'line': 2, 'original_line': '## Titre 2'},
        ]

        result = add_backlinks_to_headings(content, headings)
        assert 'Paragraphe important' in result
        assert 'Autre paragraphe' in result

    def test_add_backlinks_empty_headings(self):
        """Test avec liste de titres vide"""
        content = "# Titre\nContenu"
        result = add_backlinks_to_headings(content, [])
        assert result == content  # Contenu inchangé

    def test_add_backlinks_with_custom_ids(self):
        """Test avec IDs personnalisés - le lien doit être AVANT l'ID"""
        content = """# Titre Principal {#main}
## Section A {#section-a}
### Sous-section sans ID
"""
        headings = [
            {'level': 1, 'text': 'Titre Principal', 'line': 0, 'original_line': '# Titre Principal {#main}'},
            {'level': 2, 'text': 'Section A', 'line': 1, 'original_line': '## Section A {#section-a}'},
            {'level': 3, 'text': 'Sous-section sans ID', 'line': 2, 'original_line': '### Sous-section sans ID'},
        ]

        result = add_backlinks_to_headings(content, headings)

        # Vérifier que les liens iTOC sont AVANT les IDs personnalisés
        assert '# Titre Principal [↑](#table-of-contents) {#main}' in result
        assert '## Section A [↑](#table-of-contents) {#section-a}' in result
        assert '### Sous-section sans ID [↑](#table-of-contents)' in result

        # Vérifier qu'il n'y a PAS de liens APRÈS les IDs
        assert '{#main} [↑]' not in result
        assert '{#section-a} [↑]' not in result


class TestAddTocBacklinksLogic:
    """Tests d'intégration pour add_toc_backlinks_logic()"""

    def setup_method(self):
        """Setup temporaire pour chaque test"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup après chaque test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_add_backlinks_success(self):
        """Test ajout liens retour réussi"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-itoced.md"

        input_file.write_text("""# Introduction
Contenu
## Section A
Plus de contenu
""", encoding='utf-8')

        exit_code, result_path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file
        )

        assert exit_code == 0
        assert result_path == output_file
        assert output_file.exists()

        content = output_file.read_text(encoding='utf-8')
        assert '[↑](#table-of-contents)' in content
        assert '# Introduction [↑](#table-of-contents)' in content
        assert '## Section A [↑](#table-of-contents)' in content

    def test_add_backlinks_file_not_found(self):
        """Test fichier non trouvé"""
        input_file = self.temp_dir / "nonexistent.md"
        output_file = self.temp_dir / "output.md"

        exit_code, result_path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file
        )

        assert exit_code == 1
        assert result_path is None

    def test_add_backlinks_no_headings(self):
        """Test fichier sans titres"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-itoced.md"

        input_file.write_text("Juste du texte sans titres.", encoding='utf-8')

        exit_code, result_path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file
        )

        assert exit_code == 0
        assert result_path == output_file
        # Fichier créé même sans titres
        assert output_file.exists()

    def test_add_backlinks_with_level_filtering(self):
        """Test avec filtrage de niveaux"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-itoced.md"

        input_file.write_text("""# H1
## H2
### H3
#### H4
""", encoding='utf-8')

        exit_code, result_path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            min_level=2,
            max_level=3
        )

        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')

        # H1 et H4 ne devraient pas avoir de liens retour
        lines = content.split('\n')
        h1_line = lines[0]
        h4_line = lines[3]
        assert h1_line == '# H1'  # Pas de lien retour
        assert h4_line == '#### H4'  # Pas de lien retour

        # H2 et H3 devraient avoir des liens retour
        h2_line = lines[1]
        h3_line = lines[2]
        assert '[↑](#table-of-contents)' in h2_line
        assert '[↑](#table-of-contents)' in h3_line

    def test_add_backlinks_custom_toc_id(self):
        """Test avec ID TOC personnalisé"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-itoced.md"

        input_file.write_text("# Titre", encoding='utf-8')

        exit_code, result_path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            toc_id="custom-toc"
        )

        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')
        assert '[↑](#custom-toc)' in content

    def test_add_backlinks_custom_link_text(self):
        """Test avec texte de lien personnalisé"""
        input_file = self.temp_dir / "test.md"
        output_file = self.temp_dir / "test-itoced.md"

        input_file.write_text("# Titre", encoding='utf-8')

        exit_code, result_path = add_toc_backlinks_logic(
            input_file=input_file,
            output_file=output_file,
            link_text="⬆ Retour"
        )

        assert exit_code == 0
        content = output_file.read_text(encoding='utf-8')
        assert '[⬆ Retour](#table-of-contents)' in content
