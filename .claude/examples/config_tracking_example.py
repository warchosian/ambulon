"""
Exemple d'implémentation de --show-config-sources

Ce module démontre comment implémenter le tracking des sources de configuration
pour tracer la provenance de chaque paramètre (CLI, YAML, ENV, Default).

Usage:
    python config_tracking_example.py --show-config-sources
    python config_tracking_example.py --url https://custom.com --show-config-sources
    MY_MODULE_URL=https://env.com python config_tracking_example.py --show-config-sources
"""

import os
import sys
import argparse
import yaml
import re
from enum import Enum
from typing import Any, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


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
            "Configuration Sources Report",
            "=" * 70,
            "",
            f"{'Parameter':<20} {'Source':<20} {'Value':<30}",
            f"{'-' * 20} {'-' * 20} {'-' * 30}",
        ]

        # Trier par source puis par clé
        sorted_values = sorted(
            self.values.values(),
            key=lambda v: (v.source.value, v.key)
        )

        for config_value in sorted_values:
            display_value = "****** (masked)" if config_value.is_sensitive else str(config_value.value)
            lines.append(
                f"{config_value.key:<20} {config_value.source.value:<20} {display_value:<30}"
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
        for key, value in default_config.items():
            config[key] = value
            if tracker:
                is_sensitive = _is_sensitive_key(key)
                tracker.set(key, value, ConfigSource.DEFAULT, is_sensitive)

    # 2. Fichier YAML (avec substitution variables d'env)
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()

        # Dictionnaire pour tracker les substitutions
        env_vars_used = {}

        def replace_env_var(match):
            """Remplace ${VAR:-default} et track la source."""
            var_expr = match.group(1)
            if ':-' in var_expr:
                var_name, default_value = var_expr.split(':-', 1)
                env_value = os.getenv(var_name)
                if env_value is not None:
                    env_vars_used[var_name] = env_value
                    return env_value
                return default_value
            else:
                var_name = var_expr
                env_value = os.getenv(var_name)
                if env_value is None:
                    raise ValueError(f"Variable d'environnement requise non définie: {var_name}")
                env_vars_used[var_name] = env_value
                return env_value

        yaml_content = re.sub(r'\$\{([^}]+)\}', replace_env_var, yaml_content)
        yaml_config = yaml.safe_load(yaml_content) or {}

        # Fusionner et tracker
        flat_yaml = _flatten_dict(yaml_config)
        for key, value in flat_yaml.items():
            config[key] = value
            if tracker:
                # Déterminer si la valeur vient d'une var d'env ou du YAML
                # (simplifié : on suppose YAML, sauf si on a tracké une substitution)
                source = ConfigSource.YAML
                is_sensitive = _is_sensitive_key(key)
                tracker.set(key, value, source, is_sensitive)

        # Tracker les variables d'environnement utilisées dans le YAML
        if tracker:
            for var_name, var_value in env_vars_used.items():
                # Trouver la clé config correspondante (simplifié)
                is_sensitive = _is_sensitive_key(var_name)
                # Note: Ici on pourrait améliorer pour mapper var_name -> config key
                tracker.set(f"{var_name.lower()}", var_value, ConfigSource.ENV, is_sensitive)

    return config


def _is_sensitive_key(key: str) -> bool:
    """Détermine si une clé contient des données sensibles."""
    sensitive_keywords = ['token', 'password', 'secret', 'key', 'credential', 'apikey']
    return any(keyword in key.lower() for keyword in sensitive_keywords)


def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Aplatit un dictionnaire imbriqué."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def main(argv=None):
    """
    Point d'entrée de l'exemple de commande.

    Args:
        argv: Arguments CLI ou None pour sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(
        description="Exemple de commande avec tracking de configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Hiérarchie de configuration (priorité décroissante):
  1. Arguments CLI (--url, --timeout, etc.)
  2. Fichier YAML (--config)
  3. Variables d'environnement (MY_MODULE_*)
  4. Valeurs par défaut

Exemples:
  # Afficher la provenance de la configuration
  python config_tracking_example.py --show-config-sources

  # Avec arguments CLI
  python config_tracking_example.py --url https://cli.com --show-config-sources

  # Avec variables d'environnement
  MY_MODULE_URL=https://env.com python config_tracking_example.py --show-config-sources

  # Avec fichier de configuration
  python config_tracking_example.py --config config/example.yaml --show-config-sources
        """
    )

    # Arguments standards
    parser.add_argument("-u", "--url", help="URL à traiter")
    parser.add_argument("-t", "--timeout", type=int, help="Timeout en secondes")
    parser.add_argument("-o", "--output", help="Répertoire de sortie")
    parser.add_argument("-c", "--config", help="Fichier de configuration YAML")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")

    # Option de traçabilité (avec version abrégée)
    parser.add_argument(
        "-S", "--show-config-sources",
        action="store_true",
        help="Affiche la provenance de chaque paramètre de configuration et quitte"
    )

    args = parser.parse_args(argv)

    # Initialiser le tracker
    tracker = ConfigTracker()

    # Configuration par défaut
    default_config = {
        'url': 'https://default.example.com',
        'timeout': 30,
        'output': './output',
        'api_token': 'default_token_123',  # Sensible
        'max_retries': 3
    }

    # Charger configuration avec tracking
    config = load_config_with_tracking(
        config_path=args.config,
        default_config=default_config,
        tracker=tracker
    )

    # Appliquer arguments CLI (priorité maximale)
    if args.url is not None:
        config['url'] = args.url
        tracker.set('url', args.url, ConfigSource.CLI)

    if args.timeout is not None:
        config['timeout'] = args.timeout
        tracker.set('timeout', args.timeout, ConfigSource.CLI)

    if args.output is not None:
        config['output'] = args.output
        tracker.set('output', args.output, ConfigSource.CLI)

    # Variables d'environnement directes (non YAML)
    if os.getenv('MY_MODULE_URL'):
        env_url = os.getenv('MY_MODULE_URL')
        config['url'] = env_url
        # Si pas déjà écrasé par CLI
        if args.url is None:
            tracker.set('url', env_url, ConfigSource.ENV)

    if os.getenv('MY_MODULE_TIMEOUT'):
        env_timeout = int(os.getenv('MY_MODULE_TIMEOUT'))
        config['timeout'] = env_timeout
        if args.timeout is None:
            tracker.set('timeout', env_timeout, ConfigSource.ENV)

    # Afficher le rapport si demandé
    if args.show_config_sources:
        print(tracker.get_report())
        if args.config:
            print(f"\nConfig file: {Path(args.config).resolve()}")
        print("\n✓ Configuration sources displayed successfully")
        return 0

    # Exécuter la logique métier normalement
    if args.verbose:
        print(f"URL: {config['url']}")
        print(f"Timeout: {config['timeout']}s")
        print(f"Output: {config['output']}")

    print("\n✓ Commande exécutée avec succès !")
    print("(Utilisez --show-config-sources pour voir la provenance de la config)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
