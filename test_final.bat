@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1

echo === Test final ===
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o final.html 2>nul

echo.
echo Nombre de <nav class="table-of-contents":
findstr /c:"<nav class=" final.html | find /c "table-of-contents"

echo.
echo Nombre de "Table des matieres":
find /c "Table des matières" final.html

echo.
echo Presence de 'uarr;' (fleche HTML):
findstr /c:"&uarr;" final.html | find /c "&uarr;"

del final.html 2>nul
pause
