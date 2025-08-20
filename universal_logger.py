import requests
import pandas as pd
from datetime import datetime
import os

# Park IDs for Universal Orlando (from Queue-Times API)
PARK_IDS = {
    "Epic Universe": 68,
    "Islands of Adventure": 66,
    "Universal Studios Florida": 65
}

# Orlando coordinates
lat, lon = 28.4743, -81.4678

# Get weather: current + hourly rain probability (temp in °F)
weather_url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}"
    f"&current_weather=true"
    f"&hourly=precipitation_probability"
    f"&forecast_days=1"
    f"&temperature_unit=fahrenheit"
    f"&windspeed_unit=mph"
)
weather_data = requests.get(weather_url).json()

# Current weather
current_weather = weather_data["current_weather"]
temp_f = current_weather["temperature"]
wind = current_weather["windspeed"]
weather_time = current_weather["time"]

# Rain probability for current hour
hourly_time = weather_data["hourly"]["time"]
hourly_precip = weather_data["hourly"]["precipitation_probability"]

rain_prob = None
if weather_time in hourly_time:
    idx = hourly_time.index(weather_time)
    rain_prob = hourly_precip[idx]

records = []

# Fetch rides wait times
for park_name, park_id in PARK_IDS.items():
    url = f"https://queue-times.com/parks/{park_id}/queue_times.json"
    data = requests.get(url).json()

    for land in data["lands"]:
        for ride in land["rides"]:
            records.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "park": park_name,
                "ride": ride["name"],
                "wait_time": ride["wait_time"],
                "is_open": ride["is_open"],
                "temp_f": temp_f,
                "wind_speed_mph": wind,
                "rain_probability": rain_prob,
                "weather_time": weather_time
            })

# Create DataFrame
df = pd.DataFrame(records)

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Save to daily CSV inside /data/
date_str = datetime.now().strftime("%Y-%m-%d")
csv_path = f"data/{date_str}.csv"

# Append mode: if file exists, add rows; else create new
if os.path.exists(csv_path):
    df.to_csv(csv_path, mode="a", header=False, index=False)
else:
    df.to_csv(csv_path, index=False)

print(f"✅ Logged {len(df)} rides at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} into {csv_path}")
