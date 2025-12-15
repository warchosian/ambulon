"""Tests unitaires pour le module OCR."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from ambulon.ocr import perform_ocr, _perform_ocr_python


class TestOCRModule:
    """Tests pour le module OCR."""
    
    def test_perform_ocr_python_mock(self):
        """Test de l'OCR Python avec mock."""
        with tempfile.TemporaryDirectory() as temp_dir:
            image_file = Path(temp_dir) / "test_image.jpg"
            output_file = Path(temp_dir) / "test_output.txt"
            
            # Créer un fichier image factice
            image_file.write_bytes(b"fake image data")
            
            with patch('pytesseract.image_to_string') as mock_ocr:
                mock_ocr.return_value = "Texte extrait par OCR"
                
                with patch('PIL.Image.open') as mock_image:
                    mock_image.return_value = MagicMock()
                    
                    result = _perform_ocr_python(image_file, 'fra', output_file)
                    
                    assert isinstance(result, dict)
                    assert "success" in result
                    assert "text" in result
                    assert "output_file" in result
    
    def test_perform_ocr_file_not_found(self):
        """Test OCR avec fichier inexistant."""
        non_existent_file = Path("non_existent.jpg")
        
        result = perform_ocr(non_existent_file)
        
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__])
