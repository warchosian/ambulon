@echo off
REM ============================================================================
REM DIAGNOSTIC DE L'ENVIRONNEMENT PYTHON
REM ============================================================================
REM Ce script diagnostique le probleme "No pyvenv.cfg file"
REM ============================================================================

echo ================================================================================
echo DIAGNOSTIC DE L'ENVIRONNEMENT PYTHON
echo ================================================================================
echo.

echo [1] Verification de l'environnement conda...
echo ------------------------------------------------------------
if defined CONDA_PREFIX (
    echo [OK] CONDA_PREFIX = %CONDA_PREFIX%
    set PYTHON_PATH=%CONDA_PREFIX%\python.exe
) else (
    echo [WARNING] CONDA_PREFIX n'est pas defini
    echo Tentative de detection de Python dans PATH...
    where python.exe
    set PYTHON_PATH=python.exe
)
echo.

echo [2] Test de l'executable Python...
echo ------------------------------------------------------------
if exist "%PYTHON_PATH%" (
    echo [OK] Python trouve: %PYTHON_PATH%
    "%PYTHON_PATH%" --version
) else (
    echo [ERROR] Python introuvable a: %PYTHON_PATH%
    echo.
    echo SOLUTION: Ouvrez un nouveau terminal et lancez:
    echo   conda activate ambulon
    echo   puis relancez ce script
    pause
    exit /b 1
)
echo.

echo [3] Test des imports Python...
echo ------------------------------------------------------------
"%PYTHON_PATH%" -c "import sys; print('Python executable:', sys.executable)" 2>&1
"%PYTHON_PATH%" -c "import sys; print('Python version:', sys.version)" 2>&1
"%PYTHON_PATH%" -c "import sys; print('Python path:', sys.path[:3])" 2>&1
echo.

echo [4] Verification des modules requis...
echo ------------------------------------------------------------
"%PYTHON_PATH%" -c "import yaml; print('[OK] PyYAML version:', yaml.__version__)" 2>&1 || echo [ERROR] PyYAML non disponible
"%PYTHON_PATH%" -c "import requests; print('[OK] Requests version:', requests.__version__)" 2>&1 || echo [ERROR] Requests non disponible
"%PYTHON_PATH%" -c "import app; print('[OK] Ambulon importe')" 2>&1 || echo [ERROR] Ambulon non disponible
echo.

echo [5] Test d'execution du script de test...
echo ------------------------------------------------------------
echo Tentative de lancement de test_piag_all.py...
"%PYTHON_PATH%" test_piag_all.py --help 2>&1
set TEST_RESULT=%ERRORLEVEL%
echo.

echo ================================================================================
echo RESULTAT DU DIAGNOSTIC
echo ================================================================================
echo.

if %TEST_RESULT% EQU 0 (
    echo [32m[SUCCESS] Python fonctionne correctement ![0m
    echo.
    echo Vous pouvez lancer les tests avec:
    echo   "%PYTHON_PATH%" test_piag_all.py --config config\piag.yaml
) else (
    echo [31m[ERROR] Probleme detecte (code: %TEST_RESULT%)[0m
    echo.
    echo SOLUTIONS POSSIBLES:
    echo.
    echo 1. N'utilisez PAS Git Bash, utilisez CMD ou PowerShell Windows natif
    echo.
    echo 2. Reactivez l'environnement conda:
    echo    conda deactivate
    echo    conda activate ambulon
    echo.
    echo 3. Reinstallez les dependances:
    echo    pip install -r requirements_tests_e2e.txt
    echo.
    echo 4. Utilisez le chemin complet de Python:
    echo    %CONDA_PREFIX%\python.exe test_piag_all.py
)

echo.
echo ================================================================================
pause
