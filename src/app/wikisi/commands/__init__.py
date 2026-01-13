"""
WikiSI Commands - Ambulon

Commandes CLI pour la manipulation de données du parc applicatif WikiSI.
"""

# Import from core modules (following GEMINI architecture)
from ..core.extractor import process_parkjson2json_logic as process_parkjson2json
from ..core.json_to_md_converter import process_parkjson2md_logic as process_parkjson2md
from .wikisi_flatten import flatten_wikisi_directory
from ..core.scraper import WikiSIScraper

# Helper function for scraping
def scrape_wikisi(url, output_dir, **kwargs):
    """Wrapper for WikiSIScraper"""
    from app.core.config_loader import load_config
    config = load_config()
    config['site']['base_url'] = url
    config['output']['directory'] = str(output_dir)
    config.update(kwargs)
    scraper = WikiSIScraper(config)
    return scraper.scrape()

__all__ = [
    'process_parkjson2json',
    'process_parkjson2md',
    'flatten_wikisi_directory',
    'scrape_wikisi',
]
