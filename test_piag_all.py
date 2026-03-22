#!/usr/bin/env python3
"""
Test End-to-End complet - RAG + CHAT PIAG

Lance tous les tests E2E et génère un rapport global.

Usage:
    python test_piag_all.py [--config config/piag.yaml] [--skip-rag] [--skip-chat]
"""

import argparse
import sys
import subprocess
from datetime import datetime
from pathlib import Path


def print_header(title):
    """Affiche un header formaté."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_test(script_name: str, config_path: str):
    """Exécute un script de test et retourne le code de sortie."""
    print(f"🚀 Lancement de {script_name}...")

    try:
        result = subprocess.run(
            [sys.executable, script_name, "--config", config_path],
            capture_output=False,
            text=True
        )
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_name}: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Test End-to-End complet PIAG (RAG + CHAT)")
    parser.add_argument("--config", default="config/piag.yaml", help="Chemin vers le fichier de configuration")
    parser.add_argument("--skip-rag", action="store_true", help="Ignorer les tests RAG")
    parser.add_argument("--skip-chat", action="store_true", help="Ignorer les tests CHAT")
    args = parser.parse_args()

    print_header("TESTS END-TO-END - API PIAG COMPLÈTE")
    print(f"Configuration: {args.config}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not Path(args.config).exists():
        print(f"\n⚠️  ATTENTION: Le fichier de configuration {args.config} n'existe pas")
        print("   Les tests utiliseront les variables d'environnement et les valeurs par défaut")

    results = {}

    # Test RAG
    if not args.skip_rag:
        print_header("TEST 1/2 : API RAG")
        rag_exit_code = run_test("test_piag_rag_e2e.py", args.config)
        results['RAG'] = rag_exit_code == 0
        print(f"\n{'✓' if results['RAG'] else '❌'} Test RAG: {'RÉUSSI' if results['RAG'] else 'ÉCHOUÉ'}")
    else:
        print("\n⏭️  Tests RAG ignorés (--skip-rag)")

    # Test CHAT
    if not args.skip_chat:
        print_header("TEST 2/2 : API CHAT")
        chat_exit_code = run_test("test_piag_chat_e2e.py", args.config)
        results['CHAT'] = chat_exit_code == 0
        print(f"\n{'✓' if results['CHAT'] else '❌'} Test CHAT: {'RÉUSSI' if results['CHAT'] else 'ÉCHOUÉ'}")
    else:
        print("\n⏭️  Tests CHAT ignorés (--skip-chat)")

    # Rapport final
    print_header("RAPPORT FINAL")

    if not results:
        print("Aucun test exécuté")
        return 0

    for test_name, success in results.items():
        status = "✓ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"  {test_name:15} : {status}")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n  Total: {success_count}/{total_count} test(s) réussi(s)")

    print("\n" + "=" * 80)
    print(f"📂 Tous les résultats sont dans: {Path('test_output').absolute()}")
    print("=" * 80 + "\n")

    # Code de sortie global
    if success_count == total_count:
        print("✓ TOUS LES TESTS ONT RÉUSSI\n")
        return 0
    elif success_count > 0:
        print("⚠ CERTAINS TESTS ONT ÉCHOUÉ\n")
        return 1
    else:
        print("❌ TOUS LES TESTS ONT ÉCHOUÉ\n")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
