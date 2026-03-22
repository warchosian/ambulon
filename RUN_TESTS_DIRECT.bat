@echo off
REM ============================================================================
REM LANCEMENT DIRECT DES TESTS E2E PIAG
REM ============================================================================
REM Ce script contourne le probleme "No pyvenv.cfg file" en utilisant
REM directement l'executable Python de l'environnement conda
REM ============================================================================

echo ================================================================================
echo TESTS END-TO-END - API PIAG (RAG + CHAT)
echo ================================================================================
echo.

REM Trouver le chemin de Python dans l'environnement conda actif
set PYTHON_EXE=python.exe

REM Si CONDA_PREFIX est defini, utiliser ce Python
if defined CONDA_PREFIX (
    set PYTHON_EXE=%CONDA_PREFIX%\python.exe
    echo Environnement conda detecte: %CONDA_PREFIX%
    echo Utilisation de Python: %PYTHON_EXE%
) else (
    echo ATTENTION: Variable CONDA_PREFIX non definie
    echo Assurez-vous que conda est active: conda activate ambulon
    echo Utilisation de Python par defaut du PATH
)

echo.
echo ================================================================================
echo VERIFICATION DE L'ENVIRONNEMENT
echo ================================================================================
echo.

REM Verifier que Python fonctionne
"%PYTHON_EXE%" --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Python n'est pas accessible
    echo Veuillez activer l'environnement: conda activate ambulon
    pause
    exit /b 1
)

echo Python OK
echo.

REM Verifier les dependances
echo Verification des dependances...
"%PYTHON_EXE%" -c "import yaml; import requests; print('PyYAML:', yaml.__version__); print('Requests:', requests.__version__)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Dependances manquantes
    echo Installation des dependances...
    "%PYTHON_EXE%" -m pip install -r requirements_tests_e2e.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERREUR: Impossible d'installer les dependances
        pause
        exit /b 1
    )
)

echo Dependances OK
echo.

REM Demander quel test lancer
echo ================================================================================
echo SELECTION DU TEST
echo ================================================================================
echo.
echo Quel test voulez-vous lancer ?
echo.
echo   1. Tous les tests (RAG + CHAT)
echo   2. Test RAG uniquement
echo   3. Test CHAT uniquement
echo   4. Quitter
echo.
set /p CHOICE="Votre choix (1-4) : "

if "%CHOICE%"=="1" goto RUN_ALL
if "%CHOICE%"=="2" goto RUN_RAG
if "%CHOICE%"=="3" goto RUN_CHAT
if "%CHOICE%"=="4" goto END
echo Choix invalide
goto END

:RUN_ALL
echo.
echo ================================================================================
echo LANCEMENT DE TOUS LES TESTS
echo ================================================================================
echo.
"%PYTHON_EXE%" test_piag_all.py --config config\piag.yaml
goto RESULTS

:RUN_RAG
echo.
echo ================================================================================
echo LANCEMENT DU TEST RAG
echo ================================================================================
echo.
"%PYTHON_EXE%" test_piag_rag_e2e.py --config config\piag.yaml
goto RESULTS

:RUN_CHAT
echo.
echo ================================================================================
echo LANCEMENT DU TEST CHAT
echo ================================================================================
echo.
"%PYTHON_EXE%" test_piag_chat_e2e.py --config config\piag.yaml
goto RESULTS

:RESULTS
echo.
echo ================================================================================
echo RESULTATS
echo ================================================================================
echo.
if %ERRORLEVEL% EQU 0 (
    echo [32mSUCCES: Tous les tests ont reussi ![0m
    echo.
    echo Les resultats sont disponibles dans le repertoire test_output\
) else (
    echo [31mECHEC: Certains tests ont echoue (code: %ERRORLEVEL%)[0m
    echo.
    echo Consultez les logs dans test_output\ pour plus de details
)

:END
echo.
echo ================================================================================
pause
