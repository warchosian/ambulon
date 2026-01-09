
"""Module pour l'intégration avec l'API RAG."""

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

def create_rag_collection(
    project_id: str,
    name: str,
    description: str,
    api_token: str,
    base_url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crée une nouvelle collection (corpus) dans le projet RAG spécifié.

    Args:
        project_id: L'identifiant du projet RAG.
        name: Le nom de la nouvelle collection.
        description: La description de la nouvelle collection.
        api_token: Le token d'autorisation pour l'API RAG (Bearer token).
        base_url: L'URL de base de l'API RAG. Si None, utilise la config.
        config: Dictionnaire de configuration. Si None, utilise la config par défaut.

    Returns:
        La réponse JSON de l'API en cas de succès.

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
        "Authorization": f"Bearer {api_token}",
        "Content-Type": config.get('headers', {}).get('content_type', 'application/json')
    }

    # L'endpoint est pour les collections, avec project_id en query param
    endpoint = config.get('endpoints', {}).get('collections', '/api/v1/collections')
    url = f"{base_url.rstrip('/')}{endpoint}?project_id={project_id}"

    payload = {
        "name": name,
        "description": description
    }

    # Logger si activé dans la config
    if config.get('logging', {}).get('log_requests', False):
        print(f"[DEBUG] Requête POST vers: {url}", file=sys.stderr)
        print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}", file=sys.stderr)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP 4xx/5xx

        result = response.json()

        # Logger la réponse si activé
        if config.get('logging', {}).get('log_responses', False):
            print(f"[DEBUG] Réponse: {json.dumps(result, indent=2)}", file=sys.stderr)

        return result
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la création de la collection RAG: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"Réponse API: {e.response.text}", file=sys.stderr)
        raise

if __name__ == "__main__":
    # Exemple d'utilisation (à remplacer par de vraies valeurs ou des stubs pour les tests)
    # HIÉRARCHIE: Arguments CLI > YAML > Variables d'environnement > Valeurs par défaut
    #
    # python -m ambulon.rag.piag_collection_add --project-id <id> --name "Test" --description "Test" --token <token>
    # ou avec variable d'environnement:
    # export PIAG_RAG_API_TOKEN=<token>
    # python -m ambulon.rag.piag_collection_add --project-id <id> --name "Test" --description "Test"
    import argparse

    parser = argparse.ArgumentParser(
        description="Crée une collection RAG PIAG.",
        epilog="HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut"
    )
    parser.add_argument("--project-id", help="ID du projet RAG (écrase YAML et env).")
    parser.add_argument("--name", help="Nom de la collection (écrase YAML et env).")
    parser.add_argument("--description", help="Description de la collection (écrase YAML et env).")
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

    # 1. PROJECT_ID
    project_id = args.project_id  # Argument CLI (priorité 1)
    if not project_id:
        project_id = config.get('project', {}).get('project_id')  # YAML (priorité 2)
    if not project_id:
        project_id = os.getenv('PIAG_RAG_PROJECT_ID')  # Variable d'env (priorité 3)
    if not project_id:
        print("Erreur: project_id requis. Utilisez --project-id, définissez-le dans le YAML, ou via PIAG_RAG_PROJECT_ID", file=sys.stderr)
        sys.exit(1)

    # 2. NAME
    name = args.name  # Argument CLI (priorité 1)
    if not name:
        name = config.get('project', {}).get('name')  # YAML (priorité 2)
    if not name:
        name = os.getenv('PIAG_RAG_COLLECTION_NAME')  # Variable d'env (priorité 3)
    if not name:
        print("Erreur: name requis. Utilisez --name, définissez-le dans le YAML, ou via PIAG_RAG_COLLECTION_NAME", file=sys.stderr)
        sys.exit(1)

    # 3. DESCRIPTION
    description = args.description  # Argument CLI (priorité 1)
    if not description:
        description = config.get('project', {}).get('description')  # YAML (priorité 2)
    if not description:
        description = os.getenv('PIAG_RAG_COLLECTION_DESCRIPTION')  # Variable d'env (priorité 3)
    if not description:
        print("Erreur: description requise. Utilisez --description, définissez-la dans le YAML, ou via PIAG_RAG_COLLECTION_DESCRIPTION", file=sys.stderr)
        sys.exit(1)

    # 4. TOKEN
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

    # 5. BASE_URL (optionnel, a des valeurs par défaut)
    base_url = args.base_url  # Argument CLI (priorité 1)
    # Si None, sera géré par create_rag_collection qui utilisera le YAML puis la constante

    try:
        result = create_rag_collection(
            project_id=project_id,
            name=name,
            description=description,
            api_token=api_token,
            base_url=base_url,
            config=config
        )
        print("✅ Collection RAG créée avec succès :")
        print(json.dumps(result, indent=2))
    except requests.exceptions.RequestException:
        sys.exit(1)
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)
