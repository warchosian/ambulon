"""
Tests unitaires pour dyag.conversion.commands.md2html
"""
import pytest
from unittest.mock import Mock, patch
from dyag.conversion.commands.md2html import process_markdown_to_html


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.conversion
class TestMd2HtmlCommand:
    """Tests de la conversion Markdown vers HTML."""

    def test_convert_basic_markdown(self, temp_dir, sample_markdown):
        """Test conversion Markdown basique."""
        md_file = temp_dir / "test.md"
        md_file.write_text(sample_markdown, encoding='utf-8')

        html_file = temp_dir / "test.html"
        
        result = process_markdown_to_html(str(md_file), str(html_file))

        assert result == 0
        assert html_file.exists()
        content = html_file.read_text(encoding='utf-8')
        assert "<html>" in content or "<!DOCTYPE" in content

    def test_convert_with_code_blocks(self, temp_dir):
        """Test conversion avec blocs de code."""
        md_content = """# Test

```python
def hello():
    print("Hello")
```
"""
        md_file = temp_dir / "code.md"
        md_file.write_text(md_content, encoding='utf-8')

        html_file = temp_dir / "code.html"
        
        result = process_markdown_to_html(str(md_file), str(html_file))

        assert result == 0
        content = html_file.read_text(encoding='utf-8')
        assert "<code>" in content or "<pre>" in content

    def test_file_not_found(self):
        """Test erreur fichier non trouvé."""
        result = process_markdown_to_html("/nonexistent.md", "output.html")
        assert result != 0
