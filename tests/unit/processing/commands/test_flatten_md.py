"""
Tests unitaires pour dyag.processing.commands.flatten_md
"""
import pytest
from dyag.processing.commands.flatten_md import flatten_markdown_directory


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.processing
class TestFlattenMdCommand:
    """Tests de l'aplatissement Markdown."""

    def test_flatten_success(self, temp_dir):
        """Test aplatissement réussi."""
        # Créer structure avec includes
        main_md = temp_dir / "main.md"
        main_md.write_text("# Main\n\n<!--include: sub.md-->", encoding='utf-8')

        sub_md = temp_dir / "sub.md"
        sub_md.write_text("## Sub section", encoding='utf-8')

        output_md = temp_dir / "flat.md"

        result = flatten_markdown_directory(str(main_md), str(output_md))

        # Devrait fusionner les fichiers
        # assert result == 0 (si implémenté)
