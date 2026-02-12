#!/usr/bin/env python3
# ============================================================================
# FICHIER AUTO-GENERE par scripts/build_offline_package.py
# Date de generation: 2026-02-12 11:49:16
# Ne pas modifier manuellement - vos modifications seront ecrasees
# ============================================================================
"""
Script de desinstallation d'Ambulon.

Ce script desinstalle Ambulon et optionnellement ses dependances.

Usage:
    python uninstall_offline.py

    # Garder les dependances (desinstaller uniquement Ambulon)
    python uninstall_offline.py --keep-deps

IMPORTANT:
    Ce script a ete genere automatiquement par build_offline_package.py
    Date de generation: 2026-02-12 11:49:16
"""

import os
import sys
import subprocess
import argparse


def check_virtual_env():
    """Verifie et informe sur l'environnement virtuel."""
    # Detection robuste : variable d'env, real_prefix (virtualenv), base_prefix (venv)
    in_venv = (
        os.getenv('VIRTUAL_ENV') is not None or
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

    if not in_venv:
        print("[AVERTISSEMENT] Vous n'etes pas dans un environnement virtuel Python")
        print("                La desinstallation affectera l'installation globale")
        print()
        response = input("Continuer quand meme? (oui/non): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("[INFO] Desinstallation annulee par l'utilisateur")
            sys.exit(0)
        print()
    else:
        print("[OK] Environnement virtuel detecte")


def check_pip():
    """Verifie que pip est installe."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[OK] pip detecte")
        return True
    except subprocess.CalledProcessError:
        print("[ERREUR] pip n'est pas installe")
        sys.exit(1)


def is_package_installed(package_name):
    """Verifie si un package est installe."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def uninstall_package(package_name):
    """Desinstalle un package."""
    if not is_package_installed(package_name):
        print(f"[SKIP] {package_name} (non installe)")
        return True

    print(f"[UNINSTALL] {package_name}...", end='', flush=True)

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(" [OK]")
        return True
    except subprocess.CalledProcessError as e:
        print(f" [ERR]")
        print(f"  Erreur: {e.stderr}")
        return False


def main():
    """Point d'entree principal."""
    parser = argparse.ArgumentParser(
        description="Desinstallation d'Ambulon"
    )
    parser.add_argument(
        "--keep-deps",
        action="store_true",
        help="Garder les dependances, desinstaller uniquement Ambulon"
    )
    args = parser.parse_args()

    print("="*70)
    print("  DESINSTALLATION D'AMBULON")
    print("="*70)
    print()
    print("[INFO] Script auto-genere le 2026-02-12 11:49:16")
    print("[INFO] Par scripts/build_offline_package.py")
    print()

    # Verification
    check_pip()
    print()

    check_virtual_env()
    print()

    if not is_package_installed("ambulon"):
        print("[INFO] Ambulon n'est pas installe")
        sys.exit(0)

    print()

    # Packages a desinstaller (ordre inverse de l'installation)
    packages = ["ambulon"]

    if not args.keep_deps:
        print("[INFO] Desinstallation d'Ambulon ET de ses dependances")
        packages.extend([
            "annotated-types",
            "anyio",
            "argcomplete",
            "asttokens",
            "attrs",
            "beautifulsoup4",
            "black",
            "certifi",
            "cffi",
            "chardet",
            "charset-normalizer",
            "click",
            "colorama",
            "commitizen",
            "cryptography"
        ])
    else:
        print("[INFO] Desinstallation d'Ambulon uniquement")

    print()

    # Desinstallation
    failed = []

    for package in packages:
        if not uninstall_package(package):
            failed.append(package)

    # Resume
    print()
    print("="*70)
    print("  RESUME")
    print("="*70)

    if failed:
        print(f"\n[ERREUR] {len(failed)} package(s) ont echoue:")
        for pkg in failed:
            print(f"  - {pkg}")
        sys.exit(1)
    else:
        print("\n[OK] Desinstallation terminee avec succes !")

        if not args.keep_deps:
            print("\nAmbulon et ses dependances ont ete supprimes.")
        else:
            print("\nAmbulon a ete supprime (dependances conservees).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Desinstallation annulee par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] Exception inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
