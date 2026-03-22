@echo off
chcp 65001 >nul
echo ==========================================
echo WORKFLOW RAG AVANCE - PIAG
echo ==========================================
echo.

if "%~1"=="" (
    echo Usage: rag_advanced.bat [options]
    echo.
    echo Options:
    echo   -c, --collection-id ID    ID de la collection RAG (rapide)
    echo   --collection-name NAME    Nom de la collection (resolution auto)
    echo   -q, --question "TEXT"     Question a poser (requis)
    echo   -k, --top-k N             Nombre de chunks (defaut: 5)
    echo   -m, --mode MODE           Mode: hybrid, semantic, keyword (defaut: hybrid)
    echo   -r, --rerank              Activer le reranking
    echo   -s, --system "TEXT"       Message systeme personnalise
    echo   -o, --output FILE         Fichier de sortie (defaut: reponse_rag.md)
    echo.
    echo Exemples:
    echo   rag_advanced.bat -c PnuQzUEmwRDkxZPX -q "Procedure deploiement"
    echo   rag_advanced.bat --collection-name "Docs Tech" -q "Procedure ?"
    echo   rag_advanced.bat -c 12345 -q "Architecture" -k 10 -r -s "Tu es un expert"
    echo.
    pause
    exit /b 1
)

REM Valeurs par defaut
set COLLECTION_ID=
set COLLECTION_NAME=
set QUESTION=
set TOP_K=5
set MODE=hybrid
set RERANK=
set SYSTEM=
set OUTPUT=reponse_rag.md

REM Parsing des arguments
:parse_args
if "%~1"=="" goto :check_required

if /i "%~1"=="-c" set COLLECTION_ID=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--collection-id" set COLLECTION_ID=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--collection-name" set COLLECTION_NAME=%~2& shift & shift & goto :parse_args
if /i "%~1"=="-q" set QUESTION=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--question" set QUESTION=%~2& shift & shift & goto :parse_args
if /i "%~1"=="-k" set TOP_K=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--top-k" set TOP_K=%~2& shift & shift & goto :parse_args
if /i "%~1"=="-m" set MODE=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--mode" set MODE=%~2& shift & shift & goto :parse_args
if /i "%~1"=="-r" set RERANK=--rerank true& shift & goto :parse_args
if /i "%~1"=="--rerank" set RERANK=--rerank true& shift & goto :parse_args
if /i "%~1"=="-s" set SYSTEM=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--system" set SYSTEM=%~2& shift & shift & goto :parse_args
if /i "%~1"=="-o" set OUTPUT=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--output" set OUTPUT=%~2& shift & shift & goto :parse_args

shift
goto :parse_args

:check_required
if "%COLLECTION_ID%"=="" if "%COLLECTION_NAME%"=="" (
    echo ERREUR: --collection-id ou --collection-name requis
    exit /b 1
)
if "%QUESTION%"=="" (
    echo ERREUR: --question est requis
    exit /b 1
)

set TEMP_CHUNKS=%TEMP%\rag_adv_%RANDOM%.json

REM Construction de l'argument collection
if not "%COLLECTION_ID%"=="" (
    set COLL_ARG=--collection-id %COLLECTION_ID%
    set COLL_INFO=%COLLECTION_ID%
) else (
    set COLL_ARG=--collection-name "%COLLECTION_NAME%"
    set COLL_INFO=%COLLECTION_NAME%
)

echo Configuration:
echo   Collection: %COLL_INFO%
echo   Question: %QUESTION%
echo   Top-K: %TOP_K%
echo   Mode: %MODE%
echo   Rerank: %RERANK%
if not "%SYSTEM%"=="" echo   System: %SYSTEM%
echo   Output: %OUTPUT%
echo.

echo [1/3] Recherche semantique...
ambulon piag-search %COLL_ARG% --query "%QUESTION%" --top-k %TOP_K% --mode %MODE% %RERANK% --json > "%TEMP_CHUNKS%"
if %errorlevel% neq 0 (
    echo ERREUR: Recherche echouee
    exit /b 1
)
echo OK
echo.

echo [2/3] Generation avec contexte...
if not "%SYSTEM%"=="" (
    ambulon piag-chat-query --question "%QUESTION%" --chunks "%TEMP_CHUNKS%" --system "%SYSTEM%" --output "%OUTPUT%"
) else (
    ambulon piag-chat-query --question "%QUESTION%" --chunks "%TEMP_CHUNKS%" --output "%OUTPUT%"
)
if %errorlevel% neq 0 (
    echo ERREUR: Generation echouee
    del "%TEMP_CHUNKS%"
    exit /b 1
)
echo OK
echo.

echo [3/3] Nettoyage...
del "%TEMP_CHUNKS%"
echo OK
echo.

echo ==========================================
echo SUCCES !
echo ==========================================
echo Fichier: %OUTPUT%
echo.
type "%OUTPUT%"
echo.
pause
