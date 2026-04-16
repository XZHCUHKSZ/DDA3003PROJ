from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare setup payload folder for installer")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--out", default="dist/setup_payload", help="Output payload directory")
    parser.add_argument("--publish-dir", default="desktop_app/publish/win-x64", help="Published desktop app directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    publish_dir = (root / args.publish_dir).resolve()
    app_dir = out / "app"
    runtime_dir = out / "runtime"
    data_dir = out / "data"

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    if not publish_dir.exists():
        raise FileNotFoundError(f"publish dir not found: {publish_dir}")

    copy_tree(publish_dir, app_dir)

    runtime_files = [
        "main.py",
        "bootstrap_env.ps1",
        "bootstrap_runtime.py",
        "requirements-lock.txt",
        "run_ai_service.py",
        "ai_control_service.py",
        "heatmap_service.py",
        "data_paths.py",
        "visualizer.py",
        "data_loader.py",
        "constants.py",
        "utils.py",
        "ui_texts.py",
        "map_base.py",
        "map_renderer.py",
        "city_panel.py",
        "compare_mode.py",
        "settlement_mode.py",
        "heat_data.py",
        "heat_mode.py",
        "region_mapping.py",
        "standalone_heatmap.py",
        "start_ai_service.bat",
        "start_all.bat",
    ]
    runtime_dirs = [
        "analysis_service",
        "logs",
    ]

    runtime_dir.mkdir(parents=True, exist_ok=True)
    for rf in runtime_files:
        copy_file(root / rf, runtime_dir / rf)
    for rd in runtime_dirs:
        copy_tree(root / rd, runtime_dir / rd)

    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "README_DATA.txt").write_text(
        "Put downloaded data bundle contents here.\n"
        "Required:\n"
        "  data/combined_air_quality_data.csv\n"
        "  data/hourly/*.csv\n",
        encoding="utf-8",
    )

    print(f"[OK] payload prepared: {out}")
    print(f"[OK] app: {app_dir}")
    print(f"[OK] runtime: {runtime_dir}")
    print(f"[OK] data placeholder: {data_dir}")


if __name__ == "__main__":
    main()

