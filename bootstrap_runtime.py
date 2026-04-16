"""Project runtime bootstrap helpers (Python 3.11 + locked deps)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_MAJOR = 3
REQUIRED_MINOR = 11


def _run(cmd: list[str], *, cwd: Path, timeout: int = 180) -> tuple[bool, str]:
    try:
        proc = subprocess.run(  # noqa: S603
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return proc.returncode == 0, (proc.stdout or "").strip()


def _version_ok(py_exe: str, major: int = REQUIRED_MAJOR, minor: int = REQUIRED_MINOR) -> bool:
    ok, _ = _run(
        [py_exe, "-c", "import sys;raise SystemExit(0 if sys.version_info[:2]==(3,11) else 1)"],
        cwd=Path.cwd(),
        timeout=10,
    )
    return ok


def _resolve_python311(project_root: Path) -> str | None:
    env_py = os.getenv("APP_PYTHON_EXE", "").strip()
    if env_py and Path(env_py).exists() and _version_ok(env_py):
        return env_py

    venv_py = project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_py.exists() and _version_ok(str(venv_py)):
        return str(venv_py)

    launcher = shutil.which("py")
    if launcher:
        ok, _ = _run([launcher, "-3.11", "-c", "print('ok')"], cwd=project_root, timeout=10)
        if ok:
            return f"{launcher} -3.11"

    py311 = shutil.which("python3.11")
    if py311 and _version_ok(py311):
        return py311

    py = shutil.which("python")
    if py and _version_ok(py):
        return py
    return None


def _venv_python(project_root: Path) -> Path:
    return project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _run_py_cmd(py_cmd: str, args: list[str], *, cwd: Path, timeout: int = 180) -> tuple[bool, str]:
    if " -3.11" in py_cmd:
        launcher = py_cmd.split(" ")[0]
        return _run([launcher, "-3.11", *args], cwd=cwd, timeout=timeout)
    return _run([py_cmd, *args], cwd=cwd, timeout=timeout)


def ensure_project_runtime(project_root: Path) -> tuple[bool, str, str]:
    py_cmd = _resolve_python311(project_root)
    if not py_cmd:
        return False, "Python 3.11 not found. Please run bootstrap_env.ps1 to auto-install.", ""

    venv_py = _venv_python(project_root)
    if venv_py.exists() and not _version_ok(str(venv_py)):
        try:
            if project_root.joinpath(".venv").exists():
                shutil.rmtree(project_root / ".venv")
        except Exception as exc:  # noqa: BLE001
            return False, f"Existing .venv has wrong Python version and cannot be replaced: {exc}", ""

    if not venv_py.exists():
        ok, out = _run_py_cmd(py_cmd, ["-m", "venv", ".venv"], cwd=project_root, timeout=120)
        if not ok:
            return False, f"Failed to create .venv: {out}", ""

    venv_python = str(_venv_python(project_root))
    if not Path(venv_python).exists():
        return False, "Virtual environment created but python executable missing.", ""

    lock_file = project_root / "requirements-lock.txt"
    if not lock_file.exists():
        return False, "requirements-lock.txt not found.", ""

    ok, out = _run([venv_python, "-m", "pip", "install", "-U", "pip"], cwd=project_root, timeout=240)
    if not ok:
        return False, f"pip upgrade failed: {out}", ""

    install_cmd = [venv_python, "-m", "pip", "install", "-r", str(lock_file)]
    ok, out = _run(install_cmd, cwd=project_root, timeout=420)
    if not ok:
        mirror_cmd = install_cmd + ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]
        ok, out = _run(mirror_cmd, cwd=project_root, timeout=420)
    if not ok and (project_root / "wheelhouse").exists():
        local_cmd = install_cmd + ["--no-index", "--find-links", str(project_root / "wheelhouse")]
        ok, out = _run(local_cmd, cwd=project_root, timeout=420)
    if not ok:
        return False, f"Dependency install failed: {out}", ""

    return True, "Runtime ready.", venv_python

