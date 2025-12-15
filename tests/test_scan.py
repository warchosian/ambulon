"""Tests unitaires pour le module de scan."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from ambulon.scan import scan_document, _simulate_scan


class TestScanModule:
    """Tests pour le module de scan."""
    
    def test_simulate_scan(self):
        """Test de la simulation de scan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_scan.jpg"
            
            result = _simulate_scan(output_file, 300, {})
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "file_path" in result
            assert "message" in result
            assert output_file.exists()
    
    @patch('ambulon.scan._perform_twain_scan')
    def test_scan_document_success(self, mock_twain):
        """Test de scan de document réussi."""
        mock_twain.return_value = True
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = scan_document(300, Path(temp_dir))
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "files" in result
    
    def test_scan_document_invalid_dpi(self):
        """Test de scan avec DPI invalide."""
        with pytest.raises(ValueError):
            scan_document(50)  # DPI trop faible
        
        with pytest.raises(ValueError):
            scan_document(5000)  # DPI trop élevé


if __name__ == "__main__":
    pytest.main([__file__])
