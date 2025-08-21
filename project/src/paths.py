from __future__ import annotations
from pathlib import Path
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROC = DATA / "processed"
MODELS = ROOT / "models"

def ensure_dirs(paths: Iterable[Path] = (RAW, PROC, MODELS)) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)

def latest_raw(pattern: str = "weather_hourly_*.csv") -> Optional[Path]:
    candidates = sorted(RAW.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None