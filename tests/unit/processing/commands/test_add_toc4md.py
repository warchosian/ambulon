"""
Tests unitaires pour dyag.processing.commands.add_toc4md
"""
import pytest
from dyag.processing.commands.add_toc4md import add_toc_to_markdown


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.processing
class TestAddToc4MdCommand:
    """Tests de l'ajout de table des matières Markdown."""

    def test_add_toc_success(self, temp_dir, sample_markdown):
        """Test ajout TOC réussi."""
        md_file = temp_dir / "test.md"
        md_file.write_text(sample_markdown, encoding='utf-8')

        result = add_toc_to_markdown(str(md_file))

        assert result == 0
        # Vérifier que le fichier de sortie existe avec une TOC
        output_file = temp_dir / "test-tocced.md"
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "table" in content.lower() or "sommaire" in content.lower()

    def test_file_not_found(self):
        """Test erreur fichier non trouvé."""
        result = add_toc_to_markdown("/nonexistent.md")
        assert result != 0
