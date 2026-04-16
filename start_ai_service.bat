@echo off
setlocal
cd /d "%~dp0"
echo [START] Bootstrapping env and starting AI service...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap_env.ps1" -Mode ai
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
  echo [START][ERROR] AI startup failed. Exit code: %EXIT_CODE%
  pause
)
exit /b %EXIT_CODE%
