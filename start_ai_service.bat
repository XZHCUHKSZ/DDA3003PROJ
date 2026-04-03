@echo off
setlocal ENABLEDELAYEDEXPANSION

cd /d "%~dp0"
echo [AI] Workspace: %cd%

set "PY_CMD="
py -3 --version >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3"
if not defined PY_CMD (
  python --version >nul 2>nul
  if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD (
  echo [AI][ERROR] Python 3 is not available in PATH.
  echo [AI][TIP ] Install Python 3.10+ and check "Add python.exe to PATH".
  pause
  exit /b 1
)
echo [AI] Python launcher: !PY_CMD!

if not exist ".venv\Scripts\python.exe" (
  echo [AI] Creating virtual environment .venv ...
  !PY_CMD! -m venv .venv
  if errorlevel 1 (
    echo [AI][ERROR] Failed to create .venv.
    echo [AI][TIP ] Check Python installation and directory write permission.
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [AI][ERROR] Failed to activate virtual environment.
  pause
  exit /b 1
)

set "PIP_EXTRA="
if not "%AI_PIP_INDEX_URL%"=="" (
  set "PIP_EXTRA=--index-url %AI_PIP_INDEX_URL%"
  echo [AI] Using custom pip index: %AI_PIP_INDEX_URL%
)

echo [AI] Installing/refreshing dependencies ...
python -m pip install -U pip %PIP_EXTRA%
if errorlevel 1 (
  echo [AI][ERROR] Failed to upgrade pip.
  echo [AI][TIP ] Try setting mirror, e.g.:
  echo          set AI_PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
  pause
  exit /b 1
)

python -m pip install fastapi uvicorn pydantic %PIP_EXTRA%
if errorlevel 1 (
  echo [AI][ERROR] Dependency install failed.
  echo [AI][TIP ] Check network/proxy/certificates or use AI_PIP_INDEX_URL mirror.
  pause
  exit /b 1
)

if "%DASHSCOPE_API_KEY%"=="" (
  echo [AI][WARN] DASHSCOPE_API_KEY is not set.
  echo [AI][WARN] No default API key is built in this script.
  echo [AI][WARN] Service will run in fallback mode unless key is provided from UI or env.
  echo [AI][TIP ] Example:
  echo          set DASHSCOPE_API_KEY=your_key_here
)

if "%BAILIAN_MODEL%"=="" (
  set BAILIAN_MODEL=qwen-plus
)

echo [AI] Starting service at http://127.0.0.1:8787 ...
python -m uvicorn analysis_service.main:app --host 127.0.0.1 --port 8787
set "UV_EXIT=!ERRORLEVEL!"

echo [AI][ERROR] Service exited unexpectedly. Exit code: !UV_EXIT!
echo [AI][TIP ] Check logs or run: python -m uvicorn analysis_service.main:app --host 127.0.0.1 --port 8787 --reload
pause
exit /b !UV_EXIT!
