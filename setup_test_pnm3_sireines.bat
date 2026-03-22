@echo off
REM ============================================================================
REM setup_test_pnm3_sireines.bat
REM
REM Script complet pour créer et tester la collection RAG PNM3_SIREINES
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuration
set COLLECTION_NAME=PNM3_SIREINES
set DOCS_DIR=applications\sireines.rag
set CHUNKS_DIR=output_test_pnm3_sireines_chunks
set RESPONSE_DIR=output_test_pnm3_sireines_responses
set LOG_FILE=%RESPONSE_DIR%\test_execution.log

REM Créer les répertoires de sortie
if not exist "%CHUNKS_DIR%" mkdir "%CHUNKS_DIR%"
if not exist "%RESPONSE_DIR%" mkdir "%RESPONSE_DIR%"
if exist "%LOG_FILE%" del "%LOG_FILE%"

REM En-tête
cls
echo ================================================================================
echo     CREATION ET TEST DE LA COLLECTION PNM3_SIREINES
echo ================================================================================
echo.

REM ============================================================================
REM ETAPE 1 : Verification des prerequis
REM ============================================================================
echo.
echo ================================================================================
echo  ETAPE 1 : VERIFICATION DES PREREQUIS
echo ================================================================================
echo.

if not exist "%DOCS_DIR%" (
    echo [ERREUR] Le repertoire %DOCS_DIR% n'existe pas
    pause
    exit /b 1
)
echo [OK] Repertoire %DOCS_DIR% trouve

echo.
echo Comptage des documents disponibles...
dir /b "%DOCS_DIR%\*.md" 2>nul | find /c /v "" > "%CHUNKS_DIR%\temp_md_count.txt"
set /p MD_COUNT=<"%CHUNKS_DIR%\temp_md_count.txt"
dir /b "%DOCS_DIR%\*.pdf" 2>nul | find /c /v "" > "%CHUNKS_DIR%\temp_pdf_count.txt"
set /p PDF_COUNT=<"%CHUNKS_DIR%\temp_pdf_count.txt"
set /a TOTAL_COUNT=%MD_COUNT%+%PDF_COUNT%

echo [INFO] Documents trouves : %MD_COUNT% fichiers .md, %PDF_COUNT% fichiers .pdf (Total: %TOTAL_COUNT%)

if %TOTAL_COUNT%==0 (
    echo [ERREUR] Aucun document trouve
    pause
    exit /b 1
)

echo [OK] Prerequis valides
echo.
pause

REM ============================================================================
REM ETAPE 2 : Creation de la collection
REM ============================================================================
echo.
echo ================================================================================
echo  ETAPE 2 : CREATION DE LA COLLECTION %COLLECTION_NAME%
echo ================================================================================
echo.
echo ================================================================================
echo Command:
echo   ambulon piag-rag-create \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --description "Documentation complete SIREINES : DAT, CCTP, C4, Composants, ISO25010" \
echo     --directory "%DOCS_DIR%" \
echo     --extensions "md,pdf"
echo ================================================================================
echo.

ambulon piag-rag-create --collection-name "%COLLECTION_NAME%" --description "Documentation complete SIREINES : DAT, CCTP, C4, Composants, ISO25010" --directory "%DOCS_DIR%" --extensions "md,pdf"

if %errorlevel% equ 0 (
    echo.
    echo [OK] Collection creee avec succes
) else (
    echo.
    echo [ERREUR] Echec de la creation
    pause
    exit /b 1
)

echo.
pause

REM ============================================================================
REM ETAPE 3 : Attente indexation
REM ============================================================================
echo.
echo ================================================================================
echo  ETAPE 3 : ATTENTE DE L'INDEXATION (30 secondes)
echo ================================================================================
echo.
timeout /t 30 /nobreak
echo [OK] Indexation supposee terminee
echo.
pause

REM ============================================================================
REM ETAPE 4 : Verification
REM ============================================================================
echo.
echo ================================================================================
echo  ETAPE 4 : VERIFICATION DE LA COLLECTION
echo ================================================================================
echo.
echo ================================================================================
echo Command:
echo   ambulon piag-rag-collection-get \
echo     --collection-name "%COLLECTION_NAME%"
echo ================================================================================
echo.

ambulon piag-rag-collection-get --collection-name "%COLLECTION_NAME%"

echo.
pause

echo.
echo ================================================================================
echo Command:
echo   ambulon piag-rag-doc-list \
echo     --collection-name "%COLLECTION_NAME%"
echo ================================================================================
echo.

ambulon piag-rag-doc-list --collection-name "%COLLECTION_NAME%"

echo.
pause

REM ============================================================================
REM ETAPE 5 : Recherches RAG
REM ============================================================================
echo.
echo ================================================================================
echo  ETAPE 5 : TESTS DE RECHERCHE RAG (5 recherches)
echo ================================================================================
echo.

echo.
echo ================================================================================
echo STEP 1/5: Recherche architecture technique SIREINES
echo ================================================================================
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "architecture technique SIREINES" \
echo     --top-k 5 \
echo     --mode hybrid \
echo     --rerank \
echo     --format json
echo ================================================================================
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "architecture technique SIREINES" --top-k 5 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\search_1.json" 2>&1

