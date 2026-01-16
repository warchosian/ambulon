@echo off
echo Reinstallation d'ambulon...
call conda activate ambulon
pip uninstall -y ambulon
pip install -e .
echo.
echo Test:
ambulon -h
pause
