@echo off
REM Run tests with the correct Python path

REM Set the current directory in the Python path
set PYTHONPATH=%CD%

echo PYTHONPATH set to: %PYTHONPATH%
echo Running tests...

REM Run pytest with the current directory in the path
python -m pytest tests 