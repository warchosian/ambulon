#!/usr/bin/env python3
"""
Script de désinstallation d'Ambulon.

Ce script désinstalle Ambulon et optionnellement ses dépendances.

Usage:
    python uninstall_offline.py

    # Garder les dépendances (désinstaller uniquement Ambulon)
    python uninstall_offline.py --keep-deps
"""

import sys
import subprocess
import argparse


def check_pip():
    """Vérifie que pip est installé."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[OK] pip détecté")
        return True
    except subprocess.CalledProcessError:
        print("[ERREUR] pip n'est pas installé")
        sys.exit(1)


def is_package_installed(package_name):
    """Vérifie si un package est installé."""
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
    """Désinstalle un package."""
    if not is_package_installed(package_name):
        print(f"[SKIP] {package_name} (non installé)")
        return True

    print(f"[UNINSTALL] {package_name}...", end='', flush=True)

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(" ✓")
        return True
    except subprocess.CalledProcessError as e:
        print(f" ✗")
        print(f"  Erreur: {e.stderr}")
        return False


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Désinstallation d'Ambulon"
    )
    parser.add_argument(
        "--keep-deps",
        action="store_true",
        help="Garder les dépendances, désinstaller uniquement Ambulon"
    )
    args = parser.parse_args()

    print("="*70)
    print("  DÉSINSTALLATION D'AMBULON")
    print("="*70)
    print()

    # Vérification
    check_pip()

    if not is_package_installed("ambulon"):
        print("[INFO] Ambulon n'est pas installé")
        sys.exit(0)

    print()

    # Packages à désinstaller (ordre inverse de l'installation)
    packages = ["ambulon"]

    if not args.keep_deps:
        print("[INFO] Désinstallation d'Ambulon ET de ses dépendances")
        packages.extend([
            "mcp",
            "playwright",
            "greenlet",
            "markdown",
            "beautifulsoup4",
            "python-slugify",
            "lxml",
            "chardet",
            "pyyaml",
            "requests",
            "pymupdf",
            "pillow",
            "importlib-resources",
        ])
    else:
        print("[INFO] Désinstallation d'Ambulon uniquement")

    print()

    # Désinstallation
    failed = []

    for package in packages:
        if not uninstall_package(package):
            failed.append(package)

    # Résumé
    print()
    print("="*70)
    print("  RÉSUMÉ")
    print("="*70)

    if failed:
        print(f"\n[ERREUR] {len(failed)} package(s) ont échoué:")
        for pkg in failed:
            print(f"  - {pkg}")
        sys.exit(1)
    else:
        print("\n[OK] Désinstallation terminée avec succès ! ✓")

        if not args.keep_deps:
            print("\nAmbulonà et ses dépendances ont été supprimés.")
        else:
            print("\nAmbulonà été supprimé (dépendances conservées).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Désinstallation annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] Exception inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
