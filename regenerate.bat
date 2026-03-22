@echo off
cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Regeneration avec les corrections ===
echo.

python tools\clear_pycache.py

echo [1/3] add-toc4md...
python -B -m app.toc.commands.add_toc4md applications\sireines.rag\sireines.dat.md -o applications\sireines.rag\sireines.dat-toced.md --min-level 2
echo.

echo [2/3] add-itoc4md...
python -B -m app.toc.commands.add_itoc4md applications\sireines.rag\sireines.dat-toced.md -o applications\sireines.rag\sireines.dat-itoced.md --min-level 2
echo.

echo [3/3] md2html-diagrams...
python -B -m app.diagrams.commands.md2html applications\sireines.rag\sireines.dat-itoced.md -o applications\sireines.rag\sireines.dat-itoced.html
echo.

echo === Termine ===
echo Verifiez: applications\sireines.rag\sireines.dat-itoced.html
pause
