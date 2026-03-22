@echo off
chcp 65001 >nul
echo ==========================================
echo Verification des references api_key -> chat_token
echo ==========================================
echo.

echo [piag_chat_query.py]:
findstr /n "api_key" src\app\piag\commands\piag_chat_query.py 2>nul || echo OK - Aucune reference api_key
echo.

echo [piag_chat_basic_query.py]:
findstr /n "api_key" src\app\piag\commands\piag_chat_basic_query.py 2>nul || echo OK - Aucune reference api_key
echo.

echo ==========================================
echo Test de la commande:
echo ==========================================
ambulon piag-chat-query --question "Test" --chunks test.json 2>&1 | head -5
echo.

pause
