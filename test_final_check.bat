@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1

echo Generation...
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o final_test.html 2>nul

echo.
echo 1. Lignes avec 'Table des matieres':
findstr /n "Table des mati" final_test.html

echo.
echo 2. Lignes avec 'table-of-contents':
findstr /n "table-of-contents" final_test.html

del final_test.html 2>nul
pause
