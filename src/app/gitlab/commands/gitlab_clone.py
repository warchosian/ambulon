"""
CLI command to clone GitLab projects based on a configuration file.
This module handles CLI arguments, configuration loading, and logging.
The core cloning logic resides in app.gitlab.core.cloning.
"""
import typer
import logging
import os
from pathlib import Path
from typing import List, Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from app.gitlab.core.cloning import clone_repository

app = typer.Typer()

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

@app.command(
    help="""
    Clones GitLab projects specified in the configuration.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments (e.g., --token)
    2. YAML configuration file (`--config`)
    3. Environment variables (e.g., GITLAB_PRIVATE_TOKEN)
    4. Default values
    """
)
def clone(
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitLab Private Access Token. Overrides config file and env var."),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="GitLab username for PAT. Overrides config file and env var."),
    base_clone_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Base directory to clone projects into. Overrides config file."),
    config_path: Path = typer.Option("config/gitlab.yaml", "--config", "-c", help="Path to the gitlab.yaml configuration file."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging.")
):
    """
    Clones GitLab projects based on a flexible configuration hierarchy.
    """
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="gitlab_clone")

    # 1. Load config from YAML, substituting env vars, merged over defaults
    config = load_app_config(str(config_path), DEFAULT_CONFIG)
    
    # 2. Override with CLI arguments if they were provided
    if token:
        config['gitlab']['token'] = token
    if username:
        config['gitlab']['username'] = username
    if base_clone_dir:
        config['gitlab']['base_clone_dir'] = str(base_clone_dir)

    # 3. Validate the final configuration
    gitlab_config = config.get("gitlab", {})
    final_token = gitlab_config.get("token")
    final_username = gitlab_config.get("username")
    final_base_dir_str = gitlab_config.get("base_clone_dir")
    repositories = gitlab_config.get("repositories", [])

    if not all([final_token, final_username, final_base_dir_str, repositories]):
        logger.error("Configuration is incomplete. Missing 'token', 'username', 'base_clone_dir', or 'repositories'.")
        logger.error("Please provide them via CLI args, config/gitlab.yaml, or environment variables.")
        raise typer.Exit(code=1)

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
        raise typer.Exit(code=1)
    else:
        logger.info("\nAll repositories processed successfully.")

if __name__ == "__main__":
    app()