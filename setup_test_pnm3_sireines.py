#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test End-to-End pour la collection PNM3_SIREINES

Ce script :
1. Crée la collection PNM3_SIREINES avec tous les documents
2. Effectue 5 recherches RAG de test
3. Génère 5 réponses techniques avec RAG + CHAT
4. Organise les résultats dans des répertoires séparés

Usage: python setup_test_pnm3_sireines.py
"""

import subprocess
import sys
import time
import os
import json
from pathlib import Path
from datetime import datetime


# Forcer l'encodage UTF-8 pour Python et les sous-processus
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Configuration
COLLECTION_NAME = "PNM3_SIREINES"
DOCS_DIR = Path("applications/sireines.rag")
CHUNKS_DIR = Path("output_test_pnm3_sireines_chunks")
RESPONSE_DIR = Path("output_test_pnm3_sireines_responses")


def print_header(title):
    """Affiche un en-tête formaté."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_command(command_list, description=None, step_number=None):
    """Affiche une commande de manière visuelle."""
    print("\n" + "=" * 80)
    if step_number:
        print(f"STEP {step_number}: {description}" if description else f"STEP {step_number}")
    elif description:
        print(description)
    print("=" * 80)
    print("Command:")
    print(f"  {command_list[0]} \\")
    for arg in command_list[1:-1]:
        print(f"    {arg} \\")
    print(f"    {command_list[-1]}")
    print("=" * 80 + "\n")


def extract_json_from_output(output_text):
    """
    Extrait le JSON valide d'une sortie contenant des logs et warnings.

    Args:
        output_text: Texte complet de la sortie

    Returns:
        Chaîne JSON valide ou le texte original si pas de JSON trouvé
    """
    # Chercher le début d'un objet ou tableau JSON
    # On cherche soit { soit [ en début de ligne (après avoir ignoré les logs)
    lines = output_text.split('\n')

    json_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('{') or stripped.startswith('['):
            # Vérifier que ce n'est pas juste un log contenant {
            # Un vrai JSON commence par { ou [ en début de ligne sans préfixe
            if not any([
                line.startswith('[INFO]'),
                line.startswith('[ERROR]'),
                line.startswith('[DEBUG]'),
                line.startswith('[WARNING]'),
                'Résultats de la recherche' in line
            ]):
                json_start = i
                break

    if json_start == -1:
        # Pas de JSON trouvé, retourner le texte original
        return output_text

    # Extraire du début du JSON jusqu'à la fin
    json_text = '\n'.join(lines[json_start:])

    # Essayer de valider que c'est du JSON valide
    try:
        json.loads(json_text)
        return json_text
    except json.JSONDecodeError:
        # Si invalide, retourner l'original
        return output_text


def run_command(command_list, output_file=None, description=None, step_number=None):
    """
    Exécute une commande et retourne le code de sortie.

    Args:
        command_list: Liste des arguments de la commande
        output_file: Fichier où rediriger la sortie (optionnel)
        description: Description de la commande
        step_number: Numéro de l'étape

    Returns:
        Code de sortie de la commande
    """
    # Afficher la commande
    print_command(command_list, description, step_number)

    # Exécuter la commande
    try:
        if output_file:
            # Rediriger la sortie vers un fichier avec encodage UTF-8
            # On capture d'abord la sortie puis on l'écrit pour éviter les problèmes d'encodage
            result = subprocess.run(
                command_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                errors='replace',
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
            )

            # Nettoyer la sortie si c'est un fichier JSON
            output_content = result.stdout
            if str(output_file).endswith('.json'):
                output_content = extract_json_from_output(output_content)

            # Écrire dans le fichier avec encodage UTF-8
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
        else:
            # Afficher la sortie directement
            result = subprocess.run(
                command_list,
                encoding='utf-8',
                errors='replace',
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
            )

        # Afficher le résultat
        if result.returncode == 0:
            print("[OK] Commande exécutée avec succès\n")
        else:
            print(f"[ERREUR] Échec (code {result.returncode})\n")

        return result.returncode

    except Exception as e:
        print(f"[ERREUR] Exception: {e}\n")
        return 1


