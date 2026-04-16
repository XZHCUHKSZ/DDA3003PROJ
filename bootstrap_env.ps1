param(
    [ValidateSet("prepare", "ai", "all")]
    [string]$Mode = "all",
    [switch]$SkipPythonInstall
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Set-Location -LiteralPath $PSScriptRoot
$ProjectRoot = (Get-Location).Path
$RequiredPy = "3.11"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$ReqLock = Join-Path $ProjectRoot "requirements-lock.txt"
$Wheelhouse = Join-Path $ProjectRoot "wheelhouse"

function Write-Step([string]$msg) { Write-Host "[BOOT] $msg" -ForegroundColor Cyan }
function Write-Warn([string]$msg) { Write-Host "[BOOT][WARN] $msg" -ForegroundColor Yellow }
function Write-Err([string]$msg) { Write-Host "[BOOT][ERROR] $msg" -ForegroundColor Red }

function Test-Python311([string]$exe) {
    if ([string]::IsNullOrWhiteSpace($exe)) { return $false }
    try {
        & $exe -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(3,11) else 1)" *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Resolve-Python311 {
    if ($env:APP_PYTHON_EXE -and (Test-Path $env:APP_PYTHON_EXE) -and (Test-Python311 $env:APP_PYTHON_EXE)) {
        return $env:APP_PYTHON_EXE
    }
    if ((Test-Path $VenvPython) -and (Test-Python311 $VenvPython)) {
        return $VenvPython
    }
    try {
        py -3.11 -c "print('ok')" *> $null
        if ($LASTEXITCODE -eq 0) { return "py -3.11" }
    } catch {}
    $py311 = (Get-Command python3.11 -ErrorAction SilentlyContinue)
    if ($py311 -and (Test-Python311 $py311.Source)) { return $py311.Source }
    $py = (Get-Command python -ErrorAction SilentlyContinue)
    if ($py -and (Test-Python311 $py.Source)) { return $py.Source }
    return $null
}

function Install-Python311 {
    if ($SkipPythonInstall) {
        throw "Python 3.11 not found and auto-install is disabled."
    }
    Write-Step "Python 3.11 not found, trying winget install..."
    $wg = Get-Command winget -ErrorAction SilentlyContinue
    if ($wg) {
        try {
            winget install --id Python.Python.3.11 -e --silent --accept-package-agreements --accept-source-agreements
        } catch {
            Write-Warn "winget install failed: $($_.Exception.Message)"
        }
    } else {
        Write-Warn "winget not available."
    }
}

function Invoke-Py([string]$pyCmd, [string[]]$pyArgs) {
    if ($pyCmd -eq "py -3.11") {
        & py -3.11 @pyArgs
    } else {
        & $pyCmd @pyArgs
    }
    return $LASTEXITCODE
}

function Ensure-Venv([string]$pyCmd) {
    if (Test-Path $VenvPython) {
        if (-not (Test-Python311 $VenvPython)) {
            Write-Warn "Existing .venv is not Python 3.11, recreating..."
            Remove-Item -LiteralPath (Join-Path $ProjectRoot ".venv") -Recurse -Force
        }
    }
    if (-not (Test-Path $VenvPython)) {
        Write-Step "Creating .venv with Python $RequiredPy..."
        $exit = Invoke-Py $pyCmd @("-m", "venv", ".venv")
        if ($exit -ne 0 -or -not (Test-Path $VenvPython)) {
            throw "Failed to create .venv."
        }
    }
}

function Ensure-Deps {
    if (-not (Test-Path $ReqLock)) {
        throw "Missing requirements-lock.txt"
    }
    Write-Step "Upgrading pip..."
    & $VenvPython -m pip install -U pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

    Write-Step "Installing locked dependencies..."
    & $VenvPython -m pip install -r $ReqLock
    if ($LASTEXITCODE -eq 0) { return }

    Write-Warn "Default index failed, trying Tsinghua mirror..."
    & $VenvPython -m pip install -r $ReqLock -i "https://pypi.tuna.tsinghua.edu.cn/simple"
    if ($LASTEXITCODE -eq 0) { return }

    if (Test-Path $Wheelhouse) {
        Write-Warn "Mirror failed, trying local wheelhouse..."
        & $VenvPython -m pip install -r $ReqLock --no-index --find-links $Wheelhouse
        if ($LASTEXITCODE -eq 0) { return }
    }
    throw "Dependency installation failed."
}

function Verify-Deps {
    Write-Step "Verifying dependency imports..."
    & $VenvPython -c "import fastapi,uvicorn,pydantic,pandas,pyecharts,openpyxl;print('DEPS_OK')"
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency verification failed."
    }
    Write-Step "Dependency verification passed."
}

function Resolve-MainCsvForRun {
    $preferred = @(
        (Join-Path $ProjectRoot "..\\data\\combined_air_quality_data.csv"),
        (Join-Path $ProjectRoot "data\\combined_air_quality_data.csv"),
        (Join-Path $ProjectRoot "combined_air_quality_data.csv")
    )
    foreach ($p in $preferred) {
        if (Test-Path $p) {
            return (Resolve-Path $p).Path
        }
    }
    $roots = @(
        (Join-Path $ProjectRoot "..\\data"),
        (Join-Path $ProjectRoot "data"),
        $ProjectRoot
    )
    foreach ($r in $roots) {
        if (-not (Test-Path $r)) { continue }
        try {
            $hit = Get-ChildItem -Path $r -Recurse -File -Filter "combined_air_quality_data.csv" -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($hit) { return $hit.FullName }
        } catch {}
    }
    return ""
}

try {
    Write-Step "Workspace: $ProjectRoot"
    $pyCmd = Resolve-Python311
    if (-not $pyCmd) {
        Install-Python311
        $pyCmd = Resolve-Python311
    }
    if (-not $pyCmd) { throw "Python 3.11 still not found after install attempt." }
    Write-Step "Using Python launcher: $pyCmd"

    Ensure-Venv $pyCmd
    Ensure-Deps
    Verify-Deps
    Write-Step "Environment is ready."

    if ($Mode -eq "prepare") {
        Write-Host "[BOOT][OK] prepare mode finished."
        exit 0
    }
    if ($Mode -eq "ai") {
        Write-Step "Starting AI service on 127.0.0.1:8787 ..."
        & $VenvPython -m uvicorn analysis_service.main:app --host 127.0.0.1 --port 8787
        exit $LASTEXITCODE
    }
    if ($Mode -eq "all") {
        $mainCsv = Resolve-MainCsvForRun
        if ([string]::IsNullOrWhiteSpace($mainCsv)) {
            Write-Warn "Main CSV not found before launch; running with auto-discovery."
            Write-Step "Starting full app (main.py --ai-autostart) ..."
            & $VenvPython main.py --ai-autostart
        } else {
            Write-Step "Using data file: $mainCsv"
            Write-Step "Starting full app (main.py --data ... --ai-autostart) ..."
            & $VenvPython main.py --data $mainCsv --ai-autostart
        }
        exit $LASTEXITCODE
    }
    throw "Unknown mode: $Mode"
} catch {
    Write-Err $_.Exception.Message
    exit 1
}
