@echo off
REM Workflow RAG Pipeline - Exemple d'utilisation
REM Usage: ambulon piag-rag-pipeline run --source <dir> --prompt <file> [options]

echo === Workflow RAG Pipeline ===
echo.

REM Pipeline complet en une seule commande
ambulon piag-rag-pipeline run ^
  --source applications/sireines.rag ^
  --prompt .claude/prompts/prompt.dat_c4model.md ^
  --query "Architecture, DAT" ^
  --top-k 10 ^
  --wait-index 60 ^
  --timeout-search 10s ^
  --timeout-generate 20m ^
  --max-retries 5 ^
  --force

echo.
echo === Pipeline termine ===
pause
