"""Lightweight local control service for managing AI analysis service."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from run_ai_service import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    ensure_ai_service_running,
    is_ai_service_healthy,
)


class AIControlHandler(BaseHTTPRequestHandler):
    server_version = "AIControl/1.0"

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            ai_ok = is_ai_service_healthy()
            self._send_json(
                200,
                {
                    "status": "ok",
                    "ai_service_healthy": ai_ok,
                    "ai_url": f"http://{DEFAULT_HOST}:{DEFAULT_PORT}",
                },
            )
            return

        if self.path == "/api/ai/check":
            ai_ok = is_ai_service_healthy()
            self._send_json(
                200,
                {
                    "ok": ai_ok,
                    "message": "AI service is running" if ai_ok else "AI service is not running",
                    "host": DEFAULT_HOST,
                    "port": DEFAULT_PORT,
                },
            )
            return

        self._send_json(404, {"ok": False, "message": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/ai/start":
            payload = self._read_json()
            host = str(payload.get("host") or DEFAULT_HOST).strip() or DEFAULT_HOST
            try:
                port = int(payload.get("port") or DEFAULT_PORT)
            except Exception:
                port = DEFAULT_PORT
            wait_seconds = payload.get("wait_seconds", 8.0)
            try:
                wait_seconds = float(wait_seconds)
            except Exception:
                wait_seconds = 8.0
            wait_seconds = max(1.0, min(20.0, wait_seconds))

            ok, msg = ensure_ai_service_running(host=host, port=port, wait_seconds=wait_seconds)
            status = 200 if ok else 500
            self._send_json(
                status,
                {
                    "ok": ok,
                    "message": msg,
                    "host": host,
                    "port": port,
                },
            )
            return

        self._send_json(404, {"ok": False, "message": "Not found"})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # keep silent
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local AI control service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8790)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), AIControlHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
