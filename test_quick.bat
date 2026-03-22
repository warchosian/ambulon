@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1
python -B -m app.diagrams.commands.md2html applications\formation-ecologie.rag\formation-ecologie.c4model.md -o applications\formation-ecologie.rag\formation-ecologie.c4model.html 2>&1 | findstr "ERROR\|Conversion"
pause
