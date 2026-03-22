@echo off
chcp 65001 >nul
echo Diagnostic du fichier YAML...
python diagnose_yaml.py
pause
