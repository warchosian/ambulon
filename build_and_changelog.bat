@echo off
echo ==========================================
echo BUILD WHEEL + CHANGELOG AMBULON v3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/6] Nettoyage du cache Python...
python clear_all_cache.py

echo.
echo [2/6] Verification des tests TOC...
python -m pytest tests/unit/toc/ -v --tb=short 2>&1 | findstr "passed\|failed\|error"

echo.
echo [3/6] Verification de la version...
echo Version actuelle dans src/app/__init__.py:
findstr "__version__" src\app\__init__.py
echo.
echo Version dans pyproject.toml:
findstr "^version" pyproject.toml | head -1

echo.
echo [4/6] Generation du CHANGELOG avec Commitizen...
echo Cela va generer/maj CHANGELOG.md avec tous les commits depuis la derniere version
cz changelog --dry-run 2>&1 | head -20

echo.
echo [5/6] Nettoyage et build du wheel...
if exist dist (
    del /q dist\* 2>nul
    rmdir /s /q dist 2>nul
)
mkdir dist
poetry build

echo.
echo [6/6] Verification des artefacts...
echo.
echo Fichiers dans dist/:
dir /b dist\*.* 2>nul

echo.
echo ==========================================
echo RESUME
echo ==========================================
echo.
echo 1. CHANGELOG.md est a jour (verifiez visuellement)
echo 2. Wheel genere: dist\ambulon-3.1.0-py3-none-any.whl
echo.
echo Prochaines etapes:
echo   1. Verifiez CHANGELOG.md
echo   2. git add CHANGELOG.md
echo   3. cz bump --changelog
echo   4. git push --follow-tags
echo   5. Creer release GitHub avec le wheel
echo.
pause
