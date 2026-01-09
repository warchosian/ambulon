
"""Module pour téléverser des documents vers une collection RAG PIAG."""

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

def upload_document(
    collection_id: str,
    file_path: str,
    api_token: str,
    base_url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Téléverse un document vers une collection RAG PIAG.

    Args:
        collection_id: L'identifiant de la collection RAG.
        file_path: Chemin vers le fichier à téléverser.
        api_token: Le token d'autorisation pour l'API RAG (Bearer token).
        base_url: L'URL de base de l'API RAG. Si None, utilise la config.
        config: Dictionnaire de configuration. Si None, utilise la config par défaut.

    Returns:
        La réponse JSON de l'API en cas de succès.

    Raises:
        FileNotFoundError: Si le fichier à téléverser n'existe pas.
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

    # Vérifier que le fichier existe
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {file_path}")

    # Construire les headers
    headers = {
        "accept": config.get('headers', {}).get('accept', 'application/json'),
        "Authorization": f"Bearer {api_token}"
    }

    # L'endpoint pour téléverser un document
    endpoint = config.get('endpoints', {}).get('documents_upload', f'/api/v1/collections/{collection_id}/documents-upload-slow')
    # Remplacer {collection_id} si présent dans l'endpoint
    endpoint = endpoint.replace('{collection_id}', collection_id)

    url = f"{base_url.rstrip('/')}{endpoint}"

    # Déterminer le type MIME du fichier
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    # Logger si activé dans la config
    if config.get('logging', {}).get('log_requests', False):
        print(f"[DEBUG] Requête POST vers: {url}", file=sys.stderr)
        print(f"[DEBUG] Fichier: {file_path} (type: {mime_type})", file=sys.stderr)

    try:
        # Ouvrir le fichier et l'envoyer
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path_obj.name, f, mime_type)
            }

            response = requests.post(url, headers=headers, files=files, timeout=timeout)
            response.raise_for_status()  # Lève une exception pour les codes d'état HTTP 4xx/5xx

        result = response.json()

        # Logger la réponse si activé
        if config.get('logging', {}).get('log_responses', False):
            print(f"[DEBUG] Réponse: {json.dumps(result, indent=2)}", file=sys.stderr)

        return result
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléversement du document: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Réponse API: {e.response.text}", file=sys.stderr)
        raise

if __name__ == "__main__":
    # Exemple d'utilisation
    # HIÉRARCHIE: Arguments CLI > YAML > Variables d'environnement > Valeurs par défaut
    #
    # python -m ambulon.rag.piag_doc_upload --collection-id <id> --file <fichier> --token <token>
    # ou avec variable d'environnement:
    # export PIAG_RAG_API_TOKEN=<token>
    # python -m ambulon.rag.piag_doc_upload --collection-id <id> --file <fichier>
    import argparse

    parser = argparse.ArgumentParser(
        description="Téléverse un document vers une collection RAG PIAG.",
        epilog="HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut"
    )
    parser.add_argument("--collection-id", help="ID de la collection RAG (écrase YAML et env).")
    parser.add_argument("--file", help="Chemin vers le fichier à téléverser (requis).")
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
        collection_id = config.get('upload', {}).get('collection_id')  # YAML (priorité 2)
    if not collection_id:
        collection_id = os.getenv('PIAG_RAG_COLLECTION_ID')  # Variable d'env (priorité 3)
    if not collection_id:
        print("Erreur: collection_id requis. Utilisez --collection-id, définissez-le dans le YAML, ou via PIAG_RAG_COLLECTION_ID", file=sys.stderr)
        sys.exit(1)

    # 2. FILE
    file_path = args.file  # Argument CLI (priorité 1)
    if not file_path:
        file_path = config.get('upload', {}).get('file_path')  # YAML (priorité 2)
    if not file_path:
        file_path = os.getenv('PIAG_RAG_UPLOAD_FILE')  # Variable d'env (priorité 3)
    if not file_path:
        print("Erreur: fichier requis. Utilisez --file, définissez-le dans le YAML, ou via PIAG_RAG_UPLOAD_FILE", file=sys.stderr)
        sys.exit(1)

    # 3. TOKEN
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

    # 4. BASE_URL (optionnel, a des valeurs par défaut)
    base_url = args.base_url  # Argument CLI (priorité 1)
    # Si None, sera géré par upload_document qui utilisera le YAML puis la constante

    try:
        result = upload_document(
            collection_id=collection_id,
            file_path=file_path,
            api_token=api_token,
            base_url=base_url,
            config=config
        )

        print("✅ Document téléversé avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException:
        sys.exit(1)
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)
