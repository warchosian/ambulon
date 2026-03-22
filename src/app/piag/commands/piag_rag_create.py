"""Module CLI pour créer un RAG complet (collection + upload de documents).

Cette commande combine la création d'une collection RAG et le téléversement
de tous les documents d'un répertoire en une seule opération.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from app.piag.core import PIAGClient, load_config

# Forcer l'encodage UTF-8 pour stdout et stderr (Windows compatibility)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def main(argv=None):
    """
    Point d'entrée principal pour la commande piag-rag-create.
    
    Crée une collection RAG avec ou sans documents.
    Si --directory est fourni, tous les documents du répertoire sont uploadés.
    Sinon, une collection vide est créée.
    
    Args:
        argv: Arguments CLI (list of str), ou None pour utiliser sys.argv
        
    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)
        
    Exemples:
        # Créer une collection vide
        python -m app.piag.commands.piag_rag_create \
            --collection-name "MonRAG" \
            --description "Collection de documents techniques"
            
        # Créer une collection avec documents
        python -m app.piag.commands.piag_rag_create \
            --collection-name "MonRAG" \
            --directory ./documents \
            --description "Collection avec documents"
            
        # Avec projet et token explicites
        python -m app.piag.commands.piag_rag_create \
            --collection-name "MonRAG" \
            --directory ./documents \
            --project-id <id> \
            --token <token>
    """
    parser = argparse.ArgumentParser(
        description="Crée un RAG : collection avec ou sans upload de documents.",
        epilog="HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Arguments obligatoires
    parser.add_argument(
        "--collection-name", 
        required=True,
        help="Nom de la collection RAG à créer."
    )
    
    # Arguments optionnels
    parser.add_argument(
        "--directory", "--folder",
        dest="directory",
        help="Chemin vers le répertoire contenant les documents à téléverser (optionnel)."
    )
    
    # Arguments optionnels
    parser.add_argument(
        "--description",
        default="",
        help="Description de la collection (défaut: chaîne vide)."
    )
    parser.add_argument(
        "--project-id",
        help="ID du projet RAG (écrase YAML et env)."
    )
    parser.add_argument(
        "--token",
        help="Token API RAG Bearer (écrase YAML et env)."
    )
    parser.add_argument(
        "--base-url",
        help="URL de base de l'API RAG (écrase YAML)."
    )
    parser.add_argument(
        "--config",
        help="Chemin vers un fichier de configuration personnalisé."
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Parcourir les sous-répertoires recursivement."
    )
    parser.add_argument(
        "--extensions",
        help="Extensions de fichiers à inclure (ex: 'pdf,docx,txt'). Par défaut: tous les fichiers."
    )
    parser.add_argument(
        "--exclude",
        help="Patterns à exclure (ex: '*temp*,*.tmp')."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Active le mode debug (logging détaillé)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simule l'opération sans créer ni uploader (vérifie uniquement)."
    )
    
    args = parser.parse_args(argv)
    
    # Charger la configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}", file=sys.stderr)
        return 1
    
    # Activer le debug si demandé
    if args.debug:
        config.setdefault('piag', {}).setdefault('rag', {}).setdefault('logging', {}).update({
            'enable_debug': True,
            'log_requests': True,
            'log_responses': True
        })
    
    # Résolution de la hiérarchie de configuration : CLI > YAML > ENV
    
    # 1. PROJECT_ID
    project_id = args.project_id
    if not project_id:
        project_id = config.get('piag', {}).get('rag', {}).get('project', {}).get('project_id')
    if not project_id:
        project_id = os.getenv('PIAG_RAG_PROJECT_ID')
    if not project_id:
        print(f"Erreur: Project ID PIAG requis.", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"Solutions:", file=sys.stderr)
        print(f"  1. Utilisez l'argument --project-id:", file=sys.stderr)
        print(f"     ambulon piag-rag-create --collection-name 'MonRAG' --directory ./docs --project-id 'votre-projet'", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"  2. Définissez la variable d'environnement:", file=sys.stderr)
        print(f"     set PIAG_RAG_PROJECT_ID=votre-projet", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"  3. Configurez dans le fichier config/piag.yaml:", file=sys.stderr)
        print(f"     piag:", file=sys.stderr)
        print(f"       rag:", file=sys.stderr)
        print(f"         project:", file=sys.stderr)
        print(f"           project_id: 'votre-projet'", file=sys.stderr)
        return 1
    
    # 2. TOKEN
    api_token = args.token
    if not api_token:
        api_token = config.get('piag', {}).get('rag', {}).get('security', {}).get('token')
    if not api_token:
        token_env_var = config.get('piag', {}).get('rag', {}).get('security', {}).get('token_env_var', 'PIAG_RAG_API_TOKEN')
        api_token = os.getenv(token_env_var)
    if not api_token:
        print(f"Erreur: Token API PIAG requis.", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"Solutions:", file=sys.stderr)
        print(f"  1. Utilisez l'argument --token:", file=sys.stderr)
        print(f"     ambulon piag-rag-create --collection-name 'MonRAG' --token 'votre-token'", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"  2. Définissez la variable d'environnement:", file=sys.stderr)
        print(f"     set {token_env_var}=votre-token", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"  3. Configurez dans le fichier config/piag.yaml (déconseillé pour la sécurité):", file=sys.stderr)
        print(f"     piag:", file=sys.stderr)
        print(f"       rag:", file=sys.stderr)
        print(f"         security:", file=sys.stderr)
        print(f"           token: 'votre-token'", file=sys.stderr)
        return 1
    
    # 3. BASE_URL (optionnel)
    base_url = args.base_url
    if not base_url:
        base_url = config.get('piag', {}).get('rag', {}).get('api', {}).get('base_url')
    if not base_url:
        base_url = os.getenv('PIAG_RAG_BASE_URL')
    
    # Préparation des fichiers (si répertoire fourni)
    files_to_upload = []
    if args.directory:
        dir_path = Path(args.directory)
        if not dir_path.exists():
            print(f"Erreur: Le répertoire n'existe pas: {args.directory}", file=sys.stderr)
            return 1
        if not dir_path.is_dir():
            print(f"Erreur: Le chemin n'est pas un répertoire: {args.directory}", file=sys.stderr)
            return 1
        
        # Collecte des fichiers à uploader
        files_to_upload = _collect_files(
            dir_path, 
            recursive=args.recursive,
            extensions=args.extensions,
            exclude_pattern=args.exclude
        )
        
        if not files_to_upload:
            print(f"Erreur: Aucun fichier trouvé dans le répertoire: {args.directory}", file=sys.stderr)
            return 1
    
    # Affichage du récapitulatif
    print(f"=" * 60)
    print(f"CRÉATION DE RAG")
    print(f"=" * 60)
    print(f"Collection: {args.collection_name}")
    print(f"Description: {args.description or '(aucune)'}")
    print(f"Projet: {project_id}")
    if args.directory:
        print(f"Répertoire: {args.directory}")
        print(f"Fichiers trouvés: {len(files_to_upload)}")
        print(f"Mode récursif: {'oui' if args.recursive else 'non'}")
        if args.extensions:
            print(f"Filtre d'extensions: {args.extensions}")
    else:
        print(f"Documents: (aucun - collection vide)")
    print(f"Mode dry-run: {'oui' if args.dry_run else 'non'}")
    print(f"=" * 60)
    
    if args.dry_run:
        if files_to_upload:
            print("\nMode dry-run - Liste des fichiers qui seraient uploadés:")
            for i, f in enumerate(files_to_upload, 1):
                print(f"  {i}. {f}")
        else:
            print("\nMode dry-run - Aucun document à uploader")
        return 0
    
    # Création du client PIAG
    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du client PIAG: {e}", file=sys.stderr)
        return 1
    
    # Étape 1: Création de la collection
    has_documents = len(files_to_upload) > 0
    step_total = 2 if has_documents else 1
    print(f"\n[1/{step_total}] Création de la collection '{args.collection_name}'...", end=" ", flush=True)
    
    try:
        collection_result = client.create_collection(
            project_id=project_id,
            name=args.collection_name,
            description=args.description
        )
        collection_id = collection_result.get('id')
        if not collection_id:
            print("✗")
            print("Erreur: ID de collection manquant dans la réponse", file=sys.stderr)
            return 1
        print(f"✓ (ID: {collection_id})")
    except Exception as e:
        print("✗")
        print(f"Erreur lors de la création de la collection: {e}", file=sys.stderr)
        return 1
    
    # Étape 2: Upload des documents (si répertoire fourni)
    results = []
    success_count = 0
    error_count = 0
    
    if has_documents:
        print(f"\n[2/2] Téléversement des documents...")
        print(f"{'-' * 60}")
        
        results = _upload_files(client, collection_id, files_to_upload)
        
        print(f"{'-' * 60}")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = sum(1 for r in results if r['status'] == 'error')
    
    # Récapitulatif
    print(f"\nRÉCAPITULATIF")
    print(f"{'=' * 60}")
    print(f"Collection: {args.collection_name}")
    print(f"ID: {collection_id}")
    if has_documents:
        print(f"Documents totaux: {len(files_to_upload)}")
        print(f"Succès: {success_count}")
        print(f"Erreurs: {error_count}")
    else:
        print(f"Documents: 0 (collection vide)")
    print(f"{'=' * 60}")
    
    if args.debug:
        print("\nDétails complets:")
        debug_info = {'collection': collection_result}
        if has_documents:
            debug_info['uploads'] = results
        print(json.dumps(debug_info, indent=2, ensure_ascii=False))
    
    # Proposer les commandes de consultation
    print(f"\n📋 COMMANDES DE CONSULTATION")
    print(f"{'=' * 60}")
    print(f"# Voir les détails de la collection:")
    print(f"ambulon piag-rag-collection-get --collection-id {collection_id}")
    print(f"")
    if has_documents:
        print(f"# Lister les documents de la collection:")
        print(f"ambulon piag-rag-doc-list --collection-id {collection_id}")
        print(f"")
        print(f"# Rechercher dans le RAG:")
        print(f"ambulon piag-rag-search --collection-id {collection_id} --query \"votre question\"")
        print(f"")
    else:
        print(f"# Ajouter des documents à la collection:")
        print(f"ambulon piag-rag-doc-upload --collection-id {collection_id} --file <chemin>")
        print(f"")
    print(f"# Interroger le RAG avec contexte:")
    print(f"ambulon piag-chat-query --collection-id {collection_id} --query \"votre question\"")
    print(f"")
    print(f"# Supprimer la collection:")
    print(f"ambulon piag-rag-collection-rm --collection-id {collection_id}")
    print(f"{'=' * 60}")
    
    return 0 if error_count == 0 else 1


def _collect_files(
    directory: Path, 
    recursive: bool = False,
    extensions: str = None,
    exclude_pattern: str = None
) -> List[Path]:
    """
    Collecte les fichiers à uploader depuis un répertoire.
    
    Args:
        directory: Répertoire source
        recursive: Si True, parcourt les sous-répertoires
        extensions: Liste d'extensions séparées par des virgules (ex: 'pdf,txt')
        exclude_pattern: Patterns à exclure (non implémenté dans cette version simple)
        
    Returns:
        Liste des chemins de fichiers
    """
    files = []
    
    # Parsing des extensions
    allowed_extensions = None
    if extensions:
        allowed_extensions = [ext.strip().lower() for ext in extensions.split(',')]
        # Ajouter le point si manquant
        allowed_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in allowed_extensions]
    
    # Collecte des fichiers
    if recursive:
        iterator = directory.rglob('*')
    else:
        iterator = directory.iterdir()
    
    for item in iterator:
        if item.is_file():
            # Filtrage par extension
            if allowed_extensions:
                if item.suffix.lower() not in allowed_extensions:
                    continue
            
            # TODO: Implémenter le filtrage par exclude_pattern si nécessaire
            
            files.append(item)
    
    # Tri par nom pour un ordre déterministe
    files.sort(key=lambda p: p.name)
    
    return files


def _upload_files(
    client: PIAGClient, 
    collection_id: str, 
    files: List[Path]
) -> List[Dict[str, Any]]:
    """
    Téléverse une liste de fichiers vers une collection.
    
    Args:
        client: Instance de PIAGClient
        collection_id: ID de la collection
        files: Liste des chemins de fichiers
        
    Returns:
        Liste des résultats d'upload
    """
    results = []
    
    for i, file_path in enumerate(files, 1):
        # Affichage avec alignement
        name_display = file_path.name[:50] + "..." if len(file_path.name) > 50 else file_path.name
        print(f"  [{i:3d}/{len(files):3d}] {name_display:55s} ", end="", flush=True)
        
        try:
            result = client.upload_document(collection_id, str(file_path))
            results.append({
                'file': file_path.name,
                'path': str(file_path),
                'status': 'success',
                'result': result
            })
            print("✓")
        except Exception as e:
            results.append({
                'file': file_path.name,
                'path': str(file_path),
                'status': 'error',
                'error': str(e)
            })
            print(f"✗ ({e})")
    
    return results


if __name__ == "__main__":
    sys.exit(main())
