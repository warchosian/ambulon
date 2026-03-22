@echo off
REM ========================================================
REM Script d'installation offline d'Ambulon v3.0.1
REM ========================================================
REM Ce script installe Ambulon et toutes ses dependances
REM sans connexion Internet, a partir des wheels locales.
REM ========================================================

echo.
echo ========================================================
echo Installation offline d'Ambulon v3.0.1
echo ========================================================
echo.

REM Verification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo.
    echo Veuillez installer Python 3.10 ou superieur depuis:
    echo https://www.python.org/downloads/
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

REM Installation depuis le dossier wheels local
echo ========================================================
echo Installation d'Ambulon et de ses dependances...
echo ========================================================
echo.
echo Cette operation peut prendre 1-2 minutes...
echo.

pip install --no-index --find-links=.\wheels ambulon

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
