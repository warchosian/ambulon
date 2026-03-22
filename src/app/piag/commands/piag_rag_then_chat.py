"""Module CLI pour le pipeline RAG puis CHAT (orchestration des 4 étapes).

Ce module fournit une commande unifiée qui enchaîne automatiquement :
1. Création/suppression de la collection RAG
2. Upload et indexation des documents
3. Recherche sémantique (chunking)
4. Génération de réponse via chat

Usage:
    ambulon piag-rag-then-chat run --source <dir> --prompt <prompt_file> [options]
    ambulon piag-rag-then-chat init --source <dir> [--force]
    ambulon piag-rag-then-chat ingest --source <dir> [--wait-index]
    ambulon piag-rag-then-chat chunk --source <dir> --prompt <prompt_file> --query <query>
    ambulon piag-rag-then-chat generate --source <dir> --prompt <prompt_file>
"""

import os
import sys
import json
import time
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Forcer l'encodage UTF-8 pour stdout et stderr (Windows compatibility)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from app.piag.core import PIAGClient, load_config


def slugify(text: str) -> str:
    """Convertit un texte en slug utilisable dans un nom de fichier."""
    return text.lower().replace(' ', '_').replace(',', '').replace('?', '').replace('!', '')[:50]


def derive_collection_name(source_dir: str) -> str:
    """
    Dérive le nom de collection à partir du répertoire source.
    
    Convention: Le nom de collection = nom du répertoire sans l'extension .rag
    Ex: applications/PNM3_SIREINES.rag → PNM3_SIREINES
    """
    source_path = Path(source_dir)
    source_name = source_path.name  # "PNM3_SIREINES.rag"
    collection = source_name.replace('.rag', '')  # "PNM3_SIREINES"
    return collection


def derive_chunk_file(source_dir: str, prompt_file: str) -> str:
    """
    Dérive le nom du fichier chunks à partir du répertoire source et du prompt.
    
    Convention: piag_workplace/chunks/chunk.<COLLECTION>.<PROMPT_TYPE>.json
    
    Args:
        source_dir: Chemin du répertoire source
        prompt_file: Chemin du fichier prompt
        
    Returns:
        Chemin du fichier chunks (ex: piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json)
    """
    source_path = Path(source_dir)
    source_name = source_path.name  # "PNM3_SIREINES.rag"
    collection = source_name.replace('.rag', '')  # "PNM3_SIREINES"
    
    # Extraire le type du prompt (ex: "dat_c4model" de "prompt.dat_c4model.md")
    prompt_path = Path(prompt_file)
    prompt_name = prompt_path.stem  # "prompt.dat_c4model"
    
    if prompt_name.startswith('prompt.'):
        prompt_type = prompt_name[7:]  # "dat_c4model"
    else:
        prompt_type = prompt_name
    
    return f"piag_workplace/chunks/chunk.{collection}.{prompt_type}.json"


def derive_response_file(source_dir: str, prompt_file: str) -> str:
    """
    Dérive le nom du fichier réponse à partir du répertoire source et du prompt.
    
    Convention: piag_workplace/responses/response.<COLLECTION>.<PROMPT_TYPE>.md
    
    Args:
        source_dir: Chemin du répertoire source
        prompt_file: Chemin du fichier prompt/question
        
    Returns:
        Chemin du fichier réponse (ex: piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md)
    """
    source_path = Path(source_dir)
    source_name = source_path.name  # "PNM3_SIREINES.rag"
    collection = source_name.replace('.rag', '')  # "PNM3_SIREINES"
    
    # Extraire le type du prompt (ex: "dat_c4model" de "prompt.dat_c4model.md")
    prompt_path = Path(prompt_file)
    prompt_name = prompt_path.stem  # "prompt.dat_c4model"
    
    if prompt_name.startswith('prompt.'):
        prompt_type = prompt_name[7:]  # "dat_c4model"
    else:
        prompt_type = prompt_name
    
    return f"piag_workplace/responses/response.{collection}.{prompt_type}.md"


def parse_prompt_info(prompt_file: str) -> Dict[str, str]:
    """
    Extrait les informations du fichier prompt.
    
    Args:
        prompt_file: Chemin du fichier prompt
        
    Returns:
        Dict avec 'type', 'standard', 'full_name'
    """
    prompt_path = Path(prompt_file)
    prompt_name = prompt_path.stem
    
    if prompt_name.startswith('prompt.'):
        type_standard = prompt_name[7:]
    else:
        type_standard = prompt_name
    
    # Séparer type et standard
    parts = type_standard.split('_', 1)
    prompt_type = parts[0] if parts else "unknown"
    standard = parts[1] if len(parts) > 1 else ""
    
    return {
        'type': prompt_type,
        'standard': standard,
        'full_name': type_standard
    }


