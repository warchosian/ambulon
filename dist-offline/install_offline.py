#!/usr/bin/env python3
"""
Installation offline d'Ambulon depuis wheels locales.

Ce script installe Ambulon depuis le dossier wheels/ (OFFLINE).
Pour telecharger les wheels, utilisez d'abord download_wheels.py.

Usage:
    python install_offline.py

Prerequis:
    - Python 3.10, 3.11 ou 3.12
    - pip installe
    - Dossier wheels/ avec les 70 wheels
    - Aucune connexion internet requise
"""

import sys
import subprocess
from pathlib import Path


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


def check_wheels_dir():
    """Verifie que le dossier wheels/ existe."""
    script_dir = Path(__file__).parent
    wheels_dir = script_dir / "wheels"

    if not wheels_dir.exists():
        print(f"[ERREUR] Dossier wheels/ introuvable: {wheels_dir}")
        print()
        print("Solution:")
        print("  1. Telechargez les wheels d'abord:")
        print("     python download_wheels.py")
        print()
        print("  2. Ou clonez le depot avec les wheels:")
        print("     git clone https://github.com/warchosian/ambulon.git -b preprod/v3.0.2-stable")
        sys.exit(1)

    wheels_count = len(list(wheels_dir.glob("*.whl")))
    if wheels_count == 0:
        print(f"[ERREUR] Dossier wheels/ vide: {wheels_dir}")
        print()
        print("Solution:")
        print("  Telechargez les wheels d'abord:")
        print("  python download_wheels.py")
        sys.exit(1)

    print(f"[OK] Dossier wheels/ trouve: {wheels_dir}")
    print(f"     {wheels_count} wheels disponibles")

    # Verifier qu'ambulon est present
    ambulon_wheels = list(wheels_dir.glob("ambulon-*.whl"))
    if not ambulon_wheels:
        print(f"[ERREUR] Wheel ambulon introuvable dans {wheels_dir}")
        sys.exit(1)

    print(f"     Ambulon wheel: {ambulon_wheels[0].name}")

    return wheels_dir


def install_ambulon(wheels_dir):
    """Installe ambulon depuis les wheels locales (MODE OFFLINE)."""
    print()
    print("="*70)
    print("  INSTALLATION D'AMBULON (MODE OFFLINE)")
    print("="*70)
    print()
    print("[INFO] Mode: OFFLINE (pas de connexion internet requise)")
    print("       Installation depuis les wheels locales uniquement")
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
    simple_cmd = f"pip install --no-index --find-links={wheels_dir.name} ambulon"
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
    print("  ambulon process <fichier.pdf>")
    print("  ambulon server")


def main():
    """Point d'entree principal."""
    print("="*70)
    print("  INSTALLATION OFFLINE D'AMBULON")
    print("="*70)
    print()

    # Verifications
    check_python_version()
    check_pip()
    print()

    # Verification du dossier wheels
    print("="*70)
    print("  VERIFICATION DES WHEELS")
    print("="*70)
    print()
    wheels_dir = check_wheels_dir()

    # Installation
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
