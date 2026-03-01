"""Core backend logic — CSV loading, validation, and file-status helpers."""

import csv
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("tpms.service")

# ── Resolve project root (two levels up from this file) ──────────────
_THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _THIS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

# ── Known CSV / JSON files the service can serve ─────────────────────
SERVED_FILES: dict[str, Path] = {
    "tire_intelligence_v1.csv":   DATA_DIR / "enriched" / "tire_intelligence_v1.csv",
    "maintenance_report_v1.csv":  DATA_DIR / "enriched" / "maintenance_report_v1.csv",
    "model.info.json":            DATA_DIR / "enriched" / "model.info.json",
    # raw / processed / synthetic — read-only reference
    "configuration_data.csv":           DATA_DIR / "raw" / "configuration_data.csv",
    "cleaned_configuration_data.csv":   DATA_DIR / "processed" / "cleaned_configuration_data.csv",
}

# ── Required columns for validation ──────────────────────────────────
INTELLIGENCE_REQUIRED_COLS = {
    "vehicle_id", "stress_score", "risk_level",
    "recommended_action", "priority_rank",
}


# ── Helpers ──────────────────────────────────────────────────────────
def get_file_status() -> dict[str, bool]:
    """Return dict of filename → exists for every known served file."""
    return {name: path.is_file() for name, path in SERVED_FILES.items()}


def load_csv(path: Path) -> list[dict[str, Any]]:
    """Read a CSV and return a list of row-dicts.

    Numeric-looking values are auto-converted to int/float.
    Raises FileNotFoundError if the file is missing.
    """
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    rows: list[dict[str, Any]] = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            clean: dict[str, Any] = {}
            for k, v in row.items():
                clean[k] = _auto_type(v)
            rows.append(clean)
    logger.info("Loaded %d rows from %s", len(rows), path.name)
    return rows


def load_json(path: Path) -> Any:
    """Read a JSON file and return its content."""
    if not path.is_file():
        raise FileNotFoundError(f"JSON not found: {path}")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    logger.info("Loaded JSON from %s", path.name)
    return data


def validate_intelligence(data: list[dict[str, Any]]) -> list[str]:
    """Run sanity checks on intelligence data.  Returns list of issues (empty = OK)."""
    issues: list[str] = []
    if not data:
        issues.append("Dataset is empty.")
        return issues

    # Column check
    actual_cols = set(data[0].keys())
    missing = INTELLIGENCE_REQUIRED_COLS - actual_cols
    if missing:
        issues.append(f"Missing columns: {missing}")

    # Value range checks
    for i, row in enumerate(data):
        ss = row.get("stress_score")
        if ss is not None and not (0 <= float(ss) <= 1):
            issues.append(f"Row {i}: stress_score={ss} out of [0,1]")
        pr = row.get("priority_rank")
        if pr is not None and int(pr) < 1:
            issues.append(f"Row {i}: priority_rank={pr} < 1")

    # Dense ranking
    ranks = sorted(int(r.get("priority_rank", 0)) for r in data if r.get("priority_rank") is not None)
    expected = list(range(1, len(ranks) + 1))
    if ranks != expected:
        issues.append(f"priority_rank not dense 1..{len(ranks)}: got {ranks}")

    return issues


# ── Private ──────────────────────────────────────────────────────────
def _auto_type(value: str) -> Any:
    """Try to convert a string to int, then float; fall back to str."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    return value
