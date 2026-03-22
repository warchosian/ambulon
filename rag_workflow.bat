@echo off
chcp 65001 >nul
echo ==========================================
echo WORKFLOW RAG PIAG - Recherche + Generation
echo ==========================================
echo.

echo Usage: rag_workflow.bat [options]
echo.
echo Options (au choix):
echo   --collection-id ID      ID de la collection (rapide)
echo   --collection-name NAME  Nom de la collection (resolution auto)
echo   --question "TEXT"       Question a poser (requis)
echo   --top-k N               Nombre de chunks (defaut: 5)
echo.
echo Exemples:
echo   rag_workflow.bat --collection-id PnuQzUEmwRDkxZPX --question "Procedure ?"
echo   rag_workflow.bat --collection-name "Docs Tech" --question "Procedure ?"
echo.

REM Verification des arguments
if "%~1"=="" (
    pause
    exit /b 1
)

REM Parsing des arguments
set COLLECTION_ID=
set COLLECTION_NAME=
set QUESTION=
set TOP_K=5

:parse_args
if "%~1"=="" goto :check_required

if /i "%~1"=="--collection-id" set COLLECTION_ID=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--collection-name" set COLLECTION_NAME=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--question" set QUESTION=%~2& shift & shift & goto :parse_args
if /i "%~1"=="--top-k" set TOP_K=%~2& shift & shift & goto :parse_args

shift
goto :parse_args

:check_required
if "%COLLECTION_ID%"=="" if "%COLLECTION_NAME%"=="" (
    echo ERREUR: --collection-id ou --collection-name requis
    exit /b 1
)
if "%QUESTION%"=="" (
    echo ERREUR: --question requis
    exit /b 1
)

set TEMP_CHUNKS=%TEMP%\rag_chunks_%RANDOM%.json

REM Construction de l'argument collection
if not "%COLLECTION_ID%"=="" (
    set COLL_ARG=--collection-id %COLLECTION_ID%
    set COLL_INFO=ID: %COLLECTION_ID%
) else (
    set COLL_ARG=--collection-name "%COLLECTION_NAME%"
    set COLL_INFO=Nom: %COLLECTION_NAME%
)

echo [1/3] Recherche dans la collection (%COLL_INFO%)...
echo     Question: %QUESTION%
echo     Top-K: %TOP_K%
echo.

ambulon piag-search %COLL_ARG% --query "%QUESTION%" --top-k %TOP_K% --json > "%TEMP_CHUNKS%"
if %errorlevel% neq 0 (
    echo ERREUR: La recherche a echoue
    exit /b 1
)

REM Verification que le fichier n'est pas vide
for %%F in ("%TEMP_CHUNKS%") do if %%~zF==0 (
    echo ERREUR: Aucun resultat trouve
    del "%TEMP_CHUNKS%"
    exit /b 1
)

echo OK - Chunks recuperes
echo.

echo [2/3] Generation de la reponse avec contexte...
ambulon piag-chat-query --question "%QUESTION%" --chunks "%TEMP_CHUNKS%" --output reponse_rag.md
if %errorlevel% neq 0 (
    echo ERREUR: La generation a echoue
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
echo WORKFLOW TERMINE !
echo ==========================================
echo.
echo Fichier genere: reponse_rag.md
echo.

REM Afficher un apercu
echo Apercu de la reponse:
echo ------------------------------
type reponse_rag.md | more /e +1 2>nul

echo.
pause
