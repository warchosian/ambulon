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

from app.core.config_loader import load_config as load_app_config
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

    if not all([final_token, final_username, final_base_dir_str, repositories]):
        logger.error("Configuration is incomplete. Missing 'token', 'username', 'base_clone_dir', or 'repositories'.")
        logger.error("Please provide them via CLI args, config/gitlab.yaml, or environment variables.")
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
