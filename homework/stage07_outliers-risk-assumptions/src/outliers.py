from __future__ import annotations
import pandas as pd

def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    q1 = s.quantile(0.25); q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr; upper = q3 + k * iqr
    return (s < lower) | (s > upper)

def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    mu = s.mean(); sigma = s.std(ddof=0)
    if sigma == 0 or pd.isna(sigma):
        return pd.Series(False, index=s.index)
    z = (s - mu) / sigma
    return z.abs() > threshold

def winsorize_series(series: pd.Series, lower: float = 0.05, upper: float = 0.95) -> pd.Series:
    if not (0 <= lower < upper <= 1):
        raise ValueError("lower/upper must satisfy 0 <= lower < upper <= 1")
    s = pd.to_numeric(series, errors="coerce")
    lo = s.quantile(lower); hi = s.quantile(upper)
    return s.clip(lower=lo, upper=hi)