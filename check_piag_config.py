#!/usr/bin/env python3
"""
Vérificateur de configuration PIAG

Vérifie que la configuration est correcte avant de lancer les tests E2E.

Usage:
    python check_piag_config.py [--config config/piag.yaml]
"""

import argparse
import os
import sys
from pathlib import Path


def print_status(label: str, status: bool, value: str = ""):
    """Affiche un statut avec un symbole."""
    symbol = "✓" if status else "❌"
    if value:
        print(f"  {symbol} {label:40} : {value}")
    else:
        print(f"  {symbol} {label}")


def load_config(config_path: str = None):
    """Charge la configuration depuis le fichier YAML."""
    try:
        import yaml
    except ImportError:
        print("❌ Erreur: Le module 'pyyaml' n'est pas installé")
        print("   Installez-le avec: pip install pyyaml")
        sys.exit(1)

    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


def check_rag_config(config: dict):
    """Vérifie la configuration RAG."""
    print("\n" + "=" * 80)
    print("CONFIGURATION RAG")
    print("=" * 80)

    issues = []
    rag_config = config.get('piag', {}).get('rag', {})

    # API URL
    api_url = rag_config.get('api', {}).get('base_url')
    print_status("API Base URL", bool(api_url), api_url or "Non définie")
    if not api_url:
        issues.append("API Base URL manquante")

    # Token
    token = rag_config.get('security', {}).get('token')
    token_env_var = rag_config.get('security', {}).get('token_env_var', 'PIAG_RAG_API_TOKEN')
    token_from_env = os.getenv(token_env_var)

    if token:
        print_status("Token (depuis YAML)", True, f"{token[:10]}...{token[-5:]}")
    elif token_from_env:
        print_status(f"Token (depuis ${token_env_var})", True, f"{token_from_env[:10]}...{token_from_env[-5:]}")
    else:
        print_status(f"Token", False, f"Non trouvé (ni YAML ni ${token_env_var})")
        issues.append(f"Token RAG manquant (définissez ${token_env_var} ou configurez piag.rag.security.token)")

    # Project ID
    project_id = rag_config.get('project', {}).get('project_id')
    project_id_env = os.getenv('PIAG_RAG_PROJECT_ID')

    if project_id:
        print_status("Project ID (depuis YAML)", True, project_id)
    elif project_id_env:
        print_status("Project ID (depuis $PIAG_RAG_PROJECT_ID)", True, project_id_env)
    else:
        print_status("Project ID", False, "Non trouvé")
        issues.append("Project ID manquant (définissez PIAG_RAG_PROJECT_ID ou configurez piag.rag.project.project_id)")

    # Timeout
    timeout = rag_config.get('api', {}).get('timeout', 30)
    print_status("Timeout", True, f"{timeout}s")

    # Logging
    logging_config = rag_config.get('logging', {})
    debug = logging_config.get('enable_debug', False)
    log_requests = logging_config.get('log_requests', False)
    log_responses = logging_config.get('log_responses', False)

    print_status("Debug activé", debug, "Oui" if debug else "Non")
    print_status("Log requêtes HTTP", log_requests, "Oui" if log_requests else "Non")
    print_status("Log réponses HTTP", log_responses, "Oui" if log_responses else "Non")

    return issues


def check_chat_config(config: dict):
    """Vérifie la configuration CHAT."""
    print("\n" + "=" * 80)
    print("CONFIGURATION CHAT")
    print("=" * 80)

    issues = []
    chat_config = config.get('piag', {}).get('chat', {})

    # API URL
    api_url = chat_config.get('api', {}).get('base_url')
    print_status("API Base URL", bool(api_url), api_url or "Non définie")
    if not api_url:
        issues.append("API Base URL manquante")

    # Token
    token = chat_config.get('security', {}).get('token')
    token_env_var = chat_config.get('security', {}).get('token_env_var', 'PIAG_CHAT_API_TOKEN')
    token_from_env = os.getenv(token_env_var)

    if token:
        print_status("Token (depuis YAML)", True, f"{token[:10]}...{token[-5:]}")
    elif token_from_env:
        print_status(f"Token (depuis ${token_env_var})", True, f"{token_from_env[:10]}...{token_from_env[-5:]}")
    else:
        print_status(f"Token", False, f"Non trouvé (ni YAML ni ${token_env_var})")
        issues.append(f"Token Chat manquant (définissez ${token_env_var} ou configurez piag.chat.security.token)")

    # Modèle
    model = chat_config.get('model', 'mte-api-piag-mistral-medium-latest')
    print_status("Modèle", True, model)

    # Timeout
    timeout = chat_config.get('api', {}).get('timeout', 60)
    print_status("Timeout", True, f"{timeout}s")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Vérificateur de configuration PIAG")
    parser.add_argument("--config", default="config/piag.yaml", help="Chemin vers le fichier de configuration")
    args = parser.parse_args()

    print("=" * 80)
    print("VÉRIFICATION DE LA CONFIGURATION PIAG")
    print("=" * 80)

    # Vérifier l'existence du fichier de config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"\n⚠️  Le fichier {args.config} n'existe pas")
        print("   Les tests utiliseront uniquement les variables d'environnement\n")
        config = {}
    else:
        print(f"\n✓ Fichier de configuration trouvé: {args.config}\n")
        try:
            config = load_config(args.config)
        except Exception as e:
            print(f"\n❌ Erreur lors du chargement de la config: {e}")
            return 1

    # Vérifier RAG
    rag_issues = check_rag_config(config)

    # Vérifier CHAT
    chat_issues = check_chat_config(config)

    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)

    all_issues = rag_issues + chat_issues

    if not all_issues:
        print("\n✓ Configuration valide - Prêt pour les tests E2E\n")
        print("Vous pouvez maintenant lancer:")
        print("  python test_piag_all.py")
        print("  python test_piag_rag_e2e.py")
        print("  python test_piag_chat_e2e.py")
        return 0
    else:
        print(f"\n❌ {len(all_issues)} problème(s) détecté(s):\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")

        print("\n" + "=" * 80)
        print("ACTIONS RECOMMANDÉES")
        print("=" * 80)

        if any("Token RAG" in issue for issue in all_issues):
            print("\nPour le token RAG:")
            print("  export PIAG_RAG_API_TOKEN=\"votre-token-ici\"")
            print("  # ou configurez piag.rag.security.token dans config/piag.yaml")

        if any("Project ID" in issue for issue in all_issues):
            print("\nPour le Project ID:")
            print("  export PIAG_RAG_PROJECT_ID=\"votre-project-id\"")
            print("  # ou configurez piag.rag.project.project_id dans config/piag.yaml")

        if any("Token Chat" in issue for issue in all_issues):
            print("\nPour le token Chat:")
            print("  export PIAG_CHAT_API_TOKEN=\"votre-token-ici\"")
            print("  # ou configurez piag.chat.security.token dans config/piag.yaml")

        print("\n" + "=" * 80)

        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
