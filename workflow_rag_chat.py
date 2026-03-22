#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow_rag_chat.py - Workflow automatisé RAG + CHAT en 2 phases

Usage:
    python workflow_rag_chat.py <search_query> <question> [output_file]

Exemple:
    python workflow_rag_chat.py "architecture" "Quelle est l'architecture ?" reponse.md
"""
import subprocess
import sys
import os
from pathlib import Path

# Forcer l'encodage UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def print_header(title):
    """Affiche un en-tête formaté."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_rag_search(collection: str, query: str, output: str = "chunks.json", top_k: int = 5) -> bool:
    """
    Phase 1: Recherche RAG

    Args:
        collection: Nom de la collection
        query: Question de recherche
        output: Fichier de sortie pour les chunks
        top_k: Nombre de chunks à récupérer

    Returns:
        True si succès, False sinon
    """
    print_header("PHASE 1/2 : RECHERCHE RAG")
    print(f"Collection : {collection}")
    print(f"Requête    : {query}")
    print(f"Top-k      : {top_k}")
    print(f"Output     : {output}")
    print()

    cmd = [
        "ambulon", "piag-rag-search",
        "--collection-name", collection,
        "-q", query,
        "-o", output,
        "--top-k", str(top_k)
    ]

    print(f"Commande : {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ Phase 1 terminée avec succès")
        return True
    else:
        print("\n❌ Phase 1 échouée")
        return False


def run_chat_query(
    question: str = None,
    question_file: str = None,
    chunks: str = "chunks.json",
    output: str = "reponse.md"
) -> bool:
    """
    Phase 2: Génération CHAT

    Args:
        question: Question en texte direct (ou None si question_file)
        question_file: Fichier contenant la question (ou None si question)
        chunks: Fichier de chunks depuis RAG
        output: Fichier de sortie pour la réponse

    Returns:
        True si succès, False sinon
    """
    print_header("PHASE 2/2 : GÉNÉRATION CHAT")

    if question:
        print(f"Question : {question[:60]}{'...' if len(question) > 60 else ''}")
    elif question_file:
        print(f"Question depuis : {question_file}")

    print(f"Chunks   : {chunks}")
    print(f"Output   : {output}")
    print()

    cmd = ["ambulon", "piag-chat-query"]

    if question:
        cmd.extend(["-q", question])
    elif question_file:
        cmd.extend(["--question-file", question_file])
    else:
        print("❌ Erreur : question ou question_file requis")
        return False

    cmd.extend(["-c", chunks, "-o", output])

    print(f"Commande : {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ Phase 2 terminée avec succès")
        return True
    else:
        print("\n❌ Phase 2 échouée")
        return False


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 3:
        print("Usage: python workflow_rag_chat.py <search_query> <question> [output_file] [--top-k N]")
        print()
        print("Arguments:")
        print("  search_query    : Requête de recherche RAG")
        print("  question        : Question à poser (ou @fichier.txt pour --question-file)")
        print("  output_file     : Fichier de sortie (défaut: reponse.md)")
        print("  --top-k N       : Nombre de chunks (défaut: 5)")
        print()
        print("Exemples:")
        print("  # Question simple")
        print("  python workflow_rag_chat.py 'architecture' 'Quelle est l'architecture ?'")
        print()
        print("  # Question depuis fichier (préfixer avec @)")
        print("  python workflow_rag_chat.py 'architecture' '@question.txt'")
        print()
        print("  # Avec fichier de sortie personnalisé")
        print("  python workflow_rag_chat.py 'architecture' 'Question ?' analyse.md")
        print()
        print("  # Avec plus de chunks")
        print("  python workflow_rag_chat.py 'architecture' 'Question ?' --top-k 10")
        sys.exit(1)

    search_query = sys.argv[1]
    question_arg = sys.argv[2]

    # Déterminer si c'est une question directe ou un fichier
    if question_arg.startswith('@'):
        question = None
        question_file = question_arg[1:]  # Enlever le @
    else:
        question = question_arg
        question_file = None

    # Arguments optionnels
    output = "reponse.md"
    top_k = 5

    # Parser les arguments restants
    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--top-k" and i + 1 < len(sys.argv):
            top_k = int(sys.argv[i + 1])
            i += 2
        else:
            output = arg
            i += 1

    collection = "PNM3_SIREINES"  # Collection par défaut

    print_header("WORKFLOW RAG + CHAT EN 2 PHASES")
    print(f"Collection : {collection}")
    print(f"Recherche  : {search_query}")
    if question:
        print(f"Question   : {question[:60]}{'...' if len(question) > 60 else ''}")
    else:
        print(f"Question   : @{question_file}")
    print(f"Output     : {output}")
    print(f"Top-k      : {top_k}")

    # Phase 1: RAG
    if not run_rag_search(collection, search_query, top_k=top_k):
        sys.exit(1)

    # Phase 2: CHAT
    if not run_chat_query(question=question, question_file=question_file, output=output):
        sys.exit(1)

    # Résumé final
    print_header("RÉSUMÉ FINAL")
    print("✅ Workflow terminé avec succès")
    print()
    print("Fichiers générés :")
    print(f"  • chunks.json  (chunks RAG)")
    print(f"  • {output}  (réponse CHAT)")
    print()

    # Afficher un extrait de la réponse
    if Path(output).exists():
        with open(output, 'r', encoding='utf-8') as f:
            content = f.read()
            preview = content[:200] + "..." if len(content) > 200 else content
            print("Aperçu de la réponse :")
            print("-" * 70)
            print(preview)
            print("-" * 70)


if __name__ == "__main__":
    main()
