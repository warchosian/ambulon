@echo off
echo ==========================================
echo IGNORER LES SOUS-DEPOTS GITLAB
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1] Retirer gitlab/ de l'index git (sans supprimer les fichiers)...
git rm --cached -r gitlab/ 2>nul
echo OK
echo.

echo [2] Ajouter gitlab/ au .gitignore...
echo. >> .gitignore
echo # Sous-depots gitlab >> .gitignore
echo gitlab/ >> .gitignore
echo OK
echo.

echo [3] Commit du .gitignore...
git add .gitignore
git commit -m "chore: ignore les sous-depots gitlab/"
echo OK
echo.

echo ==========================================
echo LES SOUS-DEPOTS SONT IGNORES
echo ==========================================
echo.
echo gitlab/primesauto et gitlab/sireines.wiki
echo ne seront plus ajoutes au commit.
echo.
echo Vous pouvez maintenant faire:
echo   git add . (sans warnings)
echo.
pause
