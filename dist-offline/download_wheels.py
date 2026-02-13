#!/usr/bin/env python3
# ============================================================================
# FICHIER AUTO-GENERE par scripts/build_offline_package.py
# Date de generation: 2026-02-12 11:49:16
# Ne pas modifier manuellement - vos modifications seront ecrasees
# ============================================================================
"""
Telechargement des wheels Ambulon depuis GitHub.

Ce script telecharge uniquement les wheels (ONLINE).
Pour installer, utilisez ensuite install_offline.py.

Usage:
    python download_wheels.py

Prerequis:
    - Python 3.10, 3.11 ou 3.12
    - Connexion internet REQUISE

IMPORTANT:
    Ce script a ete genere automatiquement par build_offline_package.py
"""

import sys
import urllib.request
import urllib.error
from pathlib import Path


# Configuration
GITHUB_BASE_URL = "https://github.com/warchosian/ambulon/raw/main/dist-offline/wheels"
WHEELS_TO_DOWNLOAD = [
    "ambulon-3.0.2-py3-none-any.whl",
    "ambulon-3.0.3-py3-none-any.whl",
    "ambulon-3.0.4-py3-none-any.whl",
    "annotated_types-0.7.0-py3-none-any.whl",
    "anyio-4.12.1-py3-none-any.whl",
    "argcomplete-3.6.3-py3-none-any.whl",
    "asttokens-3.0.1-py3-none-any.whl",
    "attrs-25.4.0-py3-none-any.whl",
    "backports_asyncio_runner-1.2.0-py3-none-any.whl",
    "beautifulsoup4-4.14.3-py3-none-any.whl",
    "black-26.1.0-cp310-cp310-win_amd64.whl",
    "black-26.1.0-cp311-cp311-win_amd64.whl",
    "black-26.1.0-cp312-cp312-win_amd64.whl",
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
    "commitizen-4.13.7-py3-none-any.whl",
    "cryptography-46.0.4-cp311-abi3-win_amd64.whl",
    "cryptography-46.0.4-cp38-abi3-win_amd64.whl",
    "cryptography-46.0.5-cp311-abi3-win_amd64.whl",
    "cryptography-46.0.5-cp38-abi3-win_amd64.whl",
    "decli-0.6.3-py3-none-any.whl",
    "decorator-5.2.1-py3-none-any.whl",
    "deprecated-1.3.1-py2.py3-none-any.whl",
    "exceptiongroup-1.3.1-py3-none-any.whl",
    "executing-2.2.1-py2.py3-none-any.whl",
    "greenlet-3.3.1-cp310-cp310-win_amd64.whl",
    "greenlet-3.3.1-cp311-cp311-win_amd64.whl",
    "greenlet-3.3.1-cp312-cp312-win_amd64.whl",
    "h11-0.16.0-py3-none-any.whl",
    "httpcore-1.0.9-py3-none-any.whl",
    "httpx-0.28.1-py3-none-any.whl",
    "httpx_sse-0.4.3-py3-none-any.whl",
    "i2-0.1.63-py3-none-any.whl",
    "idna-3.11-py3-none-any.whl",
    "importlib_resources-6.5.2-py3-none-any.whl",
    "iniconfig-2.3.0-py3-none-any.whl",
    "ipython-8.38.0-py3-none-any.whl",
    "ipython-9.10.0-py3-none-any.whl",
    "ipython_pygments_lexers-1.1.1-py3-none-any.whl",
    "isort-7.0.0-py3-none-any.whl",
    "jedi-0.19.2-py2.py3-none-any.whl",
    "jinja2-3.1.6-py3-none-any.whl",
    "jsonschema-4.26.0-py3-none-any.whl",
    "jsonschema_specifications-2025.9.1-py3-none-any.whl",
    "kroki-0.1.6-py3-none-any.whl",
    "lxml-6.0.2-cp310-cp310-win_amd64.whl",
    "lxml-6.0.2-cp311-cp311-win_amd64.whl",
    "lxml-6.0.2-cp312-cp312-win_amd64.whl",
    "markdown-3.10.1-py3-none-any.whl",
    "markdown-3.10.2-py3-none-any.whl",
    "markupsafe-3.0.3-cp310-cp310-win_amd64.whl",
    "markupsafe-3.0.3-cp311-cp311-win_amd64.whl",
    "markupsafe-3.0.3-cp312-cp312-win_amd64.whl",
    "matplotlib_inline-0.2.1-py3-none-any.whl",
    "mcp-1.26.0-py3-none-any.whl",
    "mypy_extensions-1.1.0-py3-none-any.whl",
    "packaging-26.0-py3-none-any.whl",
    "parso-0.8.6-py2.py3-none-any.whl",
    "pathspec-1.0.4-py3-none-any.whl",
    "pexpect-4.9.0-py2.py3-none-any.whl",
    "pillow-12.1.0-cp310-cp310-win_amd64.whl",
    "pillow-12.1.0-cp311-cp311-win_amd64.whl",
    "pillow-12.1.0-cp312-cp312-win_amd64.whl",
    "pillow-12.1.1-cp310-cp310-win_amd64.whl",
    "pillow-12.1.1-cp311-cp311-win_amd64.whl",
    "pillow-12.1.1-cp312-cp312-win_amd64.whl",
    "platformdirs-4.5.1-py3-none-any.whl",
    "playwright-1.58.0-py3-none-win_amd64.whl",
    "pluggy-1.6.0-py3-none-any.whl",
    "prompt_toolkit-3.0.51-py3-none-any.whl",
    "prompt_toolkit-3.0.52-py3-none-any.whl",
    "ptyprocess-0.7.0-py2.py3-none-any.whl",
    "pure_eval-0.2.3-py3-none-any.whl",
    "pycparser-3.0-py3-none-any.whl",
    "pydantic-2.12.5-py3-none-any.whl",
    "pydantic_core-2.41.5-cp310-cp310-win_amd64.whl",
    "pydantic_core-2.41.5-cp311-cp311-win_amd64.whl",
    "pydantic_core-2.41.5-cp312-cp312-win_amd64.whl",
    "pydantic_settings-2.12.0-py3-none-any.whl",
    "pyee-13.0.0-py3-none-any.whl",
    "pygments-2.19.2-py3-none-any.whl",
    "pyjwt-2.11.0-py3-none-any.whl",
    "pymupdf-1.26.7-cp310-abi3-win_amd64.whl",
    "pymupdf-1.27.1-cp310-abi3-win_amd64.whl",
    "pytesseract-0.3.13-py3-none-any.whl",
    "pytest-8.4.2-py3-none-any.whl",
    "pytest-9.0.2-py3-none-any.whl",
    "pytest_asyncio-1.0.0-py3-none-any.whl",
    "pytest_asyncio-1.3.0-py3-none-any.whl",
    "python_dotenv-1.2.1-py3-none-any.whl",
    "python_multipart-0.0.22-py3-none-any.whl",
    "python_slugify-8.0.4-py2.py3-none-any.whl",
    "pytokens-0.4.1-cp310-cp310-win_amd64.whl",
    "pytokens-0.4.1-cp311-cp311-win_amd64.whl",
    "pytokens-0.4.1-cp312-cp312-win_amd64.whl",
    "pywin32-311-cp310-cp310-win_amd64.whl",
    "pywin32-311-cp311-cp311-win_amd64.whl",
    "pywin32-311-cp312-cp312-win_amd64.whl",
    "pyyaml-6.0.3-cp310-cp310-win_amd64.whl",
    "pyyaml-6.0.3-cp311-cp311-win_amd64.whl",
    "pyyaml-6.0.3-cp312-cp312-win_amd64.whl",
    "questionary-2.1.1-py3-none-any.whl",
    "referencing-0.37.0-py3-none-any.whl",
    "requests-2.32.5-py3-none-any.whl",
    "rpds_py-0.30.0-cp310-cp310-win_amd64.whl",
    "rpds_py-0.30.0-cp311-cp311-win_amd64.whl",
    "rpds_py-0.30.0-cp312-cp312-win_amd64.whl",
    "soupsieve-2.8.3-py3-none-any.whl",
    "sse_starlette-3.2.0-py3-none-any.whl",
    "stack_data-0.6.3-py3-none-any.whl",
    "starlette-0.52.1-py3-none-any.whl",
    "termcolor-3.3.0-py3-none-any.whl",
    "text_unidecode-1.3-py2.py3-none-any.whl",
    "tomli-2.4.0-cp311-cp311-win_amd64.whl",
    "tomli-2.4.0-cp312-cp312-win_amd64.whl",
    "tomli-2.4.0-py3-none-any.whl",
    "tomlkit-0.14.0-py3-none-any.whl",
    "traitlets-5.14.3-py3-none-any.whl",
    "typing_extensions-4.15.0-py3-none-any.whl",
    "typing_inspection-0.4.2-py3-none-any.whl",
    "urllib3-2.6.3-py3-none-any.whl",
    "uvicorn-0.40.0-py3-none-any.whl",
    "wcwidth-0.6.0-py3-none-any.whl",
    "wrapt-2.1.1-cp310-cp310-win_amd64.whl",
    "wrapt-2.1.1-cp311-cp311-win_amd64.whl",
    "wrapt-2.1.1-cp312-cp312-win_amd64.whl"
]


