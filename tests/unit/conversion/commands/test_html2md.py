"""
Tests unitaires pour dyag.conversion.commands.html2md
"""
import pytest
from dyag.conversion.commands.html2md import process_html_to_markdown


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.conversion
class TestHtml2MdCommand:
    """Tests de la conversion HTML vers Markdown."""

    def test_convert_basic_html(self, temp_dir, sample_html):
        """Test conversion HTML basique."""
        html_file = temp_dir / "test.html"
        html_file.write_text(sample_html, encoding='utf-8')

        md_file = temp_dir / "test.md"
        
        result = process_html_to_markdown(str(html_file), str(md_file))

        assert result == 0
        assert md_file.exists()
        content = md_file.read_text(encoding='utf-8')
        assert "#" in content  # Devrait contenir des titres Markdown
