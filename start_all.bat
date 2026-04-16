@echo off
setlocal
cd /d "%~dp0"
echo [START] Bootstrapping env and starting full application...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap_env.ps1" -Mode all
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
  echo [START][ERROR] App startup failed. Exit code: %EXIT_CODE%
  pause
)
exit /b %EXIT_CODE%