def check_python_version():
    """Verifie que Python 3.10+ est installe."""
    version = sys.version_info
    if version < (3, 10):
        print(f"[ERREUR] Python 3.10+ requis, vous avez Python {version.major}.{version.minor}")
        print("\nTelechargez Python depuis: https://www.python.org/downloads/")
        sys.exit(1)

    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} detecte")


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

    if dest.exists():
        print(f"  [SKIP] {wheel_name} (deja presente)")
        return True

    try:
        print(f"  [DOWN] {wheel_name}...", end='', flush=True)
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
    """Telecharge toutes les wheels depuis GitHub."""
    print(f"\n[INFO] Telechargement de {len(WHEELS_TO_DOWNLOAD)} wheels depuis GitHub...")
    print(f"       URL: {GITHUB_BASE_URL}")
    print(f"       ! CONNEXION INTERNET REQUISE")
    print()

    failed = []
    success = 0
    skipped = 0

    for wheel_name in WHEELS_TO_DOWNLOAD:
        dest = wheels_dir / wheel_name
        if dest.exists():
            skipped += 1
            if download_wheel(wheel_name, wheels_dir):
                continue
        else:
            if download_wheel(wheel_name, wheels_dir):
                success += 1
            else:
                failed.append(wheel_name)

    print()
    if failed:
        print(f"[ERREUR] {len(failed)} wheel(s) ont echoue:")
        for wheel in failed:
            print(f"  - {wheel}")
        return False

    if skipped > 0:
        print(f"[OK] {success} wheels telechargees, {skipped} deja presentes")
    else:
        print(f"[OK] {success}/{len(WHEELS_TO_DOWNLOAD)} wheels telechargees")

    total_size = sum(f.stat().st_size for f in wheels_dir.glob("*.whl"))
    total_mb = total_size / (1024 * 1024)
    print(f"     Taille totale: {total_mb:.1f} MB")

    return True


