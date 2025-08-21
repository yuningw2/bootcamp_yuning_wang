"""
Stage 03 helpers
"""

from __future__ import annotations
from pathlib import Path
from typing import Iterable, Sequence, Optional, Tuple
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


# ---------- Filesystem ----------
def ensure_dir(path: Path | str) -> Path:
    """Create directory (including parents) if it doesn't exist; return Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------- Data summaries ----------
def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return numeric summary stats (count, mean, std, min, quartiles, max)."""
    try:
        return df.describe(numeric_only=True)
    except TypeError:
        return df.select_dtypes(include="number").describe()


def groupby_mean(df: pd.DataFrame, by: str, cols: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """
    Group by `by` and compute means of numeric (or selected) columns.
    Returns a tidy DataFrame sorted by the group key.
    """
    if by not in df.columns:
        raise ValueError(f"'{by}' not in columns: {df.columns.tolist()}")

    if cols is None:
        cols = df.select_dtypes(include="number").columns.tolist()
    if not cols:
        raise ValueError("No numeric columns to aggregate.")

    out = (
        df.groupby(by)[list(cols)]
          .mean(numeric_only=True)
          .reset_index()
          .sort_values(by=by)
    )
    return out


# ---------- Persistence ----------
def save_table(df: pd.DataFrame, csv_path: Path | str, json_path: Optional[Path | str] = None,
               orient: str = "records", float_round: Optional[int] = None) -> Tuple[Path, Optional[Path]]:
    """
    Save a DataFrame to CSV (always) and JSON (optional). Returns paths.
    """
    csv_p = Path(csv_path)
    ensure_dir(csv_p.parent)
    df_to_write = df.copy()
    if float_round is not None:
        for c in df_to_write.select_dtypes("number").columns:
            df_to_write[c] = df_to_write[c].round(float_round)
    df_to_write.to_csv(csv_p, index=False)

    json_p = None
    if json_path:
        json_p = Path(json_path)
        ensure_dir(json_p.parent)
        json_p.write_text(df_to_write.to_json(orient=orient, indent=2))

    return csv_p, json_p


# ---------- Plots ----------
def save_histogram(series: pd.Series, out_path: Path | str, bins: int = 30,
                   title: Optional[str] = None, xlabel: Optional[str] = None) -> Path:
    """
    Save a simple histogram PNG for a numeric series.
    """
    out_p = Path(out_path)
    ensure_dir(out_p.parent)

    fig, ax = plt.subplots()
    ax.hist(series.dropna(), bins=bins)
    ax.set_title(title or "Histogram")
    ax.set_xlabel(xlabel or (series.name or ""))
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(out_p, dpi=144)
    plt.close(fig)
    return out_p


# ---------- Bonus: decorator demo from your HW ----------
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} called at {datetime.now().isoformat(timespec='seconds')}")
        return func(*args, **kwargs)
    return wrapper


@log_call
def calc_mean_std(values: Iterable[float]) -> Tuple[float, float]:
    """Return (mean, std) using NumPy."""
    a = np.asarray(list(values), dtype=float)
    return float(a.mean()), float(a.std())