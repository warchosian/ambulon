@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1
echo Generation HTML...
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o test_check.html 2>&1 | findstr DEBUG

echo.
echo Verification du HTML:
echo 1. Nombre de "table-of-contents":
findstr /c:"table-of-contents" test_check.html | find /c "table-of-contents"

echo.
echo 2. Nombre de "Table des matieres":
find /c "Table des matières" test_check.html

echo.
echo 3. Premier nav:
findstr /n "<nav" test_check.html | head -1

del test_check.html 2>nul
pause
