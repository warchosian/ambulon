@echo off
chcp 65001 >nul
echo ==========================================
echo Separation des versions gitlab-clone et gitlab-load
echo ==========================================
echo.

echo [1/8] Recuperation gitlab_clone.py depuis main...
git show main:src/app/gitlab/commands/gitlab_clone.py > gitlab_clone_main.py
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de recuperer gitlab_clone.py de main
    pause
    exit /b 1
)
echo OK
echo.

echo [2/8] Recuperation monofile.py depuis main...
git show main:src/app/gitlab/core/monofile.py > monofile_main.py
if %errorlevel% neq 0 (
    echo ERREUR: Impossible de recuperer monofile.py de main
    pause
    exit /b 1
)
echo OK
echo.

echo [3/8] Sauvegarde version actuelle vers gitlab_load.py...
copy /Y src\app\gitlab\commands\gitlab_clone.py src\app\gitlab\commands\gitlab_load.py
echo OK
echo.

echo [4/8] Sauvegarde monofile actuel vers monofile_load.py...
copy /Y src\app\gitlab\core\monofile.py src\app\gitlab\core\monofile_load.py
echo OK
echo.

echo [5/8] Mise a jour des imports dans gitlab_load.py...
powershell -Command "(Get-Content src\app\gitlab\commands\gitlab_load.py) -replace 'from app.gitlab.core.monofile import', 'from app.gitlab.core.monofile_load import' -replace \"command=\"\"gitlab-clone\"\"\", \"command=\"\"gitlab-load\"\"\" | Set-Content src\app\gitlab\commands\gitlab_load.py"
echo OK
echo.

echo [6/8] Restauration gitlab_clone.py depuis main...
copy /Y gitlab_clone_main.py src\app\gitlab\commands\gitlab_clone.py
del gitlab_clone_main.py
echo OK
echo.

echo [7/8] Restauration monofile.py depuis main...
copy /Y monofile_main.py src\app\gitlab\core\monofile.py
del monofile_main.py
echo OK
echo.

echo [8/8] Verification des fichiers...
echo.
echo Fichiers commandes:
dir src\app\gitlab\commands\gitlab_*.py /b
echo.
echo Fichiers core:
dir src\app\gitlab\core\monofile*.py /b
echo.

echo ==========================================
echo Resume:
echo ==========================================
echo gitlab-clone  : utilise monofile.py (md2html-diagrams)
echo gitlab-load   : utilise monofile_load.py (md2interactive)
echo.
pause
