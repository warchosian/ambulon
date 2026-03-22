@echo off
echo ==========================================
echo RELEASE SIMPLE v3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo ETAPE 1: Git add
git add -A
git status --short

echo.
echo ETAPE 2: Git commit
git commit -m "feat: ajoute modules TOC et diagrams avec workflow md2interactive

- Nouveau module app.toc (add-toc4md, add-itoc4md, check-toc4md, check-itoc4md)
- Nouveau module app.diagrams (md2html-diagrams avec conversion SVG)
- Nouvelle commande md2interactive (workflow complet MD vers HTML interactif)
- Tests unitaires complets pour TOC
- Corrections: doublons TOC, backlinks, encodage UTF-8"

echo.
echo ETAPE 3: Git tag
git tag v3.1.0

echo.
echo ETAPE 4: Build wheel
echo Nettoyage dist...
if exist dist rmdir /s /q dist
mkdir dist

echo Build...
python -m pip install build -q
python -m build --wheel

echo.
echo ==========================================
echo RESUME
echo ==========================================
git log -1 --oneline
git describe --tags --abbrev=0 2>nul
echo.
echo Wheel:
dir /b dist\*.whl 2>nul
echo.
echo Pour publier:
echo   git push origin main --tags
echo.
pause
