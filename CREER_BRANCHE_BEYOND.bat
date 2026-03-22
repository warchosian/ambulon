@echo off
chcp 65001 >nul
echo ==========================================
echo Creation de la branche 'beyond-basic-evolutions'
echo ==========================================
echo.

REM Verifier qu'on est sur main
echo [1/4] Verification de la branche courante...
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo      Branche courante: %CURRENT_BRANCH%

if not "%CURRENT_BRANCH%"=="main" (
    echo      Basculement sur main...
    git checkout main
    if %errorlevel% neq 0 (
        echo      ERREUR: Impossible de basculer sur main.
        pause
        exit /b 1
    )
)
echo      OK
echo.

REM Mettre a jour main depuis origin
echo [2/4] Mise a jour de main depuis origin...
git pull origin main
echo      OK
echo.

REM Creer la branche beyond-basic-evolutions
echo [3/4] Creation de la branche 'beyond-basic-evolutions'...
git checkout -b beyond-basic-evolutions
if %errorlevel% neq 0 (
    echo      ERREUR: Impossible de creer la branche.
    pause
    exit /b 1
)
echo      OK
echo.

REM Pousser sur origin
echo [4/4] Push sur origin...
git push -u origin beyond-basic-evolutions
echo      OK
echo.

echo ==========================================
echo Branche 'beyond-basic-evolutions' prete !
echo ==========================================
echo.
echo Vous etes sur: beyond-basic-evoluti
echo.
git branch -v
echo.
pause
