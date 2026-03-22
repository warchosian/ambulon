@echo off
chcp 65001 >nul
echo ==========================================
echo 1. Sauvegarde version actuelle (gitlab_load)
echo 2. Restauration version main (gitlab_clone)
echo ==========================================
echo.

echo [1/4] Recuperation de la version main...
git show main:src/app/gitlab/commands/gitlab_clone.py > gitlab_clone_main.py
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de recuperer la version de main
    pause
    exit /b 1
)
echo OK - Version main sauvegardee temporairement
echo.

echo [2/4] Copie de la version actuelle vers gitlab_load.py...
copy /Y src\app\gitlab\commands\gitlab_clone.py src\app\gitlab\commands\gitlab_load.py
echo OK
echo.

echo [3/4] Mise a jour de gitlab_load.py (changement du nom)...
powershell -Command "(Get-Content src\app\gitlab\commands\gitlab_load.py) -replace 'gitlab-clone', 'gitlab-load' -replace 'gitlab_clone', 'gitlab_load' | Set-Content src\app\gitlab\commands\gitlab_load.py"
echo OK
echo.

echo [4/4] Restauration de gitlab_clone.py depuis main...
copy /Y gitlab_clone_main.py src\app\gitlab\commands\gitlab_clone.py
del gitlab_clone_main.py
echo OK
echo.

echo ==========================================
echo Operation terminee !
echo ==========================================
echo.
echo Fichiers:
dir src\app\gitlab\commands\gitlab_*.py /b
echo.
pause
