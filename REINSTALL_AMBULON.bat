@echo off
chcp 65001 >nul
echo ==========================================
echo Reinstallation d'Ambulon
echo ==========================================
echo.

echo [1/4] Verification de l'environnement conda...
call conda activate ambulon 2>nul
if %errorlevel% neq 0 (
    echo Activation de l'environnement ambulon...
    call conda activate ambulon
)
python --version
echo.

echo [2/4] Desinstallation du package existant...
pip uninstall ambulon -y 2>nul
echo.

echo [3/4] Reinstallation avec Poetry...
poetry install
echo.

echo [4/4] Verification de l'installation...
where ambulon
ambulon --help
echo.

echo ==========================================
echo Installation terminee !
echo ==========================================
pause
