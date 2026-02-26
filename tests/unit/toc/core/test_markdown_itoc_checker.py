"""
Tests unitaires pour markdown_itoc_checker.py (vérification des liens iTOC)
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from app.toc.core.markdown_itoc_checker import (
    detect_itoc_links,
    check_itoc_exists_logic
)


class TestDetectItocLinks:
    """Tests pour detect_itoc_links()"""

    def test_detect_simple_itoc_links(self):
        """Test détection de liens iTOC simples"""
        content = """# Titre 1 [↑](#table-of-contents)
## Titre 2 [↑](#table-of-contents)
"""
        results = detect_itoc_links(content)
        assert results['has_itoc_links'] is True
        assert results['itoc_count'] == 2
        assert results['total_headings'] == 2
        assert len(results['headings_with_itoc']) == 2
        assert len(results['headings_without_itoc']) == 0

    def test_detect_partial_itoc_coverage(self):
        """Test détection avec couverture partielle"""
        content = """# Titre 1 [↑](#table-of-contents)
## Titre 2
### Titre 3 [↑](#table-of-contents)
"""
        results = detect_itoc_links(content)
        assert results['has_itoc_links'] is True
        assert results['itoc_count'] == 2
        assert results['total_headings'] == 3
        assert len(results['headings_with_itoc']) == 2
        assert len(results['headings_without_itoc']) == 1

    def test_detect_no_itoc_links(self):
        """Test détection sans liens iTOC"""
        content = """# Titre 1
## Titre 2
### Titre 3
"""
        results = detect_itoc_links(content)
        assert results['has_itoc_links'] is False
        assert results['itoc_count'] == 0
        assert results['total_headings'] == 3
        assert len(results['headings_with_itoc']) == 0
        assert len(results['headings_without_itoc']) == 3

    def test_detect_no_headings(self):
        """Test détection sans titres"""
        content = "Juste du texte sans titres."
        results = detect_itoc_links(content)
        assert results['has_itoc_links'] is False
        assert results['itoc_count'] == 0
        assert results['total_headings'] == 0

    def test_detect_custom_link_pattern(self):
        """Test détection avec pattern personnalisé"""
        content = """# Titre 1 [⬆](#toc)
## Titre 2 [⬆](#toc)
"""
        results = detect_itoc_links(content, link_pattern=r'\[⬆\]\(#[^\)]+\)')
        assert results['has_itoc_links'] is True
        assert results['itoc_count'] == 2

    def test_detect_mixed_link_targets(self):
        """Test détection avec différentes cibles de lien"""
        content = """# Titre 1 [↑](#table-of-contents)
## Titre 2 [↑](#toc)
### Titre 3 [↑](#top)
"""
        results = detect_itoc_links(content)
        assert results['has_itoc_links'] is True
        assert results['itoc_count'] == 3  # Tous détectés car le pattern accepte n'importe quel ID

    def test_detect_headings_metadata(self):
        """Test métadonnées des titres détectés"""
        content = """# Titre 1 [↑](#toc)
## Titre 2
"""
        results = detect_itoc_links(content)

        # Vérifier métadonnées du titre avec iTOC
        assert results['headings_with_itoc'][0]['level'] == 1
        assert results['headings_with_itoc'][0]['text'] == 'Titre 1 [↑](#toc)'  # Texte complet
        assert results['headings_with_itoc'][0]['line'] == 0

        # Vérifier métadonnées du titre sans iTOC
        assert results['headings_without_itoc'][0]['level'] == 2
        assert 'Titre 2' in results['headings_without_itoc'][0]['text']
        assert results['headings_without_itoc'][0]['line'] == 1


class TestCheckItocExistsLogic:
    """Tests d'intégration pour check_itoc_exists_logic()"""

    def setup_method(self):
        """Setup temporaire pour chaque test"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup après chaque test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_check_itoc_exists_full_coverage(self):
        """Test fichier avec liens iTOC complets"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre 1 [↑](#table-of-contents)
