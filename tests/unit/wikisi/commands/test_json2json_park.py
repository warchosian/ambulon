"""
Tests unitaires pour dyag.park.commands.json2json_park
"""
import pytest
import json
from dyag.park.commands.json2json_park import transform_park_json


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.park
class TestJson2JsonParkCommand:
    """Tests de la transformation JSON Park."""

    def test_transform_park_json(self, temp_dir, sample_park_json):
        """Test transformation JSON Park."""
        json_file = temp_dir / "park_input.json"
        json_file.write_text(json.dumps(sample_park_json), encoding='utf-8')

        output_file = temp_dir / "park_output.json"

        result = transform_park_json(str(json_file), str(output_file))

        # assert result == 0
