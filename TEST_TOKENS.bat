@echo off
chcp 65001 >nul
echo ==========================================
echo Verification des tokens PIAG Chat
echo ==========================================
echo.

echo [1/3] Verification de piag_chat_basic_query.py:
findstr /C:"PIAG_CHAT_API_TOKEN" src\app\piag\commands\piag_chat_basic_query.py >nul && echo OK - PIAG_CHAT_API_TOKEN trouve || echo ERREUR
findstr /C:"chat_token" src\app\piag\commands\piag_chat_basic_query.py >nul && echo OK - chat_token trouve || echo ERREUR
echo.

echo [2/3] Verification de piag_chat_query.py:
findstr /C:"PIAG_CHAT_API_TOKEN" src\app\piag\commands\piag_chat_query.py >nul && echo OK - PIAG_CHAT_API_TOKEN trouve || echo ERREUR
findstr /C:"chat_token" src\app\piag\commands\piag_chat_query.py >nul && echo OK - chat_token trouve || echo ERREUR
echo.

echo [3/3] Verification de piag.yaml.example:
findstr /C:"PIAG_CHAT_API_TOKEN" config\piag.yaml.example >nul && echo OK - PIAG_CHAT_API_TOKEN trouve || echo ERREUR
echo.

echo ==========================================
echo Test de la commande (aide):
echo ==========================================
ambulon piag-chat-basic-query --help 2>&1 | head -30
echo.

pause
