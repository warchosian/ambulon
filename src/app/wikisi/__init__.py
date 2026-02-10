"""
Module WikiSI - Ambulon

Transformation et manipulation de données du parc applicatif WikiSI.
Extraction, filtrage et conversion des données d'applications en différents formats.
"""

# Export des commandes CLI
from .commands.wikisi_extract_json import main as wikisi_extract_json_cli
from .commands.wikisi_json_to_md import main as wikisi_json_to_md_cli
from .commands.wikisi_scraper import main as wikisi_scraper_cli

# Export des fonctions métier (pour MCP et usage programmatique)
from .commands import (
    process_parkjson2json,
    process_parkjson2md,
    flatten_wikisi_directory,
    scrape_wikisi,
)

__all__ = [
    # CLI apps
    'wikisi_extract_json_cli',
    'wikisi_json_to_md_cli',
    'wikisi_scraper_cli',
    # Functions
    'process_parkjson2json',
    'process_parkjson2md',
    'flatten_wikisi_directory',
    'scrape_wikisi',
]
