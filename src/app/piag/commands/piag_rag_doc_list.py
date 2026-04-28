"""Module CLI pour lister les documents d'une collection RAG PIAG."""

from pathlib import Path
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    """
    Point d'entrée principal pour la commande piag-doc-list.

    Args:
        argv: Arguments CLI (list of str), ou None pour utiliser sys.argv

    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)
    """
    parser = argparse.ArgumentParser(
        description="Liste les documents d'une collection RAG PIAG."
    )
    parser.add_argument(
        "--collection-name",
        help="Nom de la collection RAG (résolution automatique vers ID).",
    )
    parser.add_argument(
        "--collection-id",
        help="ID exact de la collection RAG (pas de résolution, plus rapide).",
    )
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--limit", type=int, help="Nombre maximum de résultats.")
    parser.add_argument("--offset", type=int, help="Nombre de résultats à sauter.")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument(
        "--config", help="Chemin vers un fichier de configuration personnalisé."
    )
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    args = parser.parse_args(argv)

    # Charger la configuration depuis le fichier ou les variables d'environnement
    config = (
        load_config(args.config)
        if args.config
        else (load_config() if Path("config/piag.yaml").exists() else {})
    )

    if args.debug:
        config.setdefault("piag", {}).setdefault("rag", {}).setdefault(
            "logging", {}
        ).update({"enable_debug": True, "log_requests": True, "log_responses": True})

    # Hiérarchie de configuration pour les paramètres
    collection_name_or_id = (
        args.collection_name
        or os.getenv("PIAG_RAG_COLLECTION_NAME")
        or config.get("piag", {})
        .get("rag", {})
        .get("project", {})
        .get("collection_name")
    )
    collection_id = (
        args.collection_id
        or os.getenv("PIAG_RAG_COLLECTION_ID")
        or config.get("piag", {}).get("rag", {}).get("project", {}).get("collection_id")
    )
    project_id = (
        args.project_id
        or config.get("piag", {}).get("rag", {}).get("project", {}).get("project_id")
        or os.getenv("PIAG_RAG_PROJECT_ID")
    )
    api_token = (
        args.token
        or config.get("piag", {}).get("rag", {}).get("security", {}).get("token")
        or os.getenv("PIAG_RAG_API_TOKEN")
    )
    base_url = (
        args.base_url
        or config.get("piag", {}).get("rag", {}).get("api", {}).get("base_url")
        or os.getenv("PIAG_RAG_BASE_URL")
    )
    limit = (
        args.limit
        or config.get("listing", {}).get("default_limit")
        or os.getenv("PIAG_RAG_LIMIT")
        or 20
    )
    offset = (
        args.offset
        or config.get("listing", {}).get("default_offset")
        or os.getenv("PIAG_RAG_OFFSET")
        or 0
    )

    # Validations
    if not collection_name_or_id and not collection_id:
        print(
            "Erreur: La collection est requise (--collection-name, --collection-id, config, ou PIAG_RAG_COLLECTION_NAME/PIAG_RAG_COLLECTION_ID)",
            file=sys.stderr,
        )
        return 1
    if not api_token:
        print(
            "Erreur: Token API requis (--token, config, ou PIAG_RAG_API_TOKEN)",
            file=sys.stderr,
        )
        return 1
    if not project_id:
        print(
            "Erreur: Project ID requis (--project-id, config, ou PIAG_RAG_PROJECT_ID)",
            file=sys.stderr,
        )
        return 1

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)

        # Résoudre collection : si --collection-id fourni, utiliser directement, sinon résoudre
        if collection_id:
            resolved_collection_id = collection_id
        else:
            resolved_collection_id = client.resolve_collection_id(
                collection_name_or_id, project_id
            )

        # Lister les documents avec l'ID résolu
        result = client.list_documents(
            resolved_collection_id, limit=int(limit), offset=int(offset)
        )

        print("\nDocuments récupérés avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    except (ValueError, Exception) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
