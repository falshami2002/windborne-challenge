import time
import requests
import pandas as pd
from wind import forecast_wind 

BASE_URL = "https://a.windbornesystems.com/treasure/{:02d}.json"
OUTPUT_FILE = "windborne_constellation.ndjson"

def fetch_json(hour, retries=2, delay=2.0):
    """Fetch one hour of JSON with retries on failure."""
    url = BASE_URL.format(hour)
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Failure fetching {url}: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                print(f"Giving up on {url}")
                return None

def get_ballon_data():
    rows = []

    # Just doing 2 hours and 100 ballons each for testing as open meteo has rate limits
    for hour in range(0, 2):
        data = fetch_json(hour)
        if not isinstance(data, list):
            continue

        for idx, balloon in enumerate(data[:100]):
            if not (isinstance(balloon, list) and len(balloon) >= 3):
                continue

            lat, lon, alt = balloon[:3]
            balloon_id = idx + 1
            
            wind_data = forecast_wind(balloon, hour)

            rows.append({
                "balloon_id": balloon_id,
                "hour_ago": hour,
                "lat": lat,
                "lon": lon,
                "alt_km": alt,
                "wind_speed": wind_data["wind_speed"],
                "wind_direction": wind_data["wind_direction"]
            })
            time.sleep(0.2) # To avoid hitting rate limits

        print(f"Fetched hour {hour:02d}") 

    df = pd.DataFrame(rows)

    print(df.head())
    print(f"\nTotal rows: {len(df)} | Unique balloons: {df['balloon_id'].nunique()}")
    df.to_csv("windborne_constellation.csv", index=False)
    return df