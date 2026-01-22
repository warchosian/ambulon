"""Module CLI pour téléverser un document vers une collection RAG PIAG."""

import os
import sys
import json
import argparse
from pathlib import Path
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    """
    Point d'entrée principal pour la commande piag-doc-upload.

    Args:
        argv: Arguments CLI (list of str), ou None pour utiliser sys.argv

    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)
    """
    parser = argparse.ArgumentParser(description="Téléverse un ou plusieurs documents vers une collection RAG PIAG.")
    parser.add_argument("--collection-name", help="Nom de la collection RAG (résolution automatique vers ID).")
    parser.add_argument("--collection-id", help="ID exact de la collection RAG (pas de résolution, plus rapide).")
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--file", help="Chemin vers le fichier à téléverser.")
    parser.add_argument("--folder", help="Chemin vers un répertoire contenant les fichiers à téléverser.")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    args = parser.parse_args(argv)

    config = load_config(args.config)

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    # Vérification mutually exclusive: --file XOR --folder
    if args.file and args.folder:
        print("Erreur: Utilisez soit --file soit --folder, pas les deux", file=sys.stderr)
        return 1
    if not args.file and not args.folder:
        print("Erreur: --file ou --folder requis", file=sys.stderr)
        return 1

    # Hiérarchie de configuration
    collection_name_or_id = args.collection_name or os.getenv('PIAG_RAG_COLLECTION_NAME') or config.get('project', {}).get('collection_name')
    collection_id = args.collection_id or os.getenv('PIAG_RAG_COLLECTION_ID') or config.get('project', {}).get('collection_id')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')
    project_id = args.project_id or config.get('project', {}).get('project_id') or os.getenv('PIAG_RAG_PROJECT_ID')
    base_url = args.base_url or config.get('api', {}).get('base_url') or os.getenv('PIAG_RAG_BASE_URL')

    if not collection_name_or_id and not collection_id:
        print("Erreur: La collection est requise (--collection-name, --collection-id, config, ou PIAG_RAG_COLLECTION_NAME/PIAG_RAG_COLLECTION_ID)", file=sys.stderr)
        return 1
    if not api_token:
        print("Erreur: Token API requis (--token, config, ou PIAG_RAG_API_TOKEN)", file=sys.stderr)
        return 1
    if not project_id:
        print("Erreur: Project ID requis (--project-id, config, ou PIAG_RAG_PROJECT_ID)", file=sys.stderr)
        return 1

    # Déterminer la liste des fichiers à uploader
    if args.file:
        files_to_upload = [Path(args.file)]
    else:  # args.folder
        folder_path = Path(args.folder)
        if not folder_path.exists():
            print(f"Erreur: Le répertoire n'existe pas: {args.folder}", file=sys.stderr)
            return 1
        if not folder_path.is_dir():
            print(f"Erreur: Le chemin n'est pas un répertoire: {args.folder}", file=sys.stderr)
            return 1

        # Récupérer tous les fichiers du répertoire (pas les sous-dossiers)
        files_to_upload = [f for f in folder_path.iterdir() if f.is_file()]

        if not files_to_upload:
            print(f"Erreur: Aucun fichier trouvé dans le répertoire: {args.folder}", file=sys.stderr)
            return 1

        print(f"Fichiers trouvés dans {args.folder}: {len(files_to_upload)}")

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)

        # Résoudre collection : si --collection-id fourni, utiliser directement, sinon résoudre
        if collection_id:
            resolved_collection_id = collection_id
        else:
            resolved_collection_id = client.resolve_collection_id(collection_name_or_id, project_id)

        # Uploader chaque fichier
        results = []
        success_count = 0
        error_count = 0

        for file_path in files_to_upload:
            try:
                print(f"\nTéléversement de: {file_path.name}... ", end="", flush=True)
                result = client.upload_document(resolved_collection_id, str(file_path))
                results.append({
                    'file': file_path.name,
                    'status': 'success',
                    'result': result
                })
                success_count += 1
                print("✓")
            except Exception as e:
                results.append({
                    'file': file_path.name,
                    'status': 'error',
                    'error': str(e)
                })
                error_count += 1
                print(f"✗ Erreur: {e}")

        # Affichage du récapitulatif
        print(f"\n{'='*60}")
        print(f"Récapitulatif:")
        print(f"  Fichiers traités: {len(files_to_upload)}")
        print(f"  Succès: {success_count}")
        print(f"  Erreurs: {error_count}")
        print(f"{'='*60}")

        if args.debug or len(files_to_upload) == 1:
            print("\nDétails:")
            print(json.dumps(results, indent=2, ensure_ascii=False))

        return 0 if error_count == 0 else 1

    except FileNotFoundError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    except (ValueError, Exception) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
