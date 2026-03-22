@echo off
echo Reinstallation de pip et commitizen...
conda install -y pip
pip install commitizen
echo.
echo Test:
cz --version
pause
