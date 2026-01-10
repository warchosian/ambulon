"""
Module WikiSI - Ambulon

Transformation et manipulation de données du parc applicatif WikiSI.
Extraction, filtrage et conversion des données d'applications en différents formats.
"""

# Export des commandes principales
from .commands.wikisi_extract_json import process_parkjson2json
from .commands.wikisi_json_to_md import process_parkjson2md
from .commands.wikisi_flatten import flatten_wikisi_directory
from .commands.wikisi_scraper import scrape_wikisi

__all__ = [
    'process_parkjson2json',      # Extraction et filtrage JSON
    'process_parkjson2md',        # Conversion JSON vers Markdown
    'flatten_wikisi_directory',   # Aplatir arborescence WikiSI
    'scrape_wikisi',              # Aspirer site web WikiSI
]
