@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"
python tools\clear_pycache.py >nul 2>&1

echo Test generation nom fichier interactive...
ambulon make-html-interactive applications\formation-ecologie.rag\formation-ecologie.c4model.html

echo.
echo Fichier genere:
if exist "applications\formation-ecologie.rag\formation-ecologie.c4model-interactive.html" (
    echo OK: formation-ecologie.c4model-interactive.html
) else if exist "applications\formation-ecologie.rag\formation-ecologie.c4model.interactive.html" (
    echo ERREUR: formation-ecologie.c4model.interactive.html (ancien format)
) else (
    echo Fichier non trouve
)

pause
