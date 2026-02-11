import os
import requests
import sys
import pandas as pd

# Add the root project folder to the module path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from config.events import EVENTS, EVENT_FEATURES

def fetch_visualcrossing_weather(api_key, lat, lon, start_date, end_date, disaster_type):

    # Fall back to a default if type is not found
    weather_vars = EVENT_FEATURES.get(disaster_type, ['temp', 'humidity', 'precip', 'windspeed'])

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


def compute_weather_deltas(weather_df, baseline_end_date):
    """
    Compute weather deltas: deviation from pre-event baseline.
    Baseline = mean of all weather values before baseline_end_date (the event_date).

    Returns DataFrame with same shape, columns prefixed with 'delta_'.
    """
    baseline = weather_df.loc[weather_df.index < baseline_end_date].mean()
    delta_df = weather_df.subtract(baseline)
    delta_df.columns = [f"delta_{col}" for col in delta_df.columns]
    return delta_df