import joblib
import json
import os
import sys
import numpy as np
import pandas as pd
import pickle
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
        rmse_xgb, mae_xgb, r2_xgb, mape_xgb, max_err_xgb, history_xgb, preds_xgb, test_idx_xgb, y_test_xgb, xgb_model = train_xgboost_model(merged_df, features, target)
        rmse_lstm, mae_lstm, r2_lstm, mape_lstm, max_err_lstm, history_lstm, preds_lstm, test_idx_lstm, y_test_lstm, lstm_model = train_lstm_model(merged_df, features, target)

        # Define metrics output path
        metrics_path = os.path.join("results", "metrics_single.csv")
        os.makedirs("results", exist_ok=True)

        # Save metrics to CSV
        save_metrics_csv(
            metrics_path,
            [event_key, ticker, "LSTM", f"{rmse_lstm:.4f}"],
            header=["event_key", "ticker", "model", "rmse", "mae", "r2", "mape", "max_error"]
        )
        save_metrics_csv(
            metrics_path,
            [event_key, ticker, "XGBoost", f"{rmse_xgb:.4f}"]
        )

        # Save models
        model_dir = "single_models"
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"{event_key}_{ticker}_xgb.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(xgb_model, f)
        model_path = os.path.join(model_dir, f"{event_key}_{ticker}_lstm.keras")
        lstm_model.save(model_path)

        plot_predictions_separately(test_idx_lstm, y_test_lstm, preds_lstm, test_idx_xgb, y_test_xgb, preds_xgb, ticker, event_key, save_dir="plots_single_event")


def run_cross_event_analysis(event_type, api_key):
    """
    Run analysis for all events of a given disaster type (e.g., all hurricanes).
    Saves model results and summary metrics for each.
    """
    print(f"\nRunning cross-event analysis for all {event_type} events...\n")

    for event_key, event in EVENTS.items():
        if event['type'].lower() != event_type.lower():
            continue

        print(f"\n=== {event['name']} ({event_key}) ===")

        market = event['index']
        tickers = event['sector_etfs']
        start_date = event['start_date']
        end_date = event['end_date']
        event_date = event['event_date']
        lat = event['location']['lat']
        lon = event['location']['lon']
        disaster_type = event['type']

        try:
            market_df = fetch_market_data([market], start_date, end_date)[market]
            sector_dict = fetch_market_data(tickers, start_date, end_date)
        except Exception as e:
            print(f"Failed to fetch market data for {event_key}: {e}")
            continue

        estimation_window = market_df.index[market_df.index < event_date][-30:]

        try:
            model_params = estimate_market_model(market_df, sector_dict, estimation_window)
            abnormal_returns = compute_abnormal_returns(market_df, sector_dict, model_params)
            car = compute_car(abnormal_returns)
        except Exception as e:
            print(f"Modeling error for {event_key}: {e}")
            continue

        weather_df = fetch_visualcrossing_weather(api_key, lat, lon, start_date, end_date, disaster_type)
        first_sector = list(abnormal_returns.keys())[0]
        common_index = abnormal_returns[first_sector].index

        for df in abnormal_returns.values():
            common_index = common_index.intersection(df.index)
        weather_df = weather_df.reindex(common_index).ffill().bfill()

        for ticker in tickers:
            try:
                ar_series = abnormal_returns.get(ticker)
                if ar_series is None:
                    print(f"Missing abnormal returns for {ticker}")
                    continue

                merged_df = pd.concat([ar_series, weather_df], axis=1).dropna()
                merged_df.rename(columns={ticker: 'abnormal_return'}, inplace=True)

                features = EVENT_FEATURES.get(disaster_type, ['temp', 'humidity', 'precip', 'windspeed', 'pressure'])
                target = 'abnormal_return'

                rmse_xgb, mae_xgb, r2_xgb, mape_xgb, max_err_xgb, history_xgb, preds_xgb, test_idx_xgb, y_test_xgb, xgb_model = train_xgboost_model(merged_df, features, target)
                rmse_lstm, mae_lstm, r2_lstm, mape_lstm, max_err_lstm, history_lstm, preds_lstm, test_idx_lstm, y_test_lstm, lstm_model = train_lstm_model(merged_df, features, target)

                metrics_path = os.path.join("results", "metrics_cross.csv")
                os.makedirs("results", exist_ok=True)

                save_metrics_csv(
                    metrics_path,
                    [event_type, ticker, "LSTM", f"{rmse_lstm:.4f}"],
                    header=["event_type", "ticker", "model", "rmse", "mae", "r2", "mape", "max_error"]
                )
                save_metrics_csv(
                    metrics_path,
                    [event_type, ticker, "XGBoost", f"{rmse_xgb:.4f}"]
                )

                # Save models
                model_dir = "cross_models"
                os.makedirs(model_dir, exist_ok=True)
                model_path = os.path.join(model_dir, f"{event_type}_{ticker}_xgb.pkl")
                with open(model_path, "wb") as f:
                    pickle.dump(model, f)
                model_path = os.path.join(model_dir, f"{event_type}_{ticker}_lstm.keras")
                model.save(model_path)

                plot_training_history(history_xgb, "xgboost", ticker, event_type, save_dir="training_plots")
                plot_training_history(history_lstm, "lstm", ticker, event_type, save_dir="training_plots")

                plot_predictions_separately(
                    index_lstm, y_test_lstm, preds_lstm,
                    index_xgb, y_test_xgb, preds_xgb,
                    ticker, event_type, save_dir="plots_cross_event"
                )

                print(f"Saved predictions for {ticker} | RMSE XGB: {rmse_xgb:.4f}, LSTM: {rmse_lstm:.4f}")
            except Exception as e:
                print(f"Error processing {ticker} for {event_type}: {e}")
                continue

    print(f"\nFinished cross-event analysis for {event_type} events.\n")
