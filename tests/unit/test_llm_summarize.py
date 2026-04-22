"""Tests unitaires pour la commande llm-summarize."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from app.llm.commands.summarize import get_output_filename, main


class TestGetOutputFilename:
    """Tests pour la fonction get_output_filename."""
    
    def test_basic_md_file(self):
        """Test avec un fichier .md basique."""
        result = get_output_filename("project.md")
        assert result == "project.summarized.md"
    
    def test_code_md_file(self):
        """Test avec un fichier .code.md."""
        result = get_output_filename("sireines.code.md")
        assert result == "sireines.code.summarized.md"
    
    def test_file_without_md_extension(self):
        """Test avec un fichier sans extension .md."""
        result = get_output_filename("document.txt")
        assert result == "document.txt.summarized.md"
    
    def test_file_with_path(self):
        """Test avec un chemin complet."""
        result = get_output_filename("/path/to/project.code.md")
        assert result == "/path/to/project.code.summarized.md"
    
    def test_windows_path(self):
        """Test avec un chemin Windows."""
        result = get_output_filename(r"C:\Users\test\project.code.md")
        expected = str(Path(r"C:\Users\test\project.code.summarized.md"))
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
    
    @patch('app.llm.commands.summarize.summarize_document')
    @patch('pathlib.Path.exists')
    def test_successful_summarization(self, mock_exists, mock_summarize):
        """Test d'une summarisation réussie."""
        mock_exists.return_value = True
        mock_summarize.return_value = {
            'chunks': 5,
            'provider': 'claude',
            'model': 'claude-3-sonnet'
        }
        
        result = main(['-i', 'test.md'])
        
        assert result is None  # main() ne retourne rien en cas de succès
        mock_summarize.assert_called_once()
    
    @patch('app.llm.commands.summarize.summarize_document')
    @patch('pathlib.Path.exists')
    def test_custom_output_file(self, mock_exists, mock_summarize):
        """Test avec fichier de sortie personnalisé."""
        mock_exists.return_value = True
        mock_summarize.return_value = {
            'chunks': 3,
            'provider': 'kimi',
            'model': 'moonshot-v1-8k'
        }
        
        result = main(['-i', 'test.md', '-o', 'custom_summary.md'])
        
        assert result is None
        args, kwargs = mock_summarize.call_args
        assert args[1] == 'custom_summary.md'  # output_file
    
    @patch('app.llm.commands.summarize.summarize_document')
    @patch('pathlib.Path.exists')
    def test_custom_chunk_size(self, mock_exists, mock_summarize):
        """Test avec taille de chunk personnalisée."""
        mock_exists.return_value = True
        mock_summarize.return_value = {
            'chunks': 10,
            'provider': 'local',
            'model': 'llama3'
        }
        
        result = main(['-i', 'test.md', '--chunk-size', '100000'])
        
        assert result is None
        args, kwargs = mock_summarize.call_args
        assert kwargs['chunk_size'] == 100000
    
    @patch('app.llm.commands.summarize.summarize_document')
    @patch('pathlib.Path.exists')
    def test_verbose_logging(self, mock_exists, mock_summarize):
        """Test avec logging verbeux."""
        mock_exists.return_value = True
        mock_summarize.return_value = {
            'chunks': 2,
            'provider': 'chatgpt',
            'model': 'gpt-4'
        }
        
        with patch('logging.basicConfig') as mock_logging:
            result = main(['-i', 'test.md', '--verbose'])
            
            assert result is None
            mock_logging.assert_called_once()
            args, kwargs = mock_logging.call_args
            assert kwargs['level'] == 10  # logging.DEBUG
    
    @patch('app.llm.commands.summarize.summarize_document')
    @patch('pathlib.Path.exists')
    def test_summarize_exception(self, mock_exists, mock_summarize):
        """Test de gestion d'exception lors de la summarisation."""
        mock_exists.return_value = True
        mock_summarize.side_effect = Exception("LLM API error")
        
        with pytest.raises(SystemExit) as exc_info:
            main(['-i', 'test.md'])
        
        assert exc_info.value.code == 1
    
    def test_default_output_filename_generation(self):
        """Test de génération automatique du nom de fichier de sortie."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('app.llm.commands.summarize.summarize_document') as mock_summarize:
            
            mock_summarize.return_value = {
                'chunks': 4,
                'provider': 'claude',
                'model': 'claude-3-haiku'
            }
            
            main(['-i', 'project.code.md'])
            
            args, kwargs = mock_summarize.call_args
            assert args[1] == 'project.code.summarized.md'
    
    def test_default_chunk_size(self):
        """Test de la taille de chunk par défaut."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('app.llm.commands.summarize.summarize_document') as mock_summarize:
            
            mock_summarize.return_value = {
                'chunks': 1,
                'provider': 'local',
                'model': 'mistral'
            }
            
            main(['-i', 'small.md'])
            
            args, kwargs = mock_summarize.call_args
            assert kwargs['chunk_size'] == 50000  # Valeur par défaut
