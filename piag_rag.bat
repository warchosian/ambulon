@echo off 
chcp 65001 >nul 
echo ========================================== 
echo PIAG RAG - Recuperation des chunks + Requete 
echo ========================================== 
echo. 
 
:: Verifier les arguments 
if "%~1"=="" ( 
    echo Usage: piag_rag.bat <doc-id> <question> 
    echo Exemple: piag_rag.bat 12345 "Quelle est la procedure ?" 
    pause 
    exit /b 1 
) 
 
set DOC_ID=%~1 
set QUESTION=%~2 
set TEMP_CHUNKS=temp_chunks_%random%.json 
 
echo [1/3] Recuperation des chunks du document %DOC_ID%... 
ambulon piag-doc-chunks --doc-id %DOC_ID% --output %TEMP_CHUNKS% 
if %errorlevel% neq 0 ( 
    echo ERREUR: Impossible de recuperer les chunks 
    exit /b 1 
) 
echo OK 
 
echo [2/3] Interrogation de l'API avec les chunks... 
ambulon piag-query --question "%QUESTION%" --chunks %TEMP_CHUNKS% --output reponse_%DOC_ID%.md 
if %errorlevel% neq 0 ( 
    echo ERREUR: Impossible d'interroger l'API 
    del %TEMP_CHUNKS% 2>nul 
    exit /b 1 
) 
echo OK 
 
echo [3/3] Nettoyage... 
del %TEMP_CHUNKS% 2>nul 
echo OK 
 
echo ========================================== 
echo Reponse sauvegardee dans: reponse_%DOC_ID%.md 
echo ========================================== 
 
