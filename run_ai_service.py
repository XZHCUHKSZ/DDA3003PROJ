"""Utility helpers to auto-start/check the local AI analysis service."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 8790


def _health_url(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return f"http://{host}:{port}/health"


def _control_health_url(host: str = CONTROL_HOST, port: int = CONTROL_PORT) -> str:
    return f"http://{host}:{port}/health"


def _is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def is_ai_service_healthy(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 0.8) -> bool:
    try:
        with urllib.request.urlopen(_health_url(host, port), timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def is_ai_control_service_healthy(
    host: str = CONTROL_HOST,
    port: int = CONTROL_PORT,
    timeout: float = 1.5,
) -> bool:
    try:
        with urllib.request.urlopen(_control_health_url(host, port), timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _build_uvicorn_cmd(host: str, port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "analysis_service.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]


def _build_control_cmd(host: str, port: int) -> list[str]:
    project_root = Path(__file__).resolve().parent
    script_path = project_root / "ai_control_service.py"
    return [sys.executable, str(script_path), "--host", host, "--port", str(port)]


def _resolve_service_python(project_root: Path) -> str:
    if os.name == "nt":
        venv_py = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = project_root / ".venv" / "bin" / "python"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def _ensure_service_runtime(project_root: Path) -> tuple[bool, str]:
    py_bin = _resolve_service_python(project_root)
    if py_bin == sys.executable:
        # try creating venv first for dependency isolation
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(project_root / ".venv")],
                cwd=str(project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=40,
            )
        except Exception:
            pass
        py_bin = _resolve_service_python(project_root)

    try:
        subprocess.run(
            [py_bin, "-m", "pip", "install", "-q", "fastapi", "uvicorn", "pydantic"],
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=120,
        )
    except Exception:
        return False, "Dependency bootstrap failed."
    return True, py_bin


def start_ai_service(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    project_root = Path(__file__).resolve().parent
    ok, py_or_msg = _ensure_service_runtime(project_root)
    if not ok:
        return False
    py_bin = py_or_msg
    cmd = [
        py_bin,
        "-m",
        "uvicorn",
        "analysis_service.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    stdout_fp = open(logs_dir / "ai_service.out.log", "ab")
    stderr_fp = open(logs_dir / "ai_service.err.log", "ab")
    kwargs: dict = {
        "cwd": str(project_root),
        "stdout": stdout_fp,
        "stderr": stderr_fp,
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        kwargs["start_new_session"] = True

    try:
        subprocess.Popen(cmd, **kwargs)  # noqa: S603
        return True
    except Exception:
        return False


def start_ai_control_service(host: str = CONTROL_HOST, port: int = CONTROL_PORT) -> bool:
    project_root = Path(__file__).resolve().parent
    cmd = _build_control_cmd(host, port)
    kwargs: dict = {
        "cwd": str(project_root),
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        kwargs["start_new_session"] = True
    try:
        subprocess.Popen(cmd, **kwargs)  # noqa: S603
        return True
    except Exception:
        return False


def ensure_ai_control_service_running(
    host: str = CONTROL_HOST,
    port: int = CONTROL_PORT,
    wait_seconds: float = 4.0,
) -> tuple[bool, str]:
    if is_ai_control_service_healthy(host, port):
        return True, f"AI control service already running at http://{host}:{port}"

    if not start_ai_control_service(host, port):
        return False, "Failed to start AI control service process."

    deadline = time.time() + max(1.0, wait_seconds)
    while time.time() < deadline:
        if is_ai_control_service_healthy(host, port):
            return True, f"AI control service started at http://{host}:{port}"
        time.sleep(0.2)
    return False, "AI control service process started, but health check timed out."


def ensure_ai_service_running(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    wait_seconds: float = 8.0,
) -> tuple[bool, str]:
    if is_ai_service_healthy(host, port) or _is_port_open(host, port):
        return True, "AI service already running."

    if not start_ai_service(host, port):
        return False, "Failed to start AI service process."

    deadline = time.time() + max(1.0, wait_seconds)
    while time.time() < deadline:
        if is_ai_service_healthy(host, port) or _is_port_open(host, port):
            return True, f"AI service started at http://{host}:{port}"
        time.sleep(0.25)
    return True, "AI service process started; health check still warming up."
