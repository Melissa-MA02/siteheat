"""Probe the City of Melbourne sensor datasets: fields, size, and a sample row."""
import json

import requests

BASE = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets"

DATASETS = [
    "microclimate-sensors-data",       # current sensors, 15-min readings
    "microclimate-sensor-readings",    # historical sensors, 2019 onwards
    "microclimate-sensor-locations",   # site_id -> lat/lon
]


def peek(dataset: str) -> None:
    r = requests.get(f"{BASE}/{dataset}/records", params={"limit": 1}, timeout=30)
    print(f"\n=== {dataset}  (HTTP {r.status_code}) ===")
    if r.status_code != 200:
        print(r.text[:400])  # show the error body, not just the code
        return

    data = r.json()
    print("total_count:", data.get("total_count"))
    for rec in data.get("results", []):
        print("sample row:")
        print(json.dumps(rec, indent=2, default=str)[:1500])


for ds in DATASETS:
    peek(ds)
