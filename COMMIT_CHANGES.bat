@echo off
echo ==========================================
echo COMMIT DES CHANGEMENTS EN COURS
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1] Status des changements:
echo ------------------------------------------
git status --short
echo.

echo [2] Ignorer les sous-depots gitlab...
git rm --cached -r gitlab/ 2>nul
echo OK
echo.

echo [3] Ajouter les fichiers sources (sans gitlab/)...
git add src/ tests/ tools/ pyproject.toml .cz.toml README.md AGENTS.md
git add .gitignore 2>nul
echo OK
echo.

echo [4] Commit des changements:
echo ------------------------------------------
git commit -m "chore: prepare release v3.1.0 - update version and clean"
echo OK
echo.

echo [5] Verification:
echo ------------------------------------------
git status
git log -1 --oneline
echo.

echo ==========================================
echo CHANGEMENTS COMMITES!
echo ==========================================
echo.
echo Vous pouvez maintenant:
echo   git checkout main
echo   git merge ...
echo.
pause
