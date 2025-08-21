from __future__ import annotations
import pandas as pd

def resample_hourly_to_daily(df_hourly: pd.DataFrame, tz: str = "America/New_York") -> pd.DataFrame:
    df = df_hourly.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df = df.dropna(subset=["time"]).set_index("time").sort_index()
    if tz:
        df = df.tz_convert(tz)
    daily = pd.DataFrame({
        "temp_max_c": df["temperature_2m"].resample("D").max(),
        "temp_min_c": df["temperature_2m"].resample("D").min(),
        "temp_mean_c": df["temperature_2m"].resample("D").mean(),
        "precip_mm":  df["precipitation"].resample("D").sum(),
    }).reset_index().rename(columns={"time": "date"})
    daily["date"] = daily["date"].dt.tz_localize(None)
    return daily