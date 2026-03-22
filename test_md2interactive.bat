@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1
echo === Test md2interactive ===
ambulon md2interactive applications\formation-ecologie.rag\formation-ecologie.c4model.md -v
echo.
echo Fichiers generes:
dir applications\formation-ecologie.rag\formation-ecologie.c4model* /b 2>nul | findstr "itoc\|interactive"
pause
