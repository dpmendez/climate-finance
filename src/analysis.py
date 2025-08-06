import joblib
import json
import os
import sys
import numpy as np
import pandas as pd
import pickle
import traceback
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, max_error
from market import fetch_market_data
from models import train_xgboost_model, train_lstm_model
from returns import *
from utils import save_metrics_csv
from viz import plot_predictions_separately, plot_training_history
from weather import fetch_visualcrossing_weather

from config.events import EVENTS, EVENT_FEATURES

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
    save_market_model_params(model_params, event_key, 'models/single')

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
        merged_df.sort_index(inplace=True)
        print(f"Merged length for {ticker}: {len(merged_df)}")

        features = weather_df.columns.tolist()
        target = 'abnormal_return'

        print("Columns in merged_df:", merged_df.columns.tolist())
        rmse_xgb, mae_xgb, r2_xgb, mape_xgb, max_err_xgb, history_xgb, preds_xgb, test_idx_xgb, y_test_xgb, xgb_model = train_xgboost_model(merged_df, features, target)
        rmse_lstm, mae_lstm, r2_lstm, mape_lstm, max_err_lstm, history_lstm, preds_lstm, test_idx_lstm, y_test_lstm, lstm_model = train_lstm_model(merged_df, features, target)

        # Save metrics to CSV
        metrics_dir = "metrics/single"
        os.makedirs(metrics_dir, exist_ok=True)
        save_metrics_csv(
            metrics_dir + "/metrics_" + ticker + "_" + event_key + ".csv",
            [event_key, ticker, "LSTM", f"{rmse_lstm:.4f}", f"{mae_lstm:.4f}", f"{r2_lstm:.4f}", f"{mape_lstm:.4f}", f"{max_err_lstm:.4f}"],
            header=["event_key", "ticker", "lstm_model", "rmse_lstm", "mae_lstm", "r2_lstm", "mape_lstm", "max_err_lstm"]
        )
        save_metrics_csv(
            metrics_dir + "/metrics_" + ticker + "_" + event_key + ".csv",
            [event_key, ticker, "XGBoost", f"{rmse_xgb:.4f}", f"{mae_xgb:.4f}", f"{r2_xgb:.4f}", f"{mape_xgb:.4f}", f"{max_err_xgb:.4f}"],
            header=["event_key", "ticker", "xgb_model", "rmse_xgb", "mae_xgb", "r2_xgb", "mape_xgb", "max_err_xgb"]
        )

        # Save models
        model_dir = "models/single"
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"{event_key}_{ticker}_xgb.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(xgb_model, f)
        model_path = os.path.join(model_dir, f"{event_key}_{ticker}_lstm.keras")
        lstm_model.save(model_path)

        # Save training plots
        training_dir = "plots/training/single"
        plot_training_history(history_xgb, "xgboost", ticker, event_key, save_dir=training_dir)
        plot_training_history(history_lstm, "lstm", ticker, event_key, save_dir=training_dir)

        plot_predictions_separately(
            test_idx_lstm, y_test_lstm, preds_lstm,
            test_idx_xgb, y_test_xgb, preds_xgb, 
            ticker, event_key, save_dir="plots/test/single"
        )


