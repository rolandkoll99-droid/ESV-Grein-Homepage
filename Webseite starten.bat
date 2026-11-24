@echo off
chcp 65001 >nul
title ESV Grein - Webseite
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py %*
  goto ende
)
where python >nul 2>nul
if %errorlevel%==0 (
  python server.py %*
  goto ende
)
echo.
echo  Python ist auf diesem PC nicht installiert.
echo  Bitte von https://www.python.org/downloads/ installieren
echo  (beim Installieren "Add Python to PATH" anhaken) und erneut starten.
echo.
start https://www.python.org/downloads/
pause
:ende
