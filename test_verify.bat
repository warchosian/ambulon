@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1

echo Generation...
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o verify.html 2>nul

echo.
echo Cherchons TOUS les "Table des matieres":
findstr /n "Table des mati" verify.html

echo.
echo Cherchons les <nav:
findstr /n "<nav" verify.html

del verify.html 2>nul
pause
