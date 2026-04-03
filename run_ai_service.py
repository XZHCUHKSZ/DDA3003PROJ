"""Utility helpers to auto-start/check the local AI analysis service."""

from __future__ import annotations

import os
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


def is_ai_service_healthy(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 0.8) -> bool:
    try:
        with urllib.request.urlopen(_health_url(host, port), timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def is_ai_control_service_healthy(
    host: str = CONTROL_HOST,
    port: int = CONTROL_PORT,
    timeout: float = 0.6,
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


def start_ai_service(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    project_root = Path(__file__).resolve().parent
    cmd = _build_uvicorn_cmd(host, port)
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
    return True, "AI control service started in background; health check still warming up."


def ensure_ai_service_running(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    wait_seconds: float = 8.0,
) -> tuple[bool, str]:
    if is_ai_service_healthy(host, port):
        return True, "AI service already running."

    if not start_ai_service(host, port):
        return False, "Failed to start AI service process."

    deadline = time.time() + max(1.0, wait_seconds)
    while time.time() < deadline:
        if is_ai_service_healthy(host, port):
            return True, f"AI service started at http://{host}:{port}"
        time.sleep(0.25)
    return True, "AI service process started; health check still warming up."
