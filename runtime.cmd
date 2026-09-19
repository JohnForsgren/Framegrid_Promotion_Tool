@echo off
rem Called by launchers; preserve this variable in the caller's environment.
set "FRAMEGRID_PYTHON=%~dp0.venv\Scripts\python.exe"
if exist "%FRAMEGRID_PYTHON%" exit /b 0
set "FRAMEGRID_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%FRAMEGRID_PYTHON%" exit /b 0
echo Python runtime not found. See README.md for one-time setup.
exit /b 1