if %errorlevel% equ 0 (echo [OK] Recherche 1 terminee) else (echo [ERREUR] Echec)
echo.
pause

echo.
echo ================================================================================
echo STEP 2/5: Recherche module gestion alertes
echo ================================================================================
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "module gestion alertes" \
echo     --top-k 5 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo ================================================================================
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "module gestion alertes" --top-k 5 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\search_2.json" 2>&1

if %errorlevel% equ 0 (echo [OK] Recherche 2 terminee) else (echo [ERREUR] Echec)
echo.
pause

echo.
echo ================================================================================
echo STEP 3/5: Recherche modele C4
echo ================================================================================
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "modele C4" \
echo     --top-k 5 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo ================================================================================
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "modele C4" --top-k 5 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\search_3.json" 2>&1

if %errorlevel% equ 0 (echo [OK] Recherche 3 terminee) else (echo [ERREUR] Echec)
echo.
pause

echo.
echo ================================================================================
echo STEP 4/5: Recherche exigences ISO 25010
echo ================================================================================
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "exigences qualite ISO 25010" \
echo     --top-k 5 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo ================================================================================
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "exigences qualite ISO 25010" --top-k 5 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\search_4.json" 2>&1

if %errorlevel% equ 0 (echo [OK] Recherche 4 terminee) else (echo [ERREUR] Echec)
echo.
pause

echo.
echo ================================================================================
echo STEP 5/5: Recherche securite authentification
echo ================================================================================
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "securite authentification" \
echo     --top-k 5 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo ================================================================================
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "securite authentification" --top-k 5 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\search_5.json" 2>&1

if %errorlevel% equ 0 (echo [OK] Recherche 5 terminee) else (echo [ERREUR] Echec)
echo.
pause

REM ============================================================================
REM ETAPE 6 : RAG + CHAT
REM ============================================================================
echo.
echo ================================================================================
echo  ETAPE 6 : TESTS RAG + CHAT (5 questions techniques)
echo ================================================================================
echo.

REM Question 1 : Architecture
echo.
echo ================================================================================
echo QUESTION 1/5: Architecture technique
echo ================================================================================
echo [1/2] Recherche des chunks...
echo.
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "architecture technique composants technologies patterns" \
echo     --top-k 7 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "architecture technique composants technologies patterns" --top-k 7 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\architecture_chunks.json" 2>&1

if %errorlevel% equ 0 (
    echo [OK] Chunks trouves
    echo.
    echo [2/2] Generation de la reponse...
    echo.
    echo Command:
    echo   ambulon piag-chat-query \
    echo     --question "Decris l'architecture technique du systeme SIREINES..." \
    echo     --chunks "%CHUNKS_DIR%\architecture_chunks.json" \
    echo     --output "%RESPONSE_DIR%\architecture_reponse.md"
    echo.

    ambulon piag-chat-query --question "Decris l'architecture technique du systeme SIREINES en detaillant les composants, les technologies utilisees et les patterns architecturaux." --chunks "%CHUNKS_DIR%\architecture_chunks.json" --output "%RESPONSE_DIR%\architecture_reponse.md"

    if %errorlevel% equ 0 (echo [OK] Reponse generee) else (echo [ERREUR] Echec)
) else (
    echo [ERREUR] Echec recherche
)
echo.
pause

REM Question 2 : C4
echo.
echo ================================================================================
echo QUESTION 2/5: Modele C4
echo ================================================================================
echo [1/2] Recherche des chunks...
echo.
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "modele C4 context container component" \
echo     --top-k 7 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "modele C4 context container component" --top-k 7 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\c4model_chunks.json" 2>&1

if %errorlevel% equ 0 (
    echo [OK] Chunks trouves
    echo.
    echo [2/2] Generation de la reponse...
    echo.
    echo Command:
    echo   ambulon piag-chat-query \
    echo     --question "Explique le modele C4 applique a SIREINES..." \
    echo     --chunks "%CHUNKS_DIR%\c4model_chunks.json" \
    echo     --output "%RESPONSE_DIR%\c4model_reponse.md"
    echo.

    ambulon piag-chat-query --question "Explique le modele C4 applique a SIREINES. Quels sont les 4 niveaux et que representent-ils ?" --chunks "%CHUNKS_DIR%\c4model_chunks.json" --output "%RESPONSE_DIR%\c4model_reponse.md"

    if %errorlevel% equ 0 (echo [OK] Reponse generee) else (echo [ERREUR] Echec)
) else (
    echo [ERREUR] Echec recherche
)
echo.
pause

REM Question 3 : Alertes
echo.
echo ================================================================================
echo QUESTION 3/5: Module gestion alertes
echo ================================================================================
echo [1/2] Recherche des chunks...
echo.
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "module alertes fonctionnalites workflow" \
echo     --top-k 7 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "module alertes fonctionnalites workflow" --top-k 7 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\alertes_chunks.json" 2>&1

