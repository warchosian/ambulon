@echo off
chcp 65001 >nul
echo ==========================================
echo Creation d'une nouvelle branche de developpement
echo ==========================================
echo.

REM Verifier qu'on est sur main
echo Verification de la branche courante...
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo Branche courante: %CURRENT_BRANCH%
echo.

if not "%CURRENT_BRANCH%"=="main" (
    echo [AVERTISSEMENT] Vous n'etes pas sur main!
    set /p SWITCH="Basculer sur main maintenant ? (O/N): "
    if /i "!SWITCH!"=="O" (
        git checkout main
        if %errorlevel% neq 0 (
            echo ERREUR: Impossible de basculer sur main.
            pause
            exit /b 1
        )
        echo Bascule sur main reussie.
    ) else (
        echo Operation annulee. Veuillez basculer sur main manuellement.
        pause
        exit /b 1
    )
    echo.
)

REM Mettre a jour main depuis origin
echo Mise a jour de main depuis origin...
git pull origin main
echo.

REM Demander le nom de la nouvelle branche
echo Types de branches courants :
echo   - feature/nom-fonctionnalite  (nouvelle fonctionnalite)
echo   - fix/nom-correction          (correction de bug)
echo   - refactor/nom-refactoring    (refactoring)
echo   - docs/nom-documentation      (documentation)
echo   - test/nom-tests              (tests)
echo.
set /p BRANCH_NAME="Nom de la nouvelle branche: "

if "%BRANCH_NAME%"=="" (
    echo ERREUR: Le nom de branche ne peut pas etre vide.
    pause
    exit /b 1
)

echo.
echo Creation de la branche '%BRANCH_NAME%'...
git checkout -b %BRANCH_NAME%

if %errorlevel% neq 0 (
    echo ERREUR: Impossible de creer la branche.
    pause
    exit /b 1
)

echo.
echo Pousser la branche sur origin...
git push -u origin %BRANCH_NAME%

echo.
echo ==========================================
echo Branche '%BRANCH_NAME%' creee avec succes !
echo ==========================================
echo.
echo Vous etes maintenant sur la branche: %BRANCH_NAME%
echo.
echo Branches locales :
git branch -v
echo.
pause
