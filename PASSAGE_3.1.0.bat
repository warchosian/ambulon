@echo off
echo ==========================================
echo PASSAGE A LA VERSION 3.1.0
echo ==========================================
echo.

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo [1/6] Mise a jour de src\app\__init__.py...
powershell -Command "(Get-Content src\app\__init__.py) -replace '__version__ = .*', '__version__ = \"3.1.0\"' | Set-Content src\app\__init__.py"
echo OK - Version: 3.1.0
echo.

echo [2/6] Mise a jour de pyproject.toml...
powershell -Command "(Get-Content pyproject.toml) -replace '^version = .*', 'version = \"3.1.0\"' | Set-Content pyproject.toml"
echo OK
echo.

echo [3/6] Git - Retirer les sous-modules...
git rm --cached gitlab/primesauto 2>nul
git rm --cached gitlab/sireines.wiki 2>nul
git rm --cached gitlab\primesauto 2>nul
git rm --cached gitlab\sireines.wiki 2>nul
echo OK
echo.

echo [4/6] Git - Add, Commit, Tag...
git add src\app\__init__.py pyproject.toml
git add src\ app\ tests\ tools\ -A 2>nul
git commit -m "feat: release v3.1.0 - modules TOC et diagrams"
git tag -a v3.1.0 -m "Release v3.1.0"
echo OK
echo.

echo [5/6] Build du wheel avec Python...
if exist dist rmdir /s /q dist
mkdir dist
python setup.py bdist_wheel 2>nul || python -m pip wheel . -w dist
echo OK
echo.

echo [6/6] Verification...
echo Version dans __init__.py:
findstr "__version__" src\app\__init__.py
echo.
echo Tag git:
git describe --tags
echo.
echo Wheel:
dir /b dist\*.whl 2>nul || echo Pas de wheel genere
echo.
echo ==========================================
echo POUR PUBLIER:
echo   git push origin main
echo   git push origin v3.1.0
echo ==========================================
pause
