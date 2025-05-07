@echo off
echo MetaX is Starting...
setlocal
set "script_path=%~dp0"
set "python=%script_path%pyenv\python.exe"
set "main_script=%script_path%\metax\metax\gui\main_gui.py"

:: Set PYTHONPATH to ensure local code is used
set "PYTHONPATH=%script_path%metax"

:: Use -m parameter to start Python, run the script as the main module
:: Otherwise, the installed package (metaxtools) will be used
"%python%" -m metax.gui.main_gui
endlocal