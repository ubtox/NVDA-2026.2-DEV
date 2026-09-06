@echo off
rem Executes SCons within the NVDA build system's Python virtual environment.
set hereOrig=%~dp0
set here=%hereOrig%
if #%hereOrig:~-1%# == #\# set here=%hereOrig:~0,-1%

rem nvda-mathcat currently ships its abi3 extension as package data while its
rem package metadata is capped below Python 3.14. Stage the native module in
rem source explicitly so source runs and py2exe can resolve and bundle it.
set mathcatPyd=%here%\include\nvda-mathcat\assets\libmathcat_py.pyd
if not exist "%mathcatPyd%" (
	echo Error: MathCAT native module not found at "%mathcatPyd%".
	echo Ensure submodules are initialized before building NVDA.
	exit /b 1
)
copy /Y "%mathcatPyd%" "%here%\source\libmathcat_py.pyd" >nul
if errorlevel 1 (
	echo Error: failed to stage MathCAT native module for the NVDA build.
	exit /b 1
)

powershell -ExecutionPolicy Bypass -NoProfile -File "%here%\ensureuv.ps1" run --directory "%here%" SCons %*
