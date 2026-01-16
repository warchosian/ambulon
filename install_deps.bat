@echo off
echo Installation des dependances pour Ambulon MCP
echo =============================================
echo.

REM Activer environnement ambulon
call conda activate ambulon

REM Installer les dépendances essentielles
echo [1/2] Installation des packages Python...
pip install typer pyyaml requests beautifulsoup4 lxml markdown python-slugify

REM Installer le SDK MCP (optionnel pour le serveur, obligatoire pour le client)
echo [2/2] Installation du SDK MCP...
pip install mcp

echo.
echo Installation terminee !
echo.
echo Pour demarrer le serveur MCP:
echo   python -m app.mcp.commands.run_server
echo.
pause
