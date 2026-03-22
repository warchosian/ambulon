@echo off
chcp 65001 >nul
echo ==========================================
echo Test de piag-chat-query
echo ==========================================
echo.

echo Verification du mapping dans cli.py:
findstr /C:"piag-chat-query" src\app\cli\cli.py
echo.

echo Test de l'aide:
ambulon piag-chat-query --help
echo.

pause
