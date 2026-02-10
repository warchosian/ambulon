#!/usr/bin/env python3
"""
Script d'installation offline d'Ambulon.

Ce script installe Ambulon et toutes ses dépendances à partir du dossier wheels/
en respectant l'ordre des dépendances.

Usage:
    python install_offline.py
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import List, Set, Optional


def check_python_version():
    """Vérifie que Python 3.10+ est installé."""
    version = sys.version_info
    if version < (3, 10):
        print(f"[ERREUR] Python 3.10+ requis, vous avez Python {version.major}.{version.minor}")
        print("\nCe package contient des wheels pour Python 3.10, 3.11 et 3.12")
        print("Téléchargez Python depuis: https://www.python.org/downloads/")
        sys.exit(1)

    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} détecté")
    if version.major == 3 and version.minor in (10, 11, 12):
        print(f"     Version compatible avec les wheels du package")
    else:
        print(f"[AVERTISSEMENT] Python {version.major}.{version.minor} non testé")
        print(f"                 Wheels disponibles pour Python 3.10, 3.11, 3.12")


def check_pip():
    """Vérifie que pip est installé."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[OK] pip détecté: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("[ERREUR] pip n'est pas installé")
        print("Réinstallez Python avec pip inclus")
        sys.exit(1)


def find_wheels_dir():
    """Trouve le dossier wheels/ (à côté du script ou dans dist-offline/)."""
    script_dir = Path(__file__).parent

    # Cas 1: wheels/ à côté du script
    wheels_dir = script_dir / "wheels"
    if wheels_dir.exists():
        return wheels_dir

    # Cas 2: wheels/ dans dist-offline/ (structure de dev)
    wheels_dir = script_dir.parent / "dist-offline" / "wheels"
    if wheels_dir.exists():
        return wheels_dir

    # Cas 3: on est dans dist-offline/, wheels/ est au même niveau
    wheels_dir = script_dir / ".." / "wheels"
    if wheels_dir.exists():
        return wheels_dir.resolve()

    print("[ERREUR] Dossier wheels/ introuvable")
    print(f"Cherché dans:")
    print(f"  - {script_dir / 'wheels'}")
    print(f"  - {script_dir.parent / 'dist-offline' / 'wheels'}")
    sys.exit(1)

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

    # Ensure kroki is included in offline install
    if "kroki" not in deps:
        deps.append("kroki")

    # Ensure ambulon is installed last (separate step)
    deps = [d for d in deps if d != "ambulon"]
    print(f"[INFO] Dépendances résolues depuis: {source}")
    return deps


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
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[OK] {package_name} installé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec de l'installation de {package_name}")
        print(f"Commande: {' '.join(cmd)}")
        print(f"\nStdout:\n{e.stdout}")
        print(f"\nStderr:\n{e.stderr}")
        return False


def main():
    """Point d'entrée principal."""
    print("="*70)
    print("  INSTALLATION OFFLINE D'AMBULON")
    print("="*70)
    print()

    # 1. Vérifications préalables
    check_python_version()
    check_pip()

    # 2. Trouver le dossier wheels/
    wheels_dir = find_wheels_dir()
    print(f"[OK] Dossier wheels trouvé: {wheels_dir}")

    wheels_count = len(list(wheels_dir.glob("*.whl")))
    print(f"     {wheels_count} wheels disponibles")
    print()

    # 3. Résolution des dépendances
    print("="*70)
    print("  INSTALLATION DES DEPENDANCES")
    print("="*70)
    project_root = Path(__file__).resolve().parent.parent
    dependencies_order = resolve_dependencies(project_root)
    if not dependencies_order:
        print("[ERREUR] Impossible de résoudre les dépendances (poetry.lock/pyproject.toml)")
        sys.exit(1)

    failed_packages = []

    for package in dependencies_order:
        if not install_package(package, wheels_dir):
            failed_packages.append(package)
            # Continue quand même pour voir tous les échecs

    # 4. Installation d'Ambulon (en dernier)
    print()
    print("="*70)
    print("  INSTALLATION D'AMBULON")
    print("="*70)

    if not install_package("ambulon", wheels_dir):
        failed_packages.append("ambulon")

    # 5. Résumé
    print()
    print("="*70)
    print("  RÉSUMÉ")
    print("="*70)

    if failed_packages:
        print(f"\n[ERREUR] {len(failed_packages)} package(s) ont échoué:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\nL'installation est incomplète.")
        print("\nSolutions possibles:")
        print("1. Vérifiez que votre version Python est 3.10, 3.11 ou 3.12")
        print("2. Si vous avez une autre version, téléchargez les wheels manquantes:")
        print(f"   pip download {' '.join(failed_packages)} --python-version X.Y")
        print("   Puis copiez-les dans wheels/")
        sys.exit(1)
    else:
        print("\n[OK] Installation terminée avec succès !")
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
            print("  [INFO] La commande 'ambulon' n'est pas encore reconnue")
            print("         Redémarrez votre terminal ou utilisez:")
            print("         python -m app.cli.cli --version")

        print("\nPour voir toutes les commandes:")
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
