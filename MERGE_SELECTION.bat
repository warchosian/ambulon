@echo off
echo ==========================================
echo MERGER LES BRANCHES SELECTIONNEES
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo Branches disponibles:
git branch
echo.

echo Entrez le nom de la branche a merger (ou 'fin' pour terminer):
set /p BRANCH="Nom branche: "

if "%BRANCH%"=="fin" goto :end
if "%BRANCH%"=="" goto :end

echo.
echo [1] Checkout main...
git checkout main
echo.

echo [2] Merge de %BRANCH%...
git merge %BRANCH% --no-ff -m "Merge branch '%BRANCH%' into main for v3.1.0"
if errorlevel 1 (
    echo.
    echo !!! CONFLIT DETECTE !!!
    echo Resolvez les conflits puis:
    echo   git add .
    echo   git commit -m "Merge branch '%BRANCH%' into main"
    echo.
    pause
    goto :end
)
echo.

echo [3] Suppression branche locale %BRANCH%...
git branch -d %BRANCH%
echo.

echo [4] Push vers origin...
git push origin main
echo.

echo Branche %BRANCH% mergee avec succes!
echo.

echo Voulez-vous merger une autre branche? (oui/non)
set /p CONT=""
if /i "%CONT%"=="oui" goto :start

:end
echo.
echo ==========================================
echo MERGE TERMINE
echo ==========================================
git log --oneline --graph -5
echo.
pause
