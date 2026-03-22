@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Test avec UTF-8 et regex corrigee ===
python tools\clear_pycache.py >nul 2>&1

echo Generation...
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o test_utf8.html 2>&1 | findstr "Conversion\|ERROR"

echo.
echo Nombre de TOCs:
find /c "Table des mati" test_utf8.html 2>nul

del test_utf8.html 2>nul
pause
