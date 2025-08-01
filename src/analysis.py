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
        metrics_dir = "results"
        os.makedirs(metrics_dir, exist_ok=True)

       # Save metrics to CSV
        save_metrics_csv(
            "results/metrics_" + ticker + "_" + event_key + ".csv",
            [event_key, ticker, "LSTM", f"{rmse_lstm:.4f}", f"{mae_lstm:.4f}", f"{r2_lstm:.4f}", f"{mape_lstm:.4f}", f"{max_err_lstm:.4f}"],
            header=["event_key", "ticker", "lstm_model", "rmse_lstm", "mae_lstm", "r2_lstm", "mape_lstm", "max_err_lstm"]
        )
        save_metrics_csv(
            "results/metrics_" + ticker + "_" + event_key + ".csv",
            [event_key, ticker, "XGBoost", f"{rmse_xgb:.4f}", f"{mae_xgb:.4f}", f"{r2_xgb:.4f}", f"{mape_xgb:.4f}", f"{max_err_xgb:.4f}"],
            header=["event_key", "ticker", "xgb_model", "rmse_xgb", "mae_xgb", "r2_xgb", "mape_xgb", "max_err_xgb"]
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

    pooled_market_df = []
    pooled_sector_dict = {}
    sector_universe = set()

    # Collect relevant data
    for event_key, event in EVENTS.items():
        if event['type'].lower() != event_type.lower():
            continue

        print(f"Pooling event: {event['name']} ({event_key})")

        market = event['index']
        tickers = event['sector_etfs']
        start_date = event['start_date']
        end_date = event['end_date']
        event_date = event['event_date']

        try:
            market_df = fetch_market_data([market], start_date, end_date)[market]
            sector_dict = fetch_market_data(tickers, start_date, end_date)
        except Exception as e:
            print(f"Failed to fetch market data for {event_key}: {e}")
            continue

        estimation_window = market_df.index[market_df.index < event_date][-30:]

        pooled_market_df.append(market_df.loc[estimation_window])

        for ticker in tickers:
            sector_universe.add(ticker)
            if ticker not in pooled_sector_dict:
                pooled_sector_dict[ticker] = []
            if ticker in sector_dict:
                pooled_sector_dict[ticker].append(sector_dict[ticker].loc[estimation_window])


    # Concatenate pooled data
    full_market_df = pd.concat(pooled_market_df).sort_index()
    full_sector_dict = {
        ticker: pd.concat(dfs).sort_index()
        for ticker, dfs in pooled_sector_dict.items()
    }

    # Estimate one market model across all events
    try:
        model_params = estimate_market_model(full_market_df, full_sector_dict, estimation_window)
        print(f"Got market model parameters for {event_type}.")
    except Exception as e:
        print(f"Modeling error for {event_type}.")
        continue


    # Second pass: run per-event modeling using shared model
    for event_key, event in EVENTS.items():
        if event['type'].lower() != event_type.lower():
            continue

        market = event['index']
        tickers = event['sector_etfs']
        start_date = event['start_date']
        end_date = event['end_date']
        event_date = event['event_date']
        lat = event['location']['lat']
        lon = event['location']['lon']
        disaster_type = event['type']

        print(f"\n=== {event['name']} ({event_key}) ===")

        try:
            market_df = fetch_market_data([market], start_date, end_date)[market]
            sector_dict = fetch_market_data(tickers, start_date, end_date)
        except Exception as e:
            print(f"Failed to fetch market data for {event_key}: {e}")
            continue

        try:
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

                if 'Return' in merged_df.columns:
                  merged_df.rename(columns={'Return': 'abnormal_return'}, inplace=True)
                else:
                    merged_df.rename(columns={ticker: 'abnormal_return'}, inplace=True)

                if 'abnormal_return' not in merged_df.columns:
                    print(f"Skipping {ticker}: abnormal return column not found.")
                    continue

                features = EVENT_FEATURES.get(disaster_type, ['temp', 'humidity', 'precip', 'windspeed', 'pressure'])
                target = 'abnormal_return'

                rmse_xgb, mae_xgb, r2_xgb, mape_xgb, max_err_xgb, history_xgb, preds_xgb, test_idx_xgb, y_test_xgb, xgb_model = train_xgboost_model(merged_df, features, target)
                rmse_lstm, mae_lstm, r2_lstm, mape_lstm, max_err_lstm, history_lstm, preds_lstm, test_idx_lstm, y_test_lstm, lstm_model = train_lstm_model(merged_df, features, target)

                metrics_dir = "results"
                os.makedirs(metrics_dir, exist_ok=True)

                # Save metrics to CSV
                save_metrics_csv(
                    "results/metrics_" + ticker + "_" + event_type.lower() + ".csv",
                    [event_type, ticker, "LSTM", f"{rmse_lstm:.4f}", f"{mae_lstm:.4f}", f"{r2_lstm:.4f}", f"{mape_lstm:.4f}", f"{max_err_lstm:.4f}"],
                    header=["event_key", "ticker", "lstm_model", "rmse_lstm", "mae_lstm", "r2_lstm", "mape_lstm", "max_err_lstm"]
                )
                save_metrics_csv(
                    "results/metrics_" + ticker + "_" + event_type.lower() + ".csv",
                    [event_type, ticker, "XGBoost", f"{rmse_xgb:.4f}", f"{mae_xgb:.4f}", f"{r2_xgb:.4f}", f"{mape_xgb:.4f}", f"{max_err_xgb:.4f}"],
                    header=["event_key", "ticker", "xgb_model", "rmse_xgb", "mae_xgb", "r2_xgb", "mape_xgb", "max_err_xgb"]
                )

                # Save models
                model_dir = "cross_models"
                os.makedirs(model_dir, exist_ok=True)
                model_path = os.path.join(model_dir, f"{event_type}_{ticker}_xgb.pkl")
                with open(model_path, "wb") as f:
                    pickle.dump(xgb_model, f)
                model_path = os.path.join(model_dir, f"{event_type}_{ticker}_lstm.keras")
                lstm_model.save(model_path)

                plot_training_history(history_xgb, "xgboost", ticker, event_type, save_dir="training_plots")
                plot_training_history(history_lstm, "lstm", ticker, event_type, save_dir="training_plots")

                plot_predictions_separately(
                    test_idx_lstm, y_test_lstm, preds_lstm,
                    test_idx_xgb, y_test_xgb, preds_xgb,
                    ticker, event_type, save_dir="plots_cross_event"
                )

                print(f"Saved predictions for {ticker} | RMSE XGB: {rmse_xgb:.4f}, LSTM: {rmse_lstm:.4f}")
            except Exception as e:
                print(f"Error processing {ticker} for {event_type}: {e}")
                traceback.print_exc()
                continue

    print(f"\nFinished cross-event analysis for {event_type} events.\n")
