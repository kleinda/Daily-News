@echo off
chcp 65001 >nul
title Daily News
cd /d "%~dp0"

rem If the server is already running, just open the site
netstat -ano | findstr /r /c:":8000 .*LISTENING" >nul
if %errorlevel%==0 (
  start "" http://localhost:8000
  exit /b
)

echo Starting Daily News site - keep this window open. Close it to stop.
python server.py
if errorlevel 1 pause
