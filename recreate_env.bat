@echo off
echo ==========================================
echo RECREATION ENVIRONNEMENT CONDA AMBULON
echo ==========================================
echo.

echo ETAPE 1: Sauvegarde des fichiers importants
echo ------------------------------------------
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

if exist .env (
    copy .env .env.backup >nul
    echo .env sauvegarde
)

echo.
echo ETAPE 2: Suppression de l'ancien environnement
echo ------------------------------------------
conda deactivate 2>nul
conda remove -n ambulon --all -y 2>nul
if errorlevel 1 (
    echo Environnement non trouve ou deja supprime
)

echo.
echo ETAPE 3: Creation du nouvel environnement
echo ------------------------------------------
conda create -n ambulon python=3.10 -y
if errorlevel 1 (
    echo ERREUR: Creation de l'environnement echouee
    pause
    exit /b 1
)

echo.
echo ETAPE 4: Activation et installation
echo ------------------------------------------
call conda activate ambulon

echo Installation de Poetry...
pip install poetry

echo Installation des dependances...
poetry install

echo Installation de Commitizen...
pip install commitizen

echo.
echo ETAPE 5: Verification
echo ------------------------------------------
python --version
poetry --version
cz --version
pip --version

echo.
echo ==========================================
echo ENVIRONNEMENT RECREE AVEC SUCCES!
echo ==========================================
echo.
echo Reactivation:
echo   conda activate ambulon
echo.
pause
