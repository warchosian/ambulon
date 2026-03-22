#!/usr/bin/env python3
"""
Test End-to-End de l'API RAG PIAG

Ce script teste toutes les opérations RAG de bout en bout.
Tous les logs et résultats sont sauvegardés pour analyse ultérieure.

Usage:
    python test_piag_rag_e2e.py [--config config/piag.yaml]
"""

import argparse
import json
import logging
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Ajouter src au path si nécessaire
_src_path = Path(__file__).parent / "src"
if _src_path.exists() and str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

try:
    from app.piag.core import PIAGClient, load_config
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print(f"   Assurez-vous que le package ambulon est installé ou que vous êtes dans le bon répertoire")
    sys.exit(1)


# Configuration du logging détaillé
def setup_detailed_logging(log_dir: Path):
    """Configure le logging avec fichier et console."""
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_rag_e2e_{timestamp}.log"

    # Format détaillé
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler fichier
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return log_file


def save_response(output_dir: Path, step_name: str, data: dict):
    """Sauvegarde une réponse JSON pour analyse ultérieure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"{step_name}_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logging.info(f"Réponse sauvegardée: {filename}")
    return filename


def create_test_document(temp_dir: Path) -> Path:
    """Crée un document de test."""
    doc_path = temp_dir / "test_document.txt"
    content = """Ceci est un document de test pour l'API RAG PIAG.

Ce document contient plusieurs paragraphes pour tester le chunking et la recherche sémantique.

Le système RAG (Retrieval Augmented Generation) permet de faire de la recherche sémantique
dans une base documentaire et de générer des réponses contextualisées.

