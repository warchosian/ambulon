#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour comparer les réponses AVEC et SANS contexte RAG.

Ce script permet de vérifier si les chunks RAG sont vraiment utilisés
en comparant les réponses du modèle avec et sans contexte documentaire.

Usage:
    python test_compare_with_without_rag.py
    python test_compare_with_without_rag.py --question "Votre question"
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
    json_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('{') or stripped.startswith('['):
            json_start = i
            break

    if json_start == -1:
        return None

    json_text = '\n'.join(lines[json_start:])
    try:
        json.loads(json_text)
        return json_text
    except json.JSONDecodeError:
        return None


def search_rag(collection_name, query, top_k=5):
    """Effectue une recherche RAG et retourne les chunks."""
    print(f"🔍 Recherche RAG...")
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
        return None

    json_text = extract_json_from_output(result.stdout)
    if not json_text:
        return None

    try:
        data = json.loads(json_text)
        chunks = data.get('chunks', [])
        print(f"   ✅ {len(chunks)} chunks trouvés")

        # Afficher les sources des chunks
        if chunks:
            print(f"   📄 Sources:")
            seen_docs = set()
            for chunk in chunks:
                doc_name = chunk.get('document_name', 'Inconnu')
                if doc_name not in seen_docs:
                    print(f"      - {doc_name}")
                    seen_docs.add(doc_name)

        return chunks
    except json.JSONDecodeError:
        return None


