"""SiteHeat tools. Site correction removed: two checks found no site-level signal (see docs)."""
import math
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

VIC_LAT, VIC_LON = (-39.2, -33.9), (140.9, 150.0)  # rough Victoria bounding box


def find_location(place_name: str) -> dict:
    """Place name -> coordinates, so the LLM never invents lat/lon."""
    r = requests.get(GEOCODE_URL, params={"name": place_name, "count": 10, "countryCode": "AU"}, timeout=10)
    r.raise_for_status()
    vic = [p for p in r.json().get("results", []) if p.get("admin1") == "Victoria"]
    if not vic:
        return {"error": f"No Victorian location found for '{place_name}'."}
    p = vic[0]
    return {"name": p["name"], "latitude": p["latitude"], "longitude": p["longitude"], "state": "Victoria"}


def get_forecast(latitude: float, longitude: float, date: str) -> dict:
    """Peak temperature forecast for one date (YYYY-MM-DD)."""
    if not (VIC_LAT[0] <= latitude <= VIC_LAT[1] and VIC_LON[0] <= longitude <= VIC_LON[1]):
        return {"error": "Location is outside Victoria. SiteHeat only covers Victoria."}

    params = {
        "latitude": latitude, "longitude": longitude,
        "hourly": "temperature_2m,dew_point_2m,wind_speed_10m",
        "wind_speed_unit": "ms",
        "timezone": "Australia/Melbourne",
        "start_date": date, "end_date": date,
    }
    r = requests.get(FORECAST_URL, params=params, timeout=10)
    r.raise_for_status()
    h = r.json()["hourly"]

    i = max(range(len(h["temperature_2m"])), key=lambda k: h["temperature_2m"][k])  # hottest hour

    return {
        "date": date,
        "peak_hour_local": h["time"][i],
        "forecast_max_c": h["temperature_2m"][i],
        "dew_point_c": h["dew_point_2m"][i],
        "wind_speed_ms": h["wind_speed_10m"][i],
        "source": "Open-Meteo gridded forecast, no site-level correction applied",
    }


def compute_heat_stress(temperature_c: float, dew_point_c: float, wind_speed_ms: float) -> dict:
    """Deterministic heat-stress indices. Pure maths, no LLM."""
    e = 6.105 * math.exp(17.27 * dew_point_c / (237.7 + dew_point_c))  # vapour pressure, hPa
    apparent = temperature_c + 0.33 * e - 0.70 * wind_speed_ms - 4.00   # BoM apparent temperature
    wbgt = 0.567 * temperature_c + 0.393 * e + 3.94                     # BoM simplified WBGT
    return {
        "apparent_temperature_c": round(apparent, 1),
        "wbgt_estimate_c": round(wbgt, 1),
        "vapour_pressure_hpa": round(e, 1),
        "method": "BoM apparent temperature; simplified WBGT assumes moderate sun and light wind",
    }


TOOL_FUNCTIONS = {
    "find_location": find_location,
    "get_forecast": get_forecast,
    "compute_heat_stress": compute_heat_stress,
}

# Converse API tool definitions. The descriptions are what the model reads to choose tools.
TOOL_SPECS = [
    {"toolSpec": {
        "name": "find_location",
        "description": "Look up coordinates for a Victorian suburb, town or street name. "
                       "Use this whenever the user names a place instead of giving coordinates.",
        "inputSchema": {"json": {
            "type": "object",
            "properties": {"place_name": {"type": "string", "description": "e.g. 'Docklands' or 'Sunshine West'"}},
            "required": ["place_name"],
        }},
    }},
    {"toolSpec": {
        "name": "get_forecast",
        "description": "Get the peak temperature forecast for a location in Victoria on one date. "
                       "Returns the forecast maximum, dew point and wind speed.",
        "inputSchema": {"json": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "date": {"type": "string", "description": "YYYY-MM-DD, within the next 14 days"},
            },
            "required": ["latitude", "longitude", "date"],
        }},
    }},
    {"toolSpec": {
        "name": "compute_heat_stress",
        "description": "Calculate apparent temperature and an estimated WBGT. Pass forecast_max_c, "
                       "dew_point_c and wind_speed_ms from get_forecast.",
        "inputSchema": {"json": {
            "type": "object",
            "properties": {
                "temperature_c": {"type": "number"},
                "dew_point_c": {"type": "number"},
                "wind_speed_ms": {"type": "number"},
            },
            "required": ["temperature_c", "dew_point_c", "wind_speed_ms"],
        }},
    }},
]
