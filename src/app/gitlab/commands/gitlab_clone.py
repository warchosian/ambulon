"""
CLI command to clone GitLab projects based on a configuration file.
This module handles CLI arguments, configuration loading, and logging.
The core cloning logic resides in app.gitlab.core.cloning.
"""
import argparse
import logging
import os
import sys
import shutil
from pathlib import Path
from typing import List, Optional

from app.core.config_loader import load_config as load_app_config, find_config_file
from app.core.logging_config import setup_logging
from app.core.config_tracker import ConfigTracker, ConfigSource, is_sensitive_key
from app.gitlab.core.cloning import clone_repository
from app.gitlab.core.monofile import generate_code_monofile, generate_wiki_monofile, infer_repo_mode

# Post-processing imports (TOC, iTOC, Augment)
from app.toc.core.markdown_toc_generator import add_toc_to_markdown_logic
from app.toc.core.markdown_itoc import add_toc_backlinks_logic
from app.processing.commands.add_augment import augment

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

  # Avec améliorations automatiques des fichiers générés
  ambulon gitlab-clone --config config/gitlab.yaml --add-toc --add-itoc
  ambulon gitlab-clone --config config/gitlab.yaml --all-enhancements
"""
    )

    parser.add_argument("-t", "--token", type=str, help="GitLab Private Access Token. Overrides config file and env var.")
    parser.add_argument("-u", "--username", type=str, help="GitLab username for PAT. Overrides config file and env var.")
    parser.add_argument("-o", "--output", type=str, help="Base directory to clone projects into. Overrides config file.")
    parser.add_argument("-r", "--repositories", action="append", help="Git repository URL to clone (can be used multiple times). Overrides config file.")
    parser.add_argument("-c", "--config", type=str, default="config/gitlab.yaml", help="Path to the gitlab.yaml configuration file.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite of existing monofiles during generation.")

    # Options de post-traitement des fichiers générés
    parser.add_argument("--add-toc", action="store_true", help="Ajouter automatiquement une table des matières (TOC) aux fichiers Markdown générés")
    parser.add_argument("--add-itoc", action="store_true", help="Ajouter automatiquement des liens retour (iTOC) aux fichiers Markdown générés")
    parser.add_argument("--augment", action="store_true", help="Augmenter automatiquement les fichiers HTML générés avec navigation interactive")
    parser.add_argument("-E", "--all-enhancements", action="store_true", help="Appliquer toutes les améliorations (TOC + iTOC + augment). Produit des fichiers <origine>.enhanced.md")

    # Options de traçabilité de configuration
    parser.add_argument(
        "-S", "--show-config-sources",
        action="store_true",
        help="Affiche la provenance détaillée de chaque paramètre de configuration et quitte"
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Vérifie rapidement l'origine des paramètres (résumé condensé) et quitte"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="gitlab_clone")

    # Handle --all-enhancements option
    if args.all_enhancements:
        args.add_toc = True
        args.add_itoc = True
        args.augment = True
        logger.info("--all-enhancements enabled: TOC, iTOC, and augment will be applied")

    # Initialize configuration tracker
    tracker = ConfigTracker()

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

    # Track defaults first
    for key, value in DEFAULT_CONFIG.get('gitlab', {}).items():
        full_key = f"gitlab.{key}"
        display_value = value if value else "(empty)"
        if isinstance(value, list):
            display_value = f"{len(value)} repositories" if value else "(empty)"
        tracker.set(full_key, display_value, ConfigSource.DEFAULT, is_sensitive=is_sensitive_key(key))

    # Track values from loaded config (YAML or ENV via substitution)
    # Note: load_app_config already merges ENV vars via ${VAR} substitution
    loaded_gitlab = config.get('gitlab', {})
    for key, value in loaded_gitlab.items():
        full_key = f"gitlab.{key}"
        # Determine if value came from ENV or YAML by checking if it differs from default
        default_value = DEFAULT_CONFIG.get('gitlab', {}).get(key)
        display_value = value if value else "(empty)"
        if isinstance(value, list):
            display_value = f"{len(value)} repositories" if value else "(empty)"

        # If value differs from default, it came from config file or ENV
        # (We can't distinguish YAML vs ENV easily here, assume YAML unless it's from os.getenv)
        if value != default_value:
            # Check if it's a direct env var
            if key == 'token' and value == os.getenv('GITLAB_PRIVATE_TOKEN', ''):
                source = ConfigSource.ENV
            elif key == 'username' and value == os.getenv('GITLAB_USERNAME', 'oauth2') and value != 'oauth2':
                source = ConfigSource.ENV
            elif config_file_found:
                source = ConfigSource.YAML
            else:
                source = ConfigSource.DEFAULT
            tracker.set(full_key, display_value, source, is_sensitive=is_sensitive_key(key))

    # 2. Override with CLI arguments if they were provided (highest priority)
    if args.token:
        config['gitlab']['token'] = args.token
        tracker.set('gitlab.token', args.token, ConfigSource.CLI, is_sensitive=True)
    if args.username:
        config['gitlab']['username'] = args.username
        tracker.set('gitlab.username', args.username, ConfigSource.CLI)
    if args.output:
        config['gitlab']['base_clone_dir'] = args.output
        tracker.set('gitlab.base_clone_dir', args.output, ConfigSource.CLI)
    if args.repositories:
        config['gitlab']['repositories'] = args.repositories
        display_value = f"{len(args.repositories)} repositories"
        tracker.set('gitlab.repositories', display_value, ConfigSource.CLI)

    # Handle configuration source display options
    if args.show_config_sources:
        print(tracker.get_report("gitlab-clone"))
        if config_file_found:
            print(f"\nConfig file: {config_file_found}")
        else:
            print(f"\nConfig file: {args.config} (not found, using defaults)")
        print("\n✓ Configuration sources displayed successfully")
        print("\nUse this command without -S to execute the clone operation.")
        return 0

    if args.check_config:
        print(tracker.get_check_summary("gitlab-clone"))
        if config_file_found:
            print(f"\nConfig file: {config_file_found}")
        else:
            print(f"\nConfig file: {args.config} (not found)")
        print("\nUse -S/--show-config-sources for detailed view.")
        return 0

    # 3. Validate the final configuration
    gitlab_config = config.get("gitlab", {})
    automation_config = gitlab_config.get("automation", {})
    final_token = gitlab_config.get("token")
    final_username = gitlab_config.get("username")
    final_base_dir_str = gitlab_config.get("base_clone_dir")
    repositories = gitlab_config.get("repositories", [])
    if isinstance(repositories, str):
        repositories = [
            line.strip()
            for line in repositories.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

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
            env_home = os.getenv("AMBULON_HOME")
            base_dir = Path(env_home).expanduser() if env_home else Path.cwd()
            logger.error(f"  1. {base_dir / 'config' / 'gitlab.yaml'}")
            if os.getenv("AMBULON_CONFIG_DIR"):
                logger.error(f"  2. {os.getenv('AMBULON_CONFIG_DIR')}/gitlab.yaml")
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
    auto_enabled = bool(automation_config.get("enabled", False))
    output_mode = automation_config.get("output_mode", "separate")
    code_auto = automation_config.get("code_monofile", {}) if auto_enabled else {}
    wiki_auto = automation_config.get("wiki_monofile", {}) if auto_enabled else {}

    def _derive_repo_name(repo_url: str) -> str:
        repo_url_clean = repo_url
        if repo_url_clean.startswith("https://"):
            repo_url_clean = repo_url_clean[8:]
        elif repo_url_clean.startswith("http://"):
            repo_url_clean = repo_url_clean[7:]
        return Path(repo_url_clean).stem

    def _ensure_dir(path_value: Optional[str]) -> Optional[Path]:
        if not path_value:
            return None
        path = Path(path_value)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _log_output_path(output_path: Path) -> None:
        try:
            relative_path = output_path.relative_to(Path.cwd())
        except ValueError:
            relative_path = output_path.resolve()
        logger.info(f"File produced: {relative_path}")
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
            if status in ("success", "skipped") and auto_enabled:
                repo_name = result.get("repo_name") or _derive_repo_name(repo_url)
                repo_path_str = result.get("target_path")
                repo_path = Path(repo_path_str) if repo_path_str else final_base_dir / repo_name

                mode = infer_repo_mode(repo_path)
                if mode == "wiki":
                    if not wiki_auto.get("enabled", False):
                        continue
                    output_dir = _ensure_dir(wiki_auto.get("output_dir"))
                    filename_template = wiki_auto.get("filename_template")
                    templates = wiki_auto.get("templates")
                    exit_code, output_path = generate_wiki_monofile(
                        repo_dir=repo_path,
                        output_dir=output_dir,
                        output_mode=output_mode,
                        filename_template=filename_template,
                        templates=templates,
                        force=args.force,
                    )
                else:
                    if not code_auto.get("enabled", False):
                        continue
                    output_dir = _ensure_dir(code_auto.get("output_dir"))
                    filename_template = code_auto.get("filename_template")
                    templates = code_auto.get("templates")
                    exit_code, output_path = generate_code_monofile(
                        repo_dir=repo_path,
                        output_dir=output_dir,
                        output_mode=output_mode,
                        filename_template=filename_template,
                        templates=templates,
                        force=args.force,
                    )

                if exit_code == 0 and output_path:
                    _log_output_path(output_path)

                    # Determine if we need to create enhanced version
                    has_enhancements = args.add_toc or args.add_itoc or args.augment
                    enhanced_md_path = None
                    enhanced_html_path = None

                    # Post-processing: Add TOC/iTOC if requested
                    if has_enhancements and output_path.suffix == '.md':
                        # Create enhanced version: <origine>.enhanced.md
                        enhanced_md_path = output_path.parent / f"{output_path.stem}.enhanced.md"
                        try:
                            shutil.copy2(output_path, enhanced_md_path)
                            logger.info(f"Created enhanced MD: {enhanced_md_path.name}")
                        except Exception as e:
                            logger.error(f"Failed to create enhanced MD copy: {e}")
                            has_errors = True
                            enhanced_md_path = None

                        # Also create enhanced HTML if original HTML exists
                        html_path = Path(str(output_path)).with_suffix(".html")
                        if html_path.exists():
                            enhanced_html_path = output_path.parent / f"{output_path.stem}.enhanced.html"
                            try:
                                shutil.copy2(html_path, enhanced_html_path)
                                logger.info(f"Created enhanced HTML: {enhanced_html_path.name}")
                            except Exception as e:
                                logger.error(f"Failed to create enhanced HTML copy: {e}")
                                has_errors = True
                                enhanced_html_path = None

                    # Apply TOC to enhanced version
                    if args.add_toc and enhanced_md_path:
                        try:
                            logger.info(f"Adding TOC to {enhanced_md_path.name}...")
                            toc_exit_code, toc_output = add_toc_to_markdown_logic(
                                input_file=enhanced_md_path,
                                output_file=enhanced_md_path,
                                min_level=2,
                                max_level=6,
                                force=True
                            )
                            if toc_exit_code == 0:
                                logger.info(f"✓ TOC added to {enhanced_md_path.name}")
                            else:
                                logger.error(f"Failed to add TOC to {enhanced_md_path.name}")
                                has_errors = True
                        except Exception as e:
                            logger.error(f"Failed to add TOC to {enhanced_md_path.name}: {e}")
                            has_errors = True

                    # Apply iTOC to enhanced version
                    if args.add_itoc and enhanced_md_path:
                        try:
                            logger.info(f"Adding iTOC backlinks to {enhanced_md_path.name}...")
                            itoc_exit_code, itoc_output = add_toc_backlinks_logic(
                                input_file=enhanced_md_path,
                                output_file=enhanced_md_path,
                                toc_id='table-of-contents',
                                link_text='↑',
                                min_level=2,
                                max_level=6,
                                force=True
                            )
                            if itoc_exit_code == 0:
                                logger.info(f"✓ iTOC backlinks added to {enhanced_md_path.name}")
                            else:
                                logger.error(f"Failed to add iTOC to {enhanced_md_path.name}")
                                has_errors = True
                        except Exception as e:
                            logger.error(f"Failed to add iTOC to {enhanced_md_path.name}: {e}")
                            has_errors = True

                    # Log the enhanced files if created
                    if enhanced_md_path:
                        _log_output_path(enhanced_md_path)

                    # Augment enhanced HTML if it was created
                    if args.augment and enhanced_html_path:
                        try:
                            logger.info(f"Augmenting {enhanced_html_path.name} with interactive features...")
                            augment_exit_code = augment(
                                input_path=str(enhanced_html_path),
                                output_path=str(enhanced_html_path),
                                verbose=args.verbose
                            )
                            if augment_exit_code == 0:
                                logger.info(f"✓ HTML augmented: {enhanced_html_path.name}")
                                _log_output_path(enhanced_html_path)
                            else:
                                logger.error(f"Failed to augment {enhanced_html_path.name}")
                                has_errors = True
                        except Exception as e:
                            logger.error(f"Failed to augment {enhanced_html_path.name}: {e}")
                            has_errors = True

                    # Log original HTML if no enhancements were applied
                    if not has_enhancements:
                        html_path = Path(str(output_path)).with_suffix(".html")
                        if html_path.exists():
                            _log_output_path(html_path)
                elif exit_code == 0 and output_path is None:
                    logger.warning(f"Monofile skipped (no Markdown files) for {repo_path}")
                else:
                    logger.error(f"Monofile generation failed for {repo_path}")
                    has_errors = True

    if has_errors:
        logger.error("\nCompleted with errors.")
        return 1
    else:
        logger.info("\nAll repositories processed successfully.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
