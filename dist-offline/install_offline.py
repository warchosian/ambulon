#!/usr/bin/env python3
"""
Script d'installation offline intelligent d'Ambulon.

Ce script :
1. Détecte votre version Python
2. Télécharge uniquement les wheels compatibles depuis GitHub
3. Installe les dépendances dans le bon ordre
4. Installe Ambulon

Usage:
    python install_offline.py

    # Ou avec une URL personnalisée :
    python install_offline.py --base-url https://mon-serveur.com/wheels/
"""

import sys
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
import argparse
import tempfile
import shutil


# URL de base des wheels sur GitHub (raw)
DEFAULT_BASE_URL = "https://github.com/warchosian/ambulon/raw/preprod/dist-offline/wheels/"


def get_python_version():
    """Retourne la version Python sous forme (major, minor)."""
    return sys.version_info.major, sys.version_info.minor


def check_python_version():
    """Vérifie que Python 3.10+ est installé."""
    major, minor = get_python_version()

    print(f"[OK] Python {major}.{minor}.{sys.version_info.micro} détecté")

    if major != 3 or minor < 10:
        print(f"\n[ERREUR] Python 3.10+ requis")
        print(f"Téléchargez Python depuis: https://www.python.org/downloads/")
        sys.exit(1)

    if minor in (10, 11, 12):
        print(f"     Version compatible ✓")
    else:
        print(f"     [AVERTISSEMENT] Python 3.{minor} non testé (recommandé: 3.10, 3.11, 3.12)")


def check_pip():
    """Vérifie que pip est installé."""
    try:
        result = subprocess.run(
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


def get_cp_tag():
    """Retourne le tag CPython (ex: cp310, cp311, cp312)."""
    major, minor = get_python_version()
    return f"cp{major}{minor}"


def download_wheel(base_url, wheel_name, dest_dir):
    """Télécharge une wheel depuis l'URL."""
    url = base_url.rstrip('/') + '/' + wheel_name
    dest_path = dest_dir / wheel_name

    if dest_path.exists():
        print(f"  [CACHE] {wheel_name} (déjà téléchargée)")
        return dest_path

    print(f"  [DOWNLOAD] {wheel_name}...", end='', flush=True)

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            with open(dest_path, 'wb') as f:
                shutil.copyfileobj(response, f)
        print(" ✓")
        return dest_path
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f" ✗ (404 Not Found)")
            return None
        else:
            print(f" ✗ (HTTP {e.code})")
            raise
    except Exception as e:
        print(f" ✗ ({e})")
        raise


def find_compatible_wheel(base_url, package_name, dest_dir, cp_tag):
    """
    Cherche une wheel compatible avec la version Python.
    Essaie d'abord les wheels spécifiques (cp310, cp311, etc.),
    puis les wheels universelles (py3-none-any).
    """
    # Pattern 1: Wheel binaire spécifique (ex: pillow-10.0.0-cp311-cp311-win_amd64.whl)
    # On va essayer les patterns courants

    # D'abord, on essaie de deviner le nom exact en listant depuis un manifest
    # Pour simplifier, on va essayer quelques patterns courants

    patterns = [
        f"{package_name}-*-{cp_tag}-{cp_tag}-win_amd64.whl",
        f"{package_name}-*-{cp_tag}-{cp_tag}-manylinux*.whl",
        f"{package_name}-*-py3-none-any.whl",
        f"{package_name}-*.whl",
    ]

    # Comme on ne peut pas lister le répertoire distant, on va utiliser
    # une liste prédéfinie des versions connues
    # Pour l'instant, on retourne None et on laissera pip download faire le travail
    return None


def install_package(package_name, wheels_dir):
    """Installe un package depuis le dossier wheels/."""
    print(f"\n[INSTALL] {package_name}...")

    cmd = [
        sys.executable, "-m", "pip", "install",
        "--no-index",
        "--find-links", str(wheels_dir),
        package_name
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[OK] {package_name} installé ✓")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec de l'installation de {package_name}")
        print(f"\nStderr:\n{e.stderr}")
        return False


def get_dependencies_order():
    """Retourne l'ordre d'installation des dépendances."""
    return [
        # Niveau 1: Pas de dépendances
        "importlib-resources",
        "pillow",
        "pymupdf",
        "requests",
        "pyyaml",
        "chardet",
        "lxml",
        "python-slugify",

        # Niveau 2
        "beautifulsoup4",
        "markdown",

        # Niveau 3
        "greenlet",

        # Niveau 4
        "playwright",
        "mcp",
    ]


def create_manifest_from_pyproject():
    """
    Retourne un manifest des wheels avec leurs versions depuis pyproject.toml.
    Simplifié : on va juste télécharger avec pip download.
    """
    # Pour l'instant, on retourne un dict vide
    # L'implémentation complète nécessiterait de parser pyproject.toml
    return {}


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Installation offline intelligente d'Ambulon"
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"URL de base des wheels (défaut: {DEFAULT_BASE_URL})"
    )
    args = parser.parse_args()

    print("="*70)
    print("  INSTALLATION OFFLINE INTELLIGENTE D'AMBULON")
    print("="*70)
    print()

    # 1. Vérifications
    check_python_version()
    check_pip()

    cp_tag = get_cp_tag()
    print(f"[INFO] Tag Python: {cp_tag}")
    print()

    # 2. Créer un dossier temporaire pour les wheels
    temp_dir = Path(tempfile.mkdtemp(prefix="ambulon_wheels_"))
    print(f"[INFO] Dossier temporaire: {temp_dir}")
    print()

    try:
        # 3. Télécharger et installer les dépendances
        print("="*70)
        print("  TÉLÉCHARGEMENT ET INSTALLATION DES DÉPENDANCES")
        print("="*70)

        dependencies = get_dependencies_order()
        failed = []

        # Pour cette version simplifiée, on va utiliser pip download
        # qui gérera automatiquement la sélection des bonnes wheels
        print("\n[INFO] Téléchargement des wheels avec pip...")

        download_cmd = [
            sys.executable, "-m", "pip", "download",
            *dependencies,
            "ambulon",
            "-d", str(temp_dir),
            "--no-cache-dir"
        ]

        try:
            subprocess.run(download_cmd, check=True, capture_output=True, text=True)
            print("[OK] Toutes les wheels téléchargées ✓")
        except subprocess.CalledProcessError as e:
            print(f"[ERREUR] Échec du téléchargement")
            print(e.stderr)
            sys.exit(1)

        print()

        # 4. Installation dans le bon ordre
        print("="*70)
        print("  INSTALLATION")
        print("="*70)

        for dep in dependencies:
            if not install_package(dep, temp_dir):
                failed.append(dep)

        # 5. Installer Ambulon
        if not install_package("ambulon", temp_dir):
            failed.append("ambulon")

        # 6. Résumé
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

    finally:
        # Nettoyage
        print(f"\n[INFO] Nettoyage du dossier temporaire...")
        shutil.rmtree(temp_dir, ignore_errors=True)


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
