@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
echo Nettoyage complet du cache...
python clear_all_cache.py
echo.
echo Test make-html-interactive...
python -B -m app.cli.cli make-html-interactive applications\formation-ecologie.rag\formation-ecologie.c4model-itoced.html 2>&1 | findstr "ERROR\|interactive\|SUCCESS"
pause
