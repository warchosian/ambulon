"""
Tests unitaires pour dyag.conversion.commands.json2md
"""
import pytest
import json
from dyag.conversion.commands.json2md import process_json_to_markdown


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.conversion
class TestJson2MdCommand:
    """Tests de la conversion JSON vers Markdown."""

    def test_convert_basic_json(self, temp_dir, sample_json_data):
        """Test conversion JSON basique."""
        json_file = temp_dir / "test.json"
        json_file.write_text(json.dumps(sample_json_data), encoding='utf-8')

        md_file = temp_dir / "test.md"
        
        result = process_json_to_markdown(str(json_file), str(md_file))

        assert result == 0
        assert md_file.exists()
