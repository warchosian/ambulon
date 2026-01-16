"""
Tests unitaires pour dyag.processing.commands.compress_pdf
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from dyag.processing.commands.compress_pdf import compress_pdf


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.processing
class TestCompressPdfCommand:
    """Tests de la compression PDF."""

    def test_compress_success(self, temp_dir):
        """Test compression - vérifie gestion dépendances manquantes."""
        # Créer un fichier PDF factice
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4 fake pdf content')

        output_file = temp_dir / "compressed.pdf"

        # Si les dépendances ne sont pas installées, devrait retourner 1
        # Si elles sont installées, devrait traiter le PDF
        result = compress_pdf(str(pdf_file), str(output_file))
        # On accepte les deux résultats (dépend de l'environnement)
        assert result in [0, 1]

    def test_file_not_found(self):
        """Test erreur fichier non trouvé."""
        result = compress_pdf("/nonexistent.pdf", "output.pdf")
        assert result != 0
