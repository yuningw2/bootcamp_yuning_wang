import os, pathlib, datetime as dt
import requests
import pandas as pd

# Folders
DATA_RAW = pathlib.Path("data/raw")
DATA_PROC = pathlib.Path("data/processed")
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROC.mkdir(parents=True, exist_ok=True)

def ts():
    return dt.datetime.now().strftime("%Y%m%d-%H%M")

def fetch_open_meteo(latitude: float, longitude: float, timezone: str = "America/New_York") -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "precipitation"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "forecast_days": 7,
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
    df["time"] = pd.to_datetime(df["time"])
    return df

def summarize_daily(df_hourly: pd.DataFrame) -> pd.DataFrame:
    if df_hourly.empty:
        return df_hourly
    df = df_hourly.copy()
    df["date"] = df["time"].dt.date
    out = (
        df.groupby("date")
          .agg(
              temp_mean=("temperature_2m", "mean"),
              temp_max=("temperature_2m", "max"),
              temp_min=("temperature_2m", "min"),
              precip_sum=("precipitation", "sum"),
          )
          .reset_index()
    )
    return out

def main():
    # Default to NYC; override by setting LAT/LON in your .env or terminal if you want
    lat = float(os.getenv("LAT", "40.7128"))
    lon = float(os.getenv("LON", "-74.0060"))
    tz  = os.getenv("TIMEZONE", "America/New_York")

    js = fetch_open_meteo(lat, lon, tz)
    df_hourly = to_hourly_df(js)

    # Save raw
    raw_path = DATA_RAW / f"weather_hourly_{ts()}.csv"
    df_hourly.to_csv(raw_path, index=False)
    print(f"Saved raw hourly → {raw_path}")

    # Process + save daily summary
    df_daily = summarize_daily(df_hourly)
    proc_path = DATA_PROC / f"weather_daily_{ts()}.csv"
    df_daily.to_csv(proc_path, index=False)
    print(f"Saved processed daily summary → {proc_path}")

    # Quick text summary for stakeholder
    if not df_daily.empty:
        next7 = df_daily.head(7)
        hottest = next7.loc[next7["temp_max"].idxmax()]
        wettest = next7.loc[next7["precip_sum"].idxmax()]
        print("\nQuick Stakeholder Summary (next 7 days):")
        print(f"- Hottest day: {hottest['date']} (max ≈ {hottest['temp_max']:.1f} °C)")
        print(f"- Wettest day: {wettest['date']} (total precip ≈ {wettest['precip_sum']:.1f} mm)")

if __name__ == "__main__":
    main()