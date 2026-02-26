"""
Tests unitaires pour markdown_toc_checker.py
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from app.toc.core.markdown_toc_checker import (
    detect_toc_markers,
    check_toc_exists_logic
)


class TestDetectTocMarkers:
    """Tests pour detect_toc_markers()"""

    def test_detect_toc_marker(self):
        """Test détection du marqueur [TOC]"""
        content = """# Titre
[TOC]
## Section
"""
        results = detect_toc_markers(content)
        assert results['toc_marker'] is True
        assert results['any_toc'] is True

    def test_detect_toc_marker_case_insensitive(self):
        """Test détection insensible à la casse"""
        content = "[toc]"
        results = detect_toc_markers(content)
        assert results['toc_marker'] is True

    def test_detect_html_nav(self):
        """Test détection de l'élément HTML nav"""
        content = '<nav class="table-of-contents" id="toc">...</nav>'
        results = detect_toc_markers(content)
        assert results['html_nav'] is True
        assert results['any_toc'] is True

    def test_detect_html_nav_with_id(self):
        """Test détection nav avec ID"""
        content = '<nav id="table-of-contents">...</nav>'
        results = detect_toc_markers(content)
        assert results['html_nav'] is True

    def test_detect_markdown_toc_section_french(self):
        """Test détection section TOC en français"""
        content = """## Table des matières
- [Section 1](#section-1)
"""
        results = detect_toc_markers(content)
        assert results['markdown_toc_section'] is True
        assert results['any_toc'] is True

    def test_detect_markdown_toc_section_english(self):
        """Test détection section TOC en anglais"""
        content = "## Table of Contents\n"
        results = detect_toc_markers(content)
        assert results['markdown_toc_section'] is True

    def test_detect_markdown_toc_section_variations(self):
        """Test variations du titre de section TOC"""
        variations = [
            "## Table des matières",
            "# Table des Matières",
            "### Table de matières",
            "## Table of Contents",
            "# TABLE OF CONTENTS",
        ]
        for variation in variations:
            results = detect_toc_markers(variation)
            assert results['markdown_toc_section'] is True, f"Failed for: {variation}"

    def test_detect_no_toc(self):
        """Test détection sans TOC"""
        content = """# Titre
Juste du contenu sans TOC
## Section
"""
        results = detect_toc_markers(content)
        assert results['toc_marker'] is False
        assert results['html_nav'] is False
        assert results['markdown_toc_section'] is False
        assert results['any_toc'] is False

    def test_detect_multiple_toc_types(self):
        """Test détection de plusieurs types de TOC"""
        content = """# Document
[TOC]
## Table des matières
<nav class="table-of-contents"></nav>
"""
        results = detect_toc_markers(content)
        assert results['toc_marker'] is True
        assert results['html_nav'] is True
        assert results['markdown_toc_section'] is True
        assert results['any_toc'] is True


class TestCheckTocExistsLogic:
    """Tests d'intégration pour check_toc_exists_logic()"""

    def setup_method(self):
        """Setup temporaire pour chaque test"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup après chaque test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_check_toc_exists_with_marker(self):
        """Test fichier avec marqueur [TOC]"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre
[TOC]
## Section
""", encoding='utf-8')

        exit_code, results = check_toc_exists_logic(test_file)

        assert exit_code == 0  # TOC existe
        assert results is not None
        assert results['toc_marker'] is True
        assert results['any_toc'] is True

    def test_check_toc_exists_with_html_nav(self):
        """Test fichier avec nav HTML"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre
<nav class="table-of-contents">TOC</nav>
## Section
""", encoding='utf-8')

        exit_code, results = check_toc_exists_logic(test_file)

        assert exit_code == 0
        assert results['html_nav'] is True

    def test_check_toc_not_exists(self):
        """Test fichier sans TOC"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("""# Titre
Juste du contenu
## Section
""", encoding='utf-8')

        exit_code, results = check_toc_exists_logic(test_file)

        assert exit_code == 1  # Pas de TOC
        assert results is not None
        assert results['any_toc'] is False

    def test_check_toc_file_not_found(self):
        """Test fichier non trouvé"""
        test_file = self.temp_dir / "nonexistent.md"

        exit_code, results = check_toc_exists_logic(test_file)

        assert exit_code == 2  # Erreur
        assert results is None

    def test_check_toc_strict_mode_with_marker(self):
        """Test mode strict avec marqueur"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("[TOC]", encoding='utf-8')

        exit_code, results = check_toc_exists_logic(test_file, strict=True)

        assert exit_code == 0
        assert results['toc_marker'] is True

    def test_check_toc_strict_mode_with_markdown_section(self):
        """Test mode strict avec section Markdown (rejeté)"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text("## Table des matières\n", encoding='utf-8')

        exit_code, results = check_toc_exists_logic(test_file, strict=True)

        # En mode strict, seul [TOC] ou HTML nav comptent
        assert exit_code == 1  # Pas de TOC valide en mode strict
        assert results['markdown_toc_section'] is True
        assert results['toc_marker'] is False

    def test_check_toc_strict_mode_with_html_nav(self):
        """Test mode strict avec nav HTML"""
        test_file = self.temp_dir / "test.md"
        test_file.write_text('<nav id="table-of-contents"></nav>', encoding='utf-8')

        exit_code, results = check_toc_exists_logic(test_file, strict=True)

        assert exit_code == 0
        assert results['html_nav'] is True

    def test_check_toc_encoding_detection(self):
        """Test détection d'encodage"""
        test_file = self.temp_dir / "test.md"
        # Écrire avec encodage UTF-8
        test_file.write_text("# Titre avec accents: é è à\n[TOC]", encoding='utf-8')

        exit_code, results = check_toc_exists_logic(test_file)

        assert exit_code == 0
        assert results['toc_marker'] is True
