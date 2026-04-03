@echo off
setlocal

cd /d "%~dp0"

echo [AI] Workspace: %cd%

if not exist ".venv" (
  echo [AI] Creating virtual environment .venv ...
  py -m venv .venv 2>nul
  if errorlevel 1 (
    python -m venv .venv
    if errorlevel 1 (
      echo [AI][ERROR] Failed to create .venv. Install Python 3 first.
      pause
      exit /b 1
    )
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [AI][ERROR] Failed to activate virtual environment.
  pause
  exit /b 1
)

echo [AI] Installing/refreshing dependencies ...
python -m pip install -U pip >nul 2>nul
python -m pip install fastapi uvicorn pydantic
if errorlevel 1 (
  echo [AI][ERROR] Dependency install failed.
  pause
  exit /b 1
)

if "%DASHSCOPE_API_KEY%"=="" (
  echo [AI][WARN] DASHSCOPE_API_KEY is not set.
  echo [AI][WARN] Service will run in fallback mode unless you set it.
  echo [AI][TIP ] Example:
  echo          set DASHSCOPE_API_KEY=your_key_here
)

if "%BAILIAN_MODEL%"=="" (
  set BAILIAN_MODEL=qwen-plus
)

echo [AI] Starting service at http://127.0.0.1:8787 ...
python -m uvicorn analysis_service.main:app --host 127.0.0.1 --port 8787 --reload

endlocal
