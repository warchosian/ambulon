@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
echo Nettoyage complet...
python clear_all_cache.py >nul 2>&1
echo.
echo Test md2interactive:
python -B -m app.cli.cli md2interactive applications\formation-ecologie.rag\formation-ecologie.c4model.md -v
pause
