"""
CLI command for WikiSI website scraping in Ambulon.
Utilizes core logic from app.wikisi.core.scraper.
Handles CLI arguments, configuration loading, and logging.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.logging_config import setup_logging
from ..core.scraper import WikiSIScraper, load_config

logger = logging.getLogger(__name__)


def main(argv=None):
    """
    Entry point for wikisi-scrape command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Recursively scrapes a WikiSI website and downloads all HTML pages.
        Supports configuration via YAML, environment variables, and CLI arguments.

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config)
        3. Environment variables
        4. Default values
        """
    )

    parser.add_argument("--url", "-u", help="Starting URL (overrides config).")
    parser.add_argument("--output", "-o", help="Output directory (overrides config).")
    parser.add_argument("--config", "-c", help="Path to a YAML configuration file.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output messages.")
    parser.add_argument("--depth", "-d", type=int, help="Maximum crawl depth (-1 for unlimited, overrides config).")
    parser.add_argument("--delay", type=float, help="Delay between requests in seconds (overrides config).")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="wikisi_scraper")
    logger.info("[START] Starting wikisi-scraper module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    try:
        # Load configuration (merges defaults, env vars, then YAML)
        config = load_config(args.config if args.config else None)

        # Apply CLI overrides (highest priority)
        if args.url:
            config['site']['base_url'] = args.url
        if args.output:
            config['output']['directory'] = args.output
        if args.depth is not None:
            config['site']['max_depth'] = args.depth
        if args.delay is not None:
            config['site']['delay'] = args.delay
        if args.verbose:  # CLI verbose flag overrides config logging level
            config['logging']['level'] = 'debug'
        elif args.quiet:  # CLI quiet flag overrides config logging level
            config['logging']['level'] = 'warning'

        # Validate base URL
        if not config['site']['base_url'] or config['site']['base_url'] == 'https://wikisi.example.gouv.fr':
            logger.error("Error: Please configure base_url in config file, environment variable (WIKISI_BASE_URL), or provide --url argument.")
            return 1

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

        return 0

    except KeyboardInterrupt:
        logger.warning("\nScraping interrupted by user.")
        return 1

    except Exception as e:
        logger.error(f"Error: Scraping failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())