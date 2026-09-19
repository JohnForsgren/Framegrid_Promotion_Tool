@echo off
setlocal
cd /d "%~dp0"
call "%~dp0runtime.cmd"
if errorlevel 1 (pause & exit /b 1)
"%FRAMEGRID_PYTHON%" "%~dp0editor.py"
pause
