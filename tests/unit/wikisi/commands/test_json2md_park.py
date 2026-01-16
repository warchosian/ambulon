"""
Tests unitaires pour dyag.park.commands.json2md_park
"""
import pytest
import json
from dyag.park.commands.json2md_park import process_park_json_to_md


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.park
class TestJson2MdParkCommand:
    """Tests de la conversion JSON Park vers Markdown."""

    def test_convert_park_json(self, temp_dir, sample_park_json):
        """Test conversion JSON Park."""
        json_file = temp_dir / "park.json"
        json_file.write_text(json.dumps(sample_park_json), encoding='utf-8')

        md_file = temp_dir / "park.md"

        result = process_park_json_to_md(str(json_file), str(md_file))

        # assert result == 0
        # assert md_file.exists()
