import requests
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
  