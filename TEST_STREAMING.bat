@echo off
chcp 65001 >nul
echo ==========================================
echo Test du streaming
echo ==========================================
echo.

echo [1/2] Test piag-chat-basic-query avec streaming:
echo Commande: ambulon piag-chat-basic-query --question "Bonjour" --stream
echo.
ambulon piag-chat-basic-query --question "Bonjour" --stream 2>&1
echo.

echo [2/2] Test piag-chat-completion avec streaming:
echo Commande: ambulon piag-chat-completion --prompt "Bonjour" --stream
echo.
ambulon piag-chat-completion --prompt "Bonjour" --stream 2>&1
echo.

echo ==========================================
pause
