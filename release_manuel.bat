@echo off
echo ==========================================
echo RELEASE MANUELLE v3.1.0 (sans Commitizen)
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/5] Mise a jour version dans src/app/__init__.py...
echo __version__ = "3.1.0" > src\app\__init__.py.tmp
type src\app\__init__.py | findstr /v "__version__" >> src\app\__init__.py.tmp
move /y src\app\__init__.py.tmp src\app\__init__.py >nul
echo OK
echo.

echo [2/5] Mise a jour version dans pyproject.toml...
echo PAS IMPLEMENTE - faites manuellement:
echo   version = "3.1.0" dans pyproject.toml
echo.

echo [3/5] Git commit et tag...
git add -A
git commit -m "feat: release v3.1.0 - modules TOC et diagrams"
git tag -a v3.1.0 -m "Release v3.1.0: Modules TOC, diagrams, md2interactive"
echo OK
echo.

echo [4/5] Build wheel...
poetry build 2>nul || python -m build
echo OK
echo.

echo [5/5] Verification:
git log -1 --oneline
git describe --tags --abbrev=0
dir /b dist\*.whl 2>nul
echo.
echo Pour pousser: git push --follow-tags
pause
