@echo off
chcp 65001 >nul
echo ==========================================
echo 1. Restauration de piag_doc_chunks.py depuis main
echo 2. Creation du script de chainage
echo ==========================================
echo.

echo [1/3] Restauration de piag_doc_chunks.py...
git show main:src/app/piag/commands/piag_doc_chunks.py > tmp_piag_doc_chunks.py
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de recuperer la version de main
    pause
    exit /b 1
)
copy /Y tmp_piag_doc_chunks.py src\app\piag\commands\piag_doc_chunks.py
del tmp_piag_doc_chunks.py
echo OK - piag_doc_chunks.py restaure
echo.

echo [2/3] Verification des fichiers...
echo.
echo === piag_doc_chunks.py (doit contenir 'get_chunks') ===
findstr /C:"get_chunks" src\app\piag\commands\piag_doc_chunks.py >nul && echo OK - Contient get_chunks || echo ATTENTION - Ne contient pas get_chunks
echo.
echo === piag_query.py (doit contenir 'question') ===
findstr /C:"question" src\app\piag\commands\piag_query.py >nul && echo OK - Contient question || echo ATTENTION - Ne contient pas question
echo.

echo [3/3] Creation du script de chainage piag_rag.bat...
echo.
echo @echo off > piag_rag.bat
echo chcp 65001 ^>nul >> piag_rag.bat
echo echo ========================================== >> piag_rag.bat
echo echo PIAG RAG - Recuperation des chunks + Requete >> piag_rag.bat
echo echo ========================================== >> piag_rag.bat
echo echo. >> piag_rag.bat
echo. >> piag_rag.bat
echo :: Verifier les arguments >> piag_rag.bat
echo if "%%~1"=="" ^( >> piag_rag.bat
echo     echo Usage: piag_rag.bat ^<doc-id^> ^<question^> >> piag_rag.bat
echo     echo Exemple: piag_rag.bat 12345 "Quelle est la procedure ?" >> piag_rag.bat
echo     pause >> piag_rag.bat
echo     exit /b 1 >> piag_rag.bat
echo ^) >> piag_rag.bat
echo. >> piag_rag.bat
echo set DOC_ID=%%~1 >> piag_rag.bat
echo set QUESTION=%%~2 >> piag_rag.bat
echo set TEMP_CHUNKS=temp_chunks_%%random%%.json >> piag_rag.bat
echo. >> piag_rag.bat
echo echo [1/3] Recuperation des chunks du document %%DOC_ID%%... >> piag_rag.bat
echo ambulon piag-doc-chunks --doc-id %%DOC_ID%% --output %%TEMP_CHUNKS%% >> piag_rag.bat
echo if %%errorlevel%% neq 0 ^( >> piag_rag.bat
echo     echo ERREUR: Impossible de recuperer les chunks >> piag_rag.bat
echo     exit /b 1 >> piag_rag.bat
echo ^) >> piag_rag.bat
echo echo OK >> piag_rag.bat
echo. >> piag_rag.bat
echo echo [2/3] Interrogation de l'API avec les chunks... >> piag_rag.bat
echo ambulon piag-query --question "%%QUESTION%%" --chunks %%TEMP_CHUNKS%% --output reponse_%%DOC_ID%%.md >> piag_rag.bat
echo if %%errorlevel%% neq 0 ^( >> piag_rag.bat
echo     echo ERREUR: Impossible d'interroger l'API >> piag_rag.bat
echo     del %%TEMP_CHUNKS%% 2^>nul >> piag_rag.bat
echo     exit /b 1 >> piag_rag.bat
echo ^) >> piag_rag.bat
echo echo OK >> piag_rag.bat
echo. >> piag_rag.bat
echo echo [3/3] Nettoyage... >> piag_rag.bat
echo del %%TEMP_CHUNKS%% 2^>nul >> piag_rag.bat
echo echo OK >> piag_rag.bat
echo. >> piag_rag.bat
echo echo ========================================== >> piag_rag.bat
echo echo Reponse sauvegardee dans: reponse_%%DOC_ID%%.md >> piag_rag.bat
echo echo ========================================== >> piag_rag.bat
echo. >> piag_rag.bat

echo Script piag_rag.bat cree !
echo.
echo ==========================================
echo Fichiers PIAG:
echo ==========================================
dir src\app\piag\commands\piag_*.py /b
echo.
pause
