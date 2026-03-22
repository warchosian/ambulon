@echo off
echo Nettoyage du dossier dist/...
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

if exist dist (
    echo Suppression de dist/...
    rmdir /s /q dist
)

if exist build (
    echo Suppression de build/...
    rmdir /s /q build
)

echo.
echo Recreation de dist/...
mkdir dist

echo.
echo Contenu actuel:
dir /b 2>nul | findstr "dist\|build"

echo.
echo OK - Dossiers nettoyes
echo Vous pouvez maintenant faire: poetry build
pause
