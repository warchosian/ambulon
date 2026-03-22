#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Complet de Test RAG avec Recréation de Collection

Ce script automatise tout le processus :
1. Vérifie les sources dans applications/sireines.rag
2. Supprime l'ancienne collection RAG
3. Recrée la collection avec toutes les sources (nouvelles + anciennes)
4. Attend l'indexation
5. Vérifie que les documents sont bien indexés
6. Lance les tests RAG
7. Compare automatiquement avec les résultats précédents
8. Génère un rapport de comparaison

Usage:
    python workflow_test_rag_complet.py
    python workflow_test_rag_complet.py --skip-delete  # Garde l'ancienne collection
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime
import json

# Forcer l'encodage UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# Configuration
COLLECTION_NAME = "PNM3_SIREINES"
SOURCES_DIR = Path("applications/sireines.rag")
EXTENSIONS = "md,pdf"


def print_header(title):
    """Affiche un en-tête formaté."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_command(cmd, description, check=True):
    """Exécute une commande et affiche le résultat."""
    print(f"🔄 {description}...")
    print(f"   Commande: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0:
        print(f"   ✅ Succès")
        if result.stdout.strip():
            # Afficher seulement les premières lignes
            lines = result.stdout.strip().split('\n')
            for line in lines[:5]:
                print(f"      {line}")
            if len(lines) > 5:
                print(f"      ... ({len(lines) - 5} lignes supplémentaires)")
        return True
    else:
        print(f"   ❌ Échec (code {result.returncode})")
        if result.stderr.strip():
            print(f"   Erreur: {result.stderr.strip()}")
        if check:
            raise Exception(f"Commande échouée: {' '.join(cmd)}")
        return False


def count_source_files():
    """Compte les fichiers sources."""
    if not SOURCES_DIR.exists():
        print(f"❌ Répertoire non trouvé: {SOURCES_DIR}")
        return 0, 0

    md_files = list(SOURCES_DIR.glob("*.md"))
    pdf_files = list(SOURCES_DIR.glob("*.pdf"))

    return len(md_files), len(pdf_files)


def list_source_files():
    """Liste les fichiers sources."""
    if not SOURCES_DIR.exists():
        return []

    files = []
    for pattern in ["*.md", "*.pdf"]:
        files.extend(SOURCES_DIR.glob(pattern))

    return sorted([f.name for f in files])


def delete_collection():
    """Supprime la collection existante."""
    cmd = ["ambulon", "piag-rag-collection-rm", "--collection-name", COLLECTION_NAME]

    # Ne pas fail si la collection n'existe pas
    try:
        run_command(cmd, f"Suppression de la collection {COLLECTION_NAME}", check=False)
    except Exception as e:
        print(f"   ⚠️  Collection peut-être inexistante: {e}")


def create_collection():
    """Crée la collection avec toutes les sources."""
    cmd = [
        "ambulon", "piag-rag-create",
        "--collection-name", COLLECTION_NAME,
        "--description", "Documentation complète SIREINES : DAT, CCTP, C4, Composants, ISO25010",
        "--directory", str(SOURCES_DIR),
        "--extensions", EXTENSIONS
    ]

    run_command(cmd, f"Création de la collection {COLLECTION_NAME}")


def wait_indexation(seconds=30):
    """Attend que l'indexation se termine."""
    print(f"⏳ Attente de l'indexation ({seconds} secondes)...")
    for i in range(seconds, 0, -1):
        print(f"   {i}s restantes...", end='\r', flush=True)
        time.sleep(1)
    print(f"   ✅ Attente terminée" + " " * 20)


def verify_collection():
    """Vérifie le nombre de documents indexés."""
    cmd = ["ambulon", "piag-rag-doc-list", "--collection-name", COLLECTION_NAME]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0:
        # Compter les lignes qui ressemblent à des documents
        lines = result.stdout.strip().split('\n')
        doc_count = 0
        for line in lines:
            if 'sireines' in line.lower() or '.md' in line or '.pdf' in line:
                doc_count += 1

        print(f"✅ Collection vérifiée: ~{doc_count} documents indexés")
        return doc_count
    else:
        print(f"⚠️  Impossible de vérifier la collection")
        return 0


