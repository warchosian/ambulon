#!/usr/bin/env python3
# ============================================================================
# FICHIER AUTO-GENERE par scripts/build_offline_package.py
# Date de generation: 2026-02-12 11:49:16
# Ne pas modifier manuellement - vos modifications seront ecrasees
# ============================================================================
"""
Installation offline simplifiee d'Ambulon en UNE SEULE COMMANDE.

Phase 1 (ONLINE) : python download_wheels.py
Phase 2 (OFFLINE): python install_offline.py

Ce script installe ambulon + toutes dependances depuis wheels/
pip resout automatiquement l'ordre des dependances.

IMPORTANT:
    Ce script a ete genere automatiquement par build_offline_package.py
    Date de generation: 2026-02-12 11:49:16
"""

import os
import sys
import subprocess
from pathlib import Path


def check_virtual_env():
    """Verifie et demande confirmation pour environnement virtuel."""
    # Detection robuste : variable d'env, real_prefix (virtualenv), base_prefix (venv)
    in_venv = (
        os.getenv('VIRTUAL_ENV') is not None or
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

    if not in_venv:
        print("[AVERTISSEMENT] Vous n'etes pas dans un environnement virtuel Python")
        print("                Il est FORTEMENT recommande d'utiliser un environnement virtuel")
        print()
        print("Pour creer un environnement virtuel:")
        print("  python -m venv .venv")
        print("  .venv\\Scripts\\activate  (Windows)")
        print("  source .venv/bin/activate  (Linux/Mac)")
        print()
        response = input("Continuer quand meme sans environnement virtuel? (oui/non): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("[INFO] Installation annulee par l'utilisateur")
            sys.exit(0)
        print()
    else:
        print("[OK] Environnement virtuel detecte")


def check_python_version():
    """Verifie que Python 3.10+ est installe."""
    version = sys.version_info
    if version < (3, 10):
        print(f"[ERREUR] Python 3.10+ requis, vous avez Python {{version.major}}.{{version.minor}}")
        print("\nTelechargez Python depuis: https://www.python.org/downloads/")
        sys.exit(1)

    print(f"[OK] Python {{version.major}}.{{version.minor}}.{{version.micro}} detecte")


def find_wheels_dir():
    """Trouve le dossier wheels/ a cote du script."""
    script_dir = Path(__file__).parent
    wheels_dir = script_dir / "wheels"

    if not wheels_dir.exists():
        print("[ERREUR] Dossier wheels/ introuvable")
        print(f"Attendu: {{wheels_dir}}")
        print("\nExecutez d'abord : python download_wheels.py")
        sys.exit(1)

    wheels_count = len(list(wheels_dir.glob("*.whl")))
    if wheels_count == 0:
        print("[ERREUR] Aucune wheel trouvee dans wheels/")
        print("\nExecutez d'abord : python download_wheels.py")
        sys.exit(1)

    print(f"[OK] {{wheels_count}} wheels trouvees dans: {{wheels_dir}}")
    return wheels_dir


def install_ambulon(wheels_dir):
    """Installe ambulon + toutes dependances en une seule commande."""
    print("\n[INFO] Installation d'ambulon + dependances...")
    print("       Mode OFFLINE : aucun acces internet requis")
    print()

    cmd = [
        sys.executable, "-m", "pip", "install",
        "--no-index",                    # Pas d'acces internet
        "--find-links", str(wheels_dir), # Cherche dans wheels/
        "ambulon"                        # Package principal
    ]

    # Afficher la commande qui va etre executee
    cmd_str = " ".join(cmd)
    print(f"Commande executee :")
    print(f"  {cmd_str}")
    print()

    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True  # Capture la sortie pour ne pas polluer
        )

        # Afficher uniquement les lignes importantes
        output_lines = result.stdout.strip().split('\n')
        print("[INFO] Installation en cours...")

        # Afficher les packages installes/deja presents
        for line in output_lines:
            if 'Successfully installed' in line or 'Requirement already satisfied' in line:
                print(f"  {line}")
            elif 'Installing collected packages' in line:
                print(f"  {line}")

        print()
        print("[OK] Installation terminee")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERREUR] Installation echouee (code {e.returncode})")
        print("\nSortie pip :")
        print(e.stdout)
        if e.stderr:
            print("\nErreurs :")
            print(e.stderr)
        return False


def verify_installation():
    """Verifie que ambulon est installe correctement."""
    print("\n" + "="*70)
    print("  VERIFICATION")
    print("="*70)
    print()
    print("Commande executee : ambulon --version")
    print()

    try:
        result = subprocess.run(
            ["ambulon", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        print(f"[OK] {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("[INFO] La commande 'ambulon' n'est pas encore reconnue")
        print("       Redemarrez votre terminal ou utilisez:")
        print("       python -m app.cli.cli --version")
        return False


def main():
    """Point d'entree principal."""
    print("="*70)
    print("  INSTALLATION OFFLINE D'AMBULON")
    print("="*70)
    print()
    print("[INFO] Script auto-genere le 2026-02-12 11:49:16")
    print("[INFO] Par scripts/build_offline_package.py")
    print()

    # Verifications
    check_python_version()
    print()

    check_virtual_env()
    print()

    wheels_dir = find_wheels_dir()
    print()

    # Installation en UNE SEULE COMMANDE
    print("="*70)
    print("  INSTALLATION")
    print("="*70)

    if not install_ambulon(wheels_dir):
        print("\n[ERREUR] Installation incomplete")
        sys.exit(1)

    # Verification
    verify_installation()

    print()
    print("="*70)
    print("  INSTALLATION TERMINEE")
    print("="*70)
    print()
    print("[OK] Ambulon est installe !")
    print()
    print("Commandes disponibles:")
    print("  ambulon --help")
    print("  ambulon md2html fichier.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Installation annulee par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] Exception inattendue: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
