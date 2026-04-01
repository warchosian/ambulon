"""
Exemple d'intégration de --show-config-sources dans gitlab-clone

Ce fichier démontre comment intégrer le ConfigTracker dans la commande gitlab-clone
pour afficher la provenance de chaque paramètre de configuration.

Usage:
    python gitlab_clone_with_tracking.py -S
    python gitlab_clone_with_tracking.py --config config/gitlab.yaml -S
    GITLAB_PRIVATE_TOKEN=xxx python gitlab_clone_with_tracking.py -S
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass

# Setup logger
logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Sources de configuration possibles."""
    CLI = "CLI Argument"
    YAML = "YAML File"
    ENV = "Environment"
    DEFAULT = "Default"


@dataclass
class ConfigValue:
    """Valeur de configuration avec sa source."""
    key: str
    value: Any
    source: ConfigSource
    is_sensitive: bool = False


class ConfigTracker:
    """Trace la provenance de chaque paramètre de configuration."""

    def __init__(self):
        self.values: Dict[str, ConfigValue] = {}

    def set(self, key: str, value: Any, source: ConfigSource, is_sensitive: bool = False):
        """Enregistre une valeur avec sa source."""
        self.values[key] = ConfigValue(
            key=key,
            value=value,
            source=source,
            is_sensitive=is_sensitive
        )

    def get_report(self) -> str:
        """Génère le rapport de traçabilité."""
        lines = [
            "",
            "Configuration Sources Report - gitlab-clone",
            "=" * 70,
            "",
            f"{'Parameter':<25} {'Source':<20} {'Value':<25}",
            f"{'-' * 25} {'-' * 20} {'-' * 25}",
        ]

        # Trier par source puis par clé
        sorted_values = sorted(
            self.values.values(),
            key=lambda v: (v.source.value, v.key)
        )

        for config_value in sorted_values:
            display_value = "****** (masked)" if config_value.is_sensitive else str(config_value.value)
            # Tronquer les longues valeurs
            if len(display_value) > 25 and not config_value.is_sensitive:
                display_value = display_value[:22] + "..."
            lines.append(
                f"{config_value.key:<25} {config_value.source.value:<20} {display_value:<25}"
            )

        # Résumé par source
        summary = self._get_summary()
        lines.extend([
            "",
            "Summary:",
        ])
        for source, count in sorted(summary.items()):
            lines.append(f"  - {source:<18} {count} parameter(s)")

        return "\n".join(lines)

    def _get_summary(self) -> Dict[str, int]:
        """Compte le nombre de paramètres par source."""
        summary = {}
        for config_value in self.values.values():
            source_name = config_value.source.value
            summary[source_name] = summary.get(source_name, 0) + 1
        return summary


# Default configuration for gitlab-clone
DEFAULT_CONFIG = {
    'gitlab': {
        'token': os.getenv('GITLAB_PRIVATE_TOKEN', ''),
        'username': os.getenv('GITLAB_USERNAME', 'oauth2'),
        'base_clone_dir': './gitlab_clones',
        'repositories': []
    }
}


def _is_sensitive_key(key: str) -> bool:
    """Détermine si une clé contient des données sensibles."""
    sensitive_keywords = ['token', 'password', 'secret', 'key', 'credential', 'pat']
    return any(keyword in key.lower() for keyword in sensitive_keywords)


def load_config_with_tracking(
    config_path: Optional[str] = None,
    default_config: Optional[Dict[str, Any]] = None,
    tracker: Optional[ConfigTracker] = None
) -> Dict[str, Any]:
    """
    Charge la configuration avec tracking des sources.

    Args:
        config_path: Chemin vers fichier YAML (optionnel)
        default_config: Configuration par défaut
        tracker: Tracker pour enregistrer les sources (optionnel)

    Returns:
        Configuration fusionnée
    """
    config = {}

    # 1. Valeurs par défaut
    if default_config:
        for section, section_values in default_config.items():
            if isinstance(section_values, dict):
                for key, value in section_values.items():
                    full_key = f"{section}.{key}"
                    config.setdefault(section, {})[key] = value
                    if tracker:
                        is_sensitive = _is_sensitive_key(key)
                        tracker.set(full_key, value if value else "(empty)", ConfigSource.DEFAULT, is_sensitive)

    # 2. Variables d'environnement (directes)
    env_mappings = {
        'GITLAB_PRIVATE_TOKEN': ('gitlab', 'token'),
        'GITLAB_USERNAME': ('gitlab', 'username'),
    }

    for env_var, (section, key) in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value:
            config.setdefault(section, {})[key] = env_value
            if tracker:
                full_key = f"{section}.{key}"
                is_sensitive = _is_sensitive_key(key)
                tracker.set(full_key, env_value if env_value else "(empty)", ConfigSource.ENV, is_sensitive)

    # 3. Fichier YAML (simulé pour cet exemple)
    # Dans la vraie implémentation, utilisez load_app_config()
    if config_path and Path(config_path).exists():
        # Simulation de chargement YAML
        # En réalité : config = load_app_config(config_path, default_config)
        # Pour cet exemple, on suppose que le YAML définit ces valeurs
        yaml_values = {
            'gitlab': {
                'base_clone_dir': './custom_clones',
                'repositories': [
                    'https://gitlab.example.com/user/project1.git',
                    'https://gitlab.example.com/user/project2.git'
                ]
            }
        }

        for section, section_values in yaml_values.items():
            if isinstance(section_values, dict):
                for key, value in section_values.items():
                    # Ne pas écraser si déjà défini par ENV
                    if key not in config.get(section, {}):
                        config.setdefault(section, {})[key] = value
                        if tracker:
                            full_key = f"{section}.{key}"
                            is_sensitive = _is_sensitive_key(key)
                            display_value = value
                            if isinstance(value, list):
                                display_value = f"{len(value)} repositories"
                            tracker.set(full_key, display_value, ConfigSource.YAML, is_sensitive)

    return config


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
Configuration Hierarchy (priority décroissante):
  1. Arguments CLI (--token, --username, --output)
  2. Fichier YAML (--config)
  3. Variables d'environnement (GITLAB_*)
  4. Valeurs par défaut

