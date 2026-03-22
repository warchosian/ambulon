@echo off
chcp 65001 >nul
echo ==========================================
echo Finalisation: piag_chat_query.py
echo ==========================================
echo.

REM 1. Renommer le fichier
if exist "src\app\piag\commands\piag_query.py" (
    echo [1/3] Renommage piag_query.py -> piag_chat_query.py...
    move /Y "src\app\piag\commands\piag_query.py" "src\app\piag\commands\piag_chat_query.py"
    echo OK
) else (
    echo Fichier piag_query.py non trouve (deja renomme ?)
)

REM 2. Mettre a jour cli.py
echo.
echo [2/3] Mise a jour de cli.py...
powershell -Command "(Get-Content src\app\cli\cli.py) -replace 'piag-query', 'piag-chat-query' -replace 'piag_query', 'piag_chat_query' | Set-Content src\app\cli\cli.py"
echo OK

REM 3. Mettre a jour le help text dans cli.py
echo.
echo [3/3] Verification du mapping dans cli.py...
findstr /C:"piag-chat-query" src\app\cli\cli.py >nul && echo OK - piag-chat-query trouve dans cli.py || echo ATTENTION - piag-chat-query non trouve
echo.

echo ==========================================
echo Resume:
echo ==========================================
echo Commande CLI: ambulon piag-chat-query
echo Fichier: src\app\piag\commands\piag_chat_query.py
echo.
echo APIs distinctes:
echo   - PIAG RAG:   rag.api.piag.e2.rie.gouv.fr/v1 (collections, chunks)
echo   - PIAG CHAT:  preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions
echo.
pause
