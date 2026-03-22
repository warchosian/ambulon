@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Test formation-ecologie ===
python tools\clear_pycache.py
echo.
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model.md -o applications\formation-ecologie.rag\formation-ecologie.c4model.html
echo.
echo Verifiez le fichier HTML dans Chrome
echo.
pause
