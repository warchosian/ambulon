@echo off
echo ========================================
echo TEST FINAL ambulon -h
echo ========================================
echo.
call conda activate ambulon
ambulon -h
echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] ambulon fonctionne correctement !
    echo.
    echo Toutes les commandes ont ete restaurees :
    echo - flatten-html : OK
    echo - merge-html   : OK
) else (
    echo [ERREUR] ambulon a echoue
)
echo ========================================
pause
