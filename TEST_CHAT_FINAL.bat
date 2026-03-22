@echo off
chcp 65001 >nul
echo ==========================================
echo Test FINAL de piag-chat-basic-query
echo ==========================================
echo.

echo Verification de la config:
findstr /C:"chat_token" config\piag.yaml | head -1
echo.

echo [Test] Question simple:
ambulon piag-chat-basic-query --question "Quelle est la capitale de la France ?"
echo.

pause
