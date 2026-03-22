@echo off
echo ==========================================
echo REPARATION DE PIP
echo ==========================================
echo.

echo [1/3] Tentative avec ensurepip...
python -m ensurepip --default-pip 2>nul
if %errorlevel% == 0 (
    echo OK - ensurepip a fonctionne
    goto :verif
)

echo [2/3] Tentative avec conda...
conda install -y pip 2>nul
if %errorlevel% == 0 (
    echo OK - conda a reinstalle pip
    goto :verif
)

echo [3/3] Installation manuelle de pip...
curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py 2>nul
if exist get-pip.py (
    python get-pip.py
    del get-pip.py
) else (
    echo ERREUR: Impossible de telecharger get-pip.py
    echo Essayez manuellement:
    echo   python -m ensurepip
    echo   ou
    echo   conda install pip
    pause
    exit /b 1
)

:verif
echo.
echo Verification:
python -m pip --version || pip --version
if %errorlevel% == 0 (
    echo.
    echo SUCCES! Pip est reinstalle.
) else (
    echo ECHEC - Pip ne fonctionne toujours pas
)
pause
