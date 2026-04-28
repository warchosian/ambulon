@echo off
:: ==========================================
:: 🦙 lance-claude-ollama.bat
:: Lance Claude Code avec un modèle Ollama et un timeout étendu
:: Compatible Windows CMD / DOS
:: ==========================================

:: ──────────────────────────────────────────
:: Configuration par défaut
:: ──────────────────────────────────────────
set "MODEL=glm-4.7-flash"
set "TIMEOUT=180"

:: ──────────────────────────────────────────
:: Support des arguments en ligne de commande
:: Usage: lance-claude-ollama.bat [modele] [timeout]
:: Ex:    lance-claude-ollama.bat qwen2.5-coder:7b 120
:: ──────────────────────────────────────────
if "%~1" neq "" set "MODEL=%~1"
if "%~2" neq "" set "TIMEOUT=%~2"

echo ==========================================
echo 🚀 Lancement de Claude Code
echo 📦 Modèle : %MODEL%
echo ⏱️ Timeout : %TIMEOUT% secondes
echo ==========================================

:: ──────────────────────────────────────────
:: Vérification qu'Ollama est actif
:: ──────────────────────────────────────────
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe" >NUL
if errorlevel 1 (
    echo ⚠️ Ollama n'est pas détecté.
    echo 💡 Lancez Ollama avant d'exécuter ce script.
    pause
    exit /b 1
)
echo ✅ Ollama est actif.

:: ──────────────────────────────────────────
:: Application du timeout (session courante)
:: ──────────────────────────────────────────
set "CLAUDE_CODE_TIMEOUT=%TIMEOUT%"
echo 🕒 CLAUDE_CODE_TIMEOUT défini à %TIMEOUT%s

:: ──────────────────────────────────────────
:: Lancement de Claude Code
:: ──────────────────────────────────────────
echo 🦙 Démarrage de Claude Code...
ollama launch claude --model %MODEL%

echo.
echo ✅ Session terminée.
timeout /t 2 /nobreak >NUL