@echo off
echo ==========================================
echo ANALYSE DES BRANCHES POUR MERGE
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1] Statut de main:
echo ------------------------------------------
git status --short
echo.

echo [2] Branches locales:
echo ------------------------------------------
git branch -vv
echo.

echo [3] Branches distantes (non mergees dans main):
echo ------------------------------------------
git branch -r --no-merged main 2>nul || echo Toutes les branches distantes sont mergees ou pas de main
echo.

echo [4] Derniers commits de chaque branche locale:
echo ------------------------------------------
for /f "tokens=*" %%b in ('git branch --format="%%(refname:short)"') do (
    echo.
    echo === %%b ===
    git log -1 --oneline %%b
)
echo.

echo [5] Branches qui contiennent des modifs recentes (30 jours):
echo ------------------------------------------
git for-each-ref --sort=-committerdate --format="%%(refname:short) %%(committerdate:short)" refs/heads/ | findstr /v "main\|master"
echo.

echo ==========================================
echo DECISION:
echo ==========================================
echo Liste des branches a merger:
echo.
pause
