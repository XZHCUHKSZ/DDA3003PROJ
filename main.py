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

from run_ai_service import ensure_ai_service_running
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
        "--no-ai-autostart",
        action="store_true",
        help="Do not auto-start local AI service",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if not args.no_ai_autostart:
        ok, msg = ensure_ai_service_running()
        prefix = "OK" if ok else "WARN"
        print(f"[AI][{prefix}] {msg}")
    else:
        print("[AI] Auto-start skipped (--no-ai-autostart).")

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

