@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Test du workflow corrigé ===
echo.

python tools\clear_pycache.py

set SOURCE=applications\sireines.rag\sireines.dat.md
set STEP1=applications\sireines.rag\test_toced.md
set STEP2=applications\sireines.rag\test_itoced.md

echo [1/3] add-toc4md...
python -B -m app.toc.commands.add_toc4md "%SOURCE%" -o "%STEP1%" --min-level 2 -v
echo.

echo [2/3] Verification TOC dans step1...
findstr /n "Table des matières" "%STEP1%" | head -3
echo.

echo [3/3] add-itoc4md...
python -B -m app.toc.commands.add_itoc4md "%STEP1%" -o "%STEP2%" --min-level 2 -v
echo.

echo === Verification finale ===
echo Fichier: %STEP2%
echo.
echo Nombre de 'Table des matières':
find /c "## Table des matières" "%STEP2%"
echo.
echo Nombre de backlinks:
find /c "[↑](#toc-" "%STEP2%"
echo.
echo Premiere ligne avec Table des matières:
grep -n "Table des matières" "%STEP2%" | head -1
echo.
echo Exemple de backlink:
grep -n "\[↑\](#toc-" "%STEP2%" | head -2

del "%STEP1%" 2>nul
del "%STEP2%" 2>nul

pause
