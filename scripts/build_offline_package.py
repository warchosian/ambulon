#!/usr/bin/env python3
"""
Script de génération du package d'installation offline d'Ambulon.

Ce script :
1. Lit la version depuis pyproject.toml
2. Build la wheel ambulon
3. Télécharge toutes les dépendances pour Python 3.10, 3.11, 3.12
4. Copie les scripts d'installation/désinstallation
5. Génère le README
6. Crée l'archive ZIP dans dist-offline/

Usage:
    python build_offline_package.py

Note:
    Le package généré sera compatible avec Python 3.10, 3.11 et 3.12.
    Les wheels pour chaque version sont téléchargées automatiquement.
"""

import os
import sys
import shutil
import subprocess
import zipfile
import tempfile
from pathlib import Path
import re
from typing import List, Optional, Set


def read_version_from_pyproject():
    """Lit la version depuis pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("[ERREUR] pyproject.toml introuvable")
        sys.exit(1)

    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if not match:
            print("[ERREUR] Version introuvable dans pyproject.toml")
            sys.exit(1)
        return match.group(1)


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
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(
        r'\[tool\.poetry\.dependencies\](.*?)(?=\n\[|\Z)',
        content,
        re.DOTALL
    )
    if not match:
        print("[ERREUR] Section [tool.poetry.dependencies] introuvable")
        sys.exit(1)

    deps_section = match.group(1)
    dependencies = []

    for line in deps_section.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            dep_name = line.split('=')[0].strip()
            if dep_name != 'python':
                dependencies.append(dep_name)

    return dependencies


def resolve_dependencies() -> List[str]:
    """Résout les dépendances: poetry.lock -> pyproject.toml."""
    lock_path = Path("poetry.lock")
    pyproject_path = Path("pyproject.toml")

    dependencies = _parse_poetry_lock(lock_path)
    source = "poetry.lock"
    if not dependencies:
        dependencies = _parse_pyproject_dependencies(pyproject_path)
        source = "pyproject.toml"

    # S'assurer que kroki est présent (obligatoire)
    if "kroki" not in dependencies:
        dependencies.append("kroki")

    print(f"[INFO] Dépendances résolues depuis: {source}")
    return dependencies


def build_wheel(version):
    """Utilise la wheel existante ou la build avec poetry."""
    print("\n" + "="*60)
    print("Étape 1/6 : Vérification de la wheel Ambulon")
    print("="*60)

    dist_dir = Path("dist")
    wheel_file = dist_dir / f"ambulon-{version}-py3-none-any.whl"

    # Vérifier si la wheel existe déjà
    if wheel_file.exists():
        print(f"[OK] Wheel existante trouvée: {wheel_file}")
        print(f"     Taille: {wheel_file.stat().st_size / 1024:.1f} KB")
        print(f"     Utilisation de la wheel existante (pas de rebuild)")
        return wheel_file

    # La wheel n'existe pas, il faut la builder
    print(f"[INFO] Wheel inexistante, build nécessaire...")
    print("[INFO] Exécution de: poetry build")
    result = subprocess.run(
        ["poetry", "build"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("[ERREUR] Échec du build")
        print(result.stderr)
        sys.exit(1)

    if not wheel_file.exists():
        print(f"[ERREUR] Wheel non générée: {wheel_file}")
        sys.exit(1)

    print(f"[OK] Wheel générée: {wheel_file}")
    print(f"     Taille: {wheel_file.stat().st_size / 1024:.1f} KB")
    return wheel_file


def create_temp_structure(version):
    """Crée la structure temporaire du package."""
    print("\n" + "="*60)
    print("Étape 2/6 : Création de la structure temporaire")
    print("="*60)

    temp_dir = Path(tempfile.mkdtemp(prefix="ambulon_offline_"))
    package_dir = temp_dir / f"ambulon-{version}-offline-install"
    wheels_dir = package_dir / "wheels"
    scripts_dir = package_dir / "scripts"

    package_dir.mkdir()
    wheels_dir.mkdir()
    scripts_dir.mkdir()

    print(f"[OK] Structure créée dans: {package_dir}")
    return temp_dir, package_dir, wheels_dir, scripts_dir


def copy_ambulon_wheel(wheel_file, wheels_dir):
    """Copie la wheel ambulon dans le package."""
    print("\n" + "="*60)
    print("Étape 3/6 : Copie de la wheel Ambulon")
    print("="*60)

    dest = wheels_dir / wheel_file.name
    shutil.copy2(wheel_file, dest)
    print(f"[OK] Wheel copiée: {wheel_file.name}")
    return dest


def download_dependencies(dependencies, wheels_dir):
    """Télécharge toutes les dépendances pour plusieurs versions Python."""
    print("\n" + "="*60)
    print("Étape 4/6 : Téléchargement des dépendances")
    print("="*60)

    print(f"[INFO] Dépendances à télécharger: {len(dependencies)}")
    print(f"       {', '.join(dependencies)}")
    print()

    # Télécharger pour Python 3.10, 3.11, 3.12 (versions courantes)
    python_versions = ["3.10", "3.11", "3.12"]

    for py_version in python_versions:
        print(f"\n[INFO] Téléchargement pour Python {py_version}...")

        cmd = [
            "pip", "download",
            *dependencies,
            "-d", str(wheels_dir),
            "--python-version", py_version,
            "--only-binary", ":all:",
            "--no-cache-dir"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[AVERTISSEMENT] Échec du téléchargement pour Python {py_version}")
            print(result.stderr)
            # Continue avec les autres versions au lieu d'abandonner
            continue

        print(f"[OK] Téléchargement Python {py_version} réussi")

    # Compter les wheels téléchargées (en dédupliquant par nom)
    wheels = list(wheels_dir.glob("*.whl"))
    total_size = sum(w.stat().st_size for w in wheels)

    print(f"\n[OK] {len(wheels)} wheels téléchargées (toutes versions Python confondues)")
    print(f"     Taille totale: {total_size / 1024 / 1024:.1f} MB")
    print(f"     Compatible avec: Python 3.10, 3.11, 3.12")


def copy_scripts(scripts_dir, version):
    """Copie et adapte les scripts d'installation/désinstallation."""
    print("\n" + "="*60)
    print("Étape 5/6 : Génération des scripts")
    print("="*60)

    # Script d'installation offline
    install_script = scripts_dir / "install-ambulon-offline.bat"
    install_content = f"""@echo off
REM ========================================================
REM Script d'installation offline d'Ambulon v{version}
REM ========================================================
REM Ce script installe Ambulon et toutes ses dependances
REM sans connexion Internet, a partir des wheels locales.
REM ========================================================

echo.
echo ========================================================
echo Installation offline d'Ambulon v{version}
echo ========================================================
echo.

REM Verification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo.
    echo Veuillez installer Python 3.10, 3.11 ou 3.12 depuis:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Ce package contient des wheels pour Python 3.10, 3.11 et 3.12
    echo.
    pause
    exit /b 1
)

echo [OK] Python detecte:
python --version
echo.

REM Verification de pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] pip n'est pas installe
    echo.
    echo Veuillez reinstaller Python avec pip inclus.
    echo.
    pause
    exit /b 1
)

echo [OK] pip detecte:
pip --version
echo.

REM Remonter au dossier parent (depuis ambulon-{version}-offline-install/scripts/)
cd ..

REM Installation depuis le dossier wheels local
echo ========================================================
echo Installation d'Ambulon et de ses dependances...
echo ========================================================
echo.
echo Cette operation peut prendre 1-2 minutes...
echo.

REM Etape 1 : Installer TOUTES les dependances AVANT ambulon
echo [Etape 1/2] Installation des dependances...
pip install --no-index --find-links=.\\wheels ^
    importlib-resources pillow pymupdf requests pyyaml mcp chardet ^
    beautifulsoup4 lxml markdown python-slugify greenlet playwright

if errorlevel 1 (
    echo.
    echo [ERREUR] L'installation des dependances a echoue
    echo.
    pause
    exit /b 1
)

echo.
echo [Etape 2/2] Installation d'Ambulon...
pip install --no-index --find-links=.\\wheels ambulon

if errorlevel 1 (
    echo.
    echo [ERREUR] L'installation a echoue
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo Installation terminee avec succes !
echo ========================================================
echo.

REM Verification de l'installation
echo Verification de l'installation...
ambulon --version

if errorlevel 1 (
    echo.
    echo [AVERTISSEMENT] La commande 'ambulon' n'est pas accessible
    echo.
    echo Vous devrez peut-etre redemarrer votre terminal ou ajouter
    echo le dossier Scripts de Python a votre PATH.
    echo.
) else (
    echo.
    echo [OK] Ambulon est pret a l'emploi !
    echo.
    echo Exemples de commandes:
    echo   ambulon --help
    echo   ambulon init
    echo   ambulon pdf2html document.pdf
    echo.
)

pause
"""
    with open(install_script, "w", encoding="utf-8", newline='\r\n') as f:
        f.write(install_content)
    print(f"[OK] Script créé: scripts/install-ambulon-offline.bat")

    # Script de désinstallation
    uninstall_script = scripts_dir / "uninstall-ambulon.bat"
    uninstall_content = """@echo off
REM ========================================================
REM Script de desinstallation complete d'Ambulon
REM ========================================================
REM Ce script desinstalle Ambulon et propose de supprimer
REM les dependances et fichiers de configuration.
REM ========================================================

echo.
echo ========================================================
echo Desinstallation complete d'Ambulon
echo ========================================================
echo.

REM Verification de pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] pip n'est pas installe ou pas dans le PATH
    echo.
    pause
    exit /b 1
)

echo [OK] pip detecte
echo.

REM Verification qu'ambulon est installe
pip show ambulon >nul 2>&1
if errorlevel 1 (
    echo [INFO] Ambulon n'est pas installe
    echo.
    goto :check_config
)

REM Afficher la version installee
echo Version installee:
pip show ambulon | findstr "Name: Version: Location:"
echo.

REM Desinstallation d'ambulon
echo ========================================================
echo Etape 1/3 : Desinstallation d'Ambulon
echo ========================================================
echo.

set /p confirm1="Desinstaller Ambulon ? (O/N): "
if /i not "%confirm1%"=="O" (
    echo Desinstallation annulee.
    goto :end
)

echo.
echo Desinstallation en cours...
pip uninstall ambulon -y

if errorlevel 1 (
    echo [ERREUR] Echec de la desinstallation
    pause
    exit /b 1
)

echo.
echo [OK] Ambulon desinstalle avec succes
echo.

REM Verification
pip show ambulon >nul 2>&1
if not errorlevel 1 (
    echo [AVERTISSEMENT] Ambulon semble toujours installe
    echo.
) else (
    echo [OK] Verification : Ambulon n'est plus installe
    echo.
)

:remove_deps
REM Desinstallation des dependances
echo ========================================================
echo Etape 2/3 : Desinstallation des dependances
echo ========================================================
echo.
echo Les dependances suivantes peuvent etre supprimees :
echo   - requests, pyyaml, pillow, pymupdf
echo   - beautifulsoup4, lxml, mcp, chardet
echo   - markdown, python-slugify, playwright
echo   - et leurs dependances transitives
echo.
echo ATTENTION : Ne supprimez ces packages que si aucun autre
echo programme Python ne les utilise !
echo.

set /p confirm2="Supprimer les dependances ? (O/N): "
if /i not "%confirm2%"=="O" (
    echo Dependances conservees.
    goto :check_config
)

echo.
echo Suppression des dependances principales...
echo.

pip uninstall ^
    requests ^
    pyyaml ^
    pillow ^
    pymupdf ^
    beautifulsoup4 ^
    lxml ^
    mcp ^
    chardet ^
    markdown ^
    python-slugify ^
    playwright ^
    -y

echo.
echo [INFO] Dependances principales supprimees
echo.

:check_config
REM Suppression des fichiers de configuration
echo ========================================================
echo Etape 3/3 : Suppression des fichiers de configuration
echo ========================================================
echo.

set config_dir=%USERPROFILE%\\.ambulon

if not exist "%config_dir%" (
    echo [INFO] Aucun fichier de configuration trouve dans %config_dir%
    echo.
    goto :cleanup_local
)

echo Fichiers de configuration detectes dans :
echo   %config_dir%
echo.
dir /b "%config_dir%" 2>nul
echo.

set /p confirm3="Supprimer ces fichiers de configuration ? (O/N): "
if /i not "%confirm3%"=="O" (
    echo Fichiers de configuration conserves.
    goto :cleanup_local
)

echo.
echo Suppression des fichiers de configuration...
rmdir /s /q "%config_dir%"

if exist "%config_dir%" (
    echo [AVERTISSEMENT] Impossible de supprimer %config_dir%
    echo.
) else (
    echo [OK] Fichiers de configuration supprimes
    echo.
)

:cleanup_local
REM Suppression des fichiers de configuration locaux
echo Verification des fichiers de configuration locaux...
echo.

set found_local=0

if exist "config.yaml" (
    echo   - config.yaml trouve
    set found_local=1
)
if exist "piag.yaml" (
    echo   - piag.yaml trouve
    set found_local=1
)
if exist "gitlab.yaml" (
    echo   - gitlab.yaml trouve
    set found_local=1
)
if exist "wikisi.yaml" (
    echo   - wikisi.yaml trouve
    set found_local=1
)

if %found_local%==0 (
    echo [INFO] Aucun fichier de configuration local trouve
    echo.
    goto :final_check
)

echo.
set /p confirm4="Supprimer ces fichiers locaux ? (O/N): "
if /i not "%confirm4%"=="O" (
    echo Fichiers locaux conserves.
    goto :final_check
)

echo.
if exist "config.yaml" del "config.yaml" && echo [OK] config.yaml supprime
if exist "piag.yaml" del "piag.yaml" && echo [OK] piag.yaml supprime
if exist "gitlab.yaml" del "gitlab.yaml" && echo [OK] gitlab.yaml supprime
if exist "wikisi.yaml" del "wikisi.yaml" && echo [OK] wikisi.yaml supprime
echo.

:final_check
REM Verification finale
echo ========================================================
echo Verification finale
echo ========================================================
echo.

ambulon --version >nul 2>&1
if not errorlevel 1 (
    echo [AVERTISSEMENT] La commande 'ambulon' est toujours accessible
    echo.
) else (
    echo [OK] La commande 'ambulon' n'est plus accessible
    echo.
)

pip show ambulon >nul 2>&1
if not errorlevel 1 (
    echo [AVERTISSEMENT] Le package 'ambulon' semble toujours installe
    echo.
) else (
    echo [OK] Le package 'ambulon' n'est plus installe
    echo.
)

:end
echo ========================================================
echo Desinstallation terminee
echo ========================================================
echo.
pause
"""
    with open(uninstall_script, "w", encoding="utf-8", newline='\r\n') as f:
        f.write(uninstall_content)
    print(f"[OK] Script créé: scripts/uninstall-ambulon.bat")


