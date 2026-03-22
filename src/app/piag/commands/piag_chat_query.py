"""
Commande CLI pour interroger l'API PIAG CHAT (chat/completions) avec des chunks de contexte.

Cette commande utilise l'API Chat/Completion de PIAG (preprod.api.piag.e2.rie.gouv.fr)
pour envoyer des questions avec un contexte (chunks) au modèle LLM.

Conforme à l'API CHAT officielle:
- URL: https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions
- Paramètres: model, messages, stream (optionnel)

Usage:
    # Avec un fichier de chunks JSON (local)
    ambulon piag-chat-query --question "Ma question" --chunks chunks.json

    # Avec un répertoire de chunks (local)
    ambulon piag-chat-query -q "Résume ceci" --chunks-dir ./chunks/

    # Avec sortie dans un fichier
    ambulon piag-chat-query -q "Analyse" -c chunks.json -o reponse.md

Note: Pour récupérer les chunks depuis le RAG, utilisez d'abord 'piag-rag-search'
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from app.core.timeout_parser import parse_timeout, format_timeout

logger = logging.getLogger(__name__)

# Configuration pour l'API PIAG CHAT (chat/completions)
# URL: https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions
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


def load_chunks_from_file(chunks_path: Path) -> List[str]:
    """
    Charge les chunks depuis un fichier JSON.
    
    Args:
        chunks_path: Chemin vers le fichier JSON contenant les chunks
        
    Returns:
        Liste de strings (contenu des chunks)
    """
    with open(chunks_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Supporte différents formats:
    # - {"chunks": ["chunk1", "chunk2"]}
    # - [{"content": "chunk1"}, {"content": "chunk2"}]
    # - ["chunk1", "chunk2"]
    
    if isinstance(data, dict) and 'chunks' in data:
        return data['chunks']
    elif isinstance(data, list):
        chunks = []
        for item in data:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict) and 'content' in item:
                chunks.append(item['content'])
            elif isinstance(item, dict) and 'text' in item:
                chunks.append(item['text'])
        return chunks
    else:
        raise ValueError(f"Format de chunks non reconnu dans {chunks_path}")


def load_chunks_from_directory(chunks_dir: Path) -> List[str]:
    """
    Charge tous les chunks depuis un répertoire de fichiers .txt ou .md.
    
    Args:
        chunks_dir: Répertoire contenant les fichiers de chunks
        
    Returns:
        Liste de strings (contenu des chunks)
    """
    chunks = []
    
    for ext in ['*.txt', '*.md', '*.json']:
        for file_path in chunks_dir.glob(ext):
            if file_path.suffix == '.json':
                try:
                    chunks.extend(load_chunks_from_file(file_path))
                except Exception as e:
                    logger.warning(f"Impossible de charger {file_path}: {e}")
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        chunks.append(content)
    
    return chunks


def build_messages(question: str, chunks: List[str]) -> List[Dict[str, str]]:
    """
    Construit la liste des messages pour l'API PIAG.

    Format RAG optimal (un seul message user avec contexte + question):
        [
            {"role": "system", "content": "Instructions..."},
            {"role": "user", "content": "Contexte: ... Question: ..."}
        ]

    Args:
        question: La question de l'utilisateur
        chunks: Liste des chunks de contexte

    Returns:
        Liste de messages formatés pour l'API
    """
    # Construire le contexte à partir des chunks
    if chunks:
        # Numéroter les chunks pour la traçabilité
        contexte_parts = []
        for i, chunk in enumerate(chunks, 1):
            # Extraire le texte si c'est un dict avec 'text' ou 'content'
            if isinstance(chunk, dict):
                chunk_text = chunk.get('text') or chunk.get('content', str(chunk))
            else:
                chunk_text = str(chunk)

            contexte_parts.append(f"[Extrait {i}]\n{chunk_text}")

        contexte = "\n\n".join(contexte_parts)

        # Créer un message unique avec contexte + question
        messages = [
            {
                "role": "system",
                "content": "Tu es un assistant technique qui répond aux questions en te basant sur le contexte documentaire fourni. Utilise uniquement les informations du contexte pour répondre."
            },
            {
                "role": "user",
                "content": f"Contexte documentaire:\n\n{contexte}\n\n---\n\nQuestion: {question}"
            }
        ]
    else:
        # Pas de contexte, question simple
        messages = [{"role": "user", "content": question}]

    return messages


def query_piag_chat_api(
    api_url: str,
    chat_token: str,
    model: str,
    messages: List[Dict[str, str]],
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Envoie une requête à l'API PIAG CHAT (chat/completions).
    
    Args:
        api_url: URL de l'API Chat (ex: https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions)
        chat_token: Token API (Bearer token)
        model: Nom du modèle à utiliser
        messages: Liste des messages
        timeout: Timeout en secondes
        
    Returns:
        Réponse JSON de l'API
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {chat_token}'
    }
    
    payload = {
        'model': model,
        'messages': messages
    }
    
    logger.debug(f"Requête API: {api_url}")
    logger.debug(f"Modèle: {model}")
    logger.debug(f"Nombre de messages: {len(messages)}")
    
    # Convertir timeout millisecondes → secondes pour requests
    timeout_seconds = timeout / 1000.0

    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=timeout_seconds
    )
    
    response.raise_for_status()
    return response.json()


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
    Point d'entrée CLI pour piag-chat-query.
    
    Configuration Hierarchy (CLI > YAML > ENV > Defaults):
        1. Arguments CLI (--api-url, --api-key, --model)
        2. Fichier YAML (--config)
        3. Variables d'environnement (PIAG_API_KEY)
        4. Valeurs par défaut
    """
    parser = argparse.ArgumentParser(
        description="Interroger l'API PIAG avec des chunks de documents comme contexte.",
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
  # Avec un fichier de chunks JSON (local)
  ambulon piag-chat-query --question "Quelle est la procédure ?" --chunks chunks.json

  # Avec une question depuis un fichier
  ambulon piag-chat-query --question-file question.txt --chunks chunks.json

  # Avec un répertoire de chunks (local)
  ambulon piag-chat-query -q "Résume ce document" --chunks-dir ./rag/chunks/

  # Avec sortie dans un fichier
  ambulon piag-chat-query -q "Analyse" --chunks chunks.json -o reponse.md

  # Spécifier un modèle différent
  ambulon piag-chat-query -q "Question" --chunks chunks.json --model mte-api-piag-mistral-large-latest

  # Workflow complet RAG + CHAT (deux étapes):
  # 1. Récupérer les chunks avec piag-rag-search
  ambulon piag-rag-search --collection-name PNM3_SIREINES -q "architecture" -o chunks.json
  # 2. Poser la question avec les chunks
  ambulon piag-chat-query -q "Quelle est l'architecture ?" --chunks chunks.json
"""
    )
    
    parser.add_argument('-q', '--question', '--query', dest='question', help='Question à poser au modèle (texte direct)')
    parser.add_argument('--question-file', type=Path, help='Fichier texte contenant la question à poser')
    parser.add_argument('-c', '--chunks', type=Path, help='Fichier JSON contenant les chunks (local)')
    parser.add_argument('-d', '--chunks-dir', type=Path, help='Répertoire contenant les fichiers de chunks (local)')
    parser.add_argument('-o', '--output', type=Path, help='Fichier de sortie pour la réponse (default: stdout)')
    parser.add_argument('--api-url', help='URL de l\'API PIAG Completion (override config)')
    parser.add_argument('--chat-token', help='Token API PIAG Chat (override config/env)')
    parser.add_argument('--model', help='Modèle à utiliser (override config)')
    parser.add_argument('--config', type=Path, default='config/piag.yaml', help='Fichier de configuration YAML')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbeux')
    parser.add_argument('--timeout', default='60s', help='Timeout de la requête (default: 60s). Accepte: 10000, 10000ms, 10s, 2m')
    parser.add_argument('--max-retries', default='3', help='Nombre max de tentatives en cas d\'erreur (default: 3). Accepte: 5, 10')
    parser.add_argument('--retry-delay', default='5s', help='Délai entre les tentatives (default: 5s). Accepte: 5s, 30s, 1m')

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="piag_query")

    # Validation: au moins --question ou --question-file requis
    if not args.question and not args.question_file:
        logger.error("Spécifiez --question (texte) ou --question-file (fichier)")
        return 1

    # Si les deux sont fournis, --question a la priorité
    if args.question and args.question_file:
        logger.warning("--question et --question-file fournis, --question a la priorité")

    # Charger la question depuis le fichier si nécessaire
    question_text = args.question
    if not question_text and args.question_file:
        if not args.question_file.exists():
            logger.error(f"Fichier question introuvable: {args.question_file}")
            return 1
        with open(args.question_file, 'r', encoding='utf-8') as f:
            question_text = f.read().strip()
        logger.info(f"Question chargée depuis: {args.question_file}")

    if not question_text:
        logger.error("La question est vide")
        return 1
    
    # Chargement de la config
    config = load_app_config(str(args.config) if args.config.exists() else None, DEFAULT_CONFIG)
    piag_config = config.get('piag', {}).get('chat', {})
    
    # Récupération des valeurs (CLI > YAML > ENV > Defaults)
    # URL de l'API Chat (chat/completions)
    chat_api_url = args.api_url or piag_config.get('api', {}).get('base_url') or DEFAULT_CONFIG['piag']['chat']['api']['base_url']

    # Token avec hiérarchie: CLI > YAML > ENV (via token_env_var) > Erreur
    chat_token = args.chat_token  # CLI (priorité 1)
    if not chat_token:
        chat_token = piag_config.get('security', {}).get('token')  # YAML (priorité 2)
    if not chat_token:
        # Variable d'env (priorité 3)
        token_env_var = piag_config.get('security', {}).get('token_env_var', 'PIAG_CHAT_API_TOKEN')
        chat_token = os.getenv(token_env_var)

    model = args.model or piag_config.get('model') or DEFAULT_CONFIG['piag']['chat']['model']

    # Parse timeout avec suffixes (ms, s, m)
    timeout_value = args.timeout or piag_config.get('api', {}).get('timeout') or DEFAULT_CONFIG['piag']['chat']['api']['timeout']
    try:
        timeout = parse_timeout(timeout_value)  # Convertit en millisecondes
    except ValueError as e:
        logger.error(f"Erreur timeout: {e}")
        return 1

    # Parse max_retries (nombre entier)
    try:
        max_retries = int(args.max_retries)
    except ValueError:
        logger.error(f"Erreur max_retries: doit être un nombre entier")
        return 1

    # Parse retry_delay avec suffixes (ms, s, m)
    try:
        retry_delay_ms = parse_timeout(args.retry_delay)  # Convertit en millisecondes
        retry_delay_seconds = retry_delay_ms / 1000.0  # Convertit en secondes pour time.sleep()
    except ValueError as e:
        logger.error(f"Erreur retry_delay: {e}")
        return 1

    # Validation
    if not chat_token:
        token_env_var = piag_config.get('security', {}).get('token_env_var', 'PIAG_CHAT_API_TOKEN')
        logger.error(f"Token API Chat manquant. Utilisez --chat-token, définissez-le dans le YAML, ou via {token_env_var}")
        return 1

    # Validation: chunks requis (fichier ou répertoire)
    if not args.chunks and not args.chunks_dir:
        logger.error("Spécifiez --chunks (fichier) ou --chunks-dir (répertoire)")
        logger.info("Pour récupérer les chunks depuis le RAG, utilisez d'abord 'piag-rag-search'")
        return 1

    try:
        # Chargement des chunks (depuis fichier ou répertoire local)
        logger.info("Chargement des chunks...")

        if args.chunks:
            chunks = load_chunks_from_file(args.chunks)
        else:
            chunks = load_chunks_from_directory(args.chunks_dir)
        
        logger.info(f"{len(chunks)} chunks chargés")
        
        if not chunks:
            logger.error("Aucun chunk trouvé")
            return 1
        
        # Construction des messages
        messages = build_messages(question_text, chunks)
        logger.debug(f"Messages construits: {len(messages)}")

        # Appel API avec retry
        answer = None
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    logger.info(f"Tentative {attempt}/{max_retries}...")
                else:
                    logger.info("Appel de l'API PIAG...")

                # Appel API Chat (chat/completions)
                response = query_piag_chat_api(chat_api_url, chat_token, model, messages, timeout)

                # Extraction de la réponse
                answer = extract_answer(response)

                # Succès !
                if attempt > 1:
                    logger.info(f"✅ Succès à la tentative {attempt}/{max_retries}")
                break

            except requests.exceptions.HTTPError as e:
                if attempt < max_retries:
                    logger.warning(f"❌ Erreur (tentative {attempt}/{max_retries}): {e}")
                    logger.info(f"⏳ Nouvelle tentative dans {format_timeout(int(retry_delay_ms))}...")
                    time.sleep(retry_delay_seconds)
                else:
                    # Dernière tentative échouée, lever l'erreur
                    raise

        if answer is None:
            raise Exception("Aucune réponse obtenue après toutes les tentatives")
        
        # Sortie
        if args.output:
            # Créer le répertoire parent si nécessaire
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(answer)
            logger.info(f"Réponse sauvegardée dans: {args.output}")
        else:
            print(answer)
        
        return 0
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur API: {e}")
        return 1
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
