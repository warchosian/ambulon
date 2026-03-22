"""
Commande CLI pour récupérer les informations sur une apikey PIAG Chat.

Affiche le budget maximum et les dépenses associées au token.

Usage:
    ambulon piag-chat-apikey-info
    ambulon piag-chat-apikey-info --chat-token sk-xxxxx
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any
import requests

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'piag': {
        'chat': {
            'api': {
                'base_url': 'https://preprod.api.piag.e2.rie.gouv.fr/v1',
                'timeout': 60,
            },
            'security': {
                'token': os.getenv('PIAG_CHAT_API_TOKEN', ''),
            },
        }
    }
}


def get_apikey_info(api_url: str, chat_token: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Récupère les informations sur l'apikey depuis l'API PIAG.
    
    Args:
        api_url: URL de base de l'API
        chat_token: Token API (Bearer)
        timeout: Timeout en secondes
        
    Returns:
        Informations sur l'apikey (budget, spend, etc.)
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {chat_token}'
    }
    
    endpoint = f"{api_url.rstrip('/')}/apikey/info"
    
    logger.debug(f"Requête: GET {endpoint}")
    
    response = requests.get(
        endpoint,
        headers=headers,
        timeout=timeout
    )
    
    response.raise_for_status()
    return response.json()


def format_info(info: Dict[str, Any]) -> str:
    """
    Formate les informations de l'apikey pour l'affichage.
    
    Args:
        info: Dictionnaire d'informations
        
    Returns:
        Texte formaté
    """
    lines = []
    lines.append("=" * 50)
    lines.append("INFORMATIONS API KEY")
    lines.append("=" * 50)
    
    if 'max_budget' in info:
        lines.append(f"Budget maximum: {info['max_budget']}")
    if 'spend' in info:
        lines.append(f"Dépenses: {info['spend']}")
    if 'token' in info:
        # Masquer une partie du token pour la sécurité
        token = info['token']
        masked = token[:10] + "..." + token[-4:] if len(token) > 14 else "***"
        lines.append(f"Token: {masked}")
    
    # Afficher toutes les autres infos
    for key, value in info.items():
        if key not in ['max_budget', 'spend', 'token']:
            lines.append(f"{key}: {value}")
    
    lines.append("=" * 50)
    return "\n".join(lines)


def main(argv=None):
    """
    Point d'entrée CLI pour piag-chat-apikey-info.
    """
    parser = argparse.ArgumentParser(
        description="Récupérer les informations sur une apikey PIAG Chat (budget, dépenses).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Utiliser le token de la configuration
  ambulon piag-chat-apikey-info

  # Spécifier un token différent
  ambulon piag-chat-apikey-info --chat-token sk-xxxxx

  # Sortie JSON brute
  ambulon piag-chat-apikey-info --json
"""
    )
    
    parser.add_argument('--chat-token', help='Token API PIAG Chat (override config/env)')
    parser.add_argument('--api-url', help='URL de base de l\'API PIAG (override config)')
    parser.add_argument('--config', type=Path, default='config/piag.yaml', help='Fichier de configuration YAML')
    parser.add_argument('--json', action='store_true', help='Afficher la réponse JSON brute')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbeux')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout de la requête en secondes')
    
    args = parser.parse_args(argv)
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="piag_chat_apikey_info")
    
    # Chargement de la config
    config = load_app_config(str(args.config) if args.config.exists() else None, DEFAULT_CONFIG)
    piag_config = config.get('piag', {}).get('chat', {})
    
    # Récupération des valeurs
    api_url = args.api_url or piag_config.get('api', {}).get('base_url') or DEFAULT_CONFIG['piag']['chat']['api']['base_url']

    # Token avec hiérarchie: CLI > YAML > ENV (via token_env_var) > Erreur
    chat_token = args.chat_token  # CLI (priorité 1)
    if not chat_token:
        chat_token = piag_config.get('security', {}).get('token')  # YAML (priorité 2)
    if not chat_token:
        # Variable d'env (priorité 3)
        token_env_var = piag_config.get('security', {}).get('token_env_var', 'PIAG_CHAT_API_TOKEN')
        chat_token = os.getenv(token_env_var)

    timeout = args.timeout or piag_config.get('api', {}).get('timeout') or DEFAULT_CONFIG['piag']['chat']['api']['timeout']

    # Validation
    if not chat_token:
        token_env_var = piag_config.get('security', {}).get('token_env_var', 'PIAG_CHAT_API_TOKEN')
        logger.error(f"Token API Chat manquant. Utilisez --chat-token, définissez-le dans le YAML, ou via {token_env_var}")
        return 1
    
    try:
        logger.info("Récupération des informations de l'apikey...")
        info = get_apikey_info(api_url, chat_token, timeout)
        
        if args.json:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(format_info(info))
        
        return 0
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Détail: {e.response.text}")
        return 1
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
