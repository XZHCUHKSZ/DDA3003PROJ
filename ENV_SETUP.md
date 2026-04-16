# Environment Bootstrap (Windows)

This project now includes a deterministic bootstrap flow:

- Enforces Python **3.11**
- Creates/repairs `.venv`
- Installs locked dependencies from `requirements-lock.txt`
- Falls back to Tsinghua mirror and optional local `wheelhouse/`

## One-click startup

- Full app (map + services): `start_all.bat`
- AI service only: `start_ai_service.bat`

Both call:

- `bootstrap_env.ps1`

## Modes

```powershell
powershell -ExecutionPolicy Bypass -File .\bootstrap_env.ps1 -Mode prepare
powershell -ExecutionPolicy Bypass -File .\bootstrap_env.ps1 -Mode ai
powershell -ExecutionPolicy Bypass -File .\bootstrap_env.ps1 -Mode all
```

## Optional overrides

- `APP_PYTHON_EXE`: force a specific python executable (must be 3.11)
- `DASHSCOPE_API_KEY`: AI key
- `BAILIAN_MODEL`: model name

## Offline installation

If you provide local wheels under `wheelhouse/`, bootstrap will use:

```text
pip install --no-index --find-links wheelhouse -r requirements-lock.txt
```

