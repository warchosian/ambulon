@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1
echo === Test md-to-interactive-html ===
ambulon md-to-interactive-html applications\formation-ecologie.rag\formation-ecologie.c4model.md -v
echo.
echo Fichiers generes:
dir applications\formation-ecologie.rag\formation-ecologie.c4model-itoc* /b 2>nul
pause
