@echo off
REM Test du vérificateur de configuration PIAG
REM Ce script ne nécessite pas de connexion réseau

echo ================================================================================
echo TEST DU VERIFICATEUR DE CONFIGURATION PIAG
echo ================================================================================
echo.

REM Activer l'environnement conda si nécessaire
if exist "%CONDA_PREFIX%\python.exe" (
    echo Environnement conda detecte: %CONDA_PREFIX%
) else (
    echo ATTENTION: Aucun environnement conda detecte
    echo Tentative d'activation de l'environnement 'ambulon'...
    call conda activate ambulon 2>nul
)

echo.
echo Verification des dependances...
python -c "import yaml; import sys; print('PyYAML:', yaml.__version__); print('Python:', sys.version)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: PyYAML n'est pas disponible
    echo Installez-le avec: pip install pyyaml
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Lancement du verificateur de configuration...
echo ================================================================================
echo.

python check_piag_config.py --config config\piag.yaml

echo.
echo ================================================================================
echo Test termine
echo ================================================================================
echo.
echo Code de retour: %ERRORLEVEL%
if %ERRORLEVEL% EQU 0 (
    echo Resultat: Configuration valide - Pret pour les tests E2E
) else (
    echo Resultat: Problemes detectes - Voir ci-dessus
)

pause
