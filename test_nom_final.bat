@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1
echo === Test avec nouveau nom ===
ambulon md-to-interactive-html applications\formation-ecologie.rag\formation-ecologie.c4model.md -v
echo.
echo Fichier final attendu: formation-ecologie.c4model-interactive.html
echo.
dir applications\formation-ecologie.rag\formation-ecologie.c4model*interactive* /b 2>nul
pause
