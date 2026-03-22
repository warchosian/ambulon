@echo off
chcp 65001 >nul
echo ==========================================
echo Test de 'ambulon augment'
echo ==========================================
echo.

echo Test de l'aide...
ambulon augment --help 2>&1
echo.

echo Test avec un fichier HTML simple...
echo ^<!DOCTYPE html^> > test_input.html
echo ^<html^>^<head^>^<title^>Test^</title^>^</head^>^<body^> >> test_input.html
echo ^<h1^>Titre 1^</h1^>^<p^>Contenu^</p^> >> test_input.html
echo ^<h2^>Section A^</h2^>^<p^>Contenu A^</p^> >> test_input.html
echo ^</body^>^</html^> >> test_input.html

echo Execution de augment...
ambulon augment test_input.html -o test_output.html --verbose
echo.

echo Fichiers generes:
dir test_*.html /b
echo.

echo Nettoyage...
del test_*.html 2>nul
echo.

pause
