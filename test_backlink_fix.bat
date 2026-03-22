@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Test des backlinks corriges ===
echo.

python tools\clear_pycache.py

set SOURCE=applications\sireines.rag\sireines.dat.md
set STEP1=applications\sireines.rag\test_toced.md
set STEP2=applications\sireines.rag\test_itoced.md
set HTML=applications\sireines.rag\test_itoced.html

echo [1/4] add-toc4md...
python -B -m app.toc.commands.add_toc4md "%SOURCE%" -o "%STEP1%" --min-level 2
echo.

echo [2/4] add-itoc4md...
python -B -m app.toc.commands.add_itoc4md "%STEP1%" -o "%STEP2%" --min-level 2
echo.

echo [3/4] md2html-diagrams...
python -B -m app.diagrams.commands.md2html "%STEP2%" -o "%HTML%"
echo.

echo === Verification ===
echo.
echo 1. Ancres toc-xxx dans le HTML:
find /c "id=\"toc-" "%HTML%"
echo.
echo 2. Liens vers toc-xxx:
find /c "href=\"#toc-" "%HTML%"
echo.
echo 3. Exemple d'ancre dans la TOC:
grep -o "<a id=\"toc-[^\"]*\"" "%HTML%" | head -3
echo.
echo 4. Exemple de backlink dans un titre:
grep -o "<h[23][^>]*>.*\[↑\]([^)]*)" "%HTML%" | head -2
echo.

REM Nettoyage
del "%STEP1%" 2>nul
del "%STEP2%" 2>nul
del "%HTML%" 2>nul

echo === FIN ===
pause
