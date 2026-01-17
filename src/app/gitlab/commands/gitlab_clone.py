"""
CLI command to clone GitLab projects based on a configuration file.
This module handles CLI arguments, configuration loading, and logging.
The core cloning logic resides in app.gitlab.core.cloning.
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from app.core.config_loader import load_config as load_app_config, find_config_file
from app.core.logging_config import setup_logging
from app.gitlab.core.cloning import clone_repository

# Default configuration for this module
DEFAULT_CONFIG = {
    'gitlab': {
        'token': os.getenv('GITLAB_PRIVATE_TOKEN', ''),
        'username': os.getenv('GITLAB_USERNAME', 'oauth2'),
        'base_clone_dir': './gitlab_clones',
        'repositories': []
    }
}

# Setup logger for this module
logger = logging.getLogger(__name__)

def main(argv=None):
    """
    Clones GitLab projects based on a flexible configuration hierarchy.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments (e.g., --token)
    2. YAML configuration file (`--config`)
    3. Environment variables (e.g., GITLAB_PRIVATE_TOKEN)
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="Clones GitLab projects specified in the configuration.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (priority decroissante):
  1. Arguments CLI (--token, --username, --output)
  2. Fichier YAML (--config)
  3. Variables d'environnement (GITLAB_*)
  4. Valeurs par défaut

Variables d'environnement supportées:
  GITLAB_PRIVATE_TOKEN  GitLab Private Access Token
  GITLAB_USERNAME       GitLab username for PAT

Exemples:
  # Via arguments CLI complets
  ambulon gitlab-clone --token glpat-xxx --username oauth2 --output ./repos \\
    --repositories https://gitlab.example.com/user/project1.git \\
    --repositories https://gitlab.example.com/user/project2.git

  # Ou avec le raccourci -r
  ambulon gitlab-clone -t glpat-xxx -u oauth2 -o ./repos \\
    -r https://gitlab.example.com/user/project1.git \\
    -r https://gitlab.example.com/user/project2.git

  # Via fichier de configuration
  ambulon gitlab-clone --config config/gitlab.yaml

  # Via fichier avec tilde (home directory)
  ambulon gitlab-clone --config ~/config/gitlab.yaml

  # Via variables d'environnement + config file
  GITLAB_PRIVATE_TOKEN=glpat-xxx ambulon gitlab-clone
"""
    )

    parser.add_argument("-t", "--token", type=str, help="GitLab Private Access Token. Overrides config file and env var.")
    parser.add_argument("-u", "--username", type=str, help="GitLab username for PAT. Overrides config file and env var.")
    parser.add_argument("-o", "--output", type=str, help="Base directory to clone projects into. Overrides config file.")
    parser.add_argument("-r", "--repositories", action="append", help="Git repository URL to clone (can be used multiple times). Overrides config file.")
    parser.add_argument("-c", "--config", type=str, default="config/gitlab.yaml", help="Path to the gitlab.yaml configuration file.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="gitlab_clone")

    # 1. Load config from YAML, substituting env vars, merged over defaults
    # Determine if config file exists (check exact path or search standard locations)
    config_file_path = Path(args.config).expanduser()

    if config_file_path.exists():
        config_file_found = config_file_path
    elif "/" not in args.config and "\\" not in args.config:
        # If just a name (no path separators), search standard locations
        config_name = args.config.replace(".yaml", "")
        config_file_found = find_config_file(config_name)
    else:
        config_file_found = None

    config = load_app_config(args.config, DEFAULT_CONFIG)

    # 2. Override with CLI arguments if they were provided
    if args.token:
        config['gitlab']['token'] = args.token
    if args.username:
        config['gitlab']['username'] = args.username
    if args.output:
        config['gitlab']['base_clone_dir'] = args.output
    if args.repositories:
        config['gitlab']['repositories'] = args.repositories

    # 3. Validate the final configuration
    gitlab_config = config.get("gitlab", {})
    final_token = gitlab_config.get("token")
    final_username = gitlab_config.get("username")
    final_base_dir_str = gitlab_config.get("base_clone_dir")
    repositories = gitlab_config.get("repositories", [])

    # Detailed validation with clear error messages
    missing = []
    if not final_token:
        missing.append("token")
    if not final_username:
        missing.append("username")
    if not final_base_dir_str:
        missing.append("base_clone_dir")
    if not repositories:
        missing.append("repositories")

    if missing:
        logger.error("Configuration incomplète. Impossible de continuer.")
        logger.error("")

        if config_file_found:
            logger.error(f"Fichier de configuration trouvé : {config_file_found}")
            logger.error("Mais il manque des valeurs obligatoires.")
        else:
            logger.error(f"Fichier de configuration introuvable : {args.config}")
            logger.error("")
            logger.error("Emplacements vérifiés :")
            logger.error(f"  1. {Path.cwd() / 'config' / 'gitlab.yaml'}")
            logger.error(f"  2. {Path.home() / '.config' / 'ambulon' / 'gitlab.yaml'}")
            if os.getenv("AMBULON_CONFIG_DIR"):
                logger.error(f"  3. {os.getenv('AMBULON_CONFIG_DIR')}/gitlab.yaml")
        logger.error("")

        logger.error(f"Valeurs manquantes : {', '.join(missing)}")
        logger.error("")
        logger.error("Solutions possibles :")

        if "token" in missing:
            logger.error("  • Via argument CLI : --token glpat-xxx")
            logger.error("  • Via variable d'env : export GITLAB_PRIVATE_TOKEN=glpat-xxx")
            logger.error("  • Via fichier YAML : gitlab.token: \"${GITLAB_PRIVATE_TOKEN}\"")

        if "username" in missing:
            logger.error("  • Via argument CLI : --username oauth2")
            logger.error("  • Via variable d'env : export GITLAB_USERNAME=oauth2")
            logger.error("  • Via fichier YAML : gitlab.username: \"${GITLAB_USERNAME:-oauth2}\"")

        if "base_clone_dir" in missing:
            logger.error("  • Via argument CLI : --output ./gitlab_clones")
            logger.error("  • Via fichier YAML : gitlab.base_clone_dir: \"./gitlab_clones\"")

        if "repositories" in missing:
            logger.error("  • Via argument CLI : --repositories https://gitlab.example.com/user/project.git")
            logger.error("  • Via fichier YAML : gitlab.repositories: [\"https://gitlab.example.com/...\"]")

        logger.error("")
        logger.error("Exemple de fichier de configuration : voir config/gitlab.yaml.example")
        return 1

    # 4. Execute business logic
    final_base_dir = Path(final_base_dir_str)
    final_base_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Found {len(repositories)} repositories to process.")

    has_errors = False
    for repo_url in repositories:
        for result in clone_repository(repo_url, final_base_dir, final_username, final_token):
            status = result.get("status")
            message = result.get("message")

            if status == "error":
                logger.error(message)
                if result.get("stderr"):
                    logger.error(f"Details: {result['stderr']}")
                has_errors = True
            elif status == "skipped":
                logger.warning(message)
            elif status == "cloning":
                logger.info(message)
            elif status == "success":
                logger.info(message)

    if has_errors:
        logger.error("\nCompleted with errors.")
        return 1
    else:
        logger.info("\nAll repositories processed successfully.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
