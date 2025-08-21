# src/ingest_open_meteo.py
from __future__ import annotations
import os, argparse, datetime as dt
import requests
import pandas as pd

from .paths import RAW, PROC, ensure_dirs
from .features_weather import resample_hourly_to_daily  # used only if --preview

def ts():
    return dt.datetime.now().strftime("%Y%m%d-%H%M")

def fetch_open_meteo(latitude: float, longitude: float, timezone: str = "America/New_York", forecast_days: int = 7) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "forecast_days": forecast_days,
        "timezone": timezone,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def to_hourly_df(js: dict) -> pd.DataFrame:
    hourly = js.get("hourly", {})
    df = pd.DataFrame({
        "time": hourly.get("time", []),
        "temperature_2m": hourly.get("temperature_2m", []),
        "precipitation": hourly.get("precipitation", []),
    })
    if df.empty:
        return df
    # treat timestamps as UTC for downstream safety
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    return df

def main():
    ap = argparse.ArgumentParser(description="Ingest hourly weather from Open-Meteo and save to data/raw/.")
    ap.add_argument("--lat", type=float, default=float(os.getenv("LAT", "40.7128")))
    ap.add_argument("--lon", type=float, default=float(os.getenv("LON", "-74.0060")))
    ap.add_argument("--timezone", type=str, default=os.getenv("TIMEZONE", "America/New_York"))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--preview", action="store_true", help="Also write a daily preview CSV (optional).")
    args = ap.parse_args()

    ensure_dirs()

    js = fetch_open_meteo(args.lat, args.lon, args.timezone, args.days)
    df_hourly = to_hourly_df(js)

    if df_hourly.empty:
        raise SystemExit("Open-Meteo returned no hourly data.")

    raw_path = RAW / f"weather_hourly_{args.lat:.4f}_{args.lon:.4f}_{ts()}.csv"
    df_hourly.to_csv(raw_path, index=False)
    print(f"[ingest] Saved hourly → {raw_path}")

    if args.preview:
        daily = resample_hourly_to_daily(df_hourly, tz=args.timezone)
        prev_path = PROC / f"weather_daily_preview_{args.lat:.4f}_{args.lon:.4f}_{ts()}.csv"
        daily.to_csv(prev_path, index=False)
        print(f"[ingest] (preview) Saved daily → {prev_path}")

if __name__ == "__main__":
    main()