def generate_session_id() -> str:
    """Génère un ID de session unique."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_hash = hashlib.md5(timestamp.encode()).hexdigest()[:6]
    return f"rag_{timestamp}_{short_hash}"


def create_metadata(source_dir: str, prompt_file: str, collection_name: str, 
                   query: str = "", session_id: str = "") -> Dict[str, Any]:
    """Crée les métadonnées pour les fichiers générés."""
    prompt_info = parse_prompt_info(prompt_file)
    
    return {
        "pipeline_version": "3.1.0",
        "session_id": session_id or generate_session_id(),
        "generated_at": datetime.now().isoformat(),
        "source_directory": source_dir,
        "collection_name": collection_name,
        "prompt_file": prompt_file,
        "prompt_type": prompt_info['type'],
        "prompt_standard": prompt_info['standard'],
        "query": query
    }


def log_step(step_num: int, step_name: str, message: str = ""):
    """Affiche un message de progression formaté."""
    print(f"\n[{step_num}/4] {step_name}")
    if message:
        print(f"    {message}")


def step_init(collection_name: str, source_dir: str, force: bool = False) -> bool:
    """
    Étape 1: Initialisation - création/suppression de la collection.
    
    Args:
        collection_name: Nom de la collection RAG
        source_dir: Répertoire source (pour info)
        force: Si True, supprime la collection existante
        
    Returns:
        True si succès, False sinon
    """
    client = PIAGClient()
    
    # Vérifier si la collection existe
    try:
        collections = client.list_collections()
        exists = any(c.get('name') == collection_name for c in collections)
        
        if exists and force:
            print(f"    Suppression collection existante: {collection_name}")
            try:
                client.delete_collection(collection_name)
                print(f"    ✓ Collection supprimée")
            except Exception as e:
                print(f"    ⚠ Erreur suppression: {e}")
                
    except Exception as e:
        print(f"    ⚠ Impossible de vérifier l'existence: {e}")
    
    return True


def step_ingest(collection_name: str, source_dir: str, extensions: str = "md,pdf",
                wait_index: int = 60) -> Tuple[bool, int]:
    """
    Étape 2: Ingestion - upload des documents et attente indexation.
    
    Args:
        collection_name: Nom de la collection RAG
        source_dir: Répertoire contenant les documents
        extensions: Extensions de fichiers à uploader
        wait_index: Temps d'attente pour l'indexation (secondes)
        
    Returns:
        Tuple (succès, nombre de documents)
    """
    from app.piag.commands import piag_rag_create
    
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"    ✗ Répertoire source introuvable: {source_dir}")
        return False, 0
    
    # Compter les fichiers
    exts = [e.strip() for e in extensions.split(',')]
    files = []
    for ext in exts:
        files.extend(list(source_path.glob(f"*.{ext}")))
    
    if not files:
        print(f"    ✗ Aucun fichier trouvé (*.{extensions})")
        return False, 0
    
    print(f"    {len(files)} documents trouvés")
    
    # Créer la collection avec upload
    try:
        # Appeler piag-rag-create avec les bons arguments
        argv = [
            "--collection-name", collection_name,
            "--directory", str(source_path),
            "--extensions", extensions,
            "--description", f"Collection pipeline - {source_path.name}"
        ]
        
        result = piag_rag_create.main(argv)
        
        if result != 0:
            print(f"    ✗ Erreur création collection")
            return False, 0
            
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
        return False, 0
    
    # Attendre l'indexation
    print(f"    Attente indexation ({wait_index}s)...")
    time.sleep(wait_index)
    
    # Vérifier le nombre de documents indexés
    try:
        client = PIAGClient()
        docs = client.list_documents(collection_name)
        doc_count = len(docs) if docs else 0
        print(f"    ✓ {doc_count} documents indexés")
        return True, doc_count
    except Exception as e:
        print(f"    ⚠ Impossible de vérifier l'indexation: {e}")
        return True, len(files)


def step_chunk(collection_name: str, query: str, prompt_file: str,
               chunk_file: str, top_k: int = 10, timeout: str = "10s") -> bool:
    """
    Étape 3: Chunking - recherche sémantique et sauvegarde des chunks.
    
    Args:
        collection_name: Nom de la collection RAG
        query: Requête de recherche
        prompt_file: Chemin du fichier prompt (pour métadonnées)
        chunk_file: Chemin de sortie pour les chunks
        top_k: Nombre de chunks à récupérer
        timeout: Timeout pour la recherche
        
    Returns:
        True si succès, False sinon
    """
    from app.piag.commands import piag_rag_search
    
    # Créer le répertoire chunks si nécessaire
    chunk_path = Path(chunk_file)
    chunk_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"    Recherche: '{query}'")
    print(f"    Collection: {collection_name}")
    
    try:
        argv = [
            "--collection-name", collection_name,
            "--query", query,
            "--top-k", str(top_k),
            "--timeout", timeout,
            "-o", chunk_file
        ]
        
        result = piag_rag_search.main(argv)
        
        if result != 0:
            print(f"    ✗ Erreur recherche RAG")
            return False
        
        # Vérifier que le fichier a été créé
        if not Path(chunk_file).exists():
            print(f"    ✗ Fichier chunks non créé")
            return False
        
        # Compter les chunks
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                chunks = data.get('chunks', data if isinstance(data, list) else [])
                print(f"    ✓ {len(chunks)} chunks récupérés")
        except:
            print(f"    ✓ Chunks sauvegardés")
        
        return True
        
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
        return False


def step_generate(chunk_file: str, prompt_file: str, response_file: str,
                  timeout: str = "20m", max_retries: int = 5, 
                  retry_delay: str = "1m", metadata: Dict = None) -> bool:
    """
    Étape 4: Génération - création de la réponse via chat.
    
    Args:
        chunk_file: Chemin du fichier chunks JSON
        prompt_file: Chemin du fichier prompt/question
        response_file: Chemin de sortie pour la réponse
        timeout: Timeout pour la génération
        max_retries: Nombre max de tentatives
        retry_delay: Délai entre tentatives
        metadata: Métadonnées à injecter dans la réponse
        
    Returns:
        True si succès, False sinon
    """
    from app.piag.commands import piag_chat_query
    
    # Créer le répertoire reponses si nécessaire
    response_path = Path(response_file)
    response_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"    Prompt: {prompt_file}")
    print(f"    Chunks: {chunk_file}")
    
    try:
        argv = [
            "--question-file", prompt_file,
            "--chunks", chunk_file,
            "--timeout", timeout,
            "--max-retries", str(max_retries),
            "--retry-delay", retry_delay,
            "-o", response_file
        ]
        
        result = piag_chat_query.main(argv)
        
        if result != 0:
            print(f"    ✗ Erreur génération réponse")
            return False
        
        # Vérifier que le fichier a été créé
        if not Path(response_file).exists():
            print(f"    ✗ Fichier réponse non créé")
            return False
        
        # Injecter les métadonnées dans l'en-tête du fichier
        if metadata:
            try:
                with open(response_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Créer l'en-tête YAML
                meta_yaml = "---\n"
                for key, value in metadata.items():
                    meta_yaml += f"{key}: {value}\n"
                meta_yaml += "---\n\n"
                
                # Écrire avec l'en-tête
                with open(response_file, 'w', encoding='utf-8') as f:
                    f.write(meta_yaml + content)
                    
            except Exception as e:
                print(f"    ⚠ Erreur injection métadonnées: {e}")
        
        print(f"    ✓ Réponse générée")
        return True
        
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
        return False


def run_full_pipeline(args) -> int:
    """
    Exécute le pipeline complet (4 étapes).
    
    Args:
        args: Arguments parsés
        
    Returns:
        Code de sortie (0 = succès, 1 = erreur)
    """
    # Dériver les noms pour chaque phase
    collection_name = derive_collection_name(args.source)
    chunk_file = derive_chunk_file(args.source, args.prompt)
    response_file = derive_response_file(args.source, args.prompt)
    
    # Générer ID de session
    session_id = generate_session_id()
    
    print("=" * 60)
    print("🚀 RAG then CHAT - Workflow Complet")
    print("=" * 60)
    print(f"Session ID: {session_id}")
    print(f"Source:     {args.source}")
    print(f"Query:      {args.query}")
    print(f"Prompt:     {args.prompt}")
    print(f"Collection: {collection_name}")
    print(f"Chunk:      {chunk_file}")
    print(f"Response:   {response_file}")
    print("=" * 60)
    
    # Métadonnées
    metadata = create_metadata(
        args.source, args.prompt, collection_name, 
        args.query, session_id
    )
    
    # Étape 1: INIT
    log_step(1, "INIT", f"Collection: {collection_name}")
    if not step_init(collection_name, args.source, args.force):
        print("\n✗ Étape 1 échouée - Arrêt")
        return 1
    print("    ✓ Prêt")
    
    # Étape 2: INGEST
    log_step(2, "INGEST", f"Répertoire: {args.source}")
    success, doc_count = step_ingest(
        collection_name, args.source, 
        args.extensions, args.wait_index
    )
    if not success:
        print("\n✗ Étape 2 échouée - Arrêt")
        return 1
    
    # Étape 3: CHUNK
    log_step(3, "CHUNK", f"Requête: '{args.query}'")
    if not step_chunk(
        collection_name, args.query, args.prompt,
        chunk_file, args.top_k, args.timeout_search
    ):
        print("\n✗ Étape 3 échouée - Arrêt")
        return 1
    
    # Étape 4: GENERATE
    log_step(4, "GENERATE", f"Prompt: {Path(args.prompt).name}")
    if not step_generate(
        chunk_file, args.prompt, response_file,
        args.timeout_generate, args.max_retries, args.retry_delay,
        metadata
    ):
        print("\n✗ Étape 4 échouée - Arrêt")
        return 1
    
    # Résumé final
    print("\n" + "=" * 60)
    print("✅ PIPELINE TERMINÉ")
    print("=" * 60)
    print(f"\n📁 Fichiers générés:")
    print(f"   • {chunk_file}")
    print(f"   • {response_file}")
    print(f"\n📖 Lire la réponse:")
    print(f"   type {response_file}")
    print("=" * 60)
    
    return 0


def main(argv=None):
    """
    Point d'entrée principal pour la commande piag-rag-then-chat.
    
    Usage:
        ambulon piag-rag-then-chat run --source <dir> --prompt <file>
        ambulon piag-rag-then-chat init --source <dir>
        ambulon piag-rag-then-chat ingest --source <dir>
        ambulon piag-rag-then-chat chunk --source <dir> --prompt <file>
        ambulon piag-rag-then-chat generate --source <dir> --prompt <file>
    """
    parser = argparse.ArgumentParser(
        prog='ambulon piag-rag-then-chat',
        description='Pipeline RAG puis CHAT - Orchestration des 4 étapes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commandes disponibles:
  run       Exécuter le pipeline complet (4 étapes)
  init      Étape 1: Initialiser la collection (créer/supprimer)
  ingest    Étape 2: Ingestion des documents
  chunk     Étape 3: Création des chunks (recherche RAG avec --query)
  generate  Étape 4: Génération de la réponse

Exemples:
  # Pipeline complet
  ambulon piag-rag-then-chat run \\
      --source applications/sireines.rag \\
      --prompt .claude/prompts/prompt.dat_c4model.md \\
      --query "Architecture, DAT"

  # Uniquement créer la collection et uploader
  ambulon piag-rag-then-chat init --source applications/sireines.rag --force
  ambulon piag-rag-then-chat ingest --source applications/sireines.rag

  # Utiliser des chunks existants pour générer
  ambulon piag-rag-then-chat generate \\
      --source applications/sireines.rag \\
      --prompt .claude/prompts/prompt.dat_c4model.md

Convention de nommage:
  Collection: <NOM>.rag → <NOM>                       (ex: PNM3_SIREINES.rag → PNM3_SIREINES)
  Chunks:     piag_workplace/chunks/chunk.<COLLECTION>.<PROMPT_TYPE>.json
              (ex: piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json)
  Réponse:    piag_workplace/responses/response.<COLLECTION>.<PROMPT_TYPE>.md
              (ex: piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commande à exécuter')
    
    # Commande RUN (pipeline complet)
    run_parser = subparsers.add_parser('run', help='Pipeline complet (4 étapes)')
    run_parser.add_argument('--source', '-s', required=True,
                          help='Répertoire source contenant les documents')
    run_parser.add_argument('--prompt', '-p', required=True,
                          help='Chemin vers le fichier prompt (.claude/prompts/prompt.TYPE_STANDARD.md)')
    run_parser.add_argument('--query', '-q', default='Architecture, DAT',
                          help='Requête de recherche (défaut: "Architecture, DAT")')
    run_parser.add_argument('--extensions', '-e', default='md,pdf',
                          help='Extensions de fichiers à uploader (défaut: md,pdf)')
    run_parser.add_argument('--top-k', '-k', type=int, default=10,
                          help='Nombre de chunks à récupérer (défaut: 10)')
    run_parser.add_argument('--wait-index', '-w', type=int, default=60,
                          help='Temps d\'attente indexation en secondes (défaut: 60)')
    run_parser.add_argument('--timeout-search', type=str, default='10s',
                          help='Timeout recherche RAG (défaut: 10s)')
    run_parser.add_argument('--timeout-generate', type=str, default='20m',
                          help='Timeout génération (défaut: 20m)')
    run_parser.add_argument('--max-retries', '-r', type=int, default=5,
                          help='Nombre max de retries (défaut: 5)')
    run_parser.add_argument('--retry-delay', type=str, default='1m',
                          help='Délai entre retries (défaut: 1m)')
    run_parser.add_argument('--force', '-f', action='store_true',
                          help='Forcer la suppression de la collection existante')
    
    # Commande INIT
    init_parser = subparsers.add_parser('init', help='Étape 1: Initialiser la collection')
    init_parser.add_argument('--source', '-s', required=True,
                           help='Répertoire source')
    init_parser.add_argument('--force', '-f', action='store_true',
                           help='Supprimer la collection si elle existe')
    
    # Commande INGEST
    ingest_parser = subparsers.add_parser('ingest', help='Étape 2: Ingestion des documents')
    ingest_parser.add_argument('--source', '-s', required=True,
                             help='Répertoire source')
    ingest_parser.add_argument('--extensions', '-e', default='md,pdf',
                             help='Extensions à uploader (défaut: md,pdf)')
    ingest_parser.add_argument('--wait-index', '-w', type=int, default=60,
                             help='Temps d\'attente indexation (défaut: 60)')
    
    # Commande CHUNK
    chunk_parser = subparsers.add_parser('chunk', help='Étape 3: Création des chunks')
    chunk_parser.add_argument('--source', '-s', required=True,
                            help='Répertoire source')
    chunk_parser.add_argument('--query', '-q', default='Architecture, DAT',
                            help='Requête de recherche (défaut: "Architecture, DAT")')
    chunk_parser.add_argument('--top-k', '-k', type=int, default=10,
                            help='Nombre de chunks (défaut: 10)')
    chunk_parser.add_argument('--timeout', '-t', type=str, default='10s',
                            help='Timeout recherche (défaut: 10s)')
    chunk_parser.add_argument('-o', '--output',
                            help='Fichier de sortie (défaut: auto-dérivé de --source + --query)')
    
    # Commande GENERATE
    generate_parser = subparsers.add_parser('generate', help='Étape 4: Génération réponse')
    generate_parser.add_argument('--source', '-s', required=True,
                               help='Répertoire source')
    generate_parser.add_argument('--prompt', '-p', required=True,
                               help='Fichier prompt')
    generate_parser.add_argument('--chunks', '-c',
                               help='Fichier chunks (défaut: auto-dérivé)')
    generate_parser.add_argument('--timeout', '-t', type=str, default='20m',
                               help='Timeout génération (défaut: 20m)')
    generate_parser.add_argument('--max-retries', '-r', type=int, default=5,
                               help='Nombre max de retries (défaut: 5)')
    generate_parser.add_argument('--retry-delay', type=str, default='1m',
                               help='Délai entre retries (défaut: 1m)')
    generate_parser.add_argument('-o', '--output',
                               help='Fichier de sortie (défaut: auto-dérivé)')
    
    # Parser les arguments
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Exécuter la commande appropriée
    if args.command == 'run':
        return run_full_pipeline(args)
    
    elif args.command == 'init':
        collection_name = derive_collection_name(args.source)
        log_step(1, "INIT", f"Collection: {collection_name}")
        if step_init(collection_name, args.source, args.force):
            print("    ✓ Collection prête")
            return 0
        return 1
    
    elif args.command == 'ingest':
        collection_name = derive_collection_name(args.source)
        log_step(2, "INGEST", f"Collection: {collection_name}")
        success, count = step_ingest(collection_name, args.source, args.extensions, args.wait_index)
        if success:
            print(f"    ✓ {count} documents ingérés")
            return 0
        return 1
    
    elif args.command == 'chunk':
        collection_name = derive_collection_name(args.source)
        chunk_file = derive_chunk_file(args.source, args.query)
        output_file = args.output or chunk_file
        log_step(3, "CHUNK", f"Requête: '{args.query}'")
        if step_chunk(collection_name, args.query, None, output_file, args.top_k, args.timeout):
            print(f"    ✓ Chunks sauvegardés: {output_file}")
            return 0
        return 1
    
    elif args.command == 'generate':
        chunk_file = args.chunks or derive_chunk_file(args.source, args.prompt)
        output_file = args.output or derive_response_file(args.source, args.prompt)
        
        metadata = create_metadata(args.source, args.prompt, 
                                   derive_collection_name(args.source))
        
        log_step(4, "GENERATE", f"Prompt: {Path(args.prompt).name}")
        if step_generate(chunk_file, args.prompt, output_file, 
                        args.timeout, args.max_retries, args.retry_delay, metadata):
            print(f"    ✓ Réponse générée: {output_file}")
            return 0
        return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
