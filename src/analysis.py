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
import matplotlib.pyplot as plt
import pandas as pd
from market import fetch_market_data
from models import train_xgboost_model, train_lstm_model
from weather import fetch_visualcrossing_weather
from returns import *

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


def plot_predictions_separately(index_lstm, actual_lstm, preds_lstm,
                                index_xgb, actual_xgb, preds_xgb,
                                ticker, event_key, save_dir="plots"):

    os.makedirs(save_dir, exist_ok=True)

    fig, axs = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    axs[0].plot(index_lstm, actual_lstm, label='Actual', color='black')
    axs[0].plot(index_lstm, preds_lstm, label='LSTM', linestyle='--')
    axs[0].set_title(f"LSTM: {ticker} ({event_key})")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(index_xgb, actual_xgb, label='Actual', color='black')
    axs[1].plot(index_xgb, preds_xgb, label='XGBoost', linestyle=':')
    axs[1].set_title(f"XGBoost: {ticker} ({event_key})")
    axs[1].legend()
    axs[1].grid(True)

    plt.suptitle("Abnormal Return Predictions")
    plt.tight_layout()
    #plt.show()

    save_path = os.path.join(save_dir, f"{ticker}_{event_key}.png")
    plt.savefig(save_path)
    plt.close()