def generate_readme(package_dir, version):
    """Génère le README d'installation offline."""
    readme_path = package_dir / "README-OFFLINE.txt"

    readme_content = f"""================================================================================
  AMBULON v{version} - Package d'Installation Offline
================================================================================

Ce package contient Ambulon et TOUTES ses dependances pour une installation
sans connexion Internet.


================================================================================
  IMPORTANT : ORDRE D'EXECUTION DES SCRIPTS
================================================================================

Si vous avez une version precedente d'Ambulon installee :

  1. D'ABORD : Executez scripts\\uninstall-ambulon.bat
     → Cela desinstallera l'ancienne version completement

  2. ENSUITE : Executez scripts\\install-ambulon-offline.bat
     → Cela installera la nouvelle version v{version}


Si c'est une nouvelle installation (pas de version precedente) :

  1. Executez directement scripts\\install-ambulon-offline.bat


================================================================================
  PREREQUIS (sur la machine cible)
================================================================================

1. Python 3.10, 3.11 ou 3.12 doit etre installe

   Ce package contient des wheels pour Python 3.10, 3.11 et 3.12.
   Utilisez l'une de ces versions pour garantir la compatibilite.

   Pour verifier votre version:
   > python --version

   Si Python n'est pas installe, telechargez-le depuis:
   https://www.python.org/downloads/

   IMPORTANT: Cochez "Add Python to PATH" lors de l'installation !

2. pip doit etre installe (inclus avec Python par defaut)

   Pour verifier:
   > pip --version


================================================================================
  CONTENU DU PACKAGE
================================================================================

ambulon-{version}-offline-install/
├── wheels/                         (50+ fichiers .whl)
│   ├── ambulon-{version}-py3-none-any.whl
│   ├── requests-*.whl
│   ├── pyyaml-*.whl
│   └── ... (toutes les dependances)
├── scripts/
│   ├── uninstall-ambulon.bat       Script de desinstallation (A EXECUTER EN PREMIER)
│   └── install-ambulon-offline.bat Script d'installation (A EXECUTER EN SECOND)
└── README-OFFLINE.txt              Ce fichier


================================================================================
  ETAPE 0 : DESINSTALLATION DE L'ANCIENNE VERSION (OBLIGATOIRE)
================================================================================

IMPORTANT : Si vous avez deja une version d'Ambulon installee, vous DEVEZ
            la desinstaller AVANT d'installer la nouvelle version v{version}

Methode 1 - Automatique (recommande) :

  1. Ouvrez le dossier: ambulon-{version}-offline-install/scripts/
  2. Double-cliquez sur: uninstall-ambulon.bat
  3. Repondez O (Oui) a toutes les questions pour une desinstallation complete
  4. Attendez le message "Desinstallation terminee"

Methode 2 - Manuelle (ligne de commande) :

  > pip uninstall ambulon -y

Si vous n'avez AUCUNE version d'Ambulon installee :

  => Passez directement a l'etape suivante (INSTALLATION)


================================================================================
  ETAPE 1 : INSTALLATION (APRES DESINSTALLATION)
================================================================================

IMPORTANT : N'installez qu'APRES avoir desinstalle l'ancienne version !

Methode automatique (Windows) :

1. Decompressez l'archive ambulon-{version}-offline-install.zip

2. Ouvrez le dossier ambulon-{version}-offline-install/

3. Ouvrez le sous-dossier scripts/

4. Double-cliquez sur: install-ambulon-offline.bat

5. Suivez les instructions a l'ecran

6. Verifiez l'installation:
   > ambulon --version

   Doit afficher: ambulon {version}


Methode manuelle (ligne de commande) :

1. Ouvrez un terminal dans le dossier ambulon-{version}-offline-install/

2. Installer les dependances AVANT ambulon :
   > pip install --no-index --find-links=.\\wheels importlib-resources pillow pymupdf requests pyyaml mcp chardet beautifulsoup4 lxml markdown python-slugify greenlet playwright

3. Installer ambulon :
   > pip install --no-index --find-links=.\\wheels ambulon

4. Verifier :
   > ambulon --version


================================================================================
  VERIFICATION DE L'INSTALLATION
================================================================================

Pour verifier qu'Ambulon est correctement installe:

> ambulon --version
  ambulon {version}

> ambulon --help
  Usage: ambulon [OPTIONS] COMMAND [ARGS]...
  ...

Si la commande 'ambulon' n'est pas reconnue:
- Redemarrez votre terminal
- Verifiez que Python Scripts/ est dans votre PATH


================================================================================
  EXEMPLES D'UTILISATION
================================================================================

# Initialiser la configuration
ambulon init

# Convertir PDF vers HTML
ambulon pdf2html document.pdf

# Convertir Markdown vers HTML
ambulon md2html readme.md

# Encapsuler du code dans un bloc Markdown
ambulon code2md script.py

# Scanner un document (OCR)
ambulon scan-image document.jpg

# Cloner des projets GitLab
ambulon gitlab-clone --help

# Recherche RAG avec PIAG
ambulon piag-search "ma recherche" --collection-name MaCollection

# Synchroniser WikiSI
ambulon wikisi-sync-api --verbose

# Voir toutes les commandes disponibles
ambulon --help


================================================================================
  DEPANNAGE
================================================================================

Probleme : "ERROR: xxx-cp310-win_amd64.whl is not a supported wheel"
------------------------------------------------------------------------
Cause: Vous utilisez une version Python differente (ex: 3.9, 3.13)

Solution:
1. Verifiez votre version Python:
   > python --version

2. Si vous avez Python 3.9 ou 3.13:
   - Installez Python 3.10, 3.11 ou 3.12
   - OU telechargez les wheels manquantes depuis PyPI:
     > pip download <package-manquant> --python-version <votre-version>
     Puis copiez les .whl dans le dossier wheels/

3. Relancez l'installation:
   > cd scripts
   > install-ambulon-offline.bat


Probleme : "ERROR: No matching distribution found for greenlet"
------------------------------------------------------------------------
Cause: La wheel greenlet pour votre version Python est manquante

Solution:
1. Si vous avez internet temporairement:
   > pip install greenlet
   Puis relancez: install-ambulon-offline.bat

2. OU telechargez manuellement la wheel greenlet pour votre Python:
   https://pypi.org/project/greenlet/#files
   Puis copiez-la dans wheels/ et relancez l'installation


Probleme : La commande 'ambulon' n'est pas reconnue apres installation
------------------------------------------------------------------------
Solution:
1. Redemarrez votre terminal (PowerShell, CMD)
2. Verifiez que Python Scripts/ est dans votre PATH
3. Ou utilisez: python -m app.cli.cli --help


================================================================================
  SUPPORT ET DOCUMENTATION
================================================================================

Documentation complete:
https://github.com/warchosian/ambulon

Signaler un bug:
https://github.com/warchosian/ambulon/issues

Version: {version}
Licence: MIT


================================================================================
  FIN
================================================================================
"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"[OK] README créé: README-OFFLINE.txt")


def create_zip_archive(package_dir, version, dist_fat_dir):
    """Crée l'archive ZIP finale dans dist-offline/."""
    print("\n" + "="*60)
    print("Étape 6/6 : Création de l'archive ZIP")
    print("="*60)

    dist_fat_dir.mkdir(exist_ok=True)
    zip_path = dist_fat_dir / f"ambulon-{version}-offline-install.zip"

    # Supprimer l'ancienne archive si elle existe
    if zip_path.exists():
        print(f"[INFO] Suppression de l'ancienne archive: {zip_path}")
        zip_path.unlink()

    print(f"[INFO] Création de: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)

    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"[OK] Archive créée: {zip_path.name}")
    print(f"     Taille: {size_mb:.1f} MB")

    return zip_path


