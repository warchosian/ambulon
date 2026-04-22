"""Tests unitaires pour la commande llm-filter."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from app.llm.commands.filter import get_output_filename, main


class TestGetOutputFilename:
    """Tests pour la fonction get_output_filename."""
    
    def test_basic_md_file(self):
        """Test avec un fichier .md basique."""
        result = get_output_filename("project.md")
        assert result == "project.filtered.md"
    
    def test_code_md_file(self):
        """Test avec un fichier .code.md."""
        result = get_output_filename("sireines.code.md")
        assert result == "sireines.code.filtered.md"
    
    def test_file_without_md_extension(self):
        """Test avec un fichier sans extension .md."""
        result = get_output_filename("document.txt")
        assert result == "document.txt.filtered.md"
    
    def test_file_with_path(self):
        """Test avec un chemin complet."""
        result = get_output_filename("/path/to/project.code.md")
        assert result == "/path/to/project.code.filtered.md"
    
    def test_windows_path(self):
        """Test avec un chemin Windows."""
        result = get_output_filename(r"C:\Users\test\project.code.md")
        expected = str(Path(r"C:\Users\test\project.code.filtered.md"))
        assert result == expected


class TestMainFunction:
    """Tests pour la fonction main."""
    
    def test_missing_input_argument(self):
        """Test sans argument --input obligatoire."""
        with pytest.raises(SystemExit):
            main([])
    
    def test_nonexistent_input_file(self):
        """Test avec fichier d'entrée inexistant."""
        with pytest.raises(SystemExit):
            main(['-i', 'nonexistent.md'])
    
    def test_help_option(self):
        """Test de l'option --help."""
        with pytest.raises(SystemExit) as exc_info:
            main(['--help'])
        assert exc_info.value.code == 0
    
    @patch('app.llm.commands.filter.filter_document')
    @patch('pathlib.Path.exists')
    def test_successful_filtering(self, mock_exists, mock_filter):
        """Test d'un filtrage réussi."""
        mock_exists.return_value = True
        mock_filter.return_value = {
            'total': 100,
            'kept': 50,
            'excluded': 30,
            'omitted': 20,
            'total_size': 1000000,
            'kept_size': 500000
        }
        
        result = main(['-i', 'test.md'])
        
        assert result is None  # main() ne retourne rien en cas de succès
        mock_filter.assert_called_once()
    
    @patch('app.llm.commands.filter.filter_document')
    @patch('pathlib.Path.exists')
    def test_custom_output_file(self, mock_exists, mock_filter):
        """Test avec fichier de sortie personnalisé."""
        mock_exists.return_value = True
        mock_filter.return_value = {
            'total': 100,
            'kept': 50,
            'excluded': 30,
            'omitted': 20,
            'total_size': 1000000,
            'kept_size': 500000
        }
        
        result = main(['-i', 'test.md', '-o', 'custom_output.md'])
        
        assert result is None
        args, kwargs = mock_filter.call_args
        assert args[1] == 'custom_output.md'  # output_file
    
    @patch('app.llm.commands.filter.filter_document')
    @patch('pathlib.Path.exists')
    def test_custom_max_size(self, mock_exists, mock_filter):
        """Test avec taille maximale personnalisée."""
        mock_exists.return_value = True
        mock_filter.return_value = {
            'total': 100,
            'kept': 50,
            'excluded': 30,
            'omitted': 20,
            'total_size': 1000000,
            'kept_size': 500000
        }
        
        result = main(['-i', 'test.md', '--max-size', '10000'])
        
        assert result is None
        args, kwargs = mock_filter.call_args
        assert kwargs['max_file_size'] == 10000
    
    @patch('app.llm.commands.filter.filter_document')
    @patch('pathlib.Path.exists')
    def test_verbose_logging(self, mock_exists, mock_filter):
        """Test avec logging verbeux."""
        mock_exists.return_value = True
        mock_filter.return_value = {
            'total': 100,
            'kept': 50,
            'excluded': 30,
            'omitted': 20,
            'total_size': 1000000,
            'kept_size': 500000
        }
        
        with patch('logging.basicConfig') as mock_logging:
            result = main(['-i', 'test.md', '--verbose'])
            
            assert result is None
            mock_logging.assert_called_once()
            args, kwargs = mock_logging.call_args
            assert kwargs['level'] == 10  # logging.DEBUG
    
    @patch('app.llm.commands.filter.filter_document')
    @patch('pathlib.Path.exists')
    def test_filter_exception(self, mock_exists, mock_filter):
        """Test de gestion d'exception lors du filtrage."""
        mock_exists.return_value = True
        mock_filter.side_effect = Exception("Test error")
        
        with pytest.raises(SystemExit) as exc_info:
            main(['-i', 'test.md'])
        
        assert exc_info.value.code == 1
    
    def test_default_output_filename_generation(self):
        """Test de génération automatique du nom de fichier de sortie."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('app.llm.commands.filter.filter_document') as mock_filter:
            
            mock_filter.return_value = {
                'total': 100,
                'kept': 50,
                'excluded': 30,
                'omitted': 20,
                'total_size': 1000000,
                'kept_size': 500000
            }
            
            main(['-i', 'project.code.md'])
            
            args, kwargs = mock_filter.call_args
            assert args[1] == 'project.code.filtered.md'
