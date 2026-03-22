@echo off
chcp 65001 >nul
echo ==========================================
echo PIAG RAG - Exemple de chainage
echo ==========================================
echo.

if "%~1"=="" (
    echo Usage: piag_rag_simple.bat ^<doc-id^> ^<collection-id^> ^<question^>
    echo.
    echo Exemple:
    echo   piag_rag_simple.bat 12345 678 "Quelle est la procedure ?"
    echo.
    echo Cette commande va:
    echo   1. Recuperer les chunks du document 12345 depuis PIAG RAG
    echo   2. Interroger l'API PIAG avec ces chunks comme contexte
    echo.
    pause
    exit /b 1
)

set DOC_ID=%~1
set COLLECTION_ID=%~2
set QUESTION=%~3

echo [1/2] Recuperation des chunks et interrogation PIAG...
echo     Document ID: %DOC_ID%
echo     Collection ID: %COLLECTION_ID%
echo     Question: %QUESTION%
echo.

ambulon piag-query --question "%QUESTION%" --doc-id %DOC_ID% --collection-id %COLLECTION_ID% --output reponse_%DOC_ID%.md -v

if %errorlevel% neq 0 (
    echo.
    echo ERREUR: La commande a echoue
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCCES !
echo ==========================================
echo Reponse sauvegardee dans: reponse_%DOC_ID%.md
echo.

pause
