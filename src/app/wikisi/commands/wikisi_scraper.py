"""
CLI command for WikiSI website scraping in Ambulon.
Utilizes core logic from app.wikisi.core.scraper.
Handles CLI arguments, configuration loading, and logging.
"""

import typer
import logging
import os
from pathlib import Path
from typing import Optional

from app.core.logging_config import setup_logging
from ..core.scraper import WikiSIScraper, load_config

logger = logging.getLogger(__name__)

app = typer.Typer()

@app.command(
    help="""
    Recursively scrapes a WikiSI website and downloads all HTML pages.
    Supports configuration via YAML, environment variables, and CLI arguments.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (`--config`)
    3. Environment variables
    4. Default values
    """
)
def main(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="Starting URL (overrides config)."),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory (overrides config)."),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to a YAML configuration file."),
    
    # Global options
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress most output messages."),

    # Scraper specific options
    max_depth: Optional[int] = typer.Option(None, "--depth", "-d", help="Maximum crawl depth (-1 for unlimited, overrides config)."),
    delay: Optional[float] = typer.Option(None, "--delay", help="Delay between requests in seconds (overrides config)."),
):
    """
    CLI for WikiSI website scraping.
    """
    # Configure logging
    log_level = logging.DEBUG if verbose else (logging.WARNING if quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="wikisi_scraper")
    logger.info("[START] Starting wikisi-scraper module.")
    logger.debug(f"CLI arguments: {typer.Context.get_current().params}")

    try:
        # Load configuration (merges defaults, env vars, then YAML)
        config = load_config(str(config_path) if config_path else None)

        # Apply CLI overrides (highest priority)
        if url:
            config['site']['base_url'] = url
        if output_dir:
            config['output']['directory'] = str(output_dir) # Ensure it's a string for internal config
        if max_depth is not None:
            config['site']['max_depth'] = max_depth
        if delay is not None:
            config['site']['delay'] = delay
        if verbose: # CLI verbose flag overrides config logging level
            config['logging']['level'] = 'debug'
        elif quiet: # CLI quiet flag overrides config logging level
            config['logging']['level'] = 'warning'

        # Validate base URL
        if not config['site']['base_url'] or config['site']['base_url'] == 'https://wikisi.example.gouv.fr':
            logger.error("Error: Please configure base_url in config file, environment variable (WIKISI_BASE_URL), or provide --url argument.")
            raise typer.Exit(code=1)

        # Create scraper instance
        scraper = WikiSIScraper(config)

        # Start scraping
        stats = scraper.scrape()

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("SCRAPING COMPLETED")
        logger.info("="*60)
        logger.info(f"Start URL:        {stats['start_url']}")
        logger.info(f"Duration:         {stats['duration_seconds']:.2f} seconds")
        logger.info(f"Pages visited:    {stats['pages_visited']}")
        logger.info(f"Pages downloaded: {stats['pages_downloaded']}")
        logger.info(f"Pages failed:     {stats['pages_failed']}")
        logger.info(f"Total size:       {stats['total_size_bytes'] / (1024*1024):.2f} MB")
        logger.info(f"Output directory: {config['output']['directory']}")
        logger.info("="*60)

        if stats['pages_failed'] > 0:
            logger.warning(f"\nWarning: {stats['pages_failed']} pages failed to download.")
            logger.warning("Check the log file for details.")

        raise typer.Exit(code=0)

    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user.")
        raise typer.Exit(code=1)

    except Exception as e:
        logger.error(f"Error: Scraping failed: {e}", exc_info=True)
        raise typer.Exit(code=1)

if __name__ == '__main__':
    app()