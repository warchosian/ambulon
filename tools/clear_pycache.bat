@echo off
REM Clear Python cache files for Ambulon project

cd /d "G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon"

echo Clearing Python cache in: %CD%
echo ----------------------------------------

REM Remove __pycache__ directories
for /d /r "src" %%d in (__pycache__) do (
    if exist "%%d" (
        echo Removing: %%d
        rd /s /q "%%d"
    )
)

REM Remove .pyc files
for /r "src" %%f in (*.pyc) do (
    if exist "%%f" (
        echo Removing: %%f
        del /q "%%f"
    )
)

REM Also clear tests directory if it exists
if exist "tests" (
    for /d /r "tests" %%d in (__pycache__) do (
        if exist "%%d" (
            echo Removing: %%d
            rd /s /q "%%d"
        )
    )
    for /r "tests" %%f in (*.pyc) do (
        if exist "%%f" (
            echo Removing: %%f
            del /q "%%f"
        )
    )
)

echo.
echo [OK] Cache cleared!
pause
