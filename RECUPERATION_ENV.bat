@echo off
echo ==========================================
echo RECUPERATION ENVIRONNEMENT AMBULON
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/5] Desactivation environnement actuel...
conda deactivate 2>nul
conda deactivate 2>nul
echo OK

echo.
echo [2/5] Suppression environnement ambulon...
conda env remove -n ambulon -y 2>nul
echo OK

echo.
echo [3/5] Creation nouvel environnement...
conda create -n ambulon python=3.10 pip -y
if errorlevel 1 (
    echo ERREUR creation environnement
    pause
    exit /b 1
)
echo OK

echo.
echo [4/5] Installation Poetry et Commitizen...
call conda activate ambulon
python -m pip install --upgrade pip
pip install poetry commitizen
echo OK

echo.
echo [5/5] Installation projet avec Poetry...
poetry install
echo OK

echo.
echo ==========================================
echo VERIFICATION
echo ==========================================
call conda activate ambulon
python --version
poetry --version
cz --version
echo.
echo Environnement pret!
echo.
pause
