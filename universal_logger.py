import requests
import pandas as pd
from datetime import datetime
import os

# --- Step 1: Define Universal Orlando parks explicitly ---
PARK_IDS = {
    "Universal Studios Florida": 65,
    "Islands of Adventure": 64,
    "Volcano Bay": 67,
    "Epic Universe": 334
}

# Orlando coordinates
lat, lon = 28.4743, -81.4678

# --- Step 2: Get weather data (temp in °F, wind in mph, rain probability) ---
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

# --- Step 3: Collect ride wait times ---
records = []

for park_name, park_id in PARK_IDS.items():
    url = f"https://queue-times.com/parks/{park_id}/queue_times.json"
    data = requests.get(url).json()

    if "lands" in data:  # normal case
        for land in data["lands"]:
            for ride in land.get("rides", []):
                records.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "park_id": park_id,
                    "park": park_name,
                    "ride": ride["name"],
                    "wait_time": ride["wait_time"],
                    "is_open": ride["is_open"],
                    "temp_f": temp_f,
                    "wind_speed_mph": wind,
                    "rain_probability": rain_prob,
                    "weather_time": weather_time
                })
    elif "rides" in data:  # fallback if flat
        for ride in data["rides"]:
            records.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "park_id": park_id,
                "park": park_name,
                "ride": ride["name"],
                "wait_time": ride["wait_time"],
                "is_open": ride["is_open"],
                "temp_f": temp_f,
                "wind_speed_mph": wind,
                "rain_probability": rain_prob,
                "weather_time": weather_time
            })

# --- Step 4: Save to one master CSV ---
df = pd.DataFrame(records)
csv_path = "universal_wait_times.csv"

if os.path.exists(csv_path):
    df.to_csv(csv_path, mode="a", header=False, index=False)
else:
    df.to_csv(csv_path, index=False)

print(f"✅ Logged {len(df)} rides at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} into {csv_path}")