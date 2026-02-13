import sys
import argparse
import logging
import os
import requests
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.api_client import WikiSIAPIClient

logger = logging.getLogger(__name__)

# Default configuration to be merged with YAML and ENV.
# Values are defaults, but can be overridden by ENV vars using ${ENV_VAR:-default_value} in YAML.
DEFAULT_CONFIG: Dict[str, Any] = {
    'wikisi': {
        'api': {
            'url': os.getenv('WIKISI_API_URL', 'https://wikisi.e2.rie.gouv.fr/wikisi/api'),
            'token': os.getenv('WIKISI_API_TOKEN', ''),
            'user_agent': os.getenv('WIKISI_API_USER_AGENT', 'Ambulon Wiki SI Sync API/1.0'),
            'page_limit': int(os.getenv('WIKISI_API_PAGE_LIMIT', '25')),
        },
        'output': {
            'directory': os.getenv('WIKISI_OUTPUT_DIR', './wikisi-data'),
            'enumerations_file': os.getenv('WIKISI_ENUMERATIONS_FILE', 'enumerations.json'),
            'applications_file': os.getenv('WIKISI_APPLICATIONS_FILE', 'applications.json'),
            'applications_ia_file': os.getenv('WIKISI_APPLICATIONS_IA_FILE', 'applicationsIA.json'),
            'applications_ia_mini_file': os.getenv('WIKISI_APPLICATIONS_IA_MINI_FILE', 'applicationsIA_mini.json'),
        },
        'logging': {
            'level': os.getenv('WIKISI_LOG_LEVEL', 'info'),
            'log_to_file': os.getenv('WIKISI_LOG_TO_FILE', 'true').lower() == 'true',
            'log_file': os.getenv('WIKISI_LOG_FILE', './wikisi-sync-api.log'),
        }
    }
}

