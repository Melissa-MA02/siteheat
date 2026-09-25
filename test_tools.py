from datetime import date, timedelta
from tools import find_location, get_corrected_forecast, compute_heat_stress

place = find_location("Docklands")
print("1. Location:", place)

tomorrow = (date.today() + timedelta(days=1)).isoformat()
forecast = get_corrected_forecast(place["latitude"], place["longitude"], tomorrow)
print("2. Forecast:", forecast)

stress = compute_heat_stress(forecast["corrected_max_c"], forecast["dew_point_c"], forecast["wind_speed_ms"])
print("3. Heat stress:", stress)

print("4. Outside Victoria:", get_corrected_forecast(-27.47, 153.02, tomorrow))  # Brisbane