if %errorlevel% equ 0 (
    echo [OK] Chunks trouves
    echo.
    echo [2/2] Generation de la reponse...
    echo.
    echo Command:
    echo   ambulon piag-chat-query \
    echo     --question "Comment fonctionne le module de gestion des alertes..." \
    echo     --chunks "%CHUNKS_DIR%\alertes_chunks.json" \
    echo     --output "%RESPONSE_DIR%\alertes_reponse.md"
    echo.

    ambulon piag-chat-query --question "Comment fonctionne le module de gestion des alertes dans SIREINES ? Quelles sont ses fonctionnalites principales ?" --chunks "%CHUNKS_DIR%\alertes_chunks.json" --output "%RESPONSE_DIR%\alertes_reponse.md"

    if %errorlevel% equ 0 (echo [OK] Reponse generee) else (echo [ERREUR] Echec)
) else (
    echo [ERREUR] Echec recherche
)
echo.
pause

REM Question 4 : ISO 25010
echo.
echo ================================================================================
echo QUESTION 4/5: Exigences ISO 25010
echo ================================================================================
echo [1/2] Recherche des chunks...
echo.
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "ISO 25010 qualite performance securite" \
echo     --top-k 7 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "ISO 25010 qualite performance securite" --top-k 7 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\iso25010_chunks.json" 2>&1

if %errorlevel% equ 0 (
    echo [OK] Chunks trouves
    echo.
    echo [2/2] Generation de la reponse...
    echo.
    echo Command:
    echo   ambulon piag-chat-query \
    echo     --question "Quelles sont les exigences ISO 25010 pour SIREINES..." \
    echo     --chunks "%CHUNKS_DIR%\iso25010_chunks.json" \
    echo     --output "%RESPONSE_DIR%\iso25010_reponse.md"
    echo.

    ambulon piag-chat-query --question "Quelles sont les exigences de qualite ISO 25010 definies pour SIREINES ?" --chunks "%CHUNKS_DIR%\iso25010_chunks.json" --output "%RESPONSE_DIR%\iso25010_reponse.md"

    if %errorlevel% equ 0 (echo [OK] Reponse generee) else (echo [ERREUR] Echec)
) else (
    echo [ERREUR] Echec recherche
)
echo.
pause

REM Question 5 : Securite
echo.
echo ================================================================================
echo QUESTION 5/5: Securite et authentification
echo ================================================================================
echo [1/2] Recherche des chunks...
echo.
echo Command:
echo   ambulon piag-rag-search \
echo     --collection-name "%COLLECTION_NAME%" \
echo     --query "securite authentification autorisation RBAC" \
echo     --top-k 7 \
echo     --mode hybrid \
echo     --rerank true \
echo     --json
echo.

ambulon piag-rag-search --collection-name "%COLLECTION_NAME%" --query "securite authentification autorisation RBAC" --top-k 7 --mode hybrid --rerank --format json > "%CHUNKS_DIR%\securite_chunks.json" 2>&1

if %errorlevel% equ 0 (
    echo [OK] Chunks trouves
    echo.
    echo [2/2] Generation de la reponse...
    echo.
    echo Command:
    echo   ambulon piag-chat-query \
    echo     --question "Comment est implementee la securite dans SIREINES..." \
    echo     --chunks "%CHUNKS_DIR%\securite_chunks.json" \
    echo     --output "%RESPONSE_DIR%\securite_reponse.md"
    echo.

    ambulon piag-chat-query --question "Comment est implementee la securite dans SIREINES ? Decris les mecanismes d'authentification et d'autorisation." --chunks "%CHUNKS_DIR%\securite_chunks.json" --output "%RESPONSE_DIR%\securite_reponse.md"

    if %errorlevel% equ 0 (echo [OK] Reponse generee) else (echo [ERREUR] Echec)
) else (
    echo [ERREUR] Echec recherche
)
echo.
pause

REM ============================================================================
REM RESUME FINAL
REM ============================================================================
echo.
echo ================================================================================
echo  RESUME FINAL
echo ================================================================================
echo.
echo [OK] Script execute avec succes !
echo.
echo Collection : %COLLECTION_NAME%
echo Documents sources : %TOTAL_COUNT%
echo Recherches : 5
echo Questions techniques : 5
echo.
echo Fichiers generes :
echo.
echo   Repertoire CHUNKS : %CHUNKS_DIR%\
echo   - 5 fichiers search_*.json (resultats recherche)
echo   - 5 fichiers *_chunks.json (chunks trouves)
echo.
echo   Repertoire REPONSES : %RESPONSE_DIR%\
echo   - 5 fichiers *_reponse.md (reponses generees)
echo   - 1 fichier test_execution.log (log)
echo.
echo Consultez les reponses :
echo   type %RESPONSE_DIR%\architecture_reponse.md
echo   type %RESPONSE_DIR%\c4model_reponse.md
echo   type %RESPONSE_DIR%\alertes_reponse.md
echo   type %RESPONSE_DIR%\iso25010_reponse.md
echo   type %RESPONSE_DIR%\securite_reponse.md
echo.
echo Consultez les chunks :
echo   type %CHUNKS_DIR%\architecture_chunks.json
echo   type %CHUNKS_DIR%\search_1.json
echo.
echo ================================================================================
echo.
pause