def run_cross_event_analysis(event_type, api_key):
    """
    Run analysis for all events of a given disaster type (e.g., all hurricanes).
    Saves model results and summary metrics for each.
    """
    print(f"\nRunning cross-event analysis for all {event_type} events...\n")

    ar_by_event = {}  # To hold abnormal returns per event
    weather_by_event = {}
    tickers_set = set()

    # Collect relevant data
    for event_key, event in EVENTS.items():
        if event['type'].lower() != event_type.lower():
            continue

        print(f"Processing event: {event['name']} ({event_key})")

        market = event['index']
        tickers = event['sector_etfs']
        start_date = event['start_date']
        end_date = event['end_date']
        event_date = event['event_date']
        lat = event['location']['lat']
        lon = event['location']['lon']
        disaster_type = event['type']

        tickers_set.update(tickers)

        # Get market data
        try:
            market_df = fetch_market_data([market], start_date, end_date)[market]
            sector_dict = fetch_market_data(tickers, start_date, end_date)
        except Exception as e:
            print(f"Failed to fetch market data for {event_key}: {e}")
            continue

        estimation_window = market_df.index[market_df.index < event_date][-30:]

        # Compute market model parameters and abnormal returns
        try:
            model_params = estimate_market_model(market_df, sector_dict, estimation_window)
            save_market_model_params(model_params, event_type, 'models/cross')
            abnormal_returns = compute_abnormal_returns(market_df, sector_dict, model_params)
            ar_by_event[event_key] = abnormal_returns
        except Exception as e:
            print(f"Modeling error for {event_key}: {e}")
            traceback.print_exc()
            continue

        # Store ARs with relative day index
        rel_ar_dict = {}
        for ticker, series in abnormal_returns.items():
            relative_idx = (series.index - pd.to_datetime(event_date)).days
            series.index = relative_idx
            rel_ar_dict[ticker] = series
        ar_by_event[event_key] = rel_ar_dict

        # Get weather data and align to relative days
        weather_df = fetch_visualcrossing_weather(api_key, lat, lon, start_date, end_date, disaster_type)

        relative_days = (weather_df.index - pd.to_datetime(event_date)).days
        weather_df['relative_day'] = relative_days
        weather_df.set_index('relative_day', inplace=True)
        weather_by_event[event_key] = weather_df


    # Compute average abnormal return
    aar_dict = {}
    for ticker in tickers_set:
        ar_series_list = []
        for rel_ar in ar_by_event.values():
            if ticker in rel_ar:
                ar_series_list.append(rel_ar[ticker])
        if ar_series_list:
            aar_dict[ticker] = pd.concat(ar_series_list, axis=1).mean(axis=1)

    # Compute comulative average abnormal return
    caar_dict = {ticker: aar.cumsum() for ticker, aar in aar_dict.items()}
    print(f"\nComputed average abnormal returns and CAAR for {event_type} events.\n")

    # Compute average weather
    avg_weather_df = pd.DataFrame()
    for event_weather in weather_by_event.values():
        avg_weather_df = avg_weather_df.add(event_weather, fill_value=0)
    if not weather_by_event:
        print("No weather data to average. Exiting.")
        return
    avg_weather_df /= len(weather_by_event)
    print(f"\nComputed average weather for {event_type} events.\n")


    for ticker, aar_series in aar_dict.items():
        try:
            merged_df = pd.concat([aar_series.rename('abnormal_return'), avg_weather_df], axis=1).dropna()

            features = EVENT_FEATURES.get(disaster_type, ['temp', 'humidity', 'precip', 'windspeed', 'pressure'])
            target = 'abnormal_return'

            rmse_xgb, mae_xgb, r2_xgb, mape_xgb, max_err_xgb, history_xgb, preds_xgb, test_idx_xgb, y_test_xgb, xgb_model = train_xgboost_model(merged_df, features, target)
            rmse_lstm, mae_lstm, r2_lstm, mape_lstm, max_err_lstm, history_lstm, preds_lstm, test_idx_lstm, y_test_lstm, lstm_model = train_lstm_model(merged_df, features, target)

            # Save metrics to CSV
            metrics_dir = "metrics/cross"
            os.makedirs(metrics_dir, exist_ok=True)
            save_metrics_csv(
                metrics_dir + "/metrics_" + ticker + "_" + event_type.lower() + ".csv",
                [event_type, ticker, "LSTM", f"{rmse_lstm:.4f}", f"{mae_lstm:.4f}", f"{r2_lstm:.4f}", f"{mape_lstm:.4f}", f"{max_err_lstm:.4f}"],
                header=["event_type", "ticker", "lstm_model", "rmse_lstm", "mae_lstm", "r2_lstm", "mape_lstm", "max_err_lstm"]
            )
            save_metrics_csv(
                metrics_dir + "/metrics_" + ticker + "_" + event_type.lower() + ".csv",
                [event_type, ticker, "XGBoost", f"{rmse_xgb:.4f}", f"{mae_xgb:.4f}", f"{r2_xgb:.4f}", f"{mape_xgb:.4f}", f"{max_err_xgb:.4f}"],
                header=["event_type", "ticker", "xgb_model", "rmse_xgb", "mae_xgb", "r2_xgb", "mape_xgb", "max_err_xgb"]
            )

            # Save models
            model_dir = "models/cross"
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f"{event_type}_{ticker}_xgb.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(xgb_model, f)
            model_path = os.path.join(model_dir, f"{event_type}_{ticker}_lstm.keras")
            lstm_model.save(model_path)

            # Save training plots
            training_dir = "plots/training/cross"
            os.makedirs(training_dir, exist_ok=True)
            plot_training_history(history_xgb, "xgboost", ticker, event_type, save_dir=training_dir)
            plot_training_history(history_lstm, "lstm", ticker, event_type, save_dir=training_dir)

            plot_predictions_separately(
                test_idx_lstm, y_test_lstm, preds_lstm,
                test_idx_xgb, y_test_xgb, preds_xgb,
                ticker, event_type, save_dir="plots/test/cross"
            )

            print(f"Saved predictions for {ticker} | RMSE XGB: {rmse_xgb:.4f}, LSTM: {rmse_lstm:.4f}")
            
        except Exception as e:
            print(f"Error processing {ticker} for {event_type}: {e}")
            traceback.print_exc()
            continue

    print(f"\nFinished cross-event analysis for {event_type} events.\n")
