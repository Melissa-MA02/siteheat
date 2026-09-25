"""Pull archived forecasts for the sensor's exact coordinates and join them to the observations."""
import pandas as pd
import requests

DEVICE = "ICTMicroclimate-08"
ODS = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/microclimate-sensors-data/records"
ARCHIVE = "https://historical-forecast-api.open-meteo.com/v1/forecast"

# 1. Where is the sensor? Take the coordinates from the data, not from a map.
rec = requests.get(ODS, params={"select": "latlong", "where": f'device_id = "{DEVICE}"', "limit": 1}, timeout=30)
rec.raise_for_status()
latlong = rec.json()["results"][0]["latlong"]
lat, lon = latlong["lat"], latlong["lon"]
print(f"{DEVICE} at {lat:.5f}, {lon:.5f}")

# 2. Match the observation window exactly.
obs = pd.read_csv("obs_daily.csv", parse_dates=["date"])
start, end = obs["date"].min().date().isoformat(), obs["date"].max().date().isoformat()
print("window:", start, "->", end)

# 3. Archived forecasts for that point.
fc = requests.get(ARCHIVE, params={
    "latitude": lat, "longitude": lon,
    "daily": "temperature_2m_max",
    "timezone": "Australia/Melbourne",
    "start_date": start, "end_date": end,
}, timeout=60)
fc.raise_for_status()
daily = fc.json()["daily"]

forecast = pd.DataFrame({
    "date": pd.to_datetime(daily["time"]),
    "forecast_max": daily["temperature_2m_max"],
}).dropna()
print("forecast days:", len(forecast))

# 4. Join on date. Inner join keeps only days with both numbers.
joined = obs.merge(forecast, on="date", how="inner")
joined["error"] = joined["obs_max"] - joined["forecast_max"]  # positive = sensor hotter than forecast
joined.to_csv("joined.csv", index=False)

print("matched days:", len(joined))
print("saved joined.csv")