def main():
    """Point d'entrée principal du script."""

    # En-tête
    print_header("CRÉATION ET TEST DE LA COLLECTION PNM3_SIREINES")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ========================================================================
    # ÉTAPE 1 : Vérification des prérequis
    # ========================================================================
    print_header("ÉTAPE 1 : VÉRIFICATION DES PRÉREQUIS")

    if not DOCS_DIR.exists():
        print(f"[ERREUR] Le répertoire {DOCS_DIR} n'existe pas")
        sys.exit(1)
    print(f"[OK] Répertoire {DOCS_DIR} trouvé")

    # Compter les documents
    md_count = len(list(DOCS_DIR.glob("*.md")))
    pdf_count = len(list(DOCS_DIR.glob("*.pdf")))
    total_count = md_count + pdf_count

    print(f"[INFO] Documents trouvés : {md_count} fichiers .md, {pdf_count} fichiers .pdf (Total: {total_count})")

    if total_count == 0:
        print("[ERREUR] Aucun document trouvé")
        sys.exit(1)

    print("[OK] Prérequis validés\n")

    # Créer les répertoires de sortie
    CHUNKS_DIR.mkdir(exist_ok=True)
    RESPONSE_DIR.mkdir(exist_ok=True)

    input("Appuyez sur Entrée pour continuer...")

    # ========================================================================
    # ÉTAPE 2 : Création de la collection
    # ========================================================================
    print_header("ÉTAPE 2 : CRÉATION DE LA COLLECTION")

    cmd = [
        "ambulon", "piag-rag-create",
        "--collection-name", COLLECTION_NAME,
        "--description", "Documentation complète SIREINES : DAT, CCTP, C4, Composants, ISO25010",
        "--directory", str(DOCS_DIR),
        "--extensions", "md,pdf"
    ]

    returncode = run_command(cmd, description="Création de la collection et upload des documents")

    if returncode != 0:
        print("[ERREUR] Échec de la création de la collection")
        sys.exit(1)

    input("Appuyez sur Entrée pour continuer...")

    # ========================================================================
    # ÉTAPE 3 : Attente de l'indexation
    # ========================================================================
    print_header("ÉTAPE 3 : ATTENTE DE L'INDEXATION (30 secondes)")

    for i in range(30, 0, -1):
        print(f"\rTemps restant : {i}s  ", end='', flush=True)
        time.sleep(1)
    print("\n[OK] Indexation supposée terminée\n")

    input("Appuyez sur Entrée pour continuer...")

    # ========================================================================
    # ÉTAPE 4 : Vérification de la collection
    # ========================================================================
    print_header("ÉTAPE 4 : VÉRIFICATION DE LA COLLECTION")

    # Get collection
    cmd = [
        "ambulon", "piag-rag-collection-get",
        "--collection-name", COLLECTION_NAME
    ]
    run_command(cmd, description="Récupération des informations de la collection")

    input("Appuyez sur Entrée pour continuer...")

    # List documents
    cmd = [
        "ambulon", "piag-rag-doc-list",
        "--collection-name", COLLECTION_NAME
    ]
    run_command(cmd, description="Liste des documents dans la collection")

    input("Appuyez sur Entrée pour continuer...")

    # ========================================================================
    # ÉTAPE 5 : Tests de recherche RAG
    # ========================================================================
    print_header("ÉTAPE 5 : TESTS DE RECHERCHE RAG (5 recherches)")

    searches = [
        ("architecture technique SIREINES", "search_1.json"),
        ("module gestion alertes", "search_2.json"),
        ("modele C4", "search_3.json"),
        ("exigences qualite ISO 25010", "search_4.json"),
        ("securite authentification", "search_5.json"),
    ]

    for i, (query, filename) in enumerate(searches, 1):
        cmd = [
            "ambulon", "piag-rag-search",
            "--collection-name", COLLECTION_NAME,
            "--query", query,
            "--top-k", "5",
            "--mode", "hybrid",
            "--rerank",
            "--format", "json"
        ]

        output_file = CHUNKS_DIR / filename
        returncode = run_command(
            cmd,
            output_file=output_file,
            description=f"Recherche {query}",
            step_number=f"{i}/5"
        )

        input("Appuyez sur Entrée pour continuer...")

    # ========================================================================
    # ÉTAPE 6 : Tests RAG + CHAT
    # ========================================================================
    print_header("ÉTAPE 6 : TESTS RAG + CHAT (5 questions techniques)")

    questions = [
        {
            "name": "Architecture technique",
            "search_query": "architecture technique composants technologies patterns",
            "question": "Décris l'architecture technique du système SIREINES en détaillant les composants, les technologies utilisées et les patterns architecturaux.",
            "chunks_file": "architecture_chunks.json",
            "response_file": "architecture_reponse.md"
        },
        {
            "name": "Modèle C4",
            "search_query": "modele C4 context container component",
            "question": "Explique le modèle C4 appliqué à SIREINES. Quels sont les 4 niveaux et que représentent-ils ?",
            "chunks_file": "c4model_chunks.json",
            "response_file": "c4model_reponse.md"
        },
        {
            "name": "Module gestion alertes",
            "search_query": "module alertes fonctionnalites workflow",
            "question": "Comment fonctionne le module de gestion des alertes dans SIREINES ? Quelles sont ses fonctionnalités principales ?",
            "chunks_file": "alertes_chunks.json",
            "response_file": "alertes_reponse.md"
        },
        {
            "name": "Exigences ISO 25010",
            "search_query": "ISO 25010 qualite performance securite",
            "question": "Quelles sont les exigences de qualité ISO 25010 définies pour SIREINES ?",
            "chunks_file": "iso25010_chunks.json",
            "response_file": "iso25010_reponse.md"
        },
        {
            "name": "Sécurité et authentification",
            "search_query": "securite authentification autorisation RBAC",
            "question": "Comment est implémentée la sécurité dans SIREINES ? Décris les mécanismes d'authentification et d'autorisation.",
            "chunks_file": "securite_chunks.json",
            "response_file": "securite_reponse.md"
        }
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}/5: {q['name']}")
        print(f"{'='*80}\n")

        # Étape 1 : Recherche des chunks
        print(f"[1/2] Recherche des chunks...")

        cmd_search = [
            "ambulon", "piag-rag-search",
            "--collection-name", COLLECTION_NAME,
            "--query", q['search_query'],
            "--top-k", "7",
            "--mode", "hybrid",
            "--rerank",
            "--format", "json"
        ]

        chunks_file = CHUNKS_DIR / q['chunks_file']
        returncode = run_command(
            cmd_search,
            output_file=chunks_file,
            description=f"Recherche chunks pour {q['name']}"
        )

        if returncode != 0:
            print("[ERREUR] Échec de la recherche")
            input("Appuyez sur Entrée pour continuer...")
            continue

        print("[OK] Chunks trouvés\n")

        # Étape 2 : Génération de la réponse
        print(f"[2/2] Génération de la réponse...")

        cmd_chat = [
            "ambulon", "piag-chat-query",
            "--question", q['question'],
            "--chunks", str(chunks_file),
            "--output", str(RESPONSE_DIR / q['response_file'])
        ]

        returncode = run_command(
            cmd_chat,
            description=f"Génération réponse pour {q['name']}"
        )

        if returncode == 0:
            print("[OK] Réponse générée")
        else:
            print("[ERREUR] Échec de la génération")

        input("Appuyez sur Entrée pour continuer...")

    # ========================================================================
    # RÉSUMÉ FINAL
    # ========================================================================
    print_header("RÉSUMÉ FINAL")

    print("[OK] Script exécuté avec succès !\n")
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Documents sources : {total_count}")
    print(f"Recherches : 5")
    print(f"Questions techniques : 5\n")

    print("Fichiers générés :\n")
    print(f"  Répertoire CHUNKS : {CHUNKS_DIR}/")
    print(f"  - 5 fichiers search_*.json (résultats recherche)")
    print(f"  - 5 fichiers *_chunks.json (chunks trouvés)\n")

    print(f"  Répertoire RÉPONSES : {RESPONSE_DIR}/")
    print(f"  - 5 fichiers *_reponse.md (réponses générées)\n")

    print("Consultez les réponses :")
    for q in questions:
        response_file = RESPONSE_DIR / q['response_file']
        print(f"  {response_file}")

    print("\nConsultez les chunks :")
    print(f"  {CHUNKS_DIR / 'architecture_chunks.json'}")
    print(f"  {CHUNKS_DIR / 'search_1.json'}")

    print("\n" + "=" * 80)

    input("\nAppuyez sur Entrée pour terminer...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Script interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERREUR] Exception non gérée : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
