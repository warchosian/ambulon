@echo off
REM Script pour lancer les tests unitaires TOC

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo ========================================
echo Tests unitaires du module TOC
echo ========================================
echo.

REM Nettoyer le cache Python
echo [1/4] Nettoyage du cache...
python tools\clear_pycache.py >nul 2>&1
if errorlevel 1 (
    echo Note: Impossible de nettoyer le cache
)
echo.

REM Vérifier que pytest est installé
echo [2/4] Verification de pytest...
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo ERREUR: pytest n'est pas installe
    echo Installation: pip install pytest pytest-cov
    exit /b 1
)
echo OK
echo.

REM Lancer les tests
echo [3/4] Execution des tests...
echo.

set PYTHONPATH=%CD%\src

REM Options:
REM -v : verbose
REM --tb=short : traceback court
REM --color=yes : couleurs
REM -x : arrêter au premier échec

echo Mode 1: Tests rapides (sans couverture)
echo ----------------------------------------
python -m pytest tests\unit\toc\ -v --tb=short --color=yes -x

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERREUR: Des tests ont echoue
    echo ========================================
    exit /b 1
)

echo.
echo Mode 2: Tests avec couverture (optionnel)
echo ----------------------------------------
python -m pytest tests\unit\toc\ -v --tb=short --color=yes --cov=src\app\toc --cov-report=term-missing --cov-report=html:tests\unit\toc\coverage_html 2>nul

if errorlevel 1 (
    echo Note: pytest-cov non installe ou erreur de couverture
)

echo.
echo ========================================
echo SUCCES: Tous les tests sont passes!
echo ========================================

REM Ouvrir le rapport de couverture si généré
if exist "tests\unit\toc\coverage_html\index.html" (
    echo.
    echo Rapport de couverture: tests\unit\toc\coverage_html\index.html
    start tests\unit\toc\coverage_html\index.html 2>nul
)

pause
