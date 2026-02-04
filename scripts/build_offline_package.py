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


def read_dependencies_from_pyproject():
    """Extrait les dépendances depuis pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraire la section [tool.poetry.dependencies]
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
            # Ignorer python
            if dep_name != 'python':
                dependencies.append(dep_name)

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

    # 5. Copier les scripts d'installation/désinstallation
    print("\n" + "="*60)
    print("Étape 5/5 : Copie des scripts d'installation")
    print("="*60)

    scripts_source_dir = Path("dist-offline")
    install_script = scripts_source_dir / "install_offline.py"
    uninstall_script = scripts_source_dir / "uninstall_offline.py"

    if not install_script.exists():
        print(f"[ERREUR] {install_script} introuvable")
        sys.exit(1)

    if not uninstall_script.exists():
        print(f"[ERREUR] {uninstall_script} introuvable")
        sys.exit(1)

    print(f"[OK] Scripts déjà en place:")
    print(f"     {install_script}")
    print(f"     {uninstall_script}")

    # 6. Créer un README
    readme_path = dist_offline_dir / "README.md"
    readme_content = f"""# Ambulon {version} - Installation Offline (Wheels Exposées)

## Installation

1. Téléchargez `install_offline.py`
2. Exécutez :
   ```bash
   python install_offline.py
   ```

Le script téléchargera automatiquement les wheels compatibles avec votre version Python depuis ce dossier et les installera.

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
    print(f"\nScripts d'installation:")
    print(f"  {install_script.absolute()}")
    print(f"  {uninstall_script.absolute()}")
    print(f"\nPour distribuer:")
    print(f"  1. Committez dist-offline/ dans votre dépôt")
    print(f"  2. Les utilisateurs téléchargent install_offline.py")
    print(f"  3. Exécutent: python install_offline.py")
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
    dependencies = read_dependencies_from_pyproject()
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
