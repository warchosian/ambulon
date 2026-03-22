@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o test_fix.html 2>&1 | findstr DEBUG

echo.
echo Nombre de TOCs:
find /c "Table des matières" test_fix.html 2>nul

del test_fix.html 2>nul
pause
