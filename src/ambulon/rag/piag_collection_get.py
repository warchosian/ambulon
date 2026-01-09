
"""Module pour récupérer les informations d'une collection RAG PIAG."""

import json
import os
import sys
import yaml
import requests
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Charge la configuration depuis le fichier piag_rag.yaml.

    Args:
        config_path: Chemin personnalisé vers le fichier de configuration.
                     Si None, utilise config/piag_rag.yaml à la racine du projet.

    Returns:
        Dictionnaire contenant la configuration.

    Raises:
        FileNotFoundError: Si le fichier de configuration n'est pas trouvé.
        yaml.YAMLError: Si le fichier YAML est mal formé.
    """
    if config_path is None:
        # Trouver le répertoire racine du projet (où se trouve config/)
        current_dir = Path(__file__).parent
        config_path = current_dir.parent.parent.parent / "config" / "piag_rag.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

# Charger la configuration par défaut
try:
    _DEFAULT_CONFIG = load_config()
    RAG_API_BASE_URL = _DEFAULT_CONFIG['api']['base_url']
except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
    print(f"Avertissement: Impossible de charger la configuration: {e}", file=sys.stderr)
    # Fallback sur l'URL en dur
    RAG_API_BASE_URL = "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
    _DEFAULT_CONFIG = None

def get_collection(
    collection_id: str,
    api_token: str,
    base_url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Récupère les informations d'une collection RAG PIAG.

    Args:
        collection_id: L'identifiant de la collection RAG.
        api_token: Le token d'autorisation pour l'API RAG (Bearer token).
        base_url: L'URL de base de l'API RAG. Si None, utilise la config.
        config: Dictionnaire de configuration. Si None, utilise la config par défaut.

    Returns:
        La réponse JSON de l'API contenant les informations de la collection.

    Raises:
        requests.exceptions.RequestException: En cas d'erreur réseau ou de réponse HTTP non-2xx.
    """
    # Utiliser la configuration fournie ou la configuration par défaut
    if config is None:
        config = _DEFAULT_CONFIG or {}

    # Déterminer l'URL de base
    if base_url is None:
        base_url = config.get('api', {}).get('base_url', RAG_API_BASE_URL)

    # Récupérer le timeout depuis la config
    timeout = config.get('api', {}).get('timeout', 30)

    # Construire les headers depuis la config
    headers = {
        "accept": config.get('headers', {}).get('accept', 'application/json'),
        "Authorization": f"Bearer {api_token}"
    }

    # L'endpoint pour récupérer une collection
    endpoint = config.get('endpoints', {}).get('collection_detail', '/api/v1/collections/{collection_id}')
    # Remplacer {collection_id} si présent dans l'endpoint
    endpoint = endpoint.replace('{collection_id}', collection_id)

    url = f"{base_url.rstrip('/')}{endpoint}"

    # Logger si activé dans la config
    if config.get('logging', {}).get('log_requests', False):
        print(f"[DEBUG] Requête GET vers: {url}", file=sys.stderr)

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP 4xx/5xx

        result = response.json()

        # Logger la réponse si activé
        if config.get('logging', {}).get('log_responses', False):
            print(f"[DEBUG] Réponse: {json.dumps(result, indent=2)}", file=sys.stderr)

        return result
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de la collection: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Réponse API: {e.response.text}", file=sys.stderr)
        raise

if __name__ == "__main__":
    # Exemple d'utilisation
    # HIÉRARCHIE: Arguments CLI > YAML > Variables d'environnement > Valeurs par défaut
    #
    # python -m ambulon.rag.piag_rag_get --collection-id <id> --token <token>
    # ou avec variable d'environnement:
    # export PIAG_RAG_API_TOKEN=<token>
    # python -m ambulon.rag.piag_rag_get --collection-id <id>
    import argparse

    parser = argparse.ArgumentParser(
        description="Récupère les informations d'une collection RAG PIAG.",
        epilog="HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut"
    )
    parser.add_argument("--collection-id", help="ID de la collection RAG (écrase YAML et env).")
    parser.add_argument("--token", help="Token API RAG Bearer (écrase YAML et env).")
    parser.add_argument("--base-url", help="URL de base de l'API RAG (écrase YAML).")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug (logging détaillé).")

    args = parser.parse_args()

    # Charger la configuration personnalisée si spécifiée
    config = None
    if args.config:
        try:
            config = load_config(args.config)
            print(f"Configuration chargée depuis: {args.config}")
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        config = _DEFAULT_CONFIG if _DEFAULT_CONFIG else {}

    # Activer le debug si demandé
    if args.debug and config:
        if 'logging' not in config:
            config['logging'] = {}
        config['logging']['enable_debug'] = True
        config['logging']['log_requests'] = True
        config['logging']['log_responses'] = True

    # HIÉRARCHIE: Arguments CLI > YAML > Variables d'environnement > Erreur

    # 1. COLLECTION_ID
    collection_id = args.collection_id  # Argument CLI (priorité 1)
    if not collection_id:
        collection_id = config.get('project', {}).get('collection_id')  # YAML (priorité 2)
    if not collection_id:
        collection_id = os.getenv('PIAG_RAG_COLLECTION_ID')  # Variable d'env (priorité 3)
    if not collection_id:
        print("Erreur: collection_id requis. Utilisez --collection-id, définissez-le dans le YAML, ou via PIAG_RAG_COLLECTION_ID", file=sys.stderr)
        sys.exit(1)

    # 2. TOKEN
    api_token = args.token  # Argument CLI (priorité 1)
    if not api_token:
        api_token = config.get('security', {}).get('token')  # YAML (priorité 2) - NON RECOMMANDÉ
    if not api_token:
        # Variable d'env (priorité 3)
        token_env_var = config.get('security', {}).get('token_env_var', 'PIAG_RAG_API_TOKEN')
        api_token = os.getenv(token_env_var)
    if not api_token:
        print(f"Erreur: Token API requis. Utilisez --token, définissez-le dans le YAML (non recommandé), ou via {token_env_var}", file=sys.stderr)
        sys.exit(1)

    # 3. BASE_URL (optionnel, a des valeurs par défaut)
    base_url = args.base_url  # Argument CLI (priorité 1)
    # Si None, sera géré par get_collection qui utilisera le YAML puis la constante

    try:
        result = get_collection(
            collection_id=collection_id,
            api_token=api_token,
            base_url=base_url,
            config=config
        )

        print("✅ Informations de la collection récupérées avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except requests.exceptions.RequestException:
        sys.exit(1)
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)
