@echo off
chcp 65001 >nul
echo ==========================================
echo Test LIVE de piag-chat-basic-query
echo ==========================================
echo.

if not exist "config\piag.yaml" (
    echo ERREUR: config/piag.yaml n'existe pas
    echo Executez SETUP_CHAT_TOKEN.bat d'abord
    pause
    exit /b 1
)

echo [Test 1] Question simple:
echo Commande: ambulon piag-chat-basic-query --question "Quelle est la capitale de la France ?"
echo.
ambulon piag-chat-basic-query --question "Quelle est la capitale de la France ?" -v
echo.

echo [Test 2] Avec message systeme:
echo Commande: ambulon piag-chat-basic-query --question "Bonjour" --system "Tu es un assistant expert en informatique"
echo.
ambulon piag-chat-basic-query --question "Bonjour" --system "Tu es un assistant expert en informatique" -v
echo.

pause
