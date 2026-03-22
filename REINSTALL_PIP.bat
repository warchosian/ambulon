@echo off
chcp 65001 >nul
echo ==========================================
echo Reinstallation d'Ambulon avec pip
echo ==========================================
echo.

echo [1/3] Desinstallation du package existant...
pip uninstall ambulon -y 2>nul
echo.

echo [2/3] Installation en mode editable...
pip install -e .
echo.

echo [3/3] Verification de l'installation...
ambulon --help | head -20
echo.

echo ==========================================
pause