Variables d'environnement supportées:
  GITLAB_PRIVATE_TOKEN  GitLab Private Access Token
  GITLAB_USERNAME       GitLab username for PAT

Exemples:
  # Afficher la configuration
  python gitlab_clone_with_tracking.py -S

  # Via arguments CLI complets
  python gitlab_clone_with_tracking.py --token glpat-xxx --username oauth2 --output ./repos \\
    --repositories https://gitlab.example.com/user/project1.git -S

  # Via fichier de configuration
  python gitlab_clone_with_tracking.py --config config/gitlab.yaml -S

  # Via variables d'environnement
  GITLAB_PRIVATE_TOKEN=glpat-xxx python gitlab_clone_with_tracking.py -S
"""
    )

    parser.add_argument("-t", "--token", type=str, help="GitLab Private Access Token. Overrides config file and env var.")
    parser.add_argument("-u", "--username", type=str, help="GitLab username for PAT. Overrides config file and env var.")
    parser.add_argument("-o", "--output", type=str, help="Base directory to clone projects into. Overrides config file.")
    parser.add_argument("-r", "--repositories", action="append", help="Git repository URL to clone (can be used multiple times). Overrides config file.")
    parser.add_argument("-c", "--config", type=str, help="Path to the gitlab.yaml configuration file.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")

    # Option de traçabilité avec version abrégée
    parser.add_argument(
        "-S", "--show-config-sources",
        action="store_true",
        help="Affiche la provenance de chaque paramètre de configuration et quitte"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s - %(message)s'
    )

    # Initialiser le tracker
    tracker = ConfigTracker()

    # 1. Load config from YAML/ENV/Defaults avec tracking
    config = load_config_with_tracking(
        config_path=args.config,
        default_config=DEFAULT_CONFIG,
        tracker=tracker
    )

    # 2. Override with CLI arguments (priorité maximale)
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
        tracker.set('gitlab.repositories', f"{len(args.repositories)} repositories", ConfigSource.CLI)

    # Afficher le rapport si demandé
    if args.show_config_sources:
        print(tracker.get_report())
        if args.config:
            config_path = Path(args.config).resolve()
            print(f"\nConfig file: {config_path}")
            if not config_path.exists():
                print(f"  ⚠️  File not found (using defaults)")
        print("\n✓ Configuration sources displayed successfully")
        return 0

    # 3. Validate configuration
    gitlab_config = config.get("gitlab", {})
    final_token = gitlab_config.get("token")
    final_username = gitlab_config.get("username")
    final_base_dir = gitlab_config.get("base_clone_dir")
    repositories = gitlab_config.get("repositories", [])

    missing = []
    if not final_token:
        missing.append("token")
    if not final_username:
        missing.append("username")
    if not final_base_dir:
        missing.append("base_clone_dir")
    if not repositories:
        missing.append("repositories")

    if missing:
        logger.error("Configuration incomplète. Impossible de continuer.")
        logger.error(f"Valeurs manquantes : {', '.join(missing)}")
        logger.error("")
        logger.error("Utilisez -S pour voir la configuration actuelle :")
        logger.error(f"  python {sys.argv[0]} -S")
        return 1

    # 4. Execute business logic (simulé pour cet exemple)
    logger.info(f"Configuration valide !")
    logger.info(f"Token: {'*' * 20} (masked)")
    logger.info(f"Username: {final_username}")
    logger.info(f"Base directory: {final_base_dir}")
    logger.info(f"Repositories: {len(repositories)} to clone")

    logger.info("\n✓ Commande exécutée avec succès !")
    logger.info("(Utilisez -S pour voir la provenance de la config)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
