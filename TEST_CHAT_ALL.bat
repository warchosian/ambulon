@echo off
chcp 65001 >nul
echo ==========================================
echo Test de toutes les commandes piag-chat-*
echo ==========================================
echo.

echo [1/4] piag-chat-apikey-info --help
ambulon piag-chat-apikey-info --help 2>&1 | head -20
echo.

echo [2/4] piag-chat-basic-query --help
ambulon piag-chat-basic-query --help 2>&1 | head -20
echo.

echo [3/4] piag-chat-completion --help
ambulon piag-chat-completion --help 2>&1 | head -20
echo.

echo [4/4] piag-chat-query --help
ambulon piag-chat-query --help 2>&1 | head -20
echo.

echo ==========================================
echo Toutes les commandes sont disponibles !
echo ==========================================
pause
