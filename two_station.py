"""Two-station check: does an asphalt tram stop run hotter than a park on the days that matter?"""
import io
import os

import pandas as pd
import requests

URL = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/microclimate-sensors-data/exports/csv"
DEVICES = {"street": "ICTMicroclimate-08", "park": "ICTMicroclimate-01"}
MIN_READINGS_PER_DAY = 60


def daily_max(device: str) -> pd.DataFrame:
    cache = f"daily_{device}.csv"
    if os.path.exists(cache):  # don't re-download on every run
        return pd.read_csv(cache, parse_dates=["date"])

    print(f"downloading {device}...")
    r = requests.get(URL, params={
        "select": "received_at, airtemperature",
        "where": f'device_id = "{device}"',
        "delimiter": ",", "timezone": "UTC",
    }, timeout=180)
    r.raise_for_status()

    df = pd.read_csv(io.StringIO(r.text)).dropna(subset=["airtemperature"])
    df["date"] = (pd.to_datetime(df["received_at"], utc=True, format="mixed")
                  .dt.tz_convert("Australia/Melbourne").dt.normalize().dt.tz_localize(None))
    out = df.groupby("date")["airtemperature"].agg(obs_max="max", readings="count").reset_index()
    out = out[out["readings"] >= MIN_READINGS_PER_DAY].drop(columns="readings")
    out.to_csv(cache, index=False)
    return out


street = daily_max(DEVICES["street"]).rename(columns={"obs_max": "street_max"})
park = daily_max(DEVICES["park"]).rename(columns={"obs_max": "park_max"})

df = street.merge(park, on="date", how="inner")
df["diff"] = df["street_max"] - df["park_max"]  # positive = tram stop hotter than park
df.to_csv("two_station.csv", index=False)

print(f"\noverlapping days: {len(df)}  ({df['date'].min().date()} -> {df['date'].max().date()})")
print(f"mean difference: {df['diff'].mean():+.2f} C   (sd {df['diff'].std():.2f})")
print(f"street hotter on: {(df['diff'] > 0).mean():.0%} of days")

print("\nby park temperature:")
for band, grp in df.groupby(pd.cut(df["park_max"], [-999, 20, 25, 30, 35, 999],
                                   labels=["<20", "20-25", "25-30", "30-35", "35+"]), observed=True):
    print(f"  {band:<6} {grp['diff'].mean():+.2f} C   (sd {grp['diff'].std():.2f}, n={len(grp)})")

hot = df[df["park_max"] >= 30]
print(f"\nhot days (park >= 30 C): n={len(hot)}")
if len(hot):
    print(f"  mean gap {hot['diff'].mean():+.2f} C, sd {hot['diff'].std():.2f}, "
          f"range {hot['diff'].min():+.1f} to {hot['diff'].max():+.1f}")
    print("\n--- verdict ---")
    print("SITE MATTERS: gap is real and repeatable on hot days"
          if abs(hot["diff"].mean()) > 1.0 and hot["diff"].std() < abs(hot["diff"].mean())
          else "SITE EFFECT WEAK on hot days: gap is small or inconsistent")
