@echo off
chcp 65001 >nul
echo ==========================================
echo Configuration du token PIAG Chat
echo ==========================================
echo.

echo [1/2] Creation du fichier config/piag.yaml avec le token...

if not exist "config" mkdir config

echo # Configuration PIAG generee automatiquement > config\piag.yaml
echo # NE PAS COMMIT CE FICHIER >> config\piag.yaml
echo. >> config\piag.yaml
echo piag: >> config\piag.yaml
echo   chat_api_url: "https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions" >> config\piag.yaml
echo   chat_token: "sk-iyksvRDQanhNZ6O7MJCQbA" >> config\piag.yaml
echo   model: "mte-api-piag-mistral-medium-latest" >> config\piag.yaml
echo   timeout: 60 >> config\piag.yaml
echo. >> config\piag.yaml
echo rag: >> config\piag.yaml
echo   api_url: "https://rag.api.piag.e2.rie.gouv.fr/v1" >> config\piag.yaml
echo   token: "" >> config\piag.yaml
echo   default_collection: "documents" >> config\piag.yaml

echo OK - Fichier config/piag.yaml cree
echo.

echo [2/2] Verification...
findstr /C:"chat_token" config\piag.yaml >nul && echo OK - chat_token present || echo ERREUR
echo.

echo ==========================================
echo Token configure !
echo ==========================================
echo.
echo Vous pouvez maintenant utiliser:
echo   ambulon piag-chat-basic-query --question "Bonjour"
echo   ambulon piag-chat-query --question "Question" --doc-id 123 --collection-id 456
echo.
echo ATTENTION: config/piag.yaml contient un secret.
echo Ne pas commiter ce fichier !
echo.
pause
