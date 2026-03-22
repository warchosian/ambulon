@echo off
chcp 65001 >nul
echo ==========================================
echo Push de beyond-basic-evolutions
echo ==========================================
echo.

REM Verifier la branche courante
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo Branche courante: %CURRENT_BRANCH%
echo.

if not "%CURRENT_BRANCH%"=="beyond-basic-evolutions" (
    echo Basculement sur beyond-basic-evolutions...
    git checkout beyond-basic-evolutions
    if %errorlevel% neq 0 (
        echo ERREUR: Impossible de basculer sur la branche.
        pause
        exit /b 1
    )
    echo OK
echo.
)

echo Push des commits vers origin...
git push origin beyond-basic-evolutions

echo.
echo ==========================================
echo Push termine !
echo ==========================================
git log --oneline -3
echo.
pause
