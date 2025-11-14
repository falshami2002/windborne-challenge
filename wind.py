# BOILERPLATE CODE OBTAINED FROM OPEN-METEO REQUESTS DOCUMENTATION AND EDITED 
# https://open-meteo.com/en/docs?hourly=wind_speed_30hPa,wind_direction_30hPa
import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

from datetime import datetime, timezone, timedelta

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def forecast_wind(positions: list, hours_ago: int) -> dict:
    # Extract latitudes, longitudes, and height from position
    latitude = positions[0]
    longitude = positions[1]
    height = positions[2]  
    # Convert height in km to pressure level in hPa
    pressure_level = height_to_pressure_helper(height)

    # Prepare API request
    target = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).replace(minute=0, second=0, microsecond=0)
    start_date = (target - timedelta(days=1)).date()
    end_date = target.date()

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [f"wind_speed_{pressure_level}hPa", f"wind_direction_{pressure_level}hPa"],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": "UTC",
        "timeformat": "unixtime"
    }
    resp = openmeteo.weather_api(url, params=params)[0]
    hr = resp.Hourly()

    # Construct time axis
    t0 = pd.to_datetime(hr.Time(), unit="s", utc=True)
    t1 = pd.to_datetime(hr.TimeEnd(), unit="s", utc=True)
    times = pd.date_range(t0, t1, freq=pd.Timedelta(seconds=hr.Interval()), inclusive="left")

    df = pd.DataFrame({
        "time": times,
        "wind_speed": hr.Variables(0).ValuesAsNumpy(),
        "wind_direction": hr.Variables(1).ValuesAsNumpy(),
    })

    # Select that specific hour or nearest one if not exact
    row = df.loc[df["time"] == target]
    if row.empty:
        row = df.iloc[[((df["time"] - target).abs()).argmin()]]
    return {
            "wind_speed": float(row.iloc[0]["wind_speed"]),
            "wind_direction": float(row.iloc[0]["wind_direction"])
    }

def height_to_pressure_helper(height: int) -> int:
    # Dict of predefined heights and their corresponding pressures from open-meteo
    height = height * 1000  # Height from km to m
    height_to_pressure_dict = {
        110: 1000,
        320: 975,
        500: 950,
        800: 925,
        1000: 900,
        1500: 850,
        1900: 800,
        3000: 700,
        4200: 600,
        5600: 500,
        7200: 400,
        9200: 300,
        10400: 250,
        11800: 200,
        13500: 150,
        15800: 100,
        17700: 70,
        19300: 50,
        22000: 30
    }  
    # Find the closest height in the dictionary
    closest_height = min(height_to_pressure_dict.keys(), key=lambda h: abs(h - height))
    return height_to_pressure_dict[closest_height]

if __name__ == "__main__":
    # Example usage
    pos = [37.7749, -122.4194, 15]  # lat, lon, height in km
    hours_ago = 1
    wind_data = forecast_wind(pos, hours_ago)
    print(f"Wind data {hours_ago} hours ago at position {pos}: {wind_data}")