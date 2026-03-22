@echo off
echo ==========================================
echo BUILD WHEEL AMBULON v3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/4] Nettoyage du cache Python...
python clear_all_cache.py

echo.
echo [2/4] Verification des tests TOC...
python -m pytest tests/unit/toc/ -v --tb=short 2>&1 | findstr "passed\|failed\|error"
if errorlevel 1 (
    echo ATTENTION: Des tests ont echoue
    echo Voulez-vous continuer quand meme?
    pause
)

echo.
echo [3/4] Nettoyage du dossier dist/...
if exist dist (
    del /q dist\* 2>nul
    rmdir /s /q dist 2>nul
)
mkdir dist

echo.
echo [4/4] Build avec Poetry...
poetry build

echo.
echo ==========================================
echo Build termine !
echo ==========================================
echo.
echo Fichiers generes:
dir /b dist\*.* 2>nul

echo.
echo Verification du wheel:
for %%f in (dist\*.whl) do (
    echo.
    echo Details de %%f:
    python -m zipfile -l "%%f" | findstr "Name\|ambulon\|toc\|diagrams"
)

echo.
pause
