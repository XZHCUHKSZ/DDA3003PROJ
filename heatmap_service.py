from __future__ import annotations

import csv
import json
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
        try:
            with path.open("r", encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except Exception:
            continue
    raise RuntimeError(f"Cannot read csv: {path}")


def _to_int(v: Any) -> int | None:
    try:
        if v is None:
            return None
        return int(float(str(v).strip()))
    except Exception:
        return None


def _to_float(v: Any) -> float | None:
    try:
        if v is None:
            return None
        s = str(v).strip()
        if s == "" or s == "--":
            return None
        return float(s)
    except Exception:
        return None


def _month_days(month: str) -> list[str]:
    y, m = month.split("-")
    yv, mv = int(y), int(m)
    if mv == 12:
        nxt = datetime(yv + 1, 1, 1)
    else:
        nxt = datetime(yv, mv + 1, 1)
    cur = datetime(yv, mv, 1)
    out: list[str] = []
    while cur < nxt:
        out.append(cur.strftime("%Y%m%d"))
        cur = datetime.fromordinal(cur.toordinal() + 1)
    return out


def _metric_candidates(metric: str) -> list[str]:
    m = (metric or "").strip()
    fallback_map = {
        "PM2.5_24h": ["PM2.5", "PM2.5_24h"],
        "PM10_24h": ["PM10", "PM10_24h"],
        "SO2_24h": ["SO2", "SO2_24h"],
        "NO2_24h": ["NO2", "NO2_24h"],
        "O3_8h": ["O3", "O3_8h", "O3_24h"],
        "O3_8h_24h": ["O3", "O3_8h", "O3_8h_24h", "O3_24h"],
        "AQI": ["AQI"],
    }
    return fallback_map.get(m, [m])


@dataclass
class HeatmapStore:
    data_root: Path
    date_to_file: dict[str, Path] = field(default_factory=dict)
    cache: dict[str, dict[str, Any]] = field(default_factory=dict)

    def build_index(self) -> None:
        files = sorted(self.data_root.rglob("*.csv"))
        idx: dict[str, Path] = {}
        for fp in files:
            m = re.search(r"(\d{8})", fp.stem)
            if m:
                idx[m.group(1)] = fp
        self.date_to_file = idx

    def get_monthly_hourly(self, city: str, metric: str, month: str) -> dict[str, Any]:
        key = f"{city}::{metric}::{month}"
        if key in self.cache:
            return self.cache[key]

        days = _month_days(month)
        candidates = _metric_candidates(metric)
        rows: list[list[Any]] = []
        actual = 0
        expected = len(days) * 24

        for d in days:
            fp = self.date_to_file.get(d)
            if not fp:
                continue
            try:
                rows_raw = _read_csv_rows(fp)
            except Exception:
                continue
            if not rows_raw:
                continue
            if city not in rows_raw[0]:
                continue

            typed_rows = [r for r in rows_raw if str(r.get("type", "")).strip() in candidates]
            if not typed_rows:
                continue

            chosen_type_rows: list[dict[str, str]] | None = None
            for t in candidates:
                subset = [r for r in typed_rows if str(r.get("type", "")).strip() == t]
                if subset:
                    chosen_type_rows = subset
                    break
            if chosen_type_rows is None:
                continue

            for r in chosen_type_rows:
                h = _to_int(r.get("hour"))
                if h is None or h < 0 or h > 23:
                    continue
                v = _to_float(r.get(city))
                if v is None:
                    continue
                rows.append([d, h, v])
                actual += 1

        payload = {
            "ok": True,
            "city": city,
            "metric": metric,
            "month": month,
            "data": rows,
            "coverage": {
                "expected": expected,
                "actual": actual,
                "ratio": round(actual / expected, 4) if expected else 0,
            },
        }
        self.cache[key] = payload
        return payload


class _HeatmapHandler(BaseHTTPRequestHandler):
    store: HeatmapStore | None = None

    @classmethod
    def _reload_store(cls, data_root: str) -> tuple[bool, str]:
        root = Path(data_root)
        store = HeatmapStore(root)
        if root.exists():
            try:
                store.build_index()
            except Exception as exc:
                return False, f"index build failed: {exc}"
        else:
            store.date_to_file = {}
        cls.store = store
        return True, f"store reloaded: root={root}, indexed={len(store.date_to_file)}"

    def _send(self, code: int, obj: dict[str, Any]) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        if self.path.startswith("/health"):
            self._send(200, {"ok": True, "service": "heatmap", "ready": self.store is not None})
            return

        if self.path.startswith("/api/heatmap/reload"):
            q = parse_qs(urlparse(self.path).query)
            data_root = (q.get("data_root", [""])[0] or "").strip()
            if not data_root:
                cur = str(self.store.data_root) if self.store is not None else ""
                data_root = cur
            if not data_root:
                self._send(400, {"ok": False, "message": "missing data_root"})
                return
            ok, msg = self._reload_store(data_root)
            self._send(200 if ok else 500, {"ok": ok, "message": msg})
            return

        if not self.path.startswith("/api/heatmap/monthly"):
            self._send(404, {"ok": False, "message": "not found"})
            return

        if self.store is None:
            self._send(503, {"ok": False, "message": "store not ready"})
            return

        q = parse_qs(urlparse(self.path).query)
        city = (q.get("city", [""])[0] or "").strip()
        metric = (q.get("metric", ["AQI"])[0] or "AQI").strip()
        month = (q.get("month", [""])[0] or "").strip()

        if not city or not re.fullmatch(r"\d{4}-\d{2}", month):
            self._send(400, {"ok": False, "message": "invalid city/month"})
            return

        try:
            payload = self.store.get_monthly_hourly(city, metric, month)
            self._send(200, payload)
        except Exception as exc:
            self._send(500, {"ok": False, "message": str(exc)})


def ensure_heatmap_service_running(data_root: str, host: str = "127.0.0.1", port: int = 8791) -> tuple[bool, str]:
    root = Path(data_root)
    ok_reload, msg_reload = _HeatmapHandler._reload_store(str(root))
    if not ok_reload:
        return False, msg_reload

    try:
        server = ThreadingHTTPServer((host, port), _HeatmapHandler)
    except OSError:
        # Already running in another process: ask that process to reload data root.
        try:
            q = urlencode({"data_root": str(root)})
            with urlopen(f"http://{host}:{port}/api/heatmap/reload?{q}", timeout=3) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            return True, f"heatmap service already running at http://{host}:{port}; {raw}"
        except Exception as exc:
            return True, f"heatmap service already running at http://{host}:{port}; reload skipped: {exc}"

    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    indexed = len(_HeatmapHandler.store.date_to_file if _HeatmapHandler.store else {})
    if not root.exists():
        return True, f"heatmap service started at http://{host}:{port} (data path missing: {data_root})"
    return True, f"heatmap service started at http://{host}:{port} (indexed {indexed} days from {root})"
