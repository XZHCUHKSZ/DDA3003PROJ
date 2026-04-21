"""Utility helpers to auto-start/check the local monthly heatmap service."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

from bootstrap_runtime import ensure_project_runtime

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8791


def _health_url(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return f"http://{host}:{port}/health"


def _reload_url(data_root: str, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    q = urlencode({"data_root": str(data_root)})
    return f"http://{host}:{port}/api/heatmap/reload?{q}"


def _is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def is_heatmap_service_healthy(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(_health_url(host, port), timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _reload_remote_data_root(data_root: str, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(_reload_url(data_root, host, port), timeout=3.0) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        return True, raw
    except Exception as exc:
        return False, str(exc)


def start_heatmap_service(data_root: str, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    project_root = Path(__file__).resolve().parent
    ok, msg, py_bin = ensure_project_runtime(project_root)
    if not ok:
        return False

    script_path = project_root / "heatmap_service.py"
    cmd = [
        py_bin,
        str(script_path),
        "--data-root",
        str(data_root),
        "--host",
        host,
        "--port",
        str(port),
    ]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    stdout_fp = open(logs_dir / "heatmap_service.out.log", "ab")
    stderr_fp = open(logs_dir / "heatmap_service.err.log", "ab")

    kwargs: dict = {
        "cwd": str(project_root),
        "stdout": stdout_fp,
        "stderr": stderr_fp,
    }
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            flags |= subprocess.CREATE_NO_WINDOW
        kwargs["creationflags"] = flags
    else:
        kwargs["start_new_session"] = True

    try:
        subprocess.Popen(cmd, **kwargs)  # noqa: S603
        return True
    except Exception:
        return False


def ensure_heatmap_service_running(
    data_root: str,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    wait_seconds: float = 8.0,
) -> tuple[bool, str]:
    if is_heatmap_service_healthy(host, port) or _is_port_open(host, port):
        ok_reload, msg_reload = _reload_remote_data_root(data_root, host, port)
        if ok_reload:
            return True, f"heatmap service already running at http://{host}:{port}; {msg_reload}"
        return True, f"heatmap service already running at http://{host}:{port}; reload skipped: {msg_reload}"

    if not start_heatmap_service(data_root, host, port):
        return False, "Failed to start heatmap service process."

    deadline = time.time() + max(1.0, wait_seconds)
    while time.time() < deadline:
        if is_heatmap_service_healthy(host, port) or _is_port_open(host, port):
            ok_reload, msg_reload = _reload_remote_data_root(data_root, host, port)
            if ok_reload:
                return True, f"heatmap service started at http://{host}:{port}; {msg_reload}"
            return True, f"heatmap service started at http://{host}:{port}; reload skipped: {msg_reload}"
        time.sleep(0.25)
    return True, "heatmap service process started; health check still warming up."

