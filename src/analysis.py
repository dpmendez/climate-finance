import sys
import os

# Add the root project folder to the module path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from config.events import EVENTS

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from models import train_xgboost_model, train_lstm_model
from returns import compute_abnormal_returns, estimate_market_model
from market import fetch_market_data
from weather import fetch_visualcrossing_weather


def run_event_analysis(event_key, api_key):
    event = EVENTS[event_key]
    print(f"Analyzing {event['name']}...")

    market = event['index']
    tickers = event['sector_etfs']
    start_date = event['start_date']
    end_date = event['end_date']
    event_date = event['event_date']
    lat = event['location']['lat']
    lon = event['location']['lon']
    disaster_type = event['type']

    market_df = fetch_market_data([market], start_date, end_date)[market]
    sector_dict = fetch_market_data(tickers, start_date, end_date)

    # Define estimation window (30 days before event)
    estimation_window = market_df.index[market_df.index < event_date][-30:]

    # Estimate market model
    model_params = estimate_market_model(market_df, sector_dict, estimation_window)

    # Compute AR and CAR
    abnormal_returns = compute_abnormal_returns(market_df, sector_dict, model_params)
    car = compute_car(abnormal_returns)

    # Merge AR with weather, prediction, etc.
    weather_df = fetch_visualcrossing_weather(api_key, lat, lon, start_date, end_date, disaster_type)

    first_sector = list(abnormal_returns.keys())[0]
    common_index = abnormal_returns[first_sector].index

    # sectors are forced to have the same dates so we can use this line ...
    # weather_df = weather_df.reindex(abnormal_returns[first_sector].index).ffill().bfill()
    # but the intersection is safer
    for df in abnormal_returns.values():
        common_index = common_index.intersection(df.index)
    
    weather_df = weather_df.reindex(common_index).ffill().bfill()

    for ticker in tickers:
        print(f"\n--- {ticker} ---")
        merged_df = pd.concat([ar_df[[ticker]], weather_df], axis=1).dropna()
        merged_df.rename(columns={ticker: 'abnormal_return'}, inplace=True)

        features = weather_df.columns.tolist()
        target = 'abnormal_return'

        rmse_xgb, preds_xgb = train_xgboost_model(merged_df, features, target)
        print(f"XGBoost RMSE: {rmse_xgb:.4f}")

        rmse_lstm, preds_lstm, test_idx, y_test = train_lstm_model(merged_df, features, target)
        print(f"LSTM RMSE: {rmse_lstm:.4f}")

        plot_predictions(test_idx, y_test, preds_lstm, preds_xgb, ticker, event_key)


def plot_predictions(index, actual, lstm_preds, xgb_preds, ticker, event_key):
    plt.figure(figsize=(12, 6))
    plt.plot(index, actual, label='Actual', color='black')
    plt.plot(index, lstm_preds, label='LSTM', linestyle='--')
    plt.plot(index, xgb_preds, label='XGBoost', linestyle=':')
    plt.title(f"Predicted vs Actual Abnormal Returns: {ticker} ({event_key})")
    plt.xlabel("Date")
    plt.ylabel("Abnormal Return")
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()