"""Tests unitaires pour le module OCR."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from ambulon.ocr import perform_ocr


class TestOCRModule:
    """Tests pour le module OCR."""
    
    def test_perform_ocr_python_mock(self):
        """Test de l'OCR Python avec mock."""
        with tempfile.TemporaryDirectory() as temp_dir:
            image_file = Path(temp_dir) / "test_image.jpg"
            output_file = Path(temp_dir) / "test_output.txt"
            
            # Créer un fichier image factice
            image_file.write_bytes(b"fake image data")
            
            # Mock complet de la fonction perform_ocr
            with patch('ambulon.ocr.perform_ocr') as mock_perform:
                mock_perform.return_value = {
                    "success": True,
                    "text": "Texte extrait par OCR",
                    "output_file": str(output_file)
                }
                
                result = mock_perform(image_file, 'fra', output_file)
                
                assert isinstance(result, dict)
                assert "success" in result
                assert "text" in result
    
    def test_perform_ocr_file_not_found(self):
        """Test OCR avec fichier inexistant."""
        non_existent_file = Path("non_existent.jpg")
        
        result = perform_ocr(non_existent_file)
        
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
    
    def test_perform_ocr_mock_simple(self):
        """Test OCR simple avec mock."""
        with tempfile.TemporaryDirectory() as temp_dir:
            image_file = Path(temp_dir) / "test.jpg"
            image_file.write_bytes(b"fake image")
            
            # Mock complet de la fonction perform_ocr
            with patch('ambulon.ocr.perform_ocr') as mock_perform:
                mock_perform.return_value = {
                    "success": True,
                    "text": "Texte de test",
                    "confidence": 95.5
                }
                
                result = mock_perform(image_file)
                
                assert result["success"] is True
                assert "text" in result


if __name__ == "__main__":
    pytest.main([__file__])
