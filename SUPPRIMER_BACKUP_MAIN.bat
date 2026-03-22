@echo off
chcp 65001 >nul
echo ==========================================
echo Annulation du merge et suppression de backup-main
echo ==========================================
echo.

REM Annuler le merge en cours s'il y en a un
echo [1/4] Annulation du merge en cours...
git merge --abort 2>nul
if %errorlevel% == 0 (
    echo      Merge annule avec succes.
) else (
    echo      Aucun merge en cours ou deja annule.
)
echo.

REM Verifier qu'on est sur main
echo [2/4] Verification de la branche courante...
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo      Branche courante: %CURRENT_BRANCH%

if not "%CURRENT_BRANCH%"=="main" (
    echo      Basculage sur main...
    git checkout main
)
echo.

REM Supprimer la branche backup-main localement
echo [3/4] Suppression de backup-main localement...
git branch -D backup-main 2>nul
if %errorlevel% == 0 (
    echo      Branche backup-main supprimee localement.
) else (
    echo      Branche deja supprimee localement ou inexistante.
)
echo.

REM Supprimer la branche backup-main sur le remote
echo [4/4] Suppression de backup-main sur origin...
git push origin --delete backup-main 2>nul
if %errorlevel% == 0 (
    echo      Branche backup-main supprimee sur origin.
) else (
    echo      Branche inexistante sur origin ou deja supprimee.
)
echo.

echo ==========================================
echo Resume des branches restantes :
echo ==========================================
git branch -a
echo.
pause
