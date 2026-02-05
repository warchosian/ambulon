#!/usr/bin/env python3
"""
Installation d'Ambulon depuis GitHub.

Ce script :
1. Cree le repertoire wheels/
2. Telecharge les wheels depuis GitHub
3. Installe ambulon depuis les wheels locales (offline)

Usage:
    python install_from_github.py

Prerequis:
    - Python 3.10, 3.11 ou 3.12
    - Connexion internet (pour le telechargement)
"""

import sys
import subprocess
import urllib.request
import urllib.error
from pathlib import Path


# Configuration
GITHUB_BASE_URL = "https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/wheels"
WHEELS_TO_DOWNLOAD = [
    "ambulon-3.0.3-py3-none-any.whl",
    "annotated_types-0.7.0-py3-none-any.whl",
    "anyio-4.12.1-py3-none-any.whl",
    "attrs-25.4.0-py3-none-any.whl",
    "beautifulsoup4-4.14.3-py3-none-any.whl",
    "certifi-2026.1.4-py3-none-any.whl",
    "cffi-2.0.0-cp310-cp310-win_amd64.whl",
    "cffi-2.0.0-cp311-cp311-win_amd64.whl",
    "cffi-2.0.0-cp312-cp312-win_amd64.whl",
    "chardet-5.2.0-py3-none-any.whl",
    "charset_normalizer-3.4.4-cp310-cp310-win_amd64.whl",
    "charset_normalizer-3.4.4-cp311-cp311-win_amd64.whl",
    "charset_normalizer-3.4.4-cp312-cp312-win_amd64.whl",
    "click-8.3.1-py3-none-any.whl",
    "colorama-0.4.6-py2.py3-none-any.whl",
    "cryptography-46.0.4-cp311-abi3-win_amd64.whl",
    "cryptography-46.0.4-cp38-abi3-win_amd64.whl",
    "exceptiongroup-1.3.1-py3-none-any.whl",
    "greenlet-3.3.1-cp310-cp310-win_amd64.whl",
    "greenlet-3.3.1-cp311-cp311-win_amd64.whl",
    "greenlet-3.3.1-cp312-cp312-win_amd64.whl",
    "h11-0.16.0-py3-none-any.whl",
    "httpcore-1.0.9-py3-none-any.whl",
    "httpx_sse-0.4.3-py3-none-any.whl",
    "httpx-0.28.1-py3-none-any.whl",
    "idna-3.11-py3-none-any.whl",
    "importlib_resources-6.5.2-py3-none-any.whl",
    "jsonschema_specifications-2025.9.1-py3-none-any.whl",
    "jsonschema-4.26.0-py3-none-any.whl",
    "lxml-6.0.2-cp310-cp310-win_amd64.whl",
    "lxml-6.0.2-cp311-cp311-win_amd64.whl",
    "lxml-6.0.2-cp312-cp312-win_amd64.whl",
    "markdown-3.10.1-py3-none-any.whl",
    "mcp-1.26.0-py3-none-any.whl",
    "pillow-12.1.0-cp310-cp310-win_amd64.whl",
    "pillow-12.1.0-cp311-cp311-win_amd64.whl",
    "pillow-12.1.0-cp312-cp312-win_amd64.whl",
    "playwright-1.58.0-py3-none-win_amd64.whl",
    "pycparser-3.0-py3-none-any.whl",
    "pydantic_core-2.41.5-cp310-cp310-win_amd64.whl",
    "pydantic_core-2.41.5-cp311-cp311-win_amd64.whl",
    "pydantic_core-2.41.5-cp312-cp312-win_amd64.whl",
    "pydantic_settings-2.12.0-py3-none-any.whl",
    "pydantic-2.12.5-py3-none-any.whl",
    "pyee-13.0.0-py3-none-any.whl",
    "pyjwt-2.11.0-py3-none-any.whl",
    "pymupdf-1.26.7-cp310-abi3-win_amd64.whl",
    "python_dotenv-1.2.1-py3-none-any.whl",
    "python_multipart-0.0.22-py3-none-any.whl",
    "python_slugify-8.0.4-py2.py3-none-any.whl",
    "pywin32-311-cp310-cp310-win_amd64.whl",
    "pywin32-311-cp311-cp311-win_amd64.whl",
    "pywin32-311-cp312-cp312-win_amd64.whl",
    "pyyaml-6.0.3-cp310-cp310-win_amd64.whl",
    "pyyaml-6.0.3-cp311-cp311-win_amd64.whl",
    "pyyaml-6.0.3-cp312-cp312-win_amd64.whl",
    "referencing-0.37.0-py3-none-any.whl",
    "requests-2.32.5-py3-none-any.whl",
    "rpds_py-0.30.0-cp310-cp310-win_amd64.whl",
    "rpds_py-0.30.0-cp311-cp311-win_amd64.whl",
    "rpds_py-0.30.0-cp312-cp312-win_amd64.whl",
    "soupsieve-2.8.3-py3-none-any.whl",
    "sse_starlette-3.2.0-py3-none-any.whl",
    "starlette-0.52.1-py3-none-any.whl",
    "text_unidecode-1.3-py2.py3-none-any.whl",
    "typing_extensions-4.15.0-py3-none-any.whl",
    "typing_inspection-0.4.2-py3-none-any.whl",
    "urllib3-2.6.3-py3-none-any.whl",
    "uvicorn-0.40.0-py3-none-any.whl",
]


