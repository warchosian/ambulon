@echo off
call conda activate ambulon
python -c "import sys; sys.path.insert(0, 'src'); from app.cli.cli import main; print('Import CLI OK')"
echo.
echo Test ambulon -h:
ambulon -h
pause
