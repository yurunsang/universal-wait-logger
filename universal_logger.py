import requests
import pandas as pd
from datetime import datetime

# Park IDs for Universal Orlando (from Queue-Times API)
PARK_IDS = {
    "Epic Universe": 68,  # confirm with parks.json
    "Islands of Adventure": 66,
    "Universal Studios Florida": 65
}

records = []

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
                "is_open": ride["is_open"]
            })

# Convert to DataFrame
df = pd.DataFrame(records)

# Append to CSV
df.to_csv("universal_wait_times.csv", mode="a", header=not pd.io.common.file_exists("universal_wait_times.csv"), index=False)

print(f"Logged {len(df)} rides at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