def main(argv=None):
    """
    Entry point for the wikisi-sync-api command.

    This command synchronizes data (enumerations, applications) from the WikiSI API
    and saves them as JSON files locally. It also generates AI-ready formats.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. YAML configuration file (--config, e.g., config/wikisi.yaml)
    3. Environment variables (WIKISI_API_URL, WIKISI_API_TOKEN, etc.)
    4. Default values (defined in DEFAULT_CONFIG)
    """
    parser = argparse.ArgumentParser(
        description="""
        Synchronizes data (enumerations, applications) from the WikiSI API and saves
        them as local JSON files, including AI-ready formats.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (priorité décroissante):
  1. Arguments CLI (--api-url, --output-dir, etc.)
  2. Fichier YAML (--config)
  3. Variables d'environnement (WIKISI_API_URL, WIKISI_API_TOKEN, etc.)
  4. Valeurs par défaut (internes au script)

Variables d'environnement supportées:
  WIKISI_API_URL             URL de base de l'API WikiSI
  WIKISI_API_TOKEN           Jeton d'authentification pour l'API WikiSI
  WIKISI_API_USER_AGENT      User-Agent pour les requêtes API
  WIKISI_API_PAGE_LIMIT      Limite d'éléments par page pour les appels API paginés
  WIKISI_OUTPUT_DIR          Répertoire de sortie pour les fichiers JSON
  WIKISI_ENUMERATIONS_FILE   Nom du fichier JSON des énumérations
  WIKISI_APPLICATIONS_FILE   Nom du fichier JSON des applications
  WIKISI_APPLICATIONS_IA_FILE Nom du fichier JSON des applications formatées pour l'IA
  WIKISI_APPLICATIONS_IA_MINI_FILE Nom du fichier JSON des applications formatées pour l'IA (mini)
  WIKISI_LOG_LEVEL           Niveau de journalisation (info, debug, warning, error)
  WIKISI_LOG_TO_FILE         Activer la journalisation vers un fichier (true/false)
  WIKISI_LOG_FILE            Chemin du fichier de journalisation
        """
    )

    # Global options
    parser.add_argument("--config", "-c", type=Path, help="Path to a YAML configuration file (e.g., config/wikisi.yaml).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging (DEBUG level).")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress most output messages (WARNING level).")

    # API options
    parser.add_argument("--api-url", help="Override the base URL for the WikiSI API.")
    parser.add_argument("--api-token", help="Override the API authentication token.")
    parser.add_argument("--api-user-agent", help="Override the User-Agent for API requests.")
    parser.add_argument("--api-page-limit", type=int, help="Override the page limit for paginated API calls.")

    # Output options
    parser.add_argument("--output-dir", type=Path, help="Override the output directory for JSON files.")
    parser.add_argument("--enumerations-file", help="Override the filename for enumerations JSON.")
    parser.add_argument("--applications-file", help="Override the filename for applications JSON.")
    parser.add_argument("--applications-ia-file", help="Override the filename for AI-ready applications JSON.")
    parser.add_argument("--applications-ia-mini-file", help="Override the filename for mini AI-ready applications JSON.")

    args = parser.parse_args(argv)

    # Load configuration
    # config_loader handles merging defaults, YAML, and ENV vars.
    loaded_config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)

    # Extract wikisi config (all our config is under 'wikisi' key)
    app_config = loaded_config.get('wikisi', {})

    # Apply CLI overrides (highest priority)
    if args.api_url:
        app_config['api']['url'] = args.api_url
    if args.api_token:
        app_config['api']['token'] = args.api_token
    if args.api_user_agent:
        app_config['api']['user_agent'] = args.api_user_agent
    if args.api_page_limit is not None:
        app_config['api']['page_limit'] = args.api_page_limit

    if args.output_dir:
        app_config['output']['directory'] = str(args.output_dir) # Ensure it's a string for Path conversion in client
    if args.enumerations_file:
        app_config['output']['enumerations_file'] = args.enumerations_file
    if args.applications_file:
        app_config['output']['applications_file'] = args.applications_file
    if args.applications_ia_file:
        app_config['output']['applications_ia_file'] = args.applications_ia_file
    if args.applications_ia_mini_file:
        app_config['output']['applications_ia_mini_file'] = args.applications_ia_mini_file

    # Configure logging based on resolved config and CLI overrides
    log_level_str = app_config['logging']['level']
    if args.verbose:
        log_level_str = 'debug'
    elif args.quiet:
        log_level_str = 'warning'

    log_level_map = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}
    final_log_level = log_level_map.get(log_level_str.lower(), logging.INFO)

    # setup_logging() automatically creates log files with timestamps in logs/ directory
    # The log_file_prefix parameter determines the file name: logs/wikisi_sync_api.YYYY-MM-DD_HHhMMmSSs.log
    log_file_prefix = "wikisi_sync_api" if app_config['logging'].get('log_to_file', False) else None
    setup_logging(level=final_log_level, log_file_prefix=log_file_prefix)
    logger.info("[START] Starting wikisi-sync-api module.")
    logger.debug(f"Resolved Configuration: {app_config}")

    # Validate essential configuration
    if not app_config['api']['url']:
        logger.error("Error: WikiSI API URL is not configured. Use --api-url, WIKISI_API_URL environment variable, or config file.")
        return 1
    if not app_config['api']['token']:
        logger.warning("Warning: WikiSI API Token is not configured. API requests might fail if authentication is required.")
    
    try:
        client = WikiSIAPIClient(app_config)

        # 1. Fetch and save enumerations
        logger.info("Synchronizing enumerations from WikiSI API...")
        _ = client.extract_enumerations_dict() # This will also save and load internally

        # 2. Fetch and save applications
        logger.info("Synchronizing applications from WikiSI API...")
        applications_list = client.extract_applications_list() # This will also save and load internally

        # 3. Generate and save AI-ready application formats
        if applications_list:
            logger.info("Generating AI-ready application formats...")
            client.save_applications_ia_list(applications_list)
            client.save_applications_ia_mini_list(applications_list)
        else:
            logger.warning("No applications found to generate AI-ready formats.")

        logger.info("[SUCCESS] WikiSI API synchronization completed.")
        return 0

    except requests.exceptions.ConnectionError as e:
        # Check if it's a DNS resolution error (common when not on VPN)
        error_str = str(e).lower()
        if 'failed to resolve' in error_str or 'getaddrinfo failed' in error_str or 'nameresolutionerror' in error_str:
            logger.error("=" * 80)
            logger.error("Erreur de connexion: Impossible de résoudre le nom de domaine WikiSI")
            logger.error("")
            logger.error("CAUSE PROBABLE:")
            logger.error("  - Vous devez être connecté au VPN pour accéder au serveur WikiSI")
            logger.error("  - Vérifiez que votre connexion VPN est active")
            logger.error("")
            logger.error("SI LE PROBLEME PERSISTE:")
            logger.error("  - Le serveur WikiSI (wikisi.e2.rie.gouv.fr) n'est peut-être pas atteignable")
            logger.error("  - Contactez l'administrateur système")
            logger.error("=" * 80)
        else:
            logger.error(f"Erreur de connexion à l'API: {e}", exc_info=True)
        return 1
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête API: {e}", exc_info=True)
        return 1
    except Exception as e:
        logger.error(f"Une erreur inattendue s'est produite: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())