def chat_without_rag(question):
    """Pose une question SANS contexte RAG (connaissance générale du modèle)."""
    print(f"\n❓ Question SANS RAG (connaissance générale)...")

    cmd = [
        "ambulon", "piag-chat-basic-query",
        "--question", question
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode != 0:
        print(f"   ❌ Erreur")
        return None

    # Extraire la réponse
    output_lines = result.stdout.split('\n')
    in_response = False
    response_lines = []

    for line in output_lines:
        if "RÉPONSE DU MODÈLE" in line:
            in_response = True
            continue
        if in_response and "=" * 20 in line:
            if response_lines:  # Deuxième ligne === -> fin
                break
            continue
        if in_response:
            response_lines.append(line)

    response = '\n'.join(response_lines).strip()
    print(f"   ✅ Réponse générée ({len(response)} caractères)")
    return response if response else None


def chat_with_rag(question, chunks):
    """Pose une question AVEC contexte RAG."""
    print(f"\n❓ Question AVEC RAG (contexte documentaire)...")

    # Créer fichier temporaire avec chunks
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump({"chunks": chunks}, f, ensure_ascii=False, indent=2)
        chunks_file = f.name

    # Créer fichier temporaire pour la réponse
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        output_file = f.name

    try:
        cmd = [
            "ambulon", "piag-chat-query",
            "--question", question,
            "--chunks", chunks_file,
            "--output", output_file
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            print(f"   ❌ Erreur")
            return None

        # Lire la réponse
        with open(output_file, 'r', encoding='utf-8') as f:
            response = f.read().strip()

        print(f"   ✅ Réponse générée ({len(response)} caractères)")
        return response if response else None

    finally:
        Path(chunks_file).unlink(missing_ok=True)
        Path(output_file).unlink(missing_ok=True)


def compare_responses(question, response_without_rag, response_with_rag):
    """Compare et affiche les deux réponses."""
    print("\n" + "=" * 80)
    print("  COMPARAISON DES RÉPONSES")
    print("=" * 80)

    print(f"\n📝 Question: {question}\n")

    # Réponse sans RAG
    print("─" * 80)
    print("🌍 SANS CONTEXTE RAG (Connaissance générale du modèle)")
    print("─" * 80)
    if response_without_rag:
        print(response_without_rag)
    else:
        print("(Aucune réponse)")
    print()

    # Réponse avec RAG
    print("─" * 80)
    print("📚 AVEC CONTEXTE RAG (Documentation SIREINES)")
    print("─" * 80)
    if response_with_rag:
        print(response_with_rag)
    else:
        print("(Aucune réponse)")
    print()

    # Analyse comparative
    print("─" * 80)
    print("📊 ANALYSE COMPARATIVE")
    print("─" * 80)

    if response_without_rag and response_with_rag:
        len_without = len(response_without_rag)
        len_with = len(response_with_rag)

        print(f"  Longueur sans RAG:  {len_without} caractères")
        print(f"  Longueur avec RAG:  {len_with} caractères")
        print(f"  Différence:         {abs(len_with - len_without)} caractères ({len_with - len_without:+d})")
        print()

        # Vérifier la présence de termes spécifiques
        specific_terms = [
            "Struts", "Vertigo", "PostgreSQL", "Elasticsearch", "BIRT",
            "Java", "Tomcat", "Docker", "Maven", "FreeMarker",
            "sireines", "SIREINES"
        ]

        print("  Termes techniques spécifiques trouvés:")
        found_without = [t for t in specific_terms if t.lower() in response_without_rag.lower()]
        found_with = [t for t in specific_terms if t.lower() in response_with_rag.lower()]

        print(f"    - Sans RAG: {', '.join(found_without) if found_without else 'Aucun'}")
        print(f"    - Avec RAG: {', '.join(found_with) if found_with else 'Aucun'}")
        print()

        if len(found_with) > len(found_without):
            print("  ✅ La réponse avec RAG contient PLUS de détails techniques spécifiques")
        elif len(found_with) == len(found_without):
            print("  ⚠️  Les deux réponses contiennent le même niveau de détails")
        else:
            print("  ❌ La réponse sans RAG contient plus de détails (étrange!)")

    print("=" * 80)


def main():
    """Point d'entrée principal."""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Comparer réponses avec/sans RAG")
    parser.add_argument("--collection", default="PNM3_SIREINES", help="Nom de la collection")
    parser.add_argument(
        "--question",
        default="Quelle est l'architecture technique du système SIREINES ?",
        help="Question à poser"
    )
    parser.add_argument("--top-k", type=int, default=5, help="Nombre de chunks")
    parser.add_argument("--output", type=Path, help="Fichier de sortie pour sauvegarder le rapport complet")
    args = parser.parse_args()

    # Créer un fichier de sortie automatique si non spécifié
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = Path(f"rapport_comparaison_{timestamp}.md")

    # Créer un système de capture de sortie
    import io
    captured_output = io.StringIO()

    class TeeOutput:
        """Classe pour afficher ET capturer la sortie."""
        def __init__(self, *outputs):
            self.outputs = outputs

        def write(self, text):
            for output in self.outputs:
                output.write(text)

        def flush(self):
            for output in self.outputs:
                output.flush()

    # Rediriger stdout pour capturer
    original_stdout = sys.stdout
    sys.stdout = TeeOutput(original_stdout, captured_output)

    result = 1  # Par défaut, échec
    try:
        print("=" * 80)
        print("  TEST COMPARATIF: RÉPONSES AVEC vs SANS CONTEXTE RAG")
        print("=" * 80)
        print(f"\n📝 Question: {args.question}")
        print()

        # Étape 1: Réponse SANS RAG
        response_without_rag = chat_without_rag(args.question)

        # Étape 2: Recherche RAG
        chunks = search_rag(args.collection, args.question, args.top_k)

        # Étape 3: Réponse AVEC RAG
        response_with_rag = None
        if chunks:
            response_with_rag = chat_with_rag(args.question, chunks)

        # Étape 4: Comparaison
        if response_without_rag or response_with_rag:
            compare_responses(args.question, response_without_rag, response_with_rag)
            result = 0
        else:
            print("\n❌ Échec: aucune réponse générée")
            result = 1

    finally:
        # Restaurer stdout
        sys.stdout = original_stdout

        # Reconfigurer stdout en UTF-8 pour les prints finaux
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')

        # Sauvegarder le rapport dans un fichier
        report_content = captured_output.getvalue()
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\n📄 Rapport complet sauvegardé dans: {args.output}")

    return result


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
