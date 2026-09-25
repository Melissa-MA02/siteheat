"""Profile microclimate-sensors-data: devices, date ranges, locations."""
import requests

URL = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/microclimate-sensors-data/records"

params = {
    "select": "count(*) as readings, min(received_at) as first_seen, max(received_at) as last_seen",
    "group_by": "device_id, sensorlocation",  # one row per device
    "order_by": "readings desc",
    "limit": 50,
}

r = requests.get(URL, params=params, timeout=30)
print("HTTP", r.status_code)
if r.status_code != 200:
    print(r.text[:600])  # aggregation syntax errors show up here
else:
    for row in r.json()["results"]:
        print(f"{row['device_id']:<28} {str(row['sensorlocation'])[:22]:<24} "
              f"{row['readings']:>8} readings   {row['first_seen'][:10]} -> {row['last_seen'][:10]}")