def cleanup_temp(temp_dir):
    """Nettoie le dossier temporaire."""
    print(f"\n[INFO] Nettoyage du dossier temporaire...")
    shutil.rmtree(temp_dir, ignore_errors=True)


def build_zip_package(version, dependencies):
    """Build le package offline au format ZIP (ancien mode)."""
    # 1. Build la wheel
    wheel_file = build_wheel(version)

    # 2. Créer la structure temporaire
    temp_dir, package_dir, wheels_dir, scripts_dir = create_temp_structure(version)

    # 3. Copier la wheel ambulon
    copy_ambulon_wheel(wheel_file, wheels_dir)

    # 4. Télécharger les dépendances
    download_dependencies(dependencies, wheels_dir)

    # 5. Générer les scripts
    copy_scripts(scripts_dir, version)
    generate_readme(package_dir, version)

    # 6. Créer l'archive ZIP dans dist-offline/
    dist_fat_dir = Path("dist-offline")
    zip_path = create_zip_archive(package_dir, version, dist_fat_dir)

    # 7. Nettoyage
    cleanup_temp(temp_dir)

    # Résumé final
    print("\n" + "="*60)
    print("  BUILD TERMINÉ AVEC SUCCÈS (MODE ZIP)")
    print("="*60)
    print(f"\nPackage offline créé dans:")
    print(f"  {zip_path.absolute()}")
    print(f"  Taille: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\nCe fichier peut être commité dans GitHub et distribué")
    print(f"pour une installation offline d'Ambulon v{version}")
    print()


