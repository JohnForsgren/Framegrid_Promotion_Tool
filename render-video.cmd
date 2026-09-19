@echo off
setlocal
cd /d "%~dp0"
call "%~dp0runtime.cmd"
if errorlevel 1 (pause & exit /b 1)
"%FRAMEGRID_PYTHON%" "%~dp0film.py" --render
if errorlevel 1 (echo Render failed. See the error above.) else (echo Video ready in the Videos folder.)
pause