def main():
    """Point d'entree principal."""
    print("="*70)
    print("  TELECHARGEMENT DES WHEELS AMBULON")
    print("="*70)
    print()
    print("[INFO] Script auto-genere le 2026-02-12 11:49:16")
    print("[INFO] Par scripts/build_offline_package.py")
    print()

    check_python_version()
    print()

    print("="*70)
    print("  PHASE 1 : CREATION DU REPERTOIRE")
    print("="*70)
    print()
    wheels_dir = create_wheels_dir()

    print("\n" + "="*70)
    print("  PHASE 2 : TELECHARGEMENT DES WHEELS (ONLINE)")
    print("="*70)

    if not download_all_wheels(wheels_dir):
        print("\n[ERREUR] Telechargement echoue")
        sys.exit(1)

    print("\n" + "="*70)
    print("  TELECHARGEMENT TERMINE")
    print("="*70)
    print()
    print("[OK] Les wheels sont pretes dans: wheels/")
    print()

    print("Wheels telechargees:")
    wheels_list = sorted(wheels_dir.glob("*.whl"))
    for wheel in wheels_list:
        size_bytes = wheel.stat().st_size
        size_formatted = f"{size_bytes:,}".replace(",", " ")
        print(f"  - {wheel.name} ({size_formatted} octets)")

    # Calcul taille totale
    total_bytes = sum(w.stat().st_size for w in wheels_list)
    total_formatted = f"{total_bytes:,}".replace(",", " ")
    total_mb = total_bytes / (1024 * 1024)

    print()
    print("="*70)
    print("  RECAPITULATIF")
    print("="*70)
    print()
    print(f"Source GitHub : {GITHUB_BASE_URL}")
    print(f"Stockees dans : {wheels_dir.absolute()}")
    print(f"Nombre        : {len(wheels_list)} wheels")
    print(f"Taille totale : {total_formatted} octets ({total_mb:.1f} MB)")

    print()
    print("="*70)
    print("  PROCHAINE ETAPE : INSTALLATION (OFFLINE)")
    print("="*70)
    print()
    print("Pour installer Ambulon (sans connexion internet), executez:")
    print()
    print("  python install_offline.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Telechargement annule par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] Exception inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
