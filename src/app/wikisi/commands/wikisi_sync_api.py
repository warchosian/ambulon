"""
CLI command to synchronize data from the WikiSI API and save it to local JSON files.
This script fetches enumerations and application data, then formats it
into various JSON outputs, including AI-ready formats.
It adheres to the project's configuration hierarchy (CLI > YAML > ENV > Defaults).
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from app.wikisi.core.api_client import WikiSIAPIClient

logger = logging.getLogger(__name__)

# Default configuration for the wikisi_sync_api module
# These defaults will be merged with (and overridden by) YAML and ENV configs
DEFAULT_CONFIG = {
    'wikisi': {
        'api': {
            'url': 'https://wikisi.e2.rie.gouv.fr/wikisi/api',
            'token': '',
            'user_agent': 'Ambulon Wiki SI Sync API/1.0',
            'page_limit': 25
        },
        'output': {
            'directory': './wikisi-data',
            'enumerations_file': 'enumerations.json',
            'applications_file': 'applications.json',
            'applications_ia_file': 'applicationsIA.json',
            'applications_ia_mini_file': 'applicationsIA_mini.json'
        },
        'logging': {
            'level': 'info',
            'log_to_file': True,
            'log_file': './wikisi-sync-api.log'
        }
    }
}

def main(argv=None) -> int:
    """
    Entry point for the wikisi-sync-api command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="""
        Synchronize data from the WikiSI API (enumerations and applications)
        and save it into various local JSON files.

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments (--api-url, --output-dir, etc.)
        2. YAML configuration file (--config, e.g., config/wikisi.yaml)
        3. Environment variables (WIKISI_API_URL, WIKISI_OUTPUT_DIR, etc.)
        4. Default values (defined in script)

        Sensitive information like API tokens should ideally be set via
        environment variables (e.g., WIKISI_API_TOKEN) and NOT committed to version control.
        """
    )

    # API arguments
    parser.add_argument("--api-url", type=str,
                        help="Base URL of the WikiSI API (e.g., https://wikisi.example.gouv.fr/wikisi/api). "
                             "Overrides WIKISI_API_URL environment variable and config file.")
    parser.add_argument("--api-token", type=str,
                        help="API authentication token. Overrides WIKISI_API_TOKEN environment variable "
                             "and config file. Highly recommended to use environment variable for security.")
    parser.add_argument("--page-limit", type=int,
                        help="Number of items per page for API pagination (e.g., for applications lists). "
                             "Overrides WIKISI_API_PAGE_LIMIT environment variable and config file.")

    # Output arguments
    parser.add_argument("--output-dir", type=Path,
                        help="Directory to save the generated JSON files. "
                             "Overrides WIKISI_OUTPUT_DIR environment variable and config file.")
    parser.add_argument("--config", "-c", type=Path,
                        help="Path to a YAML configuration file (e.g., config/wikisi.yaml).")

    # Logging arguments
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging (DEBUG level). Overrides WIKISI_LOG_LEVEL.")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress most output messages (WARNING level). Overrides WIKISI_LOG_LEVEL.")

    args = parser.parse_args(argv)

    # Load configuration
    # The load_app_config function handles YAML, ENV, and merges with provided defaults
    loaded_config = load_app_config(
        config_path=args.config,
        default_config=DEFAULT_CONFIG
    )

    # Apply CLI overrides
    if args.api_url:
        loaded_config['wikisi']['api']['url'] = args.api_url
    if args.api_token:
        loaded_config['wikisi']['api']['token'] = args.api_token
    if args.page_limit is not None:
        loaded_config['wikisi']['api']['page_limit'] = args.page_limit
    if args.output_dir:
        loaded_config['wikisi']['output']['directory'] = str(args.output_dir) # Store as string for Path conversion in client

    # Configure logging
    log_level = loaded_config['wikisi']['logging']['level']
    if args.verbose:
        log_level = 'debug'
    elif args.quiet:
        log_level = 'warning'
    
    setup_logging(
        level=log_level,
        log_file_prefix="wikisi_sync_api",
        log_file=loaded_config['wikisi']['logging'].get('log_file'),
        log_to_file=loaded_config['wikisi']['logging'].get('log_to_file')
    )
    
    logger.info("[START] Starting WikiSI API Synchronization.")
    logger.debug(f"Effective Configuration: {loaded_config['wikisi']}")

    try:
        # Create API client instance
        client = WikiSIAPIClient(loaded_config['wikisi'])
        
        # The client constructor already handles loading/fetching enumerations and applications
        # It also generates and saves IA-ready formats
        applications_list = client._load_or_fetch_applications() # Access internal method to ensure it runs

        client.save_applications_ia_list(applications_list)
        client.save_applications_ia_mini_list(applications_list)

        logger.info("[SUCCESS] WikiSI API Synchronization completed successfully.")
        return 0

    except Exception as e:
        logger.error(f"[ERROR] WikiSI API Synchronization failed: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())