def _generate_download_wheels_script(dist_offline_dir: Path, github_base_url: str) -> None:
    """Generate dist-offline/download_wheels.py from current wheels/."""
    from datetime import datetime

    wheels_dir = dist_offline_dir / "wheels"
    wheels = sorted([w.name for w in wheels_dir.glob("*.whl")])
    ambulon_wheels = sorted([w for w in wheels if w.startswith("ambulon-")])
    if not ambulon_wheels:
        print("[ERREUR] Aucune wheel ambulon trouvée dans dist-offline/wheels")
        sys.exit(1)
    other_wheels = [w for w in wheels if not w.startswith("ambulon-")]
    wheels = ambulon_wheels + other_wheels

    if not wheels:
        print("[ERREUR] Aucun wheel trouve pour generer download_wheels.py")
        sys.exit(1)

    script_path = dist_offline_dir / "download_wheels.py"
    wheels_lines = ",\n    ".join([f"\"{w}\"" for w in wheels])
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""#!/usr/bin/env python3
# ============================================================================
# FICHIER AUTO-GENERE par scripts/build_offline_package.py
# Date de generation: {generation_date}
# Ne pas modifier manuellement - vos modifications seront ecrasees
# ============================================================================
\"\"\"
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
\"\"\"

import sys
import urllib.request
import urllib.error
from pathlib import Path


