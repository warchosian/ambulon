@echo off
chcp 65001 >nul
echo ==========================================
echo Renommage: make-html-interactive -> add-augment
echo ==========================================
echo.

REM 1. Creer add_augment.py comme copie de make_html_interactive.py
echo [1/4] Creation de add_augment.py...
copy /Y src\app\processing\commands\make_html_interactive.py src\app\processing\commands\add_augment.py >nul

REM Modifier le nom de la fonction et les references dans add_augment.py
powershell -Command "(Get-Content src\app\processing\commands\add_augment.py) -replace 'make.html.interactive', 'add-augment' -replace 'make_html_interactive', 'add_augment' -replace '-interactive.html', '-augmented.html' | Set-Content src\app\processing\commands\add_augment.py"
echo OK
echo.

REM 2. Mettre a jour md_to_interactive_html.py
echo [2/4] Mise a jour de md_to_interactive_html.py...
powershell -Command "(Get-Content src\app\processing\commands\md_to_interactive_html.py) -replace 'from .make_html_interactive import make_html_interactive', 'from .add_augment import add_augment' -replace 'make_html_interactive\(', 'add_augment(' -replace '-interactive.html', '-augmented.html' | Set-Content src\app\processing\commands\md_to_interactive_html.py"
echo OK
echo.

REM 3. Mettre a jour cli.py si necessaire
echo [3/4] Verification de cli.py...
findstr /C:"make-html-interactive" src\app\cli\cli.py >nul
if %errorlevel% == 0 (
    echo Mise a jour de cli.py...
    powershell -Command "(Get-Content src\app\cli\cli.py) -replace 'make-html-interactive', 'add-augment' -replace 'make_html_interactive', 'add_augment' | Set-Content src\app\cli\cli.py"
) else (
    echo cli.py ne contient pas make-html-interactive
)
echo OK
echo.

REM 4. Mettre a jour monofile_load.py
echo [4/4] Mise a jour de monofile_load.py...
powershell -Command "(Get-Content src\app\gitlab\core\monofile_load.py) -replace '-interactive.html', '-augmented.html' | Set-Content src\app\gitlab\core\monofile_load.py"
echo OK
echo.

echo ==========================================
echo Resume des changements:
echo ==========================================
echo - make-html-interactive -> add-augment
echo - Fichier genere: -augmented.html (au lieu de -interactive.html)
echo.
dir src\app\processing\commands\add_augment.py /b
echo.
pause
