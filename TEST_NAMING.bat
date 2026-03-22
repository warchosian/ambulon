@echo off
chcp 65001 >nul
echo ==========================================
echo Test des nouveaux noms de fichiers
echo ==========================================
echo.

echo Creation d'un fichier test...
echo # Titre 1 > test_input.md
echo. >> test_input.md
echo ## Section A >> test_input.md
echo Contenu A >> test_input.md
echo. >> test_input.md
echo ## Section B >> test_input.md
echo Contenu B >> test_input.md
echo.

echo Execution de md2interactive...
python -m app.processing.commands.md_to_interactive_html test_input.md --verbose

echo.
echo Fichiers generes:
dir test_input* /b
echo.

echo Nettoyage...
del test_input*.md test_input*.html 2>nul
echo.

pause
