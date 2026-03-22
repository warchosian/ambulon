@echo off
chcp 65001 >nul
echo ==========================================
echo Renommage: piag_query.py -> piag_chat_query.py
echo ==========================================
echo.

if exist "src\app\piag\commands\piag_query.py" (
    echo [1/2] Renommage du fichier...
    move /Y "src\app\piag\commands\piag_query.py" "src\app\piag\commands\piag_chat_query.py"
    echo OK
) else (
    echo Fichier piag_query.py non trouve
    exit /b 1
)

echo.
echo [2/2] Mise a jour de cli.py...

REM Remplacer piag-query par piag-chat-query dans cli.py
powershell -Command "(Get-Content src\app\cli\cli.py) -replace 'piag-query', 'piag-chat-query' -replace 'piag_query', 'piag_chat_query' | Set-Content src\app\cli\cli.py"

echo OK
echo.

echo ==========================================
echo Resume:
echo ==========================================
echo Commande: ambulon piag-chat-query
echo Fichier:  src\app\piag\commands\piag_chat_query.py
echo.
echo Cette commande utilise l'API PIAG Chat (chat/completions)
echo URL: https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions
echo.
pause
