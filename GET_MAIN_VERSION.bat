@echo off
chcp 65001 >nul
git show main:src/app/gitlab/commands/gitlab_clone.py > gitlab_clone_main.py
echo Version de main sauvegardee dans gitlab_clone_main.py
pause
