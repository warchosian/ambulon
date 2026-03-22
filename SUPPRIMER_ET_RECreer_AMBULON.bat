@echo off
echo ==========================================
echo SUPPRESSION ET RECREATION ENV AMBULON
echo ==========================================
echo.
echo Chemin: G:\WarchoLife\WarchoPortable\PortableWork\Anaconda\anaconda-3\envs\ambulon
echo.

echo [1/4] DESACTIVATION...
echo ------------------------------------------
call conda deactivate 2>nul
call conda deactivate 2>nul
echo OK - Environnement desactive
echo.

echo [2/4] SUPPRESSION de l'environnement ambulon...
echo ------------------------------------------
conda env remove -n ambulon -y
if errorlevel 1 (
    echo Note: L'environnement n'existait peut-etre pas
)
echo OK
echo.

echo [3/4] VERIFICATION suppression...
echo ------------------------------------------
conda env list | findstr ambulon
if errorlevel 1 (
    echo OK - ambulon n'apparait plus dans la liste
) else (
    echo ATTENTION: ambulon est toujours present
)
echo.

echo [4/4] RECREATION de l'environnement...
echo ------------------------------------------
conda create -n ambulon python=3.10 pip -y
if errorlevel 1 (
    echo ERREUR: Impossible de creer l'environnement
    pause
    exit /b 1
)
echo OK
echo.

echo ==========================================
echo ENVIRONNEMENT RECREE!
echo ==========================================
echo.
echo Prochaines etapes:
echo   1. conda activate ambulon
echo   2. pip install poetry commitizen
echo   3. cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
echo   4. poetry install
echo.
pause