def check_python_version():
    """Verifie que Python 3.10+ est installe."""
    version = sys.version_info
    if version < (3, 10):
        print(f"[ERREUR] Python 3.10+ requis, vous avez Python {version.major}.{version.minor}")
        print("\nTelechargez Python depuis: https://www.python.org/downloads/")
        sys.exit(1)

    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} detecte")
    if version.major == 3 and version.minor in (10, 11, 12):
        print(f"     Version compatible OK")
    else:
        print(f"[AVERTISSEMENT] Python {version.major}.{version.minor} non teste")


def check_pip():
    """Verifie que pip est installe."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            check=True
        )
        print(f"[OK] pip detecte")
        return True
    except subprocess.CalledProcessError:
        print("[ERREUR] pip n'est pas installe")
        sys.exit(1)


def create_wheels_dir():
    """Cree le repertoire wheels/ s'il n'existe pas."""
    script_dir = Path(__file__).parent
    wheels_dir = script_dir / "wheels"

    wheels_dir.mkdir(exist_ok=True)
    print(f"[OK] Repertoire wheels/ cree: {wheels_dir}")
    return wheels_dir


def download_wheel(wheel_name, wheels_dir):
    """Telecharge une wheel depuis GitHub."""
    url = f"{GITHUB_BASE_URL}/{wheel_name}"
    dest = wheels_dir / wheel_name

    # Skip si deja telechargee
    if dest.exists():
        return True

    try:
        print(f"  Telechargement: {wheel_name}...", end='', flush=True)
        urllib.request.urlretrieve(url, dest)
        print(" OK")
        return True
    except urllib.error.HTTPError as e:
        print(f" X (HTTP {e.code})")
        return False
    except Exception as e:
        print(f" X ({e})")
        return False


def download_all_wheels(wheels_dir):
    """Telecharge toutes les wheels depuis GitHub (CONNEXION INTERNET REQUISE)."""
    print(f"\n[INFO] Telechargement de {len(WHEELS_TO_DOWNLOAD)} wheels depuis GitHub...")
    print(f"       URL: {GITHUB_BASE_URL}")
    print(f"       !  CONNEXION INTERNET REQUISE")
    print()

    failed = []
    success = 0

    for wheel_name in WHEELS_TO_DOWNLOAD:
        if download_wheel(wheel_name, wheels_dir):
            success += 1
        else:
            failed.append(wheel_name)

    print()
    if failed:
        print(f"[AVERTISSEMENT] {len(failed)} wheel(s) ont echoue:")
        for wheel in failed:
            print(f"  - {wheel}")

    print(f"[OK] {success}/{len(WHEELS_TO_DOWNLOAD)} wheels telechargees")

    # Calculer la taille totale
    total_size = sum(f.stat().st_size for f in wheels_dir.glob("*.whl"))
    total_mb = total_size / (1024 * 1024)
    print(f"     Taille totale: {total_mb:.1f} MB")

    return len(failed) == 0


def install_ambulon(wheels_dir):
    """Installe ambulon depuis les wheels locales (MODE OFFLINE)."""
    print()
    print("="*70)
    print("  INSTALLATION D'AMBULON")
    print("="*70)
    print()
    print("[INFO] Mode: OFFLINE (pas de connexion internet requise)")
    print("       Installation depuis les wheels locales")
    print()

    cmd = [
        sys.executable, "-m", "pip", "install",
        "--no-index",
        "--find-links", str(wheels_dir),
        "ambulon"
    ]

    # Afficher la commande complete
    cmd_str = ' '.join(cmd)
    print(f"[CMD] {cmd_str}")
    print()

    # Afficher la commande simplifiee
    simple_cmd = f"pip install --no-index --find-links={wheels_dir} ambulon"
    print(f"[INFO] Equivalent simplifie:")
    print(f"       {simple_cmd}")
    print()

    try:
        subprocess.run(cmd, check=True)
        print("\n[OK] Installation terminee avec succes ! OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERREUR] Installation echouee: {e}")
        return False


def verify_installation():
    """Verifie que l'installation a reussi."""
    print("\n" + "="*70)
    print("  VERIFICATION")
    print("="*70)

    try:
        result = subprocess.run(
            ["ambulon", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"\n[OK] {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[INFO] Redemarrez votre terminal puis utilisez:")
        print("       ambulon --version")

    print("\nCommandes disponibles:")
    print("  ambulon --help")


def check_existing_wheels(wheels_dir):
    """Verifie si des wheels sont deja presentes."""
    if not wheels_dir.exists():
        return False

    existing = list(wheels_dir.glob("*.whl"))
    if len(existing) == 0:
        return False

    print(f"[INFO] {len(existing)} wheel(s) deja presente(s) dans {wheels_dir}")

    # Verifier si ambulon est present
    ambulon_wheels = [w for w in existing if w.name.startswith("ambulon-")]
    if ambulon_wheels:
        print(f"       Ambulon wheel trouvee: {ambulon_wheels[0].name}")
        return True

    return False


def main():
    """Point d'entree principal."""
    print("="*70)
    print("  INSTALLATION D'AMBULON DEPUIS GITHUB")
    print("="*70)
    print()

    # Support du mode offline via argument
    offline_mode = "--offline" in sys.argv

    # Afficher les modes disponibles
    print("[INFO] Modes d'installation disponibles:")
    print()
    print("  1. Mode AUTOMATIQUE (par defaut)")
    print("     - Telecharge les wheels depuis GitHub (internet requis)")
    print("     - Puis installe en mode offline")
    print()
    print("  2. Mode OFFLINE (--offline)")
    print("     - Utilise les wheels deja telechargees")
    print("     - Aucune connexion internet requise")
    print()

    if offline_mode:
        print("[INFO] Mode selectionne: OFFLINE")
    else:
        print("[INFO] Mode selectionne: AUTOMATIQUE")
    print()

    # Phase 1 : Verifications
    check_python_version()
    check_pip()
    print()

    # Phase 2 : Creation du repertoire
    print("="*70)
    print("  PHASE 1 : CREATION DU REPERTOIRE")
    print("="*70)
    print()
    wheels_dir = create_wheels_dir()

    # Verifier si wheels deja presentes
    has_wheels = check_existing_wheels(wheels_dir)

    if has_wheels and offline_mode:
        print("\n[INFO] Mode offline active : telechargement ignore")
        skip_download = True
    elif has_wheels:
        print("\n[QUESTION] Des wheels sont deja presentes.")
        response = input("           Voulez-vous les telecharger a nouveau ? (o/N) : ").strip().lower()
        skip_download = response not in ['o', 'oui', 'y', 'yes']
    else:
        skip_download = False

    # Phase 2 : Telechargement (si necessaire)
    if not skip_download:
        print("\n" + "="*70)
        print("  PHASE 2 : TELECHARGEMENT DES WHEELS (ONLINE)")
        print("="*70)
        print()
        print("[INFO] !  Cette phase necessite une CONNEXION INTERNET")
        print("       Les wheels seront telechargees depuis GitHub")

        if not download_all_wheels(wheels_dir):
            print("\n[AVERTISSEMENT] Certaines wheels n'ont pas pu etre telechargees")
            print("                L'installation peut echouer")
    else:
        print("\n" + "="*70)
        print("  PHASE 2 : TELECHARGEMENT (IGNORÉ - MODE OFFLINE)")
        print("="*70)
        print()
        print("[INFO] OK Utilisation des wheels existantes")
        print("       Aucune connexion internet requise")

    # Phase 3 : Installation offline
    print("\n" + "="*70)
    print("  PHASE 3 : INSTALLATION (MODE OFFLINE)")
    print("="*70)
    print()
    print("[INFO] OK Cette phase fonctionne HORS LIGNE")
    print("       Installation depuis les wheels locales uniquement")

    if install_ambulon(wheels_dir):
        verify_installation()
    else:
        print("\n[ERREUR] Installation echouee")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Installation annulee par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] Exception inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
