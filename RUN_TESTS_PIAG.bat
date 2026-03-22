@echo off
REM Script de lancement des tests E2E PIAG
REM Usage: RUN_TESTS_PIAG.bat [check|all|rag|chat]

echo ================================================================================
echo TESTS END-TO-END API PIAG
echo ================================================================================
echo.

set CONFIG_FILE=config\piag.yaml

REM Déterminer l'action
set ACTION=%1
if "%ACTION%"=="" set ACTION=all

if "%ACTION%"=="check" (
    echo [1/1] Verification de la configuration...
    echo.
    python check_piag_config.py --config %CONFIG_FILE%
    goto :end
)

if "%ACTION%"=="all" (
    echo [1/3] Verification de la configuration...
    echo.
    python check_piag_config.py --config %CONFIG_FILE%

    if errorlevel 1 (
        echo.
        echo ================================================================================
        echo ATTENTION: Configuration incomplete ou incorrecte
        echo ================================================================================
        echo.
        choice /C YN /M "Continuer quand meme"
        if errorlevel 2 goto :end
    )

    echo.
    echo [2/3] Lancement des tests RAG et CHAT...
    echo.
    python test_piag_all.py --config %CONFIG_FILE%
    goto :end
)

if "%ACTION%"=="rag" (
    echo [1/2] Verification de la configuration RAG...
    echo.
    python check_piag_config.py --config %CONFIG_FILE%

    echo.
    echo [2/2] Lancement du test RAG...
    echo.
    python test_piag_rag_e2e.py --config %CONFIG_FILE%
    goto :end
)

if "%ACTION%"=="chat" (
    echo [1/2] Verification de la configuration CHAT...
    echo.
    python check_piag_config.py --config %CONFIG_FILE%

    echo.
    echo [2/2] Lancement du test CHAT...
    echo.
    python test_piag_chat_e2e.py --config %CONFIG_FILE%
    goto :end
)

echo Action inconnue: %ACTION%
echo.
echo Usage: RUN_TESTS_PIAG.bat [check^|all^|rag^|chat]
echo.
echo   check - Verifie seulement la configuration
echo   all   - Lance tous les tests (par defaut)
echo   rag   - Lance uniquement les tests RAG
echo   chat  - Lance uniquement les tests CHAT
echo.

:end
echo.
echo ================================================================================
echo FIN
echo ================================================================================
pause
