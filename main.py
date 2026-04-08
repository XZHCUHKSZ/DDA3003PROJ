"""
CLI entrypoint.

Usage:
    python main.py
    python main.py --data path/to/data.csv
    python main.py --data data.csv --out visualizations/
"""

from __future__ import annotations

import argparse
import importlib
import os
import re
from pathlib import Path

from run_ai_service import ensure_ai_control_service_running, ensure_ai_service_running
from visualizer import InteractiveAirQualityMap


def _try_start_heatmap_service(data_path: str) -> tuple[bool, str]:
    try:
        mod = importlib.import_module("heatmap_service")
        ensure_heatmap_service_running = getattr(mod, "ensure_heatmap_service_running", None)
        if ensure_heatmap_service_running is None:
            return False, "heatmap_service.ensure_heatmap_service_running not found"
    except Exception as exc:
        return False, f"heatmap module unavailable: {exc}"
    try:
        return ensure_heatmap_service_running(data_path)
    except Exception as exc:
        return False, f"heatmap service start failed: {exc}"


def _dir_has_csv(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    # Heatmap service needs day-level files like *_YYYYMMDD.csv.
    date_pat = re.compile(r"\d{8}")
    try:
        for fp in path.rglob("*.csv"):
            if date_pat.search(fp.stem):
                return True
        return False
    except StopIteration:
        return False
    except Exception:
        return False


def _resolve_heatmap_data_root(data_path: str) -> tuple[str | None, str]:
    candidates: list[tuple[Path, str]] = []
    env_root = os.getenv("HEATMAP_DATA_ROOT", "").strip()
    if env_root:
        candidates.append((Path(env_root), "env:HEATMAP_DATA_ROOT"))
    # User-provided fixed daily-data location (local machine default).
    fixed_root = Path(r"D:\xwechat_files\wxid_t5ne9kglije022_12bf\msg\file\2026-01\data")
    candidates.append((fixed_root / "data", "fixed root data/"))
    candidates.append((fixed_root, "fixed root"))

    p = Path(data_path)
    if p.exists():
        if p.is_dir():
            candidates.append((p, "--data"))
            candidates.append((p / "data", "--data/data"))
        else:
            candidates.append((p.parent / "data", "--data sibling data/"))
            candidates.append((p.parent, "--data parent"))

    repo_data = Path(__file__).resolve().parent / "data"
    candidates.append((repo_data, "repo data/"))

    seen: set[str] = set()
    tried: list[str] = []
    for cand, label in candidates:
        key = str(cand.resolve()) if cand.exists() else str(cand)
        if key in seen:
            continue
        seen.add(key)
        if _dir_has_csv(cand):
            return str(cand), f"{label} -> {cand}"
        tried.append(f"{label} -> {cand}")

    return None, "no valid csv directory found; tried: " + "; ".join(tried)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="China city air-quality map visualizer (scroll layout)",
    )
    parser.add_argument(
        "--data",
        default=r"C:\Users\xzh88\Desktop\cleaned\combined_air_quality_data.csv",
        help="Input CSV data file path",
    )
    parser.add_argument(
        "--out",
        default=r"C:\Users\xzh88\Desktop\cleaned\visualizations",
        help="Output directory path (auto-created if not exists)",
    )
    parser.add_argument(
        "--ai-autostart",
        action="store_true",
        help="Auto-start local AI service before rendering map",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    ctrl_ok, ctrl_msg = ensure_ai_control_service_running(wait_seconds=3.0)
    ctrl_prefix = "OK" if ctrl_ok else "WARN"
    print(f"[AI-CTRL][{ctrl_prefix}] {ctrl_msg}")

    if args.ai_autostart:
        ok, msg = ensure_ai_service_running()
        prefix = "OK" if ok else "WARN"
        print(f"[AI][{prefix}] {msg}")
    else:
        # Non-blocking warm-up to reduce first online-setup failures.
        warm_ok, warm_msg = ensure_ai_service_running(wait_seconds=1.5)
        warm_prefix = "OK" if warm_ok else "WARN"
        print(f"[AI-WARMUP][{warm_prefix}] {warm_msg}")
        print("[AI] Full auto-start skipped by default. Use --ai-autostart for strict startup checks.")

    heatmap_data_root, heatmap_root_msg = _resolve_heatmap_data_root(args.data)
    if heatmap_data_root:
        print(f"[HEATMAP][INFO] data root: {heatmap_root_msg}")
        heatmap_ok, heatmap_msg = _try_start_heatmap_service(heatmap_data_root)
    else:
        print(f"[HEATMAP][WARN] {heatmap_root_msg}")
        heatmap_ok, heatmap_msg = _try_start_heatmap_service(args.data)
    heat_prefix = "OK" if heatmap_ok else "WARN"
    print(f"[HEATMAP][{heat_prefix}] {heatmap_msg}")

    if not os.path.exists(args.data):
        print(f"\n[ERROR] Data file not found: {args.data}")
        return

    visualizer = InteractiveAirQualityMap(args.data)
    visualizer.load_data()
    visualizer.run(output_dir=args.out)
    print("\n[OK] Program finished.")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
