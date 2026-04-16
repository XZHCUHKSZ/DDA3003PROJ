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


def _count_daily_csv(path: Path) -> int:
    if not _existing_dir(path):
        return 0
    pat = re.compile(r"\d{8}")
    count = 0
    for fp in path.rglob("*.csv"):
        if pat.search(fp.stem):
            count += 1
    return count


def _find_combined_csv_under(root: Path) -> Path | None:
    if not _existing_dir(root):
        return None
    direct = root / "combined_air_quality_data.csv"
    if _existing_file(direct):
        return direct
    hits = [p for p in root.rglob("combined_air_quality_data.csv") if _existing_file(p)]
    if not hits:
        return None
    hits.sort(key=lambda p: (len(p.parts), len(str(p))))
    return hits[0]


def _find_daily_root_under(root: Path) -> Path | None:
    if not _existing_dir(root):
        return None
    # Prefer canonical folders first.
    preferred = [
        root / "hourly",
        root / "data" / "hourly",
        root / "hourly" / "data",
        root / "data" / "hourly" / "data",
    ]
    for cand in preferred:
        if _dir_has_daily_csv(cand):
            return cand
    # Then search recursively and pick the directory with most daily csv files.
    best_dir: Path | None = None
    best_count = 0
    for d in [root, *[p for p in root.rglob("*") if p.is_dir()]]:
        c = _count_daily_csv(d)
        if c > best_count:
            best_count = c
            best_dir = d
    return best_dir if best_count > 0 else None


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
            candidates.append((p, "--data dir"))
            candidates.append((p / "combined_air_quality_data.csv", "--data/combined_air_quality_data.csv"))
            if p.parent != p:
                candidates.append((p.parent, "--data parent dir"))
            if p.parent.parent != p.parent:
                candidates.append((p.parent.parent, "--data grandparent dir"))

    candidates.append((project_root.parent / "data", "runtime sibling data/"))
    candidates.append((project_root.parent / "data" / "combined_air_quality_data.csv", "runtime sibling data/combined_air_quality_data.csv"))
    candidates.append((project_root / "data", "repo data/"))
    candidates.append((project_root / "data" / "combined_air_quality_data.csv", "repo data/combined_air_quality_data.csv"))
    candidates.append((project_root / "combined_air_quality_data.csv", "repo combined_air_quality_data.csv"))
    fallback_csv = os.getenv("APP_FALLBACK_MAIN_CSV", "").strip()
    if fallback_csv:
        candidates.append((Path(fallback_csv), "env:APP_FALLBACK_MAIN_CSV"))

    seen: set[str] = set()
    for cand, label in candidates:
        key = str(cand).lower()
        if key in seen:
            continue
        seen.add(key)
        if _existing_file(cand):
            return str(cand), f"{label} -> {cand}"
        if cand.suffix.lower() != ".csv":
            found = _find_combined_csv_under(cand)
            if found:
                return str(found), f"{label} (recursive) -> {found}"
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

    candidates.append((project_root.parent / "data", "runtime sibling data/"))

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
    fallback_root = os.getenv("APP_FALLBACK_HEATMAP_ROOT", "").strip()
    if fallback_root:
        candidates.append((Path(fallback_root), "env:APP_FALLBACK_HEATMAP_ROOT"))

    seen: set[str] = set()
    for cand, label in candidates:
        key = str(cand).lower()
        if key in seen:
            continue
        seen.add(key)
        if _dir_has_daily_csv(cand):
            return str(cand), f"{label} -> {cand}"
        found = _find_daily_root_under(cand)
        if found:
            return str(found), f"{label} (recursive) -> {found}"
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
