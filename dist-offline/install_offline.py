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
from typing import List, Set, Optional


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


def install_package(package_name, wheels_dir, no_deps=False):
    """Installe un package depuis le dossier wheels/."""
    print(f"\n[INFO] Installation de {package_name}...")

    cmd = [
        sys.executable, "-m", "pip", "install",
        "--no-index",
        "--find-links", str(wheels_dir),
        package_name
    ]

    if no_deps:
        cmd.append("--no-deps")

    try:
        subprocess.run(cmd, check=True)
        print(f"[OK] {package_name} installe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Echec de l'installation de {package_name}: {e}")
        return False


def _parse_poetry_lock(lock_path: Path) -> List[str]:
    """Parse poetry.lock for main dependencies (best-effort, no external deps)."""
    deps: List[str] = []
    seen: Set[str] = set()
    if not lock_path.exists():
        return deps

    current_name: Optional[str] = None
    current_category: Optional[str] = None

    for raw_line in lock_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[[package]]":
            if current_name and (current_category in (None, "main")) and current_name not in seen:
                deps.append(current_name)
                seen.add(current_name)
            current_name = None
            current_category = None
            continue

        if line.startswith("name = "):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            current_name = value
            continue

        if line.startswith("category = "):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            current_category = value
            continue

    if current_name and (current_category in (None, "main")) and current_name not in seen:
        deps.append(current_name)
        seen.add(current_name)

    return deps


def _parse_pyproject_dependencies(pyproject_path: Path) -> List[str]:
    """Parse pyproject.toml for [tool.poetry.dependencies] (best-effort)."""
    if not pyproject_path.exists():
        return []

    try:
        import tomllib  # Python 3.11+
    except Exception:
        tomllib = None

    if tomllib is not None:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        return [name for name in deps.keys() if name != "python"]

    # Fallback simple parser (Python 3.10 without tomllib)
    deps: List[str] = []
    in_section = False
    for raw_line in pyproject_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_section = (line == "[tool.poetry.dependencies]")
            continue
        if in_section and "=" in line:
            name = line.split("=", 1)[0].strip()
            if name != "python":
                deps.append(name)
    return deps


def resolve_dependencies(project_root: Path) -> List[str]:
    """Resolve dependencies with best effort: poetry.lock -> pyproject.toml."""
    lock_path = project_root / "poetry.lock"
    pyproject_path = project_root / "pyproject.toml"

    deps = _parse_poetry_lock(lock_path)
    source = "poetry.lock"
    if not deps:
        deps = _parse_pyproject_dependencies(pyproject_path)
        source = "pyproject.toml"

    if not deps:
        print("[AVERTISSEMENT] Aucun lock/pyproject trouve. Installation directe d'ambulon.")
        return []

    # Ensure kroki is included in offline install
    if "kroki" not in deps:
        deps.append("kroki")

    # Ensure ambulon is installed last (separate step)
    deps = [d for d in deps if d != "ambulon"]
    print(f"[INFO] Dependances resolues depuis: {source}")
    return deps


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

    # Installation des dependances (si resolues)
    deps = resolve_dependencies(Path(__file__).resolve().parent.parent)
    failed = []
    for package in deps:
        if not install_package(package, wheels_dir):
            failed.append(package)

    if failed:
        print(f"\n[ERREUR] {len(failed)} dependance(s) ont echoue:")
        for pkg in failed:
            print(f"  - {pkg}")
        print("\nL'installation est incomplete.")
        sys.exit(1)

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