Ce test vérifie que :
- Le document peut être uploadé
- Les chunks sont correctement générés
- La recherche sémantique fonctionne
- Les résultats sont pertinents
"""

    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logging.info(f"Document de test créé: {doc_path}")
    return doc_path


def run_rag_e2e_test(config_path: str = None):
    """Exécute le test E2E complet du RAG."""

    print("=" * 80)
    print("TEST END-TO-END - API RAG PIAG")
    print("=" * 80)

    # Créer les répertoires de sortie
    output_dir = Path("test_output") / "rag" / datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = output_dir / "logs"
    responses_dir = output_dir / "responses"

    log_file = setup_detailed_logging(log_dir)
    print(f"\n📝 Logs détaillés: {log_file}")
    print(f"📂 Répertoire de sortie: {output_dir}\n")

    logging.info("=" * 80)
    logging.info("DÉBUT DU TEST E2E RAG")
    logging.info("=" * 80)

    # Chargement de la configuration
    try:
        logging.info("Chargement de la configuration...")
        config = load_config(config_path)

        # Afficher la config (sans token)
        config_for_display = json.loads(json.dumps(config))
        if 'piag' in config_for_display and 'rag' in config_for_display['piag']:
            if 'security' in config_for_display['piag']['rag']:
                config_for_display['piag']['rag']['security']['token'] = '***MASKED***'

        logging.info(f"Configuration chargée:\n{json.dumps(config_for_display, indent=2)}")
        save_response(responses_dir, "00_config", config_for_display)

    except Exception as e:
        logging.error(f"Erreur lors du chargement de la config: {e}", exc_info=True)
        return 1

    # Récupération du token
    try:
        token = config.get('piag', {}).get('rag', {}).get('security', {}).get('token')
        if not token:
            token_env_var = config.get('piag', {}).get('rag', {}).get('security', {}).get('token_env_var', 'PIAG_RAG_API_TOKEN')
            token = os.getenv(token_env_var)

        if not token:
            logging.error("Token API RAG manquant")
            print("\n❌ ERREUR: Token API RAG non trouvé")
            print("   Définissez PIAG_RAG_API_TOKEN ou configurez config/piag.yaml")
            return 1

        logging.info(f"Token trouvé: {token[:15]}...{token[-5:]}")

        # Project ID
        project_id = config.get('piag', {}).get('rag', {}).get('project', {}).get('project_id')
        if not project_id:
            project_id = os.getenv('PIAG_RAG_PROJECT_ID')

        if not project_id:
            logging.error("Project ID manquant")
            print("\n❌ ERREUR: Project ID non trouvé")
            return 1

        logging.info(f"Project ID: {project_id}")

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des credentials: {e}", exc_info=True)
        return 1

    # Création du client
    try:
        logging.info("Création du client PIAG...")
        client = PIAGClient(api_token=token, config=config)
        logging.info(f"Client créé - Base URL: {client.base_url}")
        print(f"✓ Client PIAG créé - URL: {client.base_url}")

    except Exception as e:
        logging.error(f"Erreur lors de la création du client: {e}", exc_info=True)
        return 1

    collection_id = None
    document_id = None
    test_collection_name = f"test-e2e-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    try:
        # ÉTAPE 1: Lister les collections existantes
        print("\n" + "=" * 80)
        print("ÉTAPE 1: Lister les collections existantes")
        print("=" * 80)
        logging.info("ÉTAPE 1: list_collections")

        try:
            collections = client.list_collections(project_id=project_id, limit=10)
            logging.info(f"Collections listées: {len(collections.get('items', []))} trouvée(s)")
            save_response(responses_dir, "01_list_collections", collections)
            print(f"✓ {len(collections.get('items', []))} collection(s) existante(s)")

        except Exception as e:
            logging.error(f"Erreur list_collections: {e}", exc_info=True)
            print(f"❌ Erreur lors du listing: {e}")
            raise

        # ÉTAPE 2: Créer une collection de test
        print("\n" + "=" * 80)
        print("ÉTAPE 2: Créer une collection de test")
        print("=" * 80)
        logging.info(f"ÉTAPE 2: create_collection - {test_collection_name}")

        try:
            collection = client.create_collection(
                project_id=project_id,
                name=test_collection_name,
                description="Collection de test E2E créée automatiquement"
            )
            collection_id = collection.get('id')
            logging.info(f"Collection créée: {collection_id}")
            save_response(responses_dir, "02_create_collection", collection)
            print(f"✓ Collection créée: {collection_id}")
            print(f"  Nom: {collection.get('name')}")

        except Exception as e:
            logging.error(f"Erreur create_collection: {e}", exc_info=True)
            print(f"❌ Erreur lors de la création: {e}")
            raise

        # ÉTAPE 3: Uploader un document de test
        print("\n" + "=" * 80)
        print("ÉTAPE 3: Uploader un document de test")
        print("=" * 80)
        logging.info("ÉTAPE 3: upload_document")

        try:
            # Créer le document de test
            temp_dir = Path(tempfile.mkdtemp())
            test_doc = create_test_document(temp_dir)

            upload_result = client.upload_document(
                collection_id=collection_id,
                file_path=str(test_doc)
            )
            document_id = upload_result.get('id')
            logging.info(f"Document uploadé: {document_id}")
            save_response(responses_dir, "03_upload_document", upload_result)
            print(f"✓ Document uploadé: {document_id}")
            print(f"  Fichier: {test_doc.name}")

            # Attendre que le document soit traité (chunking asynchrone)
            # Lecture du délai depuis la configuration
            processing_delay = config.get('piag', {}).get('rag', {}).get('upload', {}).get('processing_delay', 20)
            print(f"  ⏳ Attente du traitement du document ({processing_delay} secondes)...")
            logging.info(f"Attente du traitement du document ({processing_delay}s)...")
            time.sleep(processing_delay)

        except Exception as e:
            logging.error(f"Erreur upload_document: {e}", exc_info=True)
            print(f"❌ Erreur lors de l'upload: {e}")
            raise

        # ÉTAPE 4: Lister les documents
        print("\n" + "=" * 80)
        print("ÉTAPE 4: Lister les documents de la collection")
        print("=" * 80)
        logging.info("ÉTAPE 4: list_documents")

        try:
            documents = client.list_documents(collection_id=collection_id)
            logging.info(f"Documents listés: {len(documents.get('items', []))}")
            save_response(responses_dir, "04_list_documents", documents)
            print(f"✓ {len(documents.get('items', []))} document(s) dans la collection")

        except Exception as e:
            logging.error(f"Erreur list_documents: {e}", exc_info=True)
            print(f"❌ Erreur lors du listing: {e}")
            raise

        # ÉTAPE 5: Récupérer les chunks du document
        print("\n" + "=" * 80)
        print("ÉTAPE 5: Récupérer les chunks du document")
        print("=" * 80)
        logging.info("ÉTAPE 5: get_document_chunks")

        try:
            chunks = client.get_document_chunks(
                collection_id=collection_id,
                document_id=document_id
            )

            # L'API peut retourner soit une liste directe, soit un dict avec clé 'chunks'
            if isinstance(chunks, list):
                chunks_list = chunks
            elif isinstance(chunks, dict):
                chunks_list = chunks.get('chunks', [])
            else:
                chunks_list = []

            num_chunks = len(chunks_list)
            logging.info(f"Chunks récupérés: {num_chunks}")
            save_response(responses_dir, "05_get_chunks", chunks)
            print(f"✓ {num_chunks} chunk(s) récupéré(s)")

            # Afficher les premiers chunks
            for i, chunk in enumerate(chunks_list[:3]):
                if isinstance(chunk, dict):
                    content = chunk.get('content', '')[:100]
                else:
                    content = str(chunk)[:100]
                print(f"  Chunk {i+1}: {content}...")

        except Exception as e:
            logging.error(f"Erreur get_document_chunks: {e}", exc_info=True)
            print(f"❌ Erreur lors de la récupération des chunks: {e}")
            raise

        # ÉTAPE 6: Recherche sémantique RAG
        print("\n" + "=" * 80)
        print("ÉTAPE 6: Recherche sémantique RAG")
        print("=" * 80)
        logging.info("ÉTAPE 6: search")

        test_queries = [
            "Qu'est-ce que le RAG ?",
            "Comment fonctionne la recherche sémantique ?",
            "Quels sont les objectifs du test ?"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n  Requête {i}: {query}")
            logging.info(f"Recherche: {query}")

            try:
                search_results = client.search(
                    collection_id=collection_id,
                    query=query,
                    top_k=3
                )

                num_results = len(search_results.get('results', []))
                logging.info(f"Résultats trouvés: {num_results}")
                save_response(responses_dir, f"06_search_{i}", search_results)
                print(f"  ✓ {num_results} résultat(s) trouvé(s)")

                # Afficher les résultats
                for j, result in enumerate(search_results.get('results', []), 1):
                    score = result.get('score', 0)
                    content = result.get('content', '')[:80]
                    print(f"    [{j}] Score: {score:.3f} - {content}...")

            except Exception as e:
                logging.error(f"Erreur search (requête {i}): {e}", exc_info=True)
                print(f"  ❌ Erreur: {e}")

        print("\n" + "=" * 80)
        print("✓ TOUS LES TESTS RAG ONT RÉUSSI")
        print("=" * 80)
        logging.info("TOUS LES TESTS RAG ONT RÉUSSI")

    except Exception as e:
        logging.error(f"Test échoué: {e}", exc_info=True)
        print(f"\n❌ TEST ÉCHOUÉ: {e}")
        print(f"   Voir les logs pour plus de détails: {log_file}")
        return 1

    finally:
        # NETTOYAGE
        print("\n" + "=" * 80)
        print("NETTOYAGE")
        print("=" * 80)
        logging.info("Début du nettoyage...")

        # Supprimer le document
        if document_id and collection_id:
            try:
                logging.info(f"Suppression du document: {document_id}")
                client.delete_document(collection_id=collection_id, document_id=document_id)
                print(f"✓ Document supprimé: {document_id}")
            except Exception as e:
                logging.error(f"Erreur lors de la suppression du document: {e}")
                print(f"⚠ Impossible de supprimer le document: {e}")

        # Supprimer la collection
        if collection_id:
            try:
                logging.info(f"Suppression de la collection: {collection_id}")
                client.delete_collection(collection_id=collection_id)
                print(f"✓ Collection supprimée: {collection_id}")
            except Exception as e:
                logging.error(f"Erreur lors de la suppression de la collection: {e}")
                print(f"⚠ Impossible de supprimer la collection: {e}")

    print(f"\n📝 Logs complets: {log_file}")
    print(f"📂 Réponses JSON: {responses_dir}")
    logging.info("FIN DU TEST E2E RAG")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Test End-to-End de l'API RAG PIAG")
    parser.add_argument("--config", default="config/piag.yaml", help="Chemin vers le fichier de configuration")
    args = parser.parse_args()

    try:
        exit_code = run_rag_e2e_test(args.config)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
