@echo off
chcp 65001 >nul
echo Renommage de piag_doc_chunks.py vers piag_query.py...

if exist "src\app\piag\commands\piag_doc_chunks.py" (
    move /Y "src\app\piag\commands\piag_doc_chunks.py" "src\app\piag\commands\piag_query.py"
    echo OK - Fichier renomme
) else (
    echo ERREUR: Fichier source non trouve
)

pause
