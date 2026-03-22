@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Verification ===

echo 1. Nombre de 'Table des matieres' dans test_itoced.html:
find /c "Table des matières" test_itoced.html 2>nul || echo Fichier non trouve

echo.
echo 2. Nombre de <nav class="table-of-contents":
findstr /c:"<nav class=" test_itoced.html 2>nul | find /c "table-of-contents" || echo 0

echo.
echo 3. Premier <nav:
findstr /n "<nav class=" test_itoced.html 2>nul | head -1

echo.
pause
