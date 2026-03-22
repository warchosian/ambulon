@echo off
chcp 65001 >nul
echo ==========================================
echo Verification de la config PIAG Chat
echo ==========================================
echo.

echo [Config YAML]
findstr /C:"chat_" config\piag.yaml
echo.

echo [Variables dans le code]
echo - piag_chat_basic_query.py:
findstr /C:"PIAG_CHAT_API_TOKEN" src\app\piag\commands\piag_chat_basic_query.py | head -1
echo - piag_chat_query.py:
findstr /C:"PIAG_CHAT_API_TOKEN" src\app\piag\commands\piag_chat_query.py | head -1
echo.

echo ==========================================
pause
