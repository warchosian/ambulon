@echo off
chcp 65001 >nul
echo ==========================================
echo Correction du probleme de config
echo ==========================================
echo.

echo Variable AMBULON_HOME: %AMBULON_HOME%
echo.

echo [Option 1] Supprimer AMBULON_HOME (recommande)
echo [Option 2] Copier config/gitlab.yaml vers %AMBULON_HOME%\config\
echo.

set /p CHOICE="Choix (1 ou 2): "

if "%CHOICE%"=="1" (
    echo.
    echo Suppression de AMBULON_HOME...
    setx AMBULON_HOME ""
    echo Variable supprimee. Redemarrez votre terminal.
) else if "%CHOICE%"=="2" (
    echo.
    echo Copie du fichier de config...
    if not exist "%AMBULON_HOME%\config" mkdir "%AMBULON_HOME%\config"
    copy /Y "config\gitlab.yaml" "%AMBULON_HOME%\config\gitlab.yaml"
    echo Fichier copie.
) else (
    echo Choix invalide.
)

echo.
pause
