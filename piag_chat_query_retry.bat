@echo off
REM -*- coding: utf-8 -*-
REM Script de retry automatique pour piag-chat-query
REM Gère automatiquement les erreurs 504 Gateway Timeout
REM
REM Usage:
REM   piag_chat_query_retry.bat [max_retries] [retry_delay]
REM
REM Arguments:
REM   max_retries : Nombre max de tentatives (défaut: 5)
REM   retry_delay : Délai entre tentatives (défaut: 5s)
REM                 Formats acceptés: 5, 5s, 30s, 1m, 2m
REM
REM Exemples:
REM   piag_chat_query_retry.bat           (5 tentatives, 5s délai)
REM   piag_chat_query_retry.bat 10        (10 tentatives, 5s délai)
REM   piag_chat_query_retry.bat 10 30s    (10 tentatives, 30s délai)
REM   piag_chat_query_retry.bat 20 2m     (20 tentatives, 2min délai)

chcp 65001 >nul 2>&1

setlocal enabledelayedexpansion

REM Argument 1 : MAX_RETRIES (défaut: 5)
if "%~1"=="" (
    set MAX_RETRIES=5
) else (
    set MAX_RETRIES=%~1
)

REM Argument 2 : RETRY_DELAY avec parsing des suffixes (défaut: 5s)
set RETRY_DELAY_INPUT=%~2
if "%RETRY_DELAY_INPUT%"=="" (
    set RETRY_DELAY=5
) else (
    REM Parser le délai avec suffixes (s, m)
    call :parse_delay "%RETRY_DELAY_INPUT%"
)

set ATTEMPT=1

echo ========================================
echo   PIAG CHAT QUERY AVEC RETRY AUTO
echo ========================================
echo.
echo Configuration:
echo   - Max tentatives: %MAX_RETRIES%
echo   - Delai entre tentatives: %RETRY_DELAY%s
echo   - Timeout par requete: 20m
echo.

:retry_loop
echo ----------------------------------------
echo Tentative %ATTEMPT%/%MAX_RETRIES%
echo ----------------------------------------
echo Heure: %time%
echo.

REM Exécuter la commande
ambulon piag-chat-query ^
  --question-file .claude/prompts/_prompt_dat_c4model.md ^
  --chunks chunks/chunk_PNM3_SIREINES.json ^
  --timeout 20m ^
  -o reponses/reponse_dat_c4model.md

REM Vérifier le code de retour
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✅ SUCCES ^(tentative %ATTEMPT%^)
    echo ========================================
    echo.
    echo Reponse generee dans: reponses\reponse_dat_c4model.md
    echo Heure de fin: %time%
    goto :success
)

REM Échec - vérifier si on doit réessayer
echo.
echo ❌ ECHEC ^(tentative %ATTEMPT%/%MAX_RETRIES%^)

set /a ATTEMPT+=1
if %ATTEMPT% gtr %MAX_RETRIES% (
    echo.
    echo ========================================
    echo   ❌ ECHEC APRES %MAX_RETRIES% TENTATIVES
    echo ========================================
    echo.
    echo Probleme: L'API PIAG renvoie des erreurs 504 Gateway Timeout
    echo.
    echo Solutions:
    echo   - Reduire le nombre de chunks ^(--top-k 5 au lieu de 10^)
    echo   - Raccourcir la question
    echo   - Reessayer plus tard ^(serveur moins charge^)
    goto :failure
)

echo.
echo Attente de %RETRY_DELAY% secondes avant nouvelle tentative...
timeout /t %RETRY_DELAY% /nobreak
echo.
goto :retry_loop

:success
echo.
pause
exit /b 0

:failure
echo.
pause
exit /b 1

REM ========================================
REM Fonction de parsing du délai
REM ========================================
:parse_delay
set "delay_value=%~1"

REM Vérifier si se termine par 's' (secondes)
echo %delay_value% | findstr /r "^[0-9]*s$" >nul
if %errorlevel% equ 0 (
    REM Extraire le nombre sans le 's'
    set "delay_value=%delay_value:~0,-1%"
    set RETRY_DELAY=!delay_value!
    goto :eof
)

REM Vérifier si se termine par 'm' (minutes)
echo %delay_value% | findstr /r "^[0-9]*m$" >nul
if %errorlevel% equ 0 (
    REM Extraire le nombre sans le 'm' et convertir en secondes
    set "delay_value=%delay_value:~0,-1%"
    set /a RETRY_DELAY=!delay_value! * 60
    goto :eof
)

REM Sinon, considérer comme des secondes (nombre sans suffixe)
set RETRY_DELAY=%delay_value%
goto :eof
