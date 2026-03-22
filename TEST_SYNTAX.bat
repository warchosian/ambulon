@echo off
chcp 65001 >nul
echo Test de syntaxe de monofile.py...
python -m py_compile src/app/gitlab/core/monofile.py
if %errorlevel% == 0 (
    echo Syntaxe OK !
) else (
    echo ERREUR de syntaxe !
)
pause
