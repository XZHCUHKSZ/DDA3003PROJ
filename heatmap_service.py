from __future__ import annotations

import json
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    raise RuntimeError(f"Cannot read csv: {path}")


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
        cur = cur.replace(day=cur.day + 1) if False else datetime.fromordinal(cur.toordinal() + 1)
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
                df = _read_csv(fp)
            except Exception:
                continue
            if city not in df.columns:
                continue

            day_df = df[df["type"].astype(str).isin(candidates)].copy()
            if day_df.empty:
                continue
            day_df["hour"] = pd.to_numeric(day_df["hour"], errors="coerce")
            day_df = day_df.dropna(subset=["hour"])
            day_df["hour"] = day_df["hour"].astype(int)

            chosen = None
            for t in candidates:
                sub = day_df[day_df["type"].astype(str) == t]
                if not sub.empty:
                    chosen = sub
                    break
            if chosen is None:
                continue

            for _, r in chosen.iterrows():
                h = int(r["hour"])
                if h < 0 or h > 23:
                    continue
                v = pd.to_numeric(r.get(city), errors="coerce")
                if pd.isna(v):
                    continue
                rows.append([d, h, float(v)])
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
    if not root.exists():
        return False, f"data path not found: {data_root}"

    store = HeatmapStore(root)
    try:
        store.build_index()
    except Exception as exc:
        return False, f"index build failed: {exc}"

    if not store.date_to_file:
        return False, "no csv files indexed"

    _HeatmapHandler.store = store

    try:
        server = ThreadingHTTPServer((host, port), _HeatmapHandler)
    except OSError:
        # likely already running; treat as okay
        return True, f"heatmap service already running at http://{host}:{port}"

    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    return True, f"heatmap service started at http://{host}:{port} (indexed {len(store.date_to_file)} days)"
