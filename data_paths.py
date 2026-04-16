"""Data path resolution for local/dev/packaged modes."""

from __future__ import annotations

import os
import re
from pathlib import Path


def _existing_file(path: Path) -> bool:
    return path.exists() and path.is_file()


def _existing_dir(path: Path) -> bool:
    return path.exists() and path.is_dir()


def _dir_has_daily_csv(path: Path) -> bool:
    if not _existing_dir(path):
        return False
    pat = re.compile(r"\d{8}")
    for fp in path.rglob("*.csv"):
        if pat.search(fp.stem):
            return True
    return False


def resolve_main_data_csv(cli_data: str, project_root: Path) -> tuple[str | None, str]:
    candidates: list[tuple[Path, str]] = []
    tried: list[str] = []

    env_csv = os.getenv("MAIN_DATA_CSV", "").strip()
    if env_csv:
        candidates.append((Path(env_csv), "env:MAIN_DATA_CSV"))

    env_bundle = os.getenv("APP_DATA_BUNDLE_DIR", "").strip()
    if env_bundle:
        candidates.append((Path(env_bundle) / "combined_air_quality_data.csv", "env:APP_DATA_BUNDLE_DIR/combined_air_quality_data.csv"))

    if cli_data:
        p = Path(cli_data)
        if p.suffix.lower() == ".csv":
            candidates.append((p, "--data"))
        else:
            candidates.append((p / "combined_air_quality_data.csv", "--data/combined_air_quality_data.csv"))

    candidates.append((project_root / "data" / "combined_air_quality_data.csv", "repo data/combined_air_quality_data.csv"))
    candidates.append((project_root / "combined_air_quality_data.csv", "repo combined_air_quality_data.csv"))
    candidates.append((Path(r"C:\Users\xzh88\Desktop\cleaned\combined_air_quality_data.csv"), "fixed C cleaned csv"))
    candidates.append((Path(r"D:\xwechat_files\wxid_t5ne9kglije022_12bf\msg\file\2026-01\data\combined_air_quality_data.csv"), "fixed D data csv"))

    seen: set[str] = set()
    for cand, label in candidates:
        key = str(cand).lower()
        if key in seen:
            continue
        seen.add(key)
        if _existing_file(cand):
            return str(cand), f"{label} -> {cand}"
        tried.append(f"{label} -> {cand}")
    return None, "no valid main csv found; tried: " + "; ".join(tried)


def resolve_heatmap_data_root(main_csv_path: str, project_root: Path) -> tuple[str | None, str]:
    candidates: list[tuple[Path, str]] = []
    tried: list[str] = []

    env_root = os.getenv("HEATMAP_DATA_ROOT", "").strip()
    if env_root:
        candidates.append((Path(env_root), "env:HEATMAP_DATA_ROOT"))

    env_bundle = os.getenv("APP_DATA_BUNDLE_DIR", "").strip()
    if env_bundle:
        bundle = Path(env_bundle)
        candidates.append((bundle / "data", "env:APP_DATA_BUNDLE_DIR/data"))
        candidates.append((bundle, "env:APP_DATA_BUNDLE_DIR"))

    fixed_root = Path(r"D:\xwechat_files\wxid_t5ne9kglije022_12bf\msg\file\2026-01\data")
    candidates.append((fixed_root / "data", "fixed D root data/"))
    candidates.append((fixed_root, "fixed D root"))

    if main_csv_path:
        p = Path(main_csv_path)
        if p.exists():
            if p.is_dir():
                candidates.append((p / "data", "main path/data"))
                candidates.append((p, "main path dir"))
            else:
                candidates.append((p.parent / "data", "main csv sibling data/"))
                candidates.append((p.parent, "main csv parent"))

    candidates.append((project_root / "data", "repo data/"))

    seen: set[str] = set()
    for cand, label in candidates:
        key = str(cand).lower()
        if key in seen:
            continue
        seen.add(key)
        if _dir_has_daily_csv(cand):
            return str(cand), f"{label} -> {cand}"
        tried.append(f"{label} -> {cand}")
    return None, "no valid heatmap csv directory found; tried: " + "; ".join(tried)


def resolve_output_dir(cli_out: str, project_root: Path) -> tuple[str, str]:
    env_out = os.getenv("APP_OUTPUT_DIR", "").strip()
    if env_out:
        out = Path(env_out)
        out.mkdir(parents=True, exist_ok=True)
        return str(out), f"env:APP_OUTPUT_DIR -> {out}"
    if cli_out:
        out = Path(cli_out)
        out.mkdir(parents=True, exist_ok=True)
        return str(out), f"--out -> {out}"
    out = project_root / "visualizations"
    out.mkdir(parents=True, exist_ok=True)
    return str(out), f"default repo visualizations -> {out}"

