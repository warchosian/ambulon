@echo off
chcp 65001 >nul
cd /d G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
set PYTHONPATH=src
python debug_gitlab_full.py
pause
