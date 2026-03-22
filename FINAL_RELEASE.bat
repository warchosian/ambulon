@echo off
echo ==========================================
echo RELEASE FINALE AMBULON v3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo ETAPE 1: Tests et verification
echo ==========================================
python clear_all_cache.py
echo.
python -m pytest tests/unit/toc/ -v --tb=short 2>&1 | tail -5

echo.
echo ETAPE 2: Commit des changements
echo ==========================================
git add -A
git status --short

echo.
echo ETAPE 3: Commitizen commit
echo ==========================================
echo Lancement de cz commit...
cz commit

echo.
echo ETAPE 4: Bump version 3.1.0
echo ==========================================
cz bump --changelog

echo.
echo ETAPE 5: Build wheel
echo ==========================================
poetry build

echo.
echo ==========================================
echo RELEASE TERMINEE !
echo ==========================================
echo.
git log -1 --oneline
git describe --tags --abbrev=0 2>nul
echo.
echo Fichiers a publier:
dir /b dist\*.whl 2>nul
echo.
echo Commande pour pusher:
echo   git push --follow-tags
echo.
pause
