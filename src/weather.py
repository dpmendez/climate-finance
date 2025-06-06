import requests
import pandas as pd

# Mapping of disaster type to relevant weather variables
relevant_vars = {
    "Hurricane": ['temp', 'humidity', 'precip', 'windspeed', 'pressure'],
    "Wildfire": ['temp', 'humidity', 'precip', 'windspeed', 'solarradiation'],
    "Flood": ['temp', 'humidity', 'precip'],
    "WinterStorm": ['temp', 'humidity', 'precip', 'windspeed', 'pressure'],
}

def fetch_visualcrossing_weather(api_key, lat, lon, start_date, end_date, disaster_type):

    # Fall back to a default if type is not found
    weather_vars = relevant_vars.get(disaster_type, ['temp', 'humidity', 'precip', 'windspeed'])

    # API call
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{start_date}/{end_date}?unitGroup=metric&key={api_key}&include=days"
    r = requests.get(url)
    r.raise_for_status()  # good practice for catching request errors

    data = r.json()['days']
    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

    # Only return relevant columns that exist in the DataFrame
    available_vars = [var for var in weather_vars if var in df.columns]
    return df[available_vars]
  