@echo off
chcp 65001 >nul
echo ==========================================
echo Test de piag-chat-basic-query
echo ==========================================
echo.

echo [Test 1] Aide de la commande:
ambulon piag-chat-basic-query --help
echo.

echo.
echo [Test 2] Exemple de commande (sans API key, va echouer mais montre le parsing):
echo ambulon piag-chat-basic-query --question "Quelle est la capitale de la France ?"
echo.

pause
