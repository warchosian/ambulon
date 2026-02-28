@echo off
REM Test complet du workflow add-toc4md -> add-itoc4md

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo === Test du workflow TOC ===
echo.

REM Nettoyer le cache
python tools\clear_pycache.py

REM Fichier de test
set SOURCE=applications\sireines.rag\sireines.dat.md
set STEP1=applications\sireines.rag\test_step1_toced.md
set STEP2=applications\sireines.rag\test_step2_itoced.md
set STEP3=applications\sireines.rag\test_step3_retoced.md
set STEP4=applications\sireines.rag\test_step4_reitoced.md

echo Fichier source: %SOURCE%
echo.

REM Étape 1: add-toc4md
echo === ETAPE 1: add-toc4md ===
python -B -m app.toc.commands.add_toc4md "%SOURCE%" -o "%STEP1%" --min-level 2
if errorlevel 1 (
    echo ERREUR à l'etape 1
    exit /b 1
)
echo.

REM Étape 2: add-itoc4md
echo === ETAPE 2: add-itoc4md ===
python -B -m app.toc.commands.add_itoc4md "%STEP1%" -o "%STEP2%" --min-level 2
if errorlevel 1 (
    echo ERREUR à l'etape 2
    exit /b 1
)
echo.

REM Étape 3: Re-add-toc4md (doit skipper)
echo === ETAPE 3: Re-add-toc4md (doit skipper) ===
python -B -m app.toc.commands.add_toc4md "%STEP2%" -o "%STEP3%" --min-level 2
echo.

REM Étape 4: Re-add-itoc4md (doit skipper)
echo === ETAPE 4: Re-add-itoc4md (doit skipper) ===
python -B -m app.toc.commands.add_itoc4md "%STEP2%" -o "%STEP4%" --min-level 2
echo.

REM Vérifications
echo === VERIFICATIONS ===
echo.

echo Nombre de '## Table des matières' dans %STEP2%:
find /c "## Table des matières" "%STEP2%"
echo.

echo Nombre de backlinks [↑](#toc- dans %STEP2%:
find /c "[↑](#toc-" "%STEP2%"
echo.

echo Premiere ligne de %STEP2%:
head -20 "%STEP2%"
echo.

echo === Nettoyage ===
del "%STEP1%" 2>nul
del "%STEP2%" 2>nul
del "%STEP3%" 2>nul
del "%STEP4%" 2>nul

echo === FIN ===
pause