## Titre 2 [↑](#table-of-contents)
### Titre 3 [↑](#table-of-contents)
""", encoding='utf-8')

        exit_code, results = check_itoc_exists_logic(test_file)

        assert exit_code == 0  # iTOC existe
        assert results is not None
        assert results['has_itoc_links'] is True
        assert results['itoc_count'] == 3
        assert results['total_headings'] == 3
        assert results['coverage'] == 1.0  # 100%

    def test_check_itoc_exists_partial_coverage(self):
        """Test fichier avec couverture partielle"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre 1 [↑](#toc)
## Titre 2
### Titre 3 [↑](#toc)
""", encoding='utf-8')

        exit_code, results = check_itoc_exists_logic(test_file, min_coverage=0.0)

        assert exit_code == 0  # iTOC existe (min_coverage = 0)
        assert results['itoc_count'] == 2
        assert results['total_headings'] == 3
        assert abs(results['coverage'] - 0.6667) < 0.01  # ~66.7%

    def test_check_itoc_not_exists(self):
        """Test fichier sans liens iTOC"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre 1
## Titre 2
### Titre 3
""", encoding='utf-8')

        exit_code, results = check_itoc_exists_logic(test_file)

        assert exit_code == 1  # Pas de iTOC
        assert results is not None
        assert results['has_itoc_links'] is False
        assert results['itoc_count'] == 0
        assert results['coverage'] == 0.0

    def test_check_itoc_file_not_found(self):
        """Test fichier non trouvé"""
        test_file = self.temp_dir / "nonexistent.md"

        exit_code, results = check_itoc_exists_logic(test_file)

        assert exit_code == 2  # Erreur
        assert results is None

    def test_check_itoc_min_coverage_requirement(self):
        """Test exigence de couverture minimale"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre 1 [↑](#toc)
## Titre 2
### Titre 3
#### Titre 4
""", encoding='utf-8')

        # Coverage = 1/4 = 25%
        # Exigence : 50% minimum
        exit_code, results = check_itoc_exists_logic(test_file, min_coverage=0.5)

        assert exit_code == 1  # Couverture insuffisante
        assert results['coverage'] == 0.25
        assert results['has_itoc_links'] is True  # Il y a des liens, mais pas assez

    def test_check_itoc_meets_coverage_requirement(self):
        """Test couverture satisfait l'exigence"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre 1 [↑](#toc)
## Titre 2 [↑](#toc)
### Titre 3 [↑](#toc)
#### Titre 4
""", encoding='utf-8')

        # Coverage = 3/4 = 75%
        # Exigence : 50% minimum
        exit_code, results = check_itoc_exists_logic(test_file, min_coverage=0.5)

        assert exit_code == 0  # Couverture suffisante
        assert results['coverage'] == 0.75

    def test_check_itoc_no_headings(self):
        """Test fichier sans titres"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("Juste du texte sans titres.", encoding='utf-8')

        exit_code, results = check_itoc_exists_logic(test_file)

        assert exit_code == 1  # Pas de iTOC (pas de titres)
        assert results['total_headings'] == 0
        assert results['coverage'] == 0.0

    def test_check_itoc_custom_pattern(self):
        """Test avec pattern personnalisé"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre 1 [⬆ Top](#top)
## Titre 2 [⬆ Top](#top)
""", encoding='utf-8')

        exit_code, results = check_itoc_exists_logic(
            test_file,
            link_pattern=r'\[⬆ Top\]\(#[^\)]+\)'
        )

        assert exit_code == 0
        assert results['itoc_count'] == 2

    def test_check_itoc_encoding_detection(self):
        """Test détection d'encodage"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre avec accents: é è à [↑](#toc)
## Autre titre: ç ê [↑](#toc)
""", encoding='utf-8')

        exit_code, results = check_itoc_exists_logic(test_file)

        assert exit_code == 0
        assert results['itoc_count'] == 2
