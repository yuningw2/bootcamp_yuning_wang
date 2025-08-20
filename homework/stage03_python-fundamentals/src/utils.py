# src/utils.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return numeric summary stats (count, mean, std, min, quartiles, max)."""
    return df.describe(numeric_only=True)

def groupby_mean(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Group by a categorical column and compute mean of numeric columns."""
    if by not in df.columns:
        raise KeyError(f"Column '{by}' not in DataFrame")
    return df.groupby(by).mean(numeric_only=True).reset_index()

def save_table(df: pd.DataFrame, out_csv, out_json=None) -> None:
    """Save DataFrame to CSV (and optionally JSON)."""
    ensure_dir(Path(out_csv).parent)
    df.to_csv(out_csv, index=False)
    if out_json:
        df.to_json(out_json, orient="records", indent=2)

def save_histogram(series: pd.Series, out_png, title: str = "Histogram") -> None:
    """Save a basic histogram of a numeric series."""
    ensure_dir(Path(out_png).parent)
    ax = series.hist()
    ax.set_title(title)
    ax.set_xlabel(series.name if series.name else "value")
    ax.set_ylabel("count")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()