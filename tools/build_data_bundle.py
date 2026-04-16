from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def has_daily_token(path: Path) -> bool:
    return bool(re.search(r"\d{8}", path.stem))


def collect_daily_csv(src_root: Path) -> list[Path]:
    return sorted([p for p in src_root.rglob("*.csv") if has_daily_token(p)])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build distributable data_bundle.zip")
    parser.add_argument("--main-csv", required=True, help="Path to combined_air_quality_data.csv")
    parser.add_argument("--hourly-root", required=True, help="Root folder containing daily csv files for heatmap")
    parser.add_argument("--out-dir", default="release_data", help="Output directory")
    parser.add_argument("--version", default=datetime.now().strftime("%Y.%m.%d"), help="Data bundle version")
    args = parser.parse_args()

    main_csv = Path(args.main_csv).resolve()
    hourly_root = Path(args.hourly_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    stage_dir = out_dir / f"data_bundle_{args.version}"
    data_dir = stage_dir / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    if not main_csv.exists():
        raise FileNotFoundError(f"main csv missing: {main_csv}")
    daily_csv = collect_daily_csv(hourly_root)
    if not daily_csv:
        raise RuntimeError(f"no daily csv found under: {hourly_root}")

    dst_main = data_dir / "combined_air_quality_data.csv"
    shutil.copy2(main_csv, dst_main)
    dst_hourly_root = data_dir / "hourly"
    dst_hourly_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    for fp in daily_csv:
        rel = fp.relative_to(hourly_root)
        target = dst_hourly_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fp, target)
        copied += 1

    manifest = {
        "bundle_version": args.version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "main_csv": {
            "path": "data/combined_air_quality_data.csv",
            "sha256": sha256_file(dst_main),
            "size": dst_main.stat().st_size,
        },
        "hourly_root": "data/hourly",
        "hourly_count": copied,
        "readme": "Unzip beside AQDeskShell.exe, keep folder name 'data'.",
    }
    (stage_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (stage_dir / "README_DATA.txt").write_text(
        "Data bundle usage:\n"
        "1) Unzip and keep folder 'data' beside AQDeskShell.exe\n"
        "2) Ensure files exist:\n"
        "   - data/combined_air_quality_data.csv\n"
        "   - data/hourly/*.csv\n",
        encoding="utf-8",
    )

    zip_path = out_dir / f"data_bundle_{args.version}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fp in stage_dir.rglob("*"):
            if fp.is_file():
                zf.write(fp, fp.relative_to(stage_dir))

    print(f"[OK] bundle: {zip_path}")
    print(f"[OK] manifest: {stage_dir / 'manifest.json'}")
    print(f"[OK] daily csv copied: {copied}")


if __name__ == "__main__":
    main()

