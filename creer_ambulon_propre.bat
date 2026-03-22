@echo off
echo ==========================================
echo CREATION ENV AMBULON AU BON ENDROIT
echo ==========================================
echo.

echo [1/3] Verification du chemin Anaconda...
echo ------------------------------------------
for /f "tokens=*" %%a in ('conda info --base') do set CONDA_BASE=%%a
echo Base Anaconda: %CONDA_BASE%
echo.

echo Chemin attendu: %CONDA_BASE%\envs\ambulon
echo.

echo [2/3] Suppression ancien env s'il existe...
echo ------------------------------------------
if exist "%CONDA_BASE%\envs\ambulon" (
    echo Suppression de l'ancien environnement...
    rmdir /s /q "%CONDA_BASE%\envs\ambulon"
    echo OK
) else (
    echo Pas d'ancien environnement trouve
)
echo.

echo [3/3] Creation nouvel environnement...
echo ------------------------------------------
echo Creation dans: %CONDA_BASE%\envs\ambulon
conda create --prefix "%CONDA_BASE%\envs\ambulon" python=3.11 pip -y

echo.
if errorlevel 1 (
    echo ERREUR: Creation echouee
    pause
    exit /b 1
)

echo OK - Environnement cree!
echo.
echo Verification:
dir "%CONDA_BASE%\envs\ambulon" | findstr "python.exe"
echo.

echo ==========================================
echo ETAPE SUIVANTE: Activer et installer
echo ==========================================
echo.
echo conda activate ambulon
echo pip install poetry commitizen
echo cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
echo poetry install
echo.
pause
