@echo off
echo ==========================================
echo RELEASE AMBULON v3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/7] Verification de l'environnement...
python --version >nul 2>&1 || (echo ERREUR: Python non trouve && exit /b 1)
poetry --version >nul 2>&1 || (echo ERREUR: Poetry non trouve && exit /b 1)
cz --version >nul 2>&1 || (echo ERREUR: Commitizen non trouve && exit /b 1)

echo.
echo [2/7] Nettoyage du cache Python...
python clear_all_cache.py

echo.
echo [3/7] Verification des tests...
python -m pytest tests/unit/toc/ -v --tb=short 2>&1 | findstr "passed\|failed\|error"

echo.
echo [4/7] Stage des fichiers modifies...
git add -A

echo.
echo [5/7] Commit avec Commitizen...
echo IMPORTANT: Selectionnez le type de commit approprie:
echo - feat: pour les nouvelles fonctionnalites (TOC, diagrams, md2interactive)
echo.
cz commit

echo.
echo [6/7] Bump version vers 3.1.0...
cz bump --changelog

echo.
echo [7/7] Build avec Poetry...
poetry build

echo.
echo ==========================================
echo Resume de la release:
echo ==========================================
git log -1 --oneline
echo.
echo Tag cree:
git describe --tags --abbrev=0 2>nul || echo Aucun tag
echo.
echo Fichiers wheel generes:
dir /b dist\*.whl 2>nul
echo.
echo ==========================================
echo Commandes pour publier:
echo   git push --follow-tags
echo   poetry publish (si applicable)
echo ==========================================

echo.
pause
