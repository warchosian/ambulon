@echo off
chcp 65001 >nul
echo Annulation du merge en cours...
git merge --abort
echo.
echo État git après annulation :
git status
pause
