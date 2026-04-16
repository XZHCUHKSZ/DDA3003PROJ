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
import sys
from pathlib import Path

from data_paths import resolve_heatmap_data_root, resolve_main_data_csv, resolve_output_dir
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="China city air-quality map visualizer (scroll layout)",
    )
    parser.add_argument(
        "--data",
        default="",
        help="Input CSV data file path",
    )
    parser.add_argument(
        "--out",
        default="",
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
    project_root = Path(__file__).resolve().parent

    main_data_csv, main_data_msg = resolve_main_data_csv(args.data, project_root)
    print(f"[DATA][INFO] {main_data_msg}")
    if not main_data_csv:
        print("\n[ERROR] Main CSV not found. Provide --data or set MAIN_DATA_CSV.")
        return

    output_dir, out_msg = resolve_output_dir(args.out, project_root)
    print(f"[OUT][INFO] {out_msg}")

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

    heatmap_data_root, heatmap_root_msg = resolve_heatmap_data_root(main_data_csv, project_root)
    if heatmap_data_root:
        print(f"[HEATMAP][INFO] data root: {heatmap_root_msg}")
        heatmap_ok, heatmap_msg = _try_start_heatmap_service(heatmap_data_root)
    else:
        print(f"[HEATMAP][WARN] {heatmap_root_msg}")
        heatmap_ok, heatmap_msg = _try_start_heatmap_service(main_data_csv)
    heat_prefix = "OK" if heatmap_ok else "WARN"
    print(f"[HEATMAP][{heat_prefix}] {heatmap_msg}")

    if not os.path.exists(main_data_csv):
        print(f"\n[ERROR] Data file not found: {main_data_csv}")
        return

    visualizer = InteractiveAirQualityMap(main_data_csv)
    visualizer.load_data()
    visualizer.run(output_dir=output_dir)
    print("\n[OK] Program finished.")


if __name__ == "__main__":
    main()
    try:
        if sys.stdin and sys.stdin.isatty():
            input("\nPress Enter to exit...")
    except Exception:
        pass
