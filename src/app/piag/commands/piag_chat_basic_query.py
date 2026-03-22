"""
Commande CLI pour interroger l'API PIAG CHAT (chat/completions) en mode basique.

Cette commande permet d'envoyer des questions simples au modèle LLM sans contexte (chunks).
C'est l'équivalent d'une conversation directe avec le modèle.

URL: https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions

Usage:
    ambulon piag-chat-basic-query --question "Quelle est la capitale de la France ?"
    ambulon piag-chat-basic-query -q "Explique-moi la photosynthèse" -o reponse.md
    ambulon piag-chat-basic-query -q "Résume ce texte: Bonjour le monde" --model mte-api-piag-mistral-large-latest
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging

# Forcer l'encodage UTF-8 pour stdout et stderr (Windows compatibility)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'piag': {
        'chat': {
            'api': {
                'base_url': 'https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions',
                'timeout': 60,
            },
            'security': {
                'token': '',  # Ne pas lire l'env ici, c'est géré dans main()
            },
            'model': 'mte-api-piag-mistral-medium-latest',
        }
    }
}


def query_piag_chat_api(
    api_url: str,
    chat_token: str,
    model: str,
    messages: List[Dict[str, str]],
    timeout: int = 60,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Envoie une requête à l'API PIAG CHAT (chat/completions).
    
    Args:
        api_url: URL de l'API Chat
        chat_token: Token API (Bearer token)
        model: Nom du modèle à utiliser
        messages: Liste des messages
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
        'messages': messages
    }
    
    if stream:
        payload['stream'] = True
    
    logger.debug(f"Requête API Chat: {api_url}")
    logger.debug(f"Modèle: {model}")
    logger.debug(f"Nombre de messages: {len(messages)}")
    logger.debug(f"Stream: {stream}")
    
    if stream:
        # Mode streaming : retourne un generator
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=timeout,
            stream=True
        )
        response.raise_for_status()
        return response.iter_lines()
    else:
        # Mode non-streaming : retourne la réponse JSON complète
        response = requests.post(
            api_url,
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
            
            # Ignorer les lignes vides ou les commentaires SSE
            if line.startswith('data: '):
                data = line[6:]  # Enlever 'data: '
                
                if data == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(data)
                    # Extraire le delta de content
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content.append(content)
                            # Afficher immédiatement pour l'effet "streaming"
                            print(content, end='', flush=True)
                except json.JSONDecodeError:
                    logger.warning(f"Chunk JSON invalide: {data}")
                    continue
    
    print()  # Nouvelle ligne à la fin
    return ''.join(full_content)


def extract_answer(api_response: Dict[str, Any]) -> str:
    """
    Extrait la réponse du modèle depuis la réponse API.
    
    Args:
        api_response: Réponse JSON de l'API
        
    Returns:
        Texte de la réponse
    """
    try:
        return api_response['choices'][0]['message']['content']
    except (KeyError, IndexError) as e:
        raise ValueError(f"Format de réponse inattendu: {e}")


def main(argv=None):
    """
    Point d'entrée CLI pour piag-chat-basic-query.
    
    Configuration Hierarchy (CLI > YAML > ENV > Defaults):
        1. Arguments CLI (--api-url, --api-key, --model)
        2. Fichier YAML (--config)
        3. Variables d'environnement (PIAG_API_KEY)
        4. Valeurs par défaut
    """
    parser = argparse.ArgumentParser(
        description="Interroger l'API PIAG CHAT (chat/completions) en mode basique sans contexte.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (priorité décroissante):
  1. Arguments CLI (--api-url, --api-key, --model)
  2. Fichier YAML (--config)
  3. Variables d'environnement (PIAG_API_KEY)
  4. Valeurs par défaut

Variables d'environnement:
  PIAG_CHAT_API_TOKEN   Token API pour l'authentification Bearer (API Chat)

Exemples:
  # Question simple
  ambulon piag-chat-basic-query --question "Quelle est la capitale de la France ?"

  # Avec sortie dans un fichier
  ambulon piag-chat-basic-query -q "Explique la photosynthèse" -o reponse.md

  # Conversation multi-tours (contexte simple)
  ambulon piag-chat-basic-query -q "Bonjour" --system "Tu es un expert en histoire"

  # Spécifier un modèle différent
  ambulon piag-chat-basic-query -q "Question" --model mte-api-piag-mistral-large-latest

  # Activer le streaming (réponse progressive)
  ambulon piag-chat-basic-query -q "Raconte une histoire" --stream
"""
    )
    
    parser.add_argument('-q', '--question', required=True, help='Question à poser au modèle')
    parser.add_argument('--system', help='Message système pour définir le comportement du modèle')
    parser.add_argument('-o', '--output', type=Path, help='Fichier de sortie pour la réponse (default: stdout)')
    parser.add_argument('--api-url', help='URL de l\'API PIAG Chat (override config)')
    parser.add_argument('--chat-token', help='Token API PIAG Chat (override config/env)')
    parser.add_argument('--model', help='Modèle à utiliser (override config)')
    parser.add_argument('--config', type=Path, default='config/piag.yaml', help='Fichier de configuration YAML')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbeux')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout de la requête en secondes (default: 60)')
    parser.add_argument('--stream', action='store_true', help='Activer le streaming de la réponse')
    
    args = parser.parse_args(argv)
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="piag_chat_basic_query")
    
    # Chargement de la config
    config = load_app_config(str(args.config) if args.config.exists() else None, DEFAULT_CONFIG)
    piag_config = config.get('piag', {}).get('chat', {})
    
    # Récupération des valeurs (CLI > YAML > ENV > Defaults)
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
        # Construction des messages
        messages = []
        
        # Message système optionnel
        if args.system:
            messages.append({"role": "system", "content": args.system})
            logger.debug(f"Message système ajouté: {args.system[:50]}...")
        
        # Message utilisateur (question)
        messages.append({"role": "user", "content": args.question})
        logger.debug(f"Question: {args.question}")
        
        # Appel API
        logger.info(f"Envoi de la requête à l'API PIAG Chat (modèle: {model})...")
        
        response = query_piag_chat_api(api_url, chat_token, model, messages, timeout, stream=args.stream)
        
        if args.stream:
            # Mode streaming
            print()
            print("=" * 60)
            print("RÉPONSE DU MODÈLE (STREAMING)")
            print("=" * 60)
            
            answer = process_stream(response)
            
            print("=" * 60)
            
            # Sauvegarde si demandée
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(answer)
                logger.info(f"Réponse sauvegardée dans: {args.output}")
        else:
            # Mode non-streaming
            # Extraction de la réponse
            answer = extract_answer(response)
            
            # Informations sur l'utilisation (si disponible)
            usage = response.get('usage', {})
            if usage:
                prompt_tokens = usage.get('prompt_tokens', 'N/A')
                completion_tokens = usage.get('completion_tokens', 'N/A')
                total_tokens = usage.get('total_tokens', 'N/A')
                logger.info(f"Tokens utilisés: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}")
            
            # Sortie
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(answer)
                logger.info(f"Réponse sauvegardée dans: {args.output}")
                print(f"\n✓ Réponse sauvegardée: {args.output}")
            else:
                print()
                print("=" * 60)
                print("RÉPONSE DU MODÈLE")
                print("=" * 60)
                print(answer)
                print("=" * 60)
        
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
