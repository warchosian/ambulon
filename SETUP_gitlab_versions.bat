@echo off
chcp 65001 >nul
echo ==========================================
echo Setup: gitlab-clone (simple) + gitlab-load (interactif)
echo ==========================================
echo.

echo [1/6] Recuperation versions main...
git show main:src/app/gitlab/commands/gitlab_clone.py > tmp_clone.py
git show main:src/app/gitlab/core/monofile.py > tmp_mono.py
echo OK
echo.

echo [2/6] Creation gitlab_load.py (version interactive)...
copy /Y src\app\gitlab\commands\gitlab_clone.py src\app\gitlab\commands\gitlab_load.py >nul
echo OK
echo.

echo [3/6] Creation monofile_load.py (version interactive)...
copy /Y src\app\gitlab\core\monofile.py src\app\gitlab\core\monofile_load.py >nul
echo OK
echo.

echo [4/6] Restauration gitlab_clone.py (version simple)...
copy /Y tmp_clone.py src\app\gitlab\commands\gitlab_clone.py >nul
del tmp_clone.py
echo OK
echo.

echo [5/6] Restauration monofile.py (version simple)...
copy /Y tmp_mono.py src\app\gitlab\core\monofile.py >nul
del tmp_mono.py
echo OK
echo.

echo [6/6] Mise a jour imports dans gitlab_load.py...
powershell -Command "(Get-Content src\app\gitlab\commands\gitlab_load.py) -replace 'from app.gitlab.core.monofile import', 'from app.gitlab.core.monofile_load import' | Set-Content src\app\gitlab\commands\gitlab_load.py"
echo OK
echo.

echo ==========================================
echo Resume:
echo ==========================================
echo gitlab-clone  : monofile.py    -^> HTML simple (md2html-diagrams)
echo gitlab-load   : monofile_load.py -^> HTML interactif (md2interactive)
echo.
dir src\app\gitlab\commands\gitlab_*.py /b
dir src\app\gitlab\core\monofile*.py /b
echo.
pause
