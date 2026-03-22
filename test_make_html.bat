@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1
ambulon make-html-interactive applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.html 2>&1 | findstr "ERROR\|interactive"
pause
