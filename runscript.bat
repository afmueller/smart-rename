@echo off
echo Current Directory is %cd%
echo Current batch run is %~dpnx0
echo Files to rename: %*
echo.
SET script_path=%~dpnx0%
SET script_dir=%script_path:\runscript.bat=%
echo cmd /k "cd /d %script_dir%\venv\Scripts & activate & cd /d %script_dir% & python smart_rename.py %*"
cmd /k "cd /d %script_dir%\venv\Scripts & activate & cd /d %script_dir% & python --version & python smart_rename.py %* & deactivate & exit 0"
pause
REM cmd /k "cd /d C:\Users\Admin\Desktop\venv\Scripts & activate & cd /d  C:\Users\Admin\Desktop\helloworld & python manage.py runserver"