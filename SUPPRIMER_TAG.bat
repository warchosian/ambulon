@echo off
echo ==========================================
echo SUPPRESSION DU TAG 1.0.1
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1] Liste des tags existants:
echo ------------------------------------------
git tag
echo.

echo [2] Suppression du tag LOCAL 1.0.1...
git tag -d 1.0.1
echo.

echo [3] Suppression du tag DISTANT 1.0.1 (origin)...
git push origin --delete 1.0.1 2>nul || echo Tag distant 1.0.1 n'existe pas ou deja supprime
echo.

echo [4] Verification:
echo ------------------------------------------
echo Tags restants:
git tag | findstr /v "^$"
echo.

echo ==========================================
echo TAG 1.0.1 SUPPRIME!
echo ==========================================
echo.
pause
