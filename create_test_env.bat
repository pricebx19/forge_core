@echo off
REM Create a test environment that can import forge_core

REM Get the parent directory (repo root)
cd ..
set REPO_ROOT=%CD%
cd forge_core

REM Create a symbolic link to make forge_core importable
echo Creating symbolic link for forge_core...
mkdir %TEMP%\forge_test_env 2>nul
cd %TEMP%\forge_test_env
rmdir /s /q forge_core 2>nul
mklink /d forge_core %REPO_ROOT%\forge_core
if errorlevel 1 (
    echo Failed to create symbolic link. 
    echo Try running this script as administrator or
    echo manually create a directory junction:
    echo.
    echo mklink /d %TEMP%\forge_test_env\forge_core %REPO_ROOT%\forge_core
    exit /b 1
)

REM Add the temp directory to Python path and run tests
set PYTHONPATH=%TEMP%\forge_test_env;%PYTHONPATH%
echo PYTHONPATH set to: %PYTHONPATH%

REM Run tests in the correct path
cd %REPO_ROOT%\forge_core
echo Running tests...
python -m pytest tests

REM Return exit code from pytest
exit /b %ERRORLEVEL% 