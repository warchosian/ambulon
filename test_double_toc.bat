@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Test correction double TOC ===
echo.

python tools\clear_pycache.py

echo [1/2] Test avec formation-ecologie.c4model-toced.md...
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-toced.md -o test_toced.html
echo.
echo Nombre de "Table des matières" dans test_toced.html:
find /c "Table des matières" test_toced.html
echo.

echo [2/2] Test avec formation-ecologie.c4model-itoced.md...
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.md -o test_itoced.html
echo.
echo Nombre de "Table des matières" dans test_itoced.html:
find /c "Table des matières" test_itoced.html
echo.

del test_toced.html 2>nul
del test_itoced.html 2>nul

echo === FIN ===
pause
