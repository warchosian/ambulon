#!/usr/bin/env python3
"""
Installation d'Ambulon depuis les wheels locales.

Ce script installe Ambulon depuis le dossier wheels/ adjacent.

Usage:
    cd dist-offline
    python install_from_wheels.py

Prérequis:
    - Le dossier wheels/ doit être présent à côté de ce script
    - Python 3.10, 3.11 ou 3.12
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Vérifie que Python 3.10+ est installé."""
    version = sys.version_info
    if version < (3, 10):
        print(f"[ERREUR] Python 3.10+ requis, vous avez Python {version.major}.{version.minor}")
        print("\nTéléchargez Python depuis: https://www.python.org/downloads/")
        sys.exit(1)

    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} détecté")
    if version.major == 3 and version.minor in (10, 11, 12):
        print(f"     Version compatible ✓")
    else:
        print(f"[AVERTISSEMENT] Python {version.major}.{version.minor} non testé")


def check_pip():
    """Vérifie que pip est installé."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            check=True
        )
        print(f"[OK] pip détecté")
        return True
    except subprocess.CalledProcessError:
        print("[ERREUR] pip n'est pas installé")
        sys.exit(1)


def find_wheels_dir():
    """Trouve le dossier wheels/."""
    script_dir = Path(__file__).parent
    wheels_dir = script_dir / "wheels"

    if wheels_dir.exists():
        wheels_count = len(list(wheels_dir.glob("*.whl")))
        if wheels_count > 0:
            print(f"[OK] Dossier wheels trouvé: {wheels_dir}")
            print(f"     {wheels_count} wheels disponibles")
            return wheels_dir

    print("[ERREUR] Dossier wheels/ introuvable ou vide")
    print(f"         Cherché dans: {wheels_dir}")
    print()
    print("Solution:")
    print("  1. Assurez-vous d'être dans le dossier dist-offline/")
    print("  2. Ou téléchargez les wheels depuis:")
    print("     https://github.com/warchosian/ambulon/tree/preprod/v3.0.2-stable/dist-offline/wheels")
    sys.exit(1)


def install_package(package_name, wheels_dir):
    """Installe un package depuis le dossier wheels/."""
    print(f"[INSTALL] {package_name}...", end='', flush=True)

    cmd = [
        sys.executable, "-m", "pip", "install",
        "--no-index",
        "--find-links", str(wheels_dir),
        package_name
    ]

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(" ✓")
        return True
    except subprocess.CalledProcessError as e:
        print(" ✗")
        print(f"    Erreur: {e.stderr}")
        return False


def main():
    """Point d'entrée principal."""
    print("="*70)
    print("  INSTALLATION D'AMBULON DEPUIS WHEELS LOCALES")
    print("="*70)
    print()

    # 1. Vérifications
    check_python_version()
    check_pip()
    wheels_dir = find_wheels_dir()
    print()

    # 2. Ordre d'installation des dépendances
    print("="*70)
    print("  INSTALLATION DES DÉPENDANCES")
    print("="*70)
    print()

    dependencies_order = [
        "importlib-resources",
        "pillow",
        "pymupdf",
        "requests",
        "pyyaml",
        "chardet",
        "lxml",
        "python-slugify",
        "beautifulsoup4",
        "markdown",
        "greenlet",
        "playwright",
        "mcp",
    ]

    failed = []

    for package in dependencies_order:
        if not install_package(package, wheels_dir):
            failed.append(package)

    # 3. Installation d'Ambulon
    print()
    print("="*70)
    print("  INSTALLATION D'AMBULON")
    print("="*70)
    print()

    if not install_package("ambulon", wheels_dir):
        failed.append("ambulon")

    # 4. Résumé
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
        print("\n[OK] Installation terminée avec succès ! ✓")
        print("\nVérification:")
        try:
            result = subprocess.run(
                ["ambulon", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  [INFO] Redémarrez votre terminal puis utilisez:")
            print("         ambulon --version")

        print("\nCommandes disponibles:")
        print("  ambulon --help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Installation annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] Exception inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
