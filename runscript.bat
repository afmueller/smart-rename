@echo off
echo Current Directory is %cd%
echo Current batch run is %~dpnx0

set filesC=0
for %%f in (%*) do Set /A filesC+=1
echo Files to rename: %filesC%

echo.
SET script_path=%~dpnx0%
SET script_dir=%script_path:\runscript.bat=%
echo cmd /k "cd /d %script_dir%\venv\Scripts & activate & cd /d %script_dir% & python smart_rename.py %*"
cmd /k "cd /d %script_dir%\venv\Scripts & activate & cd /d %script_dir% & python --version & python smart_rename.py %* & deactivate & exit 0"
pause
