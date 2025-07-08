import sys
import os

# Add the root project folder to the module path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from config.events import EVENTS

import joblib
import json
import numpy as np
import pandas as pd
from market import fetch_market_data
from models import train_xgboost_model, train_lstm_model
from weather import fetch_visualcrossing_weather
from returns import *
from viz import plot_predictions_separately


def collect_cross_event_data(events_dict, api_key, disaster_type, target_ticker):
    all_data = []

    for event_key, event in events_dict.items():
        if event['type'] != disaster_type:
            continue
        if target_ticker not in event['sector_etfs']:
            continue

        print(f"Processing {event_key}...")

        try:
            market = event['index']
            tickers = event['sector_etfs']
            start_date = event['start_date']
            end_date = event['end_date']
            event_date = event['event_date']
            lat = event['location']['lat']
            lon = event['location']['lon']

            market_df = fetch_market_data([market], start_date, end_date)[market]
            sector_dict = fetch_market_data(tickers, start_date, end_date)

            # Estimation window
            estimation_window = market_df.index[market_df.index < event_date][-30:]
            model_params = estimate_market_model(market_df, sector_dict, estimation_window)

            # Compute abnormal returns
            abnormal_returns = compute_abnormal_returns(market_df, sector_dict, model_params)

            # Get weather data
            weather_df = fetch_visualcrossing_weather(api_key, lat, lon, start_date, end_date, disaster_type)

            # Align index
            ar_df = abnormal_returns[target_ticker]
            common_index = ar_df.index.intersection(weather_df.index)
            ar_df = ar_df.reindex(common_index).dropna()
            weather_df = weather_df.reindex(common_index).ffill().bfill()

            # Combine into one DataFrame
            merged_df = pd.concat([ar_df.rename('abnormal_return'), weather_df], axis=1).dropna()
            merged_df['event_key'] = event_key
            merged_df['event_type'] = disaster_type
            merged_df['ticker'] = target_ticker

            all_data.append(merged_df)

        except Exception as e:
            print(f"Failed on {event_key}: {e}")
            continue

    if all_data:
        return pd.concat(all_data)
    else:
        return pd.DataFrame()


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
    save_market_model_params(model_params, market, event_key)

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

        ar = abnormal_returns[ticker]
        if isinstance(ar, pd.DataFrame):
            ar = ar.squeeze()

        merged_df = pd.concat([ar.rename('abnormal_return'), weather_df], axis=1).dropna()
        # merged_df = pd.concat([abnormal_returns[ticker], weather_df], axis=1).dropna()
        # merged_df.rename(columns={ticker: 'abnormal_return'}, inplace=True)

        features = weather_df.columns.tolist()
        target = 'abnormal_return'

        print("Columns in merged_df:", merged_df.columns.tolist())
        rmse_xgb, preds_xgb, test_idx_xgb, y_test_xgb, xgb_model = train_xgboost_model(merged_df, features, target)
        print(f"XGBoost RMSE: {rmse_xgb:.4f}")

        rmse_lstm, preds_lstm, test_idx_lstm, y_test_lstm, lstm_model = train_lstm_model(merged_df, features, target)
        print(f"LSTM RMSE: {rmse_lstm:.4f}")

        # Save XGBoost model if desired
        joblib.dump(xgb_model, f"models/{event_key}_{ticker}_xgb.pkl")

        # Save LSTM model if desired
        lstm_model.save(f"models/{event_key}_{ticker}_lstm.keras")

        #plot_predictions(test_idx, y_test, preds_lstm, preds_xgb, ticker, event_key)
        plot_predictions_separately(test_idx_lstm, y_test_lstm, preds_lstm, test_idx_xgb, y_test_xgb, preds_xgb, ticker, event_key)