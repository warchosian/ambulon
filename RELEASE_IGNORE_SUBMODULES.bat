@echo off
echo ==========================================
echo RELEASE v3.1.0 (ignore submodules)
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo ETAPE 1: Retirer les submodules de l'index
git rm --cached gitlab/primesauto 2>nul
git rm --cached gitlab/sireines.wiki 2>nul
git rm --cached gitlab\primesauto 2>nul
git rm --cached gitlab\sireines.wiki 2>nul
echo OK
echo.

echo ETAPE 2: Ajouter seulement les fichiers sources
git add src/
git add tests/
git add pyproject.toml
git add poetry.lock
git add README.md
git add CHANGELOG.md 2>nul
git add .cz.toml
git add AGENTS.md
git add tools/
echo OK
echo.

echo ETAPE 3: Status
git status --short
echo.

echo ETAPE 4: Commit
git commit -m "feat: release v3.1.0 - modules TOC et diagrams

- Nouveau module app.toc (add-toc4md, add-itoc4md, check-toc4md, check-itoc4md)
- Nouveau module app.diagrams (md2html-diagrams avec conversion SVG)
- Nouvelle commande md2interactive (workflow complet MD vers HTML interactif)
- Tests unitaires complets pour TOC
- Corrections: doublons TOC, backlinks, encodage UTF-8"

echo.
echo ETAPE 5: Tag
git tag v3.1.0
echo OK
echo.

echo ETAPE 6: Build wheel
if exist dist rmdir /s /q dist
mkdir dist
python -m pip install build -q 2>nul
python -m build --wheel

echo.
echo ==========================================
echo RESUME
echo ==========================================
git log -1 --oneline
git describe --tags --abbrev=0 2>nul
echo.
echo Wheel genere:
dir /b dist\*.whl 2>nul
echo.
pause
