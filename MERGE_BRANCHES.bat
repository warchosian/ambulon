@echo off
echo ==========================================
echo MERGE DES BRANCHES AVANT RELEASE 3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/5] Branches existantes:
echo ------------------------------------------
git branch -a | findstr /v "HEAD\|origin/HEAD"
echo.

echo [2/5] Branches locales:
echo ------------------------------------------
git branch
echo.

echo [3/5] Branches distantes (origin):
echo ------------------------------------------
git branch -r
echo.

echo [4/5] Verifier si on est sur main/master:
echo ------------------------------------------
git branch --show-current
echo.

echo [5/5] Pour merger une branche:
echo ------------------------------------------
echo Si vous voulez merger une branche 'feature-xxx' dans main:
echo.
echo   git checkout main
echo   git merge feature-xxx
echo   git branch -d feature-xxx  (supprimer la branche locale)
echo.
echo Branches a merger? Listez-les ici:
echo.
pause
