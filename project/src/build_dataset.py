from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

from paths import ensure_dirs, RAW, PROC, latest_raw
from io_utils import read_csv_dt, write_csv, write_parquet
from validation import validate_weather_df
from features_weather import (
    resample_hourly_to_daily, add_calendar_features,
    add_lags, add_rollings, make_regression_target, make_rain_label
)

def main():
    ap = argparse.ArgumentParser(description="Build supervised dataset from hourly weather CSV(s).")
    ap.add_argument("--input", type=str, default=None,
                    help="Path to raw hourly CSV (columns: time, temperature_2m, precipitation, ...). If omitted, uses latest in data/raw.")
    ap.add_argument("--pattern", type=str, default="weather_hourly_*.csv",
                    help="Glob for selecting latest raw file if --input not provided.")
    ap.add_argument("--timezone", type=str, default="America/New_York",
                    help="Timezone for daily resampling (e.g., America/New_York).")
    ap.add_argument("--task", type=str, choices=["reg_temp_max_nextday", "clf_rain10_nextday"],
                    default="reg_temp_max_nextday", help="Which target to create.")
    ap.add_argument("--lags", type=int, nargs="+", default=[1, 2, 3], help="Lag days to add.")
    ap.add_argument("--windows", type=int, nargs="+", default=[3, 7, 14], help="Rolling windows to add.")
    ap.add_argument("--outstem", type=str, default="weather_features", help="Output filename stem.")
    args = ap.parse_args()

    ensure_dirs()

    # Locate raw
    raw_path = Path(args.input) if args.input else latest_raw(args.pattern)
    if raw_path is None or not raw_path.exists():
        raise SystemExit("No raw file found. Provide --input or place a file under data/raw matching the pattern.")

    # Read + validate hourly
    dfh = read_csv_dt(raw_path, parse_dates=("time",), assume_utc=True)
    validate_weather_df(dfh)

    # Daily aggregation in local timezone
    daily = resample_hourly_to_daily(dfh, tz=args.timezone)
    daily = add_calendar_features(daily)

    # Feature set
    base_cols = ["temp_max_c", "temp_mean_c", "precip_mm"]
    daily = add_lags(daily, cols=base_cols, lags=args.lags)
    daily = add_rollings(daily, cols=["temp_max_c", "precip_mm"], windows=args.windows, funcs=("mean", "max", "sum"))

    # Targets
    if args.task == "reg_temp_max_nextday":
        daily = make_regression_target(daily, base_col="temp_max_c", horizon=1)
    elif args.task == "clf_rain10_nextday":
        daily = make_rain_label(daily, threshold_mm=10.0, horizon=1)

    # Drop rows with NaNs introduced by lags/rollings/targets
    out = daily.dropna().reset_index(drop=True)

    # Save
    stem = f"{args.outstem}_{args.task}"
    csv_path = PROC / f"{stem}.csv"
    pq_path  = PROC / f"{stem}.parquet"
    write_csv(out, csv_path)
    write_parquet(out, pq_path)
    print(f"Saved: {csv_path}")
    print(f"Saved: {pq_path}")

if __name__ == "__main__":
    main()
