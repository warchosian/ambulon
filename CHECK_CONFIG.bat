@echo off
REM Verificateur de configuration PIAG - Sans reseau
REM Ce script peut etre lance directement depuis Windows

echo ================================================================================
echo VERIFICATION DE LA CONFIGURATION PIAG
echo ================================================================================
echo.

REM Tester si Python est accessible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Python n'est pas trouve dans le PATH
    echo Activez d'abord votre environnement conda: conda activate ambulon
    pause
    exit /b 1
)

echo Python trouve:
python --version
echo.

REM Executer le verificateur
python check_piag_config.py --config config\piag.yaml

echo.
echo ================================================================================
echo Code de retour: %ERRORLEVEL%
echo ================================================================================

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [32mSUCCES: Configuration valide - Pret pour les tests E2E[0m
    echo.
) else (
    echo.
    echo [31mERREUR: Problemes detectes dans la configuration[0m
    echo.
)

pause
