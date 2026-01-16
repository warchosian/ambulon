"""Module CLI pour créer une collection RAG PIAG."""

import os
import sys
import argparse
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    """
    Script CLI pour créer une collection RAG PIAG.

    HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut

    Exemple d'utilisation:
        python -m app.piag.commands.piag_collection_add --project-id <id> --name "Test" --description "Test" --token <token>

    Ou avec variable d'environnement:
        export PIAG_RAG_API_TOKEN=<token>
        python -m app.piag.commands.piag_collection_add --project-id <id> --name "Test" --description "Test"
    """
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

    args = parser.parse_args(argv)

    # Charger la configuration personnalisée si spécifiée
    config = None
    if args.config:
        try:
            config = load_config(args.config)
            print(f"Configuration chargée depuis: {args.config}")
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}", file=sys.stderr)
            return 1
    else:
        try:
            config = load_config()
        except Exception:
            config = {}

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
        return 1

    # 2. NAME
    name = args.name  # Argument CLI (priorité 1)
    if not name:
        name = config.get('project', {}).get('name')  # YAML (priorité 2)
    if not name:
        name = os.getenv('PIAG_RAG_COLLECTION_NAME')  # Variable d'env (priorité 3)
    if not name:
        print("Erreur: name requis. Utilisez --name, définissez-le dans le YAML, ou via PIAG_RAG_COLLECTION_NAME", file=sys.stderr)
        return 1

    # 3. DESCRIPTION
    description = args.description  # Argument CLI (priorité 1)
    if not description:
        description = config.get('project', {}).get('description')  # YAML (priorité 2)
    if not description:
        description = os.getenv('PIAG_RAG_COLLECTION_DESCRIPTION')  # Variable d'env (priorité 3)
    if not description:
        print("Erreur: description requise. Utilisez --description, définissez-la dans le YAML, ou via PIAG_RAG_COLLECTION_DESCRIPTION", file=sys.stderr)
        return 1

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
        return 1

    # 5. BASE_URL (optionnel, a des valeurs par défaut)
    base_url = args.base_url  # Argument CLI (priorité 1)

    try:
        # Créer le client PIAG
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)

        # Créer la collection
        result = client.create_collection(
            project_id=project_id,
            name=name,
            description=description
        )

        print("Collection RAG créée avec succès :")
        import json
        print(json.dumps(result, indent=2))
        return 0

    except Exception as e:
        print(f"Une erreur est survenue : {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