def run_rag_tests():
    """Lance les tests RAG."""
    cmd = ["python", "test_rag_questions_ciblees.py"]

    print(f"🧪 Lancement des tests RAG...")
    print(f"   Commande: {' '.join(cmd)}")
    print(f"   (Cela peut prendre 2-3 minutes...)")

    result = subprocess.run(
        cmd,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0:
        print(f"✅ Tests terminés avec succès")
        return True
    else:
        print(f"⚠️  Tests terminés avec code {result.returncode}")
        return False


def compare_results():
    """Compare les résultats avec l'exécution précédente."""
    cmd = ["python", "compare_rag_results.py", "--auto"]

    print(f"📊 Comparaison des résultats...")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode == 0:
        print(f"✅ Rapport de comparaison généré")
        # Afficher le résumé
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            in_summary = False
            for line in lines:
                if 'RÉSUMÉ' in line or in_summary:
                    in_summary = True
                    print(f"   {line}")
        return True
    else:
        print(f"⚠️  Comparaison échouée")
        if result.stderr:
            print(f"   {result.stderr}")
        return False


def find_latest_test_dir():
    """Trouve le répertoire de test le plus récent."""
    current_dir = Path.cwd()
    test_dirs = sorted(
        current_dir.glob("tests_rag_ciblés_*"),
        key=lambda p: p.name,
        reverse=True
    )

    if test_dirs:
        return test_dirs[0]
    return None


def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Workflow complet de test RAG avec recréation de collection"
    )
    parser.add_argument(
        '--skip-delete',
        action='store_true',
        help="Ne pas supprimer l'ancienne collection (ajouter aux documents existants)"
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help="Recréer la collection sans lancer les tests"
    )
    parser.add_argument(
        '--skip-compare',
        action='store_true',
        help="Ne pas comparer avec les résultats précédents"
    )

    args = parser.parse_args()

    print_header("WORKFLOW COMPLET DE TEST RAG")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Sources: {SOURCES_DIR}")
    print()

    try:
        # Étape 1: Vérification des sources
        print_header("ÉTAPE 1/7 : VÉRIFICATION DES SOURCES")

        md_count, pdf_count = count_source_files()
        total_count = md_count + pdf_count

        print(f"📂 Répertoire source: {SOURCES_DIR.absolute()}")
        print(f"📄 Fichiers trouvés:")
        print(f"   - Markdown (.md): {md_count}")
        print(f"   - PDF (.pdf): {pdf_count}")
        print(f"   - Total: {total_count}")

        if total_count == 0:
            print(f"\n❌ Aucun fichier trouvé dans {SOURCES_DIR}")
            print(f"   Ajoutez des fichiers .md ou .pdf avant de continuer")
            return 1

        print(f"\n📋 Liste des fichiers:")
        files = list_source_files()
        for i, f in enumerate(files[:10], 1):
            print(f"   {i:2d}. {f}")
        if len(files) > 10:
            print(f"   ... et {len(files) - 10} autres fichiers")

        input("\n⏸️  Appuyez sur Entrée pour continuer...")

        # Étape 2: Suppression de l'ancienne collection
        if not args.skip_delete:
            print_header("ÉTAPE 2/7 : SUPPRESSION DE L'ANCIENNE COLLECTION")
            delete_collection()
        else:
            print_header("ÉTAPE 2/7 : SUPPRESSION IGNORÉE (--skip-delete)")

        input("\n⏸️  Appuyez sur Entrée pour continuer...")

        # Étape 3: Création de la nouvelle collection
        print_header("ÉTAPE 3/7 : CRÉATION DE LA NOUVELLE COLLECTION")
        create_collection()

        input("\n⏸️  Appuyez sur Entrée pour continuer...")

        # Étape 4: Attente de l'indexation
        print_header("ÉTAPE 4/7 : ATTENTE DE L'INDEXATION")
        wait_indexation(30)

        # Étape 5: Vérification
        print_header("ÉTAPE 5/7 : VÉRIFICATION DE LA COLLECTION")
        indexed_count = verify_collection()

        if indexed_count == 0:
            print(f"\n⚠️  Attention: Aucun document indexé détecté")
            print(f"   Cela peut être normal si la commande de vérification a échoué")
            print(f"   Les tests vont continuer...")

        input("\n⏸️  Appuyez sur Entrée pour continuer...")

        # Étape 6: Lancement des tests
        if not args.skip_tests:
            print_header("ÉTAPE 6/7 : LANCEMENT DES TESTS RAG")
            run_rag_tests()
        else:
            print_header("ÉTAPE 6/7 : TESTS IGNORÉS (--skip-tests)")

        # Étape 7: Comparaison
        if not args.skip_compare and not args.skip_tests:
            print_header("ÉTAPE 7/7 : COMPARAISON DES RÉSULTATS")
            compare_results()

            # Afficher le chemin du rapport
            if Path("COMPARAISON_RAG.md").exists():
                print(f"\n📄 Rapport de comparaison: COMPARAISON_RAG.md")
        else:
            print_header("ÉTAPE 7/7 : COMPARAISON IGNORÉE")

        # Résumé final
        print_header("RÉSUMÉ FINAL")
        print(f"✅ Workflow terminé avec succès")
        print()
        print(f"📊 Résultats:")
        print(f"   - Fichiers sources: {total_count}")
        print(f"   - Documents indexés: ~{indexed_count}")

        latest_test = find_latest_test_dir()
        if latest_test:
            print(f"   - Répertoire de test: {latest_test.name}")
            print(f"   - Rapport synthèse: {latest_test / '00_SYNTHESE.md'}")

        if Path("COMPARAISON_RAG.md").exists():
            print(f"   - Comparaison: COMPARAISON_RAG.md")

        print()
        print("=" * 80)

        return 0

    except KeyboardInterrupt:
        print("\n\n⏸️  Workflow interrompu par l'utilisateur")
        return 1

    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
