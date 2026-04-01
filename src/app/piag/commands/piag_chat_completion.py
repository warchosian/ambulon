"""
Commande CLI pour l'API PIAG Chat Complétion (legacy).

Cette commande utilise l'endpoint /v1/completions (format prompt/completion)
au lieu de /v1/chat/completions (format messages).

Usage:
    ambulon piag-chat-completion --prompt "Bonjour"
    ambulon piag-chat-completion --prompt "Ecris un poème" --max-tokens 100 --temperature 0.8
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
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
            'model': 'mte-api-piag-mistral-medium-latest',
        }
    }
}


def query_completion_api(
    api_url: str,
    chat_token: str,
    model: str,
    prompt: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    timeout: int = 60,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Envoie une requête à l'API PIAG Completions (legacy).
    
    Args:
        api_url: URL de base de l'API
        chat_token: Token API (Bearer)
        model: Nom du modèle
        prompt: Texte d'amorçage
        max_tokens: Nombre maximum de tokens à générer
        temperature: Température pour la génération (0.0 à 1.0)
        timeout: Timeout en secondes
        stream: Activer le streaming (default: False)
        
    Returns:
        Réponse JSON de l'API (ou generator si stream=True)
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {chat_token}'
    }
    
    payload = {
        'model': model,
        'prompt': prompt
    }
    
    if max_tokens is not None:
        payload['max_tokens'] = max_tokens
    if temperature is not None:
        payload['temperature'] = temperature
    if stream:
        payload['stream'] = True
    
    endpoint = f"{api_url.rstrip('/')}/completions"
    
    logger.debug(f"Requête: POST {endpoint}")
    logger.debug(f"Modèle: {model}")
    logger.debug(f"Prompt: {prompt[:50]}...")
    logger.debug(f"Stream: {stream}")
    
    if stream:
        # Mode streaming
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=timeout,
            stream=True
        )
        response.raise_for_status()
        return response.iter_lines()
    else:
        # Mode non-streaming
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()


def process_stream(response_iter) -> str:
    """
    Traite un stream SSE et retourne le texte complet.
    
    Args:
        response_iter: Iterator sur les lignes de la réponse stream
        
    Returns:
        Texte complet assemblé
    """
    full_content = []
    
    for line in response_iter:
        if line:
            line = line.decode('utf-8') if isinstance(line, bytes) else line
            
            if line.startswith('data: '):
                data = line[6:]  # Enlever 'data: '
                
                if data == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(data)
                    # Extraire le texte du delta
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        text = delta.get('content', '') or chunk['choices'][0].get('text', '')
                        if text:
                            full_content.append(text)
                            print(text, end='', flush=True)
                except json.JSONDecodeError:
                    logger.warning(f"Chunk JSON invalide: {data}")
                    continue
    
    print()  # Nouvelle ligne à la fin
    return ''.join(full_content)


def extract_completion(api_response: Dict[str, Any]) -> str:
    """
    Extrait le texte de complétion depuis la réponse API.
    
    Args:
        api_response: Réponse JSON de l'API
        
    Returns:
        Texte de complétion
    """
    try:
        return api_response['choices'][0]['text']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Format de réponse inattendu: {e}")


def main(argv=None):
    """
    Point d'entrée CLI pour piag-chat-completion.
    """
    parser = argparse.ArgumentParser(
        description="API PIAG Chat Complétion (legacy endpoint /completions).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Cette commande utilise l'endpoint legacy /v1/completions (format prompt/completion).
Pour le format conversationnel moderne, utilisez piag-chat-basic-query.

Exemples:
  # Complétion simple
  ambulon piag-chat-completion --prompt "Bonjour"

  # Avec paramètres de génération
  ambulon piag-chat-completion --prompt "Ecris un poème" --max-tokens 100 --temperature 0.8

  # Complétion de code
  ambulon piag-chat-completion --prompt "def factorial(n):" --max-tokens 50

  # Mode streaming (réponse progressive)
  ambulon piag-chat-completion --prompt "Raconte une histoire" --stream

  # Sortie JSON brute
  ambulon piag-chat-completion --prompt "Test" --json
"""
    )
    
    parser.add_argument('-p', '--prompt', required=True, help='Texte d\'amorçage (prompt)')
    parser.add_argument('--max-tokens', type=int, help='Nombre maximum de tokens à générer')
    parser.add_argument('--temperature', type=float, help='Température (0.0 = déterministe, 1.0 = créatif)')
    parser.add_argument('--chat-token', help='Token API PIAG Chat (override config/env)')
    parser.add_argument('--api-url', help='URL de base de l\'API PIAG (override config)')
    parser.add_argument('--model', help='Modèle à utiliser (override config)')
    parser.add_argument('--config', type=Path, default='config/piag.yaml', help='Fichier de configuration YAML')
    parser.add_argument('--json', action='store_true', help='Afficher la réponse JSON brute')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbeux')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout de la requête en secondes')
    parser.add_argument('--stream', action='store_true', help='Activer le streaming de la réponse')
    
    args = parser.parse_args(argv)
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="piag_chat_completion")
    
    # Chargement de la config
    # Ne pas vérifier args.config.exists() car load_app_config cherche dans plusieurs emplacements
    # et peut fallback sur le fichier .example si le fichier principal n'existe pas
    config = load_app_config(str(args.config), DEFAULT_CONFIG)
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

    model = args.model or piag_config.get('model') or DEFAULT_CONFIG['piag']['chat']['model']
    timeout = args.timeout or piag_config.get('api', {}).get('timeout') or DEFAULT_CONFIG['piag']['chat']['api']['timeout']

    # Validation
    if not chat_token:
        token_env_var = piag_config.get('security', {}).get('token_env_var', 'PIAG_CHAT_API_TOKEN')
        logger.error(f"Token API Chat manquant. Utilisez --chat-token, définissez-le dans le YAML, ou via {token_env_var}")
        return 1
    
    try:
        logger.info(f"Envoi de la requête de complétion (modèle: {model}, stream={args.stream})...")
        
        response = query_completion_api(
            api_url, chat_token, model,
            args.prompt, args.max_tokens, args.temperature,
            timeout, stream=args.stream
        )
        
        if args.stream:
            # Mode streaming
            print()
            print("=" * 60)
            print("PROMPT:")
            print("=" * 60)
            print(args.prompt)
            print()
            print("=" * 60)
            print("COMPLETION (STREAMING):")
            print("=" * 60)
            
            completion = process_stream(response)
            
            print("=" * 60)
        elif args.json:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            completion = extract_completion(response)
            print()
            print("=" * 60)
            print("PROMPT:")
            print("=" * 60)
            print(args.prompt)
            print()
            print("=" * 60)
            print("COMPLETION:")
            print("=" * 60)
            print(completion)
            print("=" * 60)
            
            # Informations d'utilisation si disponibles
            usage = response.get('usage', {})
            if usage:
                print(f"\nTokens: prompt={usage.get('prompt_tokens', 'N/A')}, "
                      f"completion={usage.get('completion_tokens', 'N/A')}, "
                      f"total={usage.get('total_tokens', 'N/A')}")
        
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
