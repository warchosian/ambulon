"""
Exemple d'utilisation du ConfigManager générique

Ce fichier démontre comment utiliser le ConfigManager pour simplifier
la gestion de configuration avec tracking automatique des sources.

Usage:
    python config_manager_usage.py -S
    python config_manager_usage.py --check-config
    MYAPP_URL=https://test.com python config_manager_usage.py -S
"""

import sys
import argparse
from pathlib import Path

# Ajouter le path src pour import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.app.core.config_manager import ConfigManager


def main(argv=None):
    """Exemple d'utilisation du ConfigManager."""

    parser = argparse.ArgumentParser(
        description="Exemple d'utilisation du ConfigManager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy:
  1. CLI Arguments (highest priority)
  2. YAML File
  3. Environment Variables
  4. Defaults (lowest priority)

Environment Variables:
  MYAPP_URL       API URL
  MYAPP_TIMEOUT   Timeout in seconds
  MYAPP_TOKEN     API Token (sensitive)

Examples:
  # Check configuration
  python config_manager_usage.py -S
  python config_manager_usage.py --check-config

  # With environment variables
  MYAPP_URL=https://prod.example.com python config_manager_usage.py -S

  # With CLI arguments
  python config_manager_usage.py --url https://cli.com --timeout 60 -S
        """
    )

    # Arguments métier
    parser.add_argument("-u", "--url", help="API URL")
    parser.add_argument("-t", "--timeout", type=int, help="Timeout in seconds")
    parser.add_argument("--token", help="API Token")
    parser.add_argument("-c", "--config", help="Config file path")

    # Arguments de diagnostic
    parser.add_argument(
        "-S", "--show-config-sources",
        action="store_true",
        help="Show detailed configuration sources"
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Quick configuration check (summary)"
    )

    args = parser.parse_args(argv)

    # Définir les defaults
    defaults = {
        'api': {
            'url': 'https://default.example.com',
            'timeout': 30,
            'token': ''
        },
        'output': {
            'directory': './output',
            'format': 'json'
        }
    }

    # Créer le ConfigManager
    manager = ConfigManager(
        module_name='myapp',
        defaults=defaults,
        env_prefix='MYAPP',
        sensitive_keys=['token']  # Clés sensibles supplémentaires
    )

    # Charger la configuration avec CLI overrides
    config = manager.load(
        config_path=args.config,
        cli_overrides={
            'api.url': args.url,
            'api.timeout': args.timeout,
            'api.token': args.token,
        }
    )

    # Afficher le rapport si demandé
    if args.show_config_sources:
        print(manager.get_report())
        return 0

    if args.check_config:
        print(manager.get_check_summary())
        return 0

    # Valider la configuration
    is_valid, missing = manager.validate(required_keys=['api.url', 'api.token'])

    if not is_valid:
        print(f"\n❌ Configuration incomplète. Valeurs manquantes : {', '.join(missing)}")
        print("\nUtilisez -S pour voir d'où viennent les valeurs actuelles.")
        return 1

    # Exécuter la logique métier
    api_url = manager.get_value('api.url')
    api_timeout = manager.get_value('api.timeout')
    api_token = manager.get_value('api.token')

    print(f"\n✓ Configuration validée !")
    print(f"  URL: {api_url}")
    print(f"  Timeout: {api_timeout}s")
    print(f"  Token: {'*' * 20} (masked)")

    print("\n(Utilisez -S pour voir la provenance de chaque paramètre)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
