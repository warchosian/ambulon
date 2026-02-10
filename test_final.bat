@echo off
echo ========================================
echo Test final ambulon -h
echo ========================================
call conda activate ambulon
ambulon -h
echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: ambulon fonctionne !
) else (
    echo ERREUR: ambulon a echoue
)
echo ========================================
pause
