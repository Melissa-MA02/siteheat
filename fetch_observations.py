"""Download one sensor's temperature series and reduce it to a daily maximum."""
import io

import pandas as pd
import requests

DEVICE = "ICTMicroclimate-08"      # Swanston St tram stop, street level
MIN_READINGS_PER_DAY = 60          # a day with few readings can miss the true peak
OUT = "obs_daily.csv"

URL = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/microclimate-sensors-data/exports/csv"
params = {
    "select": "received_at, airtemperature",
    "where": f'device_id = "{DEVICE}"',
    "delimiter": ",",
    "timezone": "UTC",
}

print(f"Downloading {DEVICE}...")
r = requests.get(URL, params=params, timeout=180)
r.raise_for_status()

df = pd.read_csv(io.StringIO(r.text))
print("rows downloaded:", len(df))

df = df.dropna(subset=["airtemperature"])
df["ts_local"] = pd.to_datetime(df["received_at"], utc=True, format="mixed").dt.tz_convert("Australia/Melbourne")
df["date"] = df["ts_local"].dt.date

daily = df.groupby("date")["airtemperature"].agg(obs_max="max", readings="count").reset_index()
thin = daily[daily["readings"] < MIN_READINGS_PER_DAY]
daily = daily[daily["readings"] >= MIN_READINGS_PER_DAY]  # drop days with poor coverage

daily.to_csv(OUT, index=False)
print(f"\nkept {len(daily)} days, dropped {len(thin)} thin days")
print("range:", daily["date"].min(), "->", daily["date"].max())
print("observed daily max: mean %.1f C, min %.1f C, max %.1f C"
      % (daily["obs_max"].mean(), daily["obs_max"].min(), daily["obs_max"].max()))
print(f"saved {OUT}")