# Configuration
GITHUB_BASE_URL = \"{github_base_url}\"
WHEELS_TO_DOWNLOAD = [
    {wheels_lines}
]


def check_python_version():
    \"\"\"Verifie que Python 3.10+ est installe.\"\"\"
    version = sys.version_info
    if version < (3, 10):
        print(f\"[ERREUR] Python 3.10+ requis, vous avez Python {{version.major}}.{{version.minor}}\")
        print(\"\\nTelechargez Python depuis: https://www.python.org/downloads/\")
        sys.exit(1)

    print(f\"[OK] Python {{version.major}}.{{version.minor}}.{{version.micro}} detecte\")


def create_wheels_dir():
    \"\"\"Cree le repertoire wheels/ s'il n'existe pas.\"\"\"
    script_dir = Path(__file__).parent
    wheels_dir = script_dir / \"wheels\"

    wheels_dir.mkdir(exist_ok=True)
    print(f\"[OK] Repertoire wheels/ cree: {{wheels_dir}}\")
    return wheels_dir


def download_wheel(wheel_name, wheels_dir):
    \"\"\"Telecharge une wheel depuis GitHub.\"\"\"
    url = f\"{{GITHUB_BASE_URL}}/{{wheel_name}}\"
    dest = wheels_dir / wheel_name

    if dest.exists():
        print(f\"  [SKIP] {{wheel_name}} (deja presente)\")
        return True

    try:
        print(f\"  [DOWN] {{wheel_name}}...\", end='', flush=True)
        urllib.request.urlretrieve(url, dest)
        print(\" OK\")
        return True
    except urllib.error.HTTPError as e:
        print(f\" X (HTTP {{e.code}})\")
        return False
    except Exception as e:
        print(f\" X ({{e}})\")
        return False


def download_all_wheels(wheels_dir):
    \"\"\"Telecharge toutes les wheels depuis GitHub.\"\"\"
    print(f\"\\n[INFO] Telechargement de {{len(WHEELS_TO_DOWNLOAD)}} wheels depuis GitHub...\")
    print(f\"       URL: {{GITHUB_BASE_URL}}\")
    print(f\"       ! CONNEXION INTERNET REQUISE\")
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
        print(f\"[ERREUR] {{len(failed)}} wheel(s) ont echoue:\")
        for wheel in failed:
            print(f\"  - {{wheel}}\")
        return False

    if skipped > 0:
        print(f\"[OK] {{success}} wheels telechargees, {{skipped}} deja presentes\")
    else:
        print(f\"[OK] {{success}}/{{len(WHEELS_TO_DOWNLOAD)}} wheels telechargees\")

    total_size = sum(f.stat().st_size for f in wheels_dir.glob(\"*.whl\"))
    total_mb = total_size / (1024 * 1024)
    print(f\"     Taille totale: {{total_mb:.1f}} MB\")

    return True


def main():
    \"\"\"Point d'entree principal.\"\"\"
    print(\"=\"*70)
    print(\"  TELECHARGEMENT DES WHEELS AMBULON\")
    print(\"=\"*70)
    print()
    print(\"[INFO] Script auto-genere le {generation_date}\")
    print(\"[INFO] Par scripts/build_offline_package.py\")
    print()

    check_python_version()
    print()

    print(\"=\"*70)
    print(\"  PHASE 1 : CREATION DU REPERTOIRE\")
    print(\"=\"*70)
    print()
    wheels_dir = create_wheels_dir()

    print(\"\\n\" + \"=\"*70)
    print(\"  PHASE 2 : TELECHARGEMENT DES WHEELS (ONLINE)\")
    print(\"=\"*70)

    if not download_all_wheels(wheels_dir):
        print(\"\\n[ERREUR] Telechargement echoue\")
        sys.exit(1)

    print(\"\\n\" + \"=\"*70)
    print(\"  TELECHARGEMENT TERMINE\")
    print(\"=\"*70)
    print()
    print(\"[OK] Les wheels sont pretes dans: wheels/\")
    print()

    print(\"Wheels telechargees:\")
    wheels_list = sorted(wheels_dir.glob(\"*.whl\"))
    for wheel in wheels_list:
        size_bytes = wheel.stat().st_size
        size_formatted = f\"{{size_bytes:,}}\".replace(\",\", \" \")
        print(f\"  - {{wheel.name}} ({{size_formatted}} octets)\")

    # Calcul taille totale
    total_bytes = sum(w.stat().st_size for w in wheels_list)
    total_formatted = f\"{{total_bytes:,}}\".replace(\",\", \" \")
    total_mb = total_bytes / (1024 * 1024)

    print()
    print(\"=\"*70)
    print(\"  RECAPITULATIF\")
    print(\"=\"*70)
    print()
    print(f\"Source GitHub : {{GITHUB_BASE_URL}}\")
    print(f\"Stockees dans : {{wheels_dir.absolute()}}\")
    print(f\"Nombre        : {{len(wheels_list)}} wheels\")
    print(f\"Taille totale : {{total_formatted}} octets ({{total_mb:.1f}} MB)\")

    print()
    print(\"=\"*70)
    print(\"  PROCHAINE ETAPE : INSTALLATION (OFFLINE)\")
    print(\"=\"*70)
    print()
    print(\"Pour installer Ambulon (sans connexion internet), executez:\")
    print()
    print(\"  python install_offline.py\")
    print()


if __name__ == \"__main__\":
    try:
        main()
    except KeyboardInterrupt:
        print(\"\\n\\n[INFO] Telechargement annule par l'utilisateur\")
        sys.exit(1)
    except Exception as e:
        print(f\"\\n[ERREUR] Exception inattendue: {{e}}\")
        import traceback
        traceback.print_exc()
        sys.exit(1)
"""

    script_path.write_text(content, encoding="utf-8")
    print(f"[OK] download_wheels.py mis a jour: {script_path}")


def _generate_install_offline_script(dist_offline_dir: Path) -> None:
    """Generate dist-offline/install_offline.py."""
    from datetime import datetime

    script_path = dist_offline_dir / "install_offline.py"
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Template sans f-string pour éviter les problèmes d'échappement
    template = '''#!/usr/bin/env python3
# ============================================================================
# FICHIER AUTO-GENERE par scripts/build_offline_package.py
# Date de generation: __GENERATION_DATE__
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
    Date de generation: __GENERATION_DATE__
"""

import sys
import subprocess
from pathlib import Path


def check_virtual_env():
    """Verifie et demande confirmation pour environnement virtuel."""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    if not in_venv:
        print("[AVERTISSEMENT] Vous n'etes pas dans un environnement virtuel Python")
        print("                Il est FORTEMENT recommande d'utiliser un environnement virtuel")
        print()
        print("Pour creer un environnement virtuel:")
        print("  python -m venv .venv")
        print("  .venv\\\\Scripts\\\\activate  (Windows)")
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
    \"\"\"Verifie que Python 3.10+ est installe.\"\"\"
    version = sys.version_info
    if version < (3, 10):
        print(f\"[ERREUR] Python 3.10+ requis, vous avez Python {{version.major}}.{{version.minor}}\")
        print(\"\\nTelechargez Python depuis: https://www.python.org/downloads/\")
        sys.exit(1)

    print(f\"[OK] Python {{version.major}}.{{version.minor}}.{{version.micro}} detecte\")


def find_wheels_dir():
    \"\"\"Trouve le dossier wheels/ a cote du script.\"\"\"
    script_dir = Path(__file__).parent
    wheels_dir = script_dir / \"wheels\"

    if not wheels_dir.exists():
        print(\"[ERREUR] Dossier wheels/ introuvable\")
        print(f\"Attendu: {{wheels_dir}}\")
        print(\"\\nExecutez d'abord : python download_wheels.py\")
        sys.exit(1)

    wheels_count = len(list(wheels_dir.glob(\"*.whl\")))
    if wheels_count == 0:
        print(\"[ERREUR] Aucune wheel trouvee dans wheels/\")
        print(\"\\nExecutez d'abord : python download_wheels.py\")
        sys.exit(1)

    print(f\"[OK] {{wheels_count}} wheels trouvees dans: {{wheels_dir}}\")
    return wheels_dir


def install_ambulon(wheels_dir):
    \"\"\"Installe ambulon + toutes dependances en une seule commande.\"\"\"
    print(\"\\n[INFO] Installation d'ambulon + dependances...\")
    print(\"       Mode OFFLINE : aucun acces internet requis\")
    print()

    cmd = [
        sys.executable, \"-m\", \"pip\", \"install\",
        \"--no-index\",                    # Pas d'acces internet
        \"--find-links\", str(wheels_dir), # Cherche dans wheels/
        \"ambulon\"                        # Package principal
    ]

    # Afficher la commande qui va etre executee
    cmd_str = \" \".join(cmd)
    print(f\"Commande executee :\")
    print(f\"  {cmd_str}\")
    print()

    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True  # Capture la sortie pour ne pas polluer
        )

        # Afficher uniquement les lignes importantes
        output_lines = result.stdout.strip().split('\\n')
        print(\"[INFO] Installation en cours...\")

        # Afficher les packages installes/deja presents
        for line in output_lines:
            if 'Successfully installed' in line or 'Requirement already satisfied' in line:
                print(f\"  {line}\")
            elif 'Installing collected packages' in line:
                print(f\"  {line}\")

        print()
        print(\"[OK] Installation terminee\")
        return True
    except subprocess.CalledProcessError as e:
        print(f\"\\n[ERREUR] Installation echouee (code {e.returncode})\")
        print(\"\\nSortie pip :\")
        print(e.stdout)
        if e.stderr:
            print(\"\\nErreurs :\")
            print(e.stderr)
        return False


def verify_installation():
    \"\"\"Verifie que ambulon est installe correctement.\"\"\"
    print(\"\\n\" + \"=\"*70)
    print(\"  VERIFICATION\")
    print(\"=\"*70)
    print()
    print(\"Commande executee : ambulon --version\")
    print()

    try:
        result = subprocess.run(
            [\"ambulon\", \"--version\"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        print(f\"[OK] {result.stdout.strip()}\")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print(\"[INFO] La commande 'ambulon' n'est pas encore reconnue\")
        print(\"       Redemarrez votre terminal ou utilisez:\")
        print(\"       python -m app.cli.cli --version\")
        return False


def main():
    \"\"\"Point d'entree principal.\"\"\"
    print(\"=\"*70)
    print(\"  INSTALLATION OFFLINE D'AMBULON\")
    print(\"=\"*70)
    print()
    print(\"[INFO] Script auto-genere le {generation_date}\")
    print(\"[INFO] Par scripts/build_offline_package.py\")
    print()

    # Verifications
    check_python_version()
    print()

    check_virtual_env()
    print()

    wheels_dir = find_wheels_dir()
    print()

    # Installation en UNE SEULE COMMANDE
    print(\"=\"*70)
    print(\"  INSTALLATION\")
    print(\"=\"*70)

    if not install_ambulon(wheels_dir):
        print(\"\\n[ERREUR] Installation incomplete\")
        sys.exit(1)

    # Verification
    verify_installation()

    print()
    print(\"=\"*70)
    print(\"  INSTALLATION TERMINEE\")
    print(\"=\"*70)
    print()
    print(\"[OK] Ambulon est installe !\")
    print()
    print(\"Commandes disponibles:\")
    print(\"  ambulon --help\")
    print(\"  ambulon md2html fichier.md\")
    print()


if __name__ == \"__main__\":
    try:
        main()
    except KeyboardInterrupt:
        print(\"\\n\\n[INFO] Installation annulee par l'utilisateur\")
        sys.exit(1)
    except Exception as e:
        print(f\"\\n[ERREUR] Exception inattendue: {{e}}\")
        import traceback
        traceback.print_exc()
        sys.exit(1)
'''

    # Remplacer les placeholders
    content = template.replace("__GENERATION_DATE__", generation_date)
    content = content.replace("{generation_date}", generation_date)

    script_path.write_text(content, encoding="utf-8")
    print(f"[OK] install_offline.py mis a jour: {script_path}")


def _generate_uninstall_offline_script(dist_offline_dir: Path, dependencies: List[str]) -> None:
    """Generate dist-offline/uninstall_offline.py with current dependencies."""
    from datetime import datetime

    script_path = dist_offline_dir / "uninstall_offline.py"
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract main dependency names (exclude 'python')
    dep_names = [d for d in dependencies if d != "python"]
    # Format as Python list with proper indentation
    deps_lines = ",\n            ".join([f'"{dep}"' for dep in dep_names[:15]])  # Top 15 deps

    content = f"""#!/usr/bin/env python3
# ============================================================================
# FICHIER AUTO-GENERE par scripts/build_offline_package.py
# Date de generation: {generation_date}
# Ne pas modifier manuellement - vos modifications seront ecrasees
# ============================================================================
\"\"\"
Script de desinstallation d'Ambulon.

Ce script desinstalle Ambulon et optionnellement ses dependances.

Usage:
    python uninstall_offline.py

    # Garder les dependances (desinstaller uniquement Ambulon)
    python uninstall_offline.py --keep-deps

IMPORTANT:
    Ce script a ete genere automatiquement par build_offline_package.py
    Date de generation: {generation_date}
\"\"\"

import sys
import subprocess
import argparse


def check_virtual_env():
    \"\"\"Verifie et informe sur l'environnement virtuel.\"\"\"
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    if not in_venv:
        print(\"[AVERTISSEMENT] Vous n'etes pas dans un environnement virtuel Python\")
        print(\"                La desinstallation affectera l'installation globale\")
        print()
        response = input(\"Continuer quand meme? (oui/non): \")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print(\"[INFO] Desinstallation annulee par l'utilisateur\")
            sys.exit(0)
        print()
    else:
        print(\"[OK] Environnement virtuel detecte\")


def check_pip():
    \"\"\"Verifie que pip est installe.\"\"\"
    try:
        subprocess.run(
            [sys.executable, \"-m\", \"pip\", \"--version\"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f\"[OK] pip detecte\")
        return True
    except subprocess.CalledProcessError:
        print(\"[ERREUR] pip n'est pas installe\")
        sys.exit(1)


def is_package_installed(package_name):
    \"\"\"Verifie si un package est installe.\"\"\"
    try:
        subprocess.run(
            [sys.executable, \"-m\", \"pip\", \"show\", package_name],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def uninstall_package(package_name):
    \"\"\"Desinstalle un package.\"\"\"
    if not is_package_installed(package_name):
        print(f\"[SKIP] {{package_name}} (non installe)\")
        return True

    print(f\"[UNINSTALL] {{package_name}}...\", end='', flush=True)

    try:
        subprocess.run(
            [sys.executable, \"-m\", \"pip\", \"uninstall\", \"-y\", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(\" [OK]\")
        return True
    except subprocess.CalledProcessError as e:
        print(f\" [ERR]\")
        print(f\"  Erreur: {{e.stderr}}\")
        return False


def main():
    \"\"\"Point d'entree principal.\"\"\"
    parser = argparse.ArgumentParser(
        description=\"Desinstallation d'Ambulon\"
    )
    parser.add_argument(
        \"--keep-deps\",
        action=\"store_true\",
        help=\"Garder les dependances, desinstaller uniquement Ambulon\"
    )
    args = parser.parse_args()

    print(\"=\"*70)
    print(\"  DESINSTALLATION D'AMBULON\")
    print(\"=\"*70)
    print()
    print(\"[INFO] Script auto-genere le {generation_date}\")
    print(\"[INFO] Par scripts/build_offline_package.py\")
    print()

    # Verification
    check_pip()
    print()

    check_virtual_env()
    print()

    if not is_package_installed(\"ambulon\"):
        print(\"[INFO] Ambulon n'est pas installe\")
        sys.exit(0)

    print()

    # Packages a desinstaller (ordre inverse de l'installation)
    packages = [\"ambulon\"]

    if not args.keep_deps:
        print(\"[INFO] Desinstallation d'Ambulon ET de ses dependances\")
        packages.extend([
            {deps_lines}
        ])
    else:
        print(\"[INFO] Desinstallation d'Ambulon uniquement\")

    print()

    # Desinstallation
    failed = []

    for package in packages:
        if not uninstall_package(package):
            failed.append(package)

    # Resume
    print()
    print(\"=\"*70)
    print(\"  RESUME\")
    print(\"=\"*70)

    if failed:
        print(f\"\\n[ERREUR] {{len(failed)}} package(s) ont echoue:\")
        for pkg in failed:
            print(f\"  - {{pkg}}\")
        sys.exit(1)
    else:
        print(\"\\n[OK] Desinstallation terminee avec succes !\")

        if not args.keep_deps:
            print(\"\\nAmbulon et ses dependances ont ete supprimes.\")
        else:
            print(\"\\nAmbulon a ete supprime (dependances conservees).\")


if __name__ == \"__main__\":
    try:
        main()
    except KeyboardInterrupt:
        print(\"\\n\\n[INFO] Desinstallation annulee par l'utilisateur\")
        sys.exit(1)
    except Exception as e:
        print(f\"\\n[ERREUR] Exception inattendue: {{e}}\")
        import traceback
        traceback.print_exc()
        sys.exit(1)
"""

    script_path.write_text(content, encoding="utf-8")
    print(f"[OK] uninstall_offline.py mis a jour: {script_path}")


def build_exposed_package(version, dependencies):
    """Build le package offline avec wheels exposées (nouveau mode)."""
    # 1. Build la wheel
    wheel_file = build_wheel(version)

    # 2. Créer la structure dist-offline/
    dist_offline_dir = Path("dist-offline")
    wheels_dir = dist_offline_dir / "wheels"
    dist_offline_dir.mkdir(exist_ok=True)
    wheels_dir.mkdir(exist_ok=True)

    print("\n" + "="*60)
    print("Étape 2/5 : Structure dist-offline/ créée")
    print("="*60)
    print(f"[OK] {dist_offline_dir}/")
    print(f"[OK] {wheels_dir}/")

    # 3. Copier la wheel ambulon
    print("\n" + "="*60)
    print("Étape 3/5 : Copie de la wheel Ambulon")
    print("="*60)
    dest = wheels_dir / wheel_file.name
    shutil.copy2(wheel_file, dest)
    print(f"[OK] {wheel_file.name} copiée")

    # 4. Télécharger les dépendances
    download_dependencies(dependencies, wheels_dir)

    # 5. Generer les scripts d'installation/desinstallation
    print("\n" + "="*60)
    print("Etape 5/5 : Generation des scripts")
    print("="*60)

    github_base_url = f"https://github.com/warchosian/ambulon/raw/main/dist-offline/wheels"
    print(f"[INFO] URL des wheels GitHub: {github_base_url}")

    _generate_download_wheels_script(dist_offline_dir, github_base_url)
    _generate_install_offline_script(dist_offline_dir)
    _generate_uninstall_offline_script(dist_offline_dir, dependencies)

    print(f"[OK] Tous les scripts ont ete generes avec succes")

    # 7. Créer un README
    readme_path = dist_offline_dir / "README.md"
    readme_content = f"""# Ambulon {version} - Installation Offline (Wheels Exposées)

## Installation

1. Assurez-vous que le dossier `wheels/` contient toutes les wheels (dont `kroki`)
2. Exécutez la commande suivante :
   ```bash
   python -m pip install --no-index --find-links=wheels ambulon
   ```

Cette commande installe Ambulon et toutes les dépendances depuis les wheels locales.

## Désinstallation

```bash
python uninstall_offline.py
```

## Versions Python supportées

- Python 3.10
- Python 3.11
- Python 3.12

## Structure

```
dist-offline/
├── wheels/              # Wheels pour toutes les versions Python
│   ├── ambulon-{version}-py3-none-any.whl
│   ├── pillow-*-cp310-*.whl
│   ├── pillow-*-cp311-*.whl
│   ├── pillow-*-cp312-*.whl
│   └── ...
├── install_offline.py   # Script d'installation intelligent
├── uninstall_offline.py # Script de désinstallation
└── README.md           # Ce fichier
```

## Utilisation

Après installation :
```bash
ambulon --version
ambulon --help
```

---
**Version**: {version}
**Licence**: MIT
"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"[OK] README créé: {readme_path.name}")

    # Compter les wheels
    wheels_count = len(list(wheels_dir.glob("*.whl")))
    total_size = sum(w.stat().st_size for w in wheels_dir.glob("*.whl")) / 1024 / 1024

    # Résumé final
    print("\n" + "="*60)
    print("  BUILD TERMINÉ AVEC SUCCÈS (MODE EXPOSED)")
    print("="*60)
    print(f"\nWheels exposées dans:")
    print(f"  {wheels_dir.absolute()}")
    print(f"  {wheels_count} wheels ({total_size:.1f} MB)")
    print(f"\nScripts générés:")
    print(f"  {(dist_offline_dir / 'download_wheels.py').absolute()}")
    print(f"  {(dist_offline_dir / 'install_offline.py').absolute()}")
    print(f"  {(dist_offline_dir / 'uninstall_offline.py').absolute()}")
    print(f"\nPour distribuer:")
    print(f"  1. Committez dist-offline/ dans votre depot Git")
    print(f"  2. Les utilisateurs executent: python download_wheels.py (ONLINE)")
    print(f"  3. Puis: python install_offline.py (OFFLINE)")
    print()


def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build package offline d'Ambulon"
    )
    parser.add_argument(
        "--mode",
        choices=["zip", "exposed"],
        default="exposed",
        help=(
            "Mode de packaging : "
            "'zip' = créer un ZIP massif (ancien mode), "
            "'exposed' = exposer les wheels dans dist-offline/ (nouveau mode, par défaut)"
        )
    )
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  BUILD PACKAGE OFFLINE AMBULON")
    print(f"  Mode: {args.mode.upper()}")
    print("="*60)

    # Vérifier qu'on est à la racine du projet
    if not Path("pyproject.toml").exists():
        print("[ERREUR] pyproject.toml introuvable")
        print("        Executez ce script depuis la racine du projet")
        sys.exit(1)

    # Lire la version
    version = read_version_from_pyproject()
    print(f"\n[INFO] Version detectee: {version}")

    # Lire les dépendances
    dependencies = resolve_dependencies()
    print(f"[INFO] Dependances detectees: {len(dependencies)}")

    # Dispatcher selon le mode
    try:
        if args.mode == "zip":
            build_zip_package(version, dependencies)
        else:  # exposed
            build_exposed_package(version, dependencies)
    except KeyboardInterrupt:
        print("\n\n[INFO] Build interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
