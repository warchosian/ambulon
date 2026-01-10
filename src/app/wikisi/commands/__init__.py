"""
WikiSI Commands - Ambulon

Commandes CLI pour la manipulation de données du parc applicatif WikiSI.
"""

from .wikisi_extract_json import process_parkjson2json
from .wikisi_json_to_md import process_parkjson2md

__all__ = [
    'process_parkjson2json',
    'process_parkjson2md',
]
