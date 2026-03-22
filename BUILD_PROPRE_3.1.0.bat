@echo off
echo ==========================================
echo BUILD PROPRE v3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/8] Nettoyage complet...
python clear_all_cache.py >nul 2>&1
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
mkdir dist
echo OK
echo.

echo [2/8] Mise a jour version dans src\app\__init__.py...
echo __version__ = "3.1.0" > src\app\__init__.py
echo. >> src\app\__init__.py
echo "Ambulon v" + __version__ >> src\app\__init__.py
type src\app\__init__.py
echo.

echo [3/8] Mise a jour pyproject.toml...
echo TODO: Editez pyproject.toml manuellement
echo Remplacez: version = "3.0.5" par version = "3.1.0"
echo.

echo [4/8] Git add des fichiers sources...
git add src\ tests\ tools\.cz.toml README.md AGENTS.md
pause

echo [5/8] Git commit...
git commit -m "feat: release v3.1.0 - modules TOC et diagrams with md2interactive"
echo OK
echo.

echo [6/8] Git tag...
git tag -a v3.1.0 -m "Release v3.1.0: Modules TOC, diagrams, tests"
echo OK
echo.

echo [7/8] Build wheel avec Python...
python -m pip install build -q 2>nul
python -m build --wheel --outdir dist
echo OK
echo.

echo [8/8] Verification...
echo Version:
findstr "__version__" src\app\__init__.py
echo.
echo Tag:
git describe --tags
echo.
echo Wheel genere:
dir /b dist\*.whl 2>nul
echo.
echo ==========================================
echo POUR PUBLIER:
echo   git push origin main --tags
echo ==========================================
pause
