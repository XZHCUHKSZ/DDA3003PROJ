"""
CLI entrypoint.

Usage:
    python main.py
    python main.py --data path/to/data.csv
    python main.py --data data.csv --out visualizations/
"""

from __future__ import annotations

import argparse
import os

from run_ai_service import ensure_ai_control_service_running, ensure_ai_service_running
from heatmap_service import ensure_heatmap_service_running
from visualizer import InteractiveAirQualityMap


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

    heatmap_ok, heatmap_msg = ensure_heatmap_service_running(args.data)
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
