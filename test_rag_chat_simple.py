#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour tester le workflow RAG + CHAT complet.

Usage:
    python test_rag_chat_simple.py
    python test_rag_chat_simple.py --question "Votre question" --top-k 5
"""

import subprocess
import json
import sys
import os
import tempfile
from pathlib import Path

# Forcer l'encodage UTF-8 pour Python et les sous-processus
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Forcer l'encodage UTF-8 pour stdout et stderr (Windows compatibility)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def extract_json_from_output(output_text):
    """Extrait le JSON valide d'une sortie contenant des logs."""
    lines = output_text.split('\n')

    # Chercher la première ligne qui commence par { ou [
    json_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('{') or stripped.startswith('['):
            json_start = i
            break

    if json_start == -1:
        return None

    # Extraire du début du JSON jusqu'à la fin
    json_text = '\n'.join(lines[json_start:])

    try:
        json.loads(json_text)  # Valider
        return json_text
    except json.JSONDecodeError:
        return None


def search_rag(collection_name, query, top_k=5):
    """Effectue une recherche RAG et retourne les chunks."""
    print(f"🔍 Recherche RAG: '{query}'")
    print(f"   Collection: {collection_name}, Top-K: {top_k}")

    cmd = [
        "ambulon", "piag-rag-search",
        "--collection-name", collection_name,
        "--query", query,
        "--top-k", str(top_k),
        "--mode", "hybrid",
        "--rerank",
        "--format", "json"
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode != 0:
        print(f"❌ Erreur lors de la recherche RAG")
        print(result.stderr)
        return None

    # Extraire le JSON valide
    json_text = extract_json_from_output(result.stdout)
    if not json_text:
        print(f"❌ Impossible d'extraire le JSON de la réponse")
        return None

    # Parser le JSON
    try:
        data = json.loads(json_text)
        chunks = data.get('chunks', [])
        print(f"✅ {len(chunks)} chunks trouvés")
        return chunks
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return None


def chat_with_chunks(question, chunks, output_file=None):
    """Envoie une question avec des chunks au CHAT."""
    print(f"\n💬 Question CHAT: '{question}'")
    print(f"   Contexte: {len(chunks)} chunks")

    # Créer un fichier temporaire avec les chunks
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump({"chunks": chunks}, f, ensure_ascii=False, indent=2)
        chunks_file = f.name

    # Créer un fichier temporaire pour la réponse si non spécifié
    temp_output = None
    if not output_file:
        temp_output = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
        temp_output.close()
        output_file = temp_output.name

    try:
        cmd = [
            "ambulon", "piag-chat-query",
            "--question", question,
            "--chunks", chunks_file,
            "--output", str(output_file)
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            print(f"❌ Erreur lors de l'appel CHAT")
            print(result.stderr)
            return None

        print(f"✅ Réponse générée")

        # Lire la réponse depuis le fichier
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                response = f.read().strip()
                return response if response else None
        except Exception as e:
            print(f"⚠️  Erreur lecture fichier: {e}")
            return None

    finally:
        # Nettoyer le fichier temporaire des chunks
        Path(chunks_file).unlink(missing_ok=True)

        # Nettoyer le fichier temporaire de sortie si on l'a créé
        if temp_output:
            Path(temp_output.name).unlink(missing_ok=True)


def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(description="Test simple RAG + CHAT")
    parser.add_argument("--collection", default="PNM3_SIREINES", help="Nom de la collection")
    parser.add_argument("--question", default="Quelle est l'architecture technique de SIREINES ?", help="Question à poser")
    parser.add_argument("--top-k", type=int, default=5, help="Nombre de chunks à récupérer")
    parser.add_argument("--output", type=Path, help="Fichier de sortie pour la réponse")
    args = parser.parse_args()

    print("=" * 80)
    print("  TEST SIMPLE RAG + CHAT")
    print("=" * 80)

    # Étape 1: Recherche RAG
    chunks = search_rag(args.collection, args.question, args.top_k)

    if not chunks:
        print("\n❌ Échec: aucun chunk trouvé")
        return 1

    # Étape 2: Question CHAT avec contexte
    response = chat_with_chunks(args.question, chunks, args.output)

    if not response:
        print("\n❌ Échec: aucune réponse générée")
        return 1

    # Affichage du résultat
    print("\n" + "=" * 80)
    print("  RÉPONSE")
    print("=" * 80)
    print(response)
    print("=" * 80)

    if args.output:
        print(f"\n📄 Réponse sauvegardée dans: {args.output}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
