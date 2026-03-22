@echo off
chcp 65001 >nul
echo ==========================================
echo Test du workflow RAG mis a jour
echo ==========================================
echo.

echo [1] Aide du workflow simple:
call rag_workflow.bat --help 2>&1 | head -20
echo.

echo [2] Aide du workflow avance:
call rag_advanced.bat 2>&1 | head -25
echo.

echo [3] Exemples de commandes avec nom:
echo.
echo   Recherche par NOM:
echo   ambulon piag-search --collection-name "Docs Tech" --query "Test"
echo.
echo   Recuperation par NOM:
echo   ambulon piag-doc-chunks --document-name "fichier.pdf" --collection-name "Docs"
echo.
echo [4] Limitation de piag-chat-query:
echo   Cette commande ne supporte que les IDs (--doc-id, --collection-id)
echo   Pour utiliser des noms: d'abord piag-doc-chunks (nom) puis piag-chat-query --chunks
echo.

echo ==========================================
pause
