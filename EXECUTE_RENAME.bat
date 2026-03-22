@echo off
chcp 65001 >nul
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo Renommage des fichiers dans .claude/prompts...

python tooling-mcp-like/rename_files.py .claude/prompts "_prompt_" "prompt."

echo.
echo Appuyez sur une touche pour quitter...
pause >nul
