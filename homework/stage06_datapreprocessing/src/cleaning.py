# src/cleaning.py
from __future__ import annotations
from typing import Sequence, Optional
import numpy as np
import pandas as pd


def fill_missing_median(
    df: pd.DataFrame,
    cols: Optional[Sequence[str]] = None,
    inplace: bool = False
) -> pd.DataFrame:
    """
    Fill NaNs in numeric columns with the column median (ignoring NaNs).

    Parameters
    ----------
    df : DataFrame
        Input data.
    cols : list[str] | None
        Which columns to fill. If None, all numeric columns are used.
    inplace : bool
        If True, modify df in place. Otherwise, return a copy.

    Returns
    -------
    DataFrame
        Data with selected columns filled.
    """
    target = df if inplace else df.copy()
    use_cols = (
        target.select_dtypes(include="number").columns.tolist()
        if cols is None else [c for c in cols if c in target.columns]
    )
    for c in use_cols:
        if pd.api.types.is_numeric_dtype(target[c]):
            med = target[c].median(skipna=True)
            target[c] = target[c].fillna(med)
    return target


def drop_missing(
    df: pd.DataFrame,
    threshold: float = 0.5,
    axis: str = "rows",
    inplace: bool = False
) -> pd.DataFrame:
    """
    Drop rows or columns that don't meet a minimum non-missing fraction.

    Parameters
    ----------
    df : DataFrame
    threshold : float
        Required fraction of non-null values to keep (0..1).
        Example: threshold=0.6 keeps rows/columns with >=60% non-null.
    axis : {'rows', 'columns'}
        Where to drop.
    inplace : bool
        If True, modify df in place.

    Returns
    -------
    DataFrame
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    if axis not in {"rows", "columns"}:
        raise ValueError("axis must be 'rows' or 'columns'")

    target = df if inplace else df.copy()
    if axis == "rows":
        min_non_null = int(np.ceil(threshold * target.shape[1]))
        return target.dropna(axis=0, thresh=min_non_null)
    else:
        min_non_null = int(np.ceil(threshold * target.shape[0]))
        return target.dropna(axis=1, thresh=min_non_null)


def normalize_data(
    df: pd.DataFrame,
    cols: Sequence[str],
    method: str = "minmax",
    inplace: bool = False
) -> pd.DataFrame:
    """
    Normalize selected numeric columns.

    Parameters
    ----------
    df : DataFrame
    cols : list[str]
        Columns to scale (ignored if missing or non-numeric).
    method : {'minmax', 'zscore'}
        'minmax' scales to [0, 1]; 'zscore' to mean 0, std 1.
    inplace : bool
        If True, modify df in place.

    Returns
    -------
    DataFrame
    """
    target = df if inplace else df.copy()
    for c in cols:
        if c not in target.columns or not pd.api.types.is_numeric_dtype(target[c]):
            continue
        s = target[c].astype(float)
        if s.isna().all():
            continue

        if method == "minmax":
            mn, mx = s.min(), s.max()
            if mn == mx:
                # constant column — skip to avoid divide-by-zero
                continue
            target[c] = (s - mn) / (mx - mn)
        elif method == "zscore":
            mu, sigma = s.mean(), s.std(ddof=0)
            if sigma == 0:
                continue
            target[c] = (s - mu) / sigma
        else:
            raise ValueError("method must be 'minmax' or 'zscore'")

    return target