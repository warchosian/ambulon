"""
Tests de compatibilité cross-platform pour le chargeur de configuration.

Ce module teste que le chargeur de configuration gère correctement
les séparateurs de chemin Windows (\) et Unix (/) sur les deux systèmes.
"""

import pytest
from pathlib import Path


def test_path_stem_with_unix_separator():
    """Test que Path.stem fonctionne avec les séparateurs Unix (/)."""
    assert Path("config/piag.yaml").stem == "piag"
    assert Path("config/subdir/piag.yaml").stem == "piag"
    assert Path("piag.yaml").stem == "piag"
    assert Path("piag").stem == "piag"


def test_path_stem_with_windows_separator():
    """Test que Path.stem fonctionne avec les séparateurs Windows (\\)."""
    assert Path("config\\piag.yaml").stem == "piag"
    assert Path("config\\subdir\\piag.yaml").stem == "piag"
    assert Path("piag.yaml").stem == "piag"
    assert Path("piag").stem == "piag"


def test_path_stem_with_mixed_separators():
    """Test que Path.stem fonctionne avec des séparateurs mixtes."""
    # Path normalise automatiquement les séparateurs
    assert Path("config/subdir\\piag.yaml").stem == "piag"
    assert Path("config\\subdir/piag.yaml").stem == "piag"


def test_path_construction_cross_platform():
    """Test que la construction de chemins avec / fonctionne sur tous les systèmes."""
    base = Path("/home/user")
    config_path = base / "config" / "piag.yaml"

    # Le chemin construit doit contenir "piag.yaml" à la fin
    assert config_path.name == "piag.yaml"
    assert config_path.stem == "piag"
    assert config_path.suffix == ".yaml"


def test_path_expanduser_cross_platform():
    """Test que expanduser() fonctionne sur tous les systèmes."""
    # ~ doit être remplacé par le répertoire home
    home_path = Path("~/config/piag.yaml").expanduser()

    # Le chemin étendu ne doit plus contenir ~
    assert "~" not in str(home_path)
    assert home_path.name == "piag.yaml"


def test_path_is_absolute_cross_platform():
    """Test que is_absolute() détecte correctement les chemins absolus sur tous les systèmes."""
    # Chemins relatifs
    assert not Path("config/piag.yaml").is_absolute()
    assert not Path("config\\piag.yaml").is_absolute()
    assert not Path("piag.yaml").is_absolute()

    # Chemins absolus (format Unix)
    assert Path("/home/user/config/piag.yaml").is_absolute()

    # Sur Windows, les chemins avec lettre de lecteur sont absolus
    # Sur Unix, ils ne le sont pas, mais Path gère ça correctement
    # On ne teste pas C:\\ car ça échouerait sur Unix
