@echo off
REM -*- coding: utf-8 -*-
REM Workflow complet RAG SIREINES en 5 commandes (Windows)
REM Usage: workflow_rag_sireines_5cmd.bat

chcp 65001 >nul 2>&1

echo ========================================
echo   WORKFLOW RAG SIREINES - 5 COMMANDES
echo ========================================
echo.
echo Date: %date% %time%
echo.

REM 0. Lister les collections existantes
echo 0/5 - Liste des collections existantes...
echo ----------------------------------------
ambulon piag-rag-collection-list
echo.
echo Appuyez sur une touche pour continuer...
pause >nul
echo.

REM 1. Supprimer l'ancienne collection
echo 1/5 - Suppression collection PNM3_SIREINES...
echo ----------------------------------------------
ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES 2>nul
if %errorlevel%==0 (
    echo Collection supprimee avec succes
) else (
    echo Collection n'existait pas ^(OK^)
)
echo.

REM 2. Recréer la collection avec documents
echo 2/5 - Creation collection + upload documents...
echo ------------------------------------------------
ambulon piag-rag-create ^
  --collection-name PNM3_SIREINES ^
  --description "Documentation complete SIREINES : DAT, C4, Composants, Wiki" ^
  --directory applications/sireines.rag ^
  --extensions md,pdf
echo.

REM Attendre indexation
echo Attente indexation ^(60 secondes^)...
timeout /t 60 /nobreak
echo.

REM 3. Créer les chunks sur "Architecture, DAT"
echo 3/5 - Creation chunks Architecture/DAT ^(timeout 10s^)...
echo -----------------------------------------------------------
if not exist chunks mkdir chunks
ambulon piag-rag-search ^
  --collection-name PNM3_SIREINES ^
  --query "Architecture, DAT" ^
  --top-k 10 ^
  --timeout 10s ^
  -o chunks/chunk_PNM3_SIREINES.json
echo.

REM 4. Générer la réponse CHAT
echo 4/5 - Generation reponse CHAT ^(timeout 20m, max 5 retries, delai 1m^)...
echo -------------------------------------------------------------------------
if not exist reponses mkdir reponses
ambulon piag-chat-query ^
  --question-file .claude/prompts/_prompt_dat_c4model.md ^
  --chunks chunks/chunk_PNM3_SIREINES.json ^
  --timeout 20m ^
  --max-retries 5 ^
  --retry-delay 1m ^
  -o reponses/reponse_dat_c4model.md
echo.

REM 5. Vérification finale
echo 5/5 - Verification finale...
echo -----------------------------
echo Collections apres workflow:
ambulon piag-rag-collection-list | findstr PNM3_SIREINES
echo.

echo ========================================
echo   WORKFLOW TERMINE AVEC SUCCES
echo ========================================
echo.
echo Fichiers generes:
echo   - chunks/chunk_PNM3_SIREINES.json
echo   - reponses/reponse_dat_c4model.md
echo.
echo Pour lire la reponse:
echo   type reponses\reponse_dat_c4model.md
echo.
echo Appuyez sur une touche pour quitter...
pause >nul
