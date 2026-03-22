@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Test avec correction regex ===
python tools\clear_pycache.py >nul 2>&1

echo Generation HTML...
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o test_fix.html 2>&1 | findstr "Conversion\|ERROR"

echo.
echo Verification:
find /c "Table des matières" test_fix.html 2>nul && echo. || echo Erreur

echo.
echo Nombre de table-of-contents:
findstr /c:"table-of-contents" test_fix.html | find /c "table-of-contents"

del test_fix.html 2>nul
pause
