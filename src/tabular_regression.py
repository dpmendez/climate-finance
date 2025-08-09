import sys
import os
import argparse
import pickle
import numpy as np
import pandas as pd

# Add config directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.events import EVENTS, EVENT_FEATURES
from models import train_xgboost_model
from utils import save_metrics_csv
from viz import plot_training_history, plot_predictions


def run_tabular_regression(data_dir, event_type, features=["temperature"], target="abnormal_return"):
    """
    Run tabular regression for each sector/ticker using saved AAR + weather CSVs.
    """
    all_results = {}

    for fname in os.listdir(data_dir):
        if not fname.endswith(".csv"):
            continue

        ticker = fname.split("_")[0]
        csv_path = os.path.join(data_dir, fname)

        df = pd.read_csv(csv_path, index_col=0).dropna()

        if not all(col in df.columns for col in features + [target]):
            print(f"Skipping {ticker}: missing required columns")
            continue

        print(f"\nRunning tabular regression for {ticker}...\n")

        try:
            rmse, mae, r2, mape, max_err, history, y_pred, idx, y_true, model  = train_xgboost_model(df, features, target)
            all_results[ticker] = {"RMSE": rmse, "MAE": mae, "R2": r2}

            # === Directories ===
            metrics_dir = "metrics/tabular"
            model_dir   = "models/tabular"
            training_dir = "plots/training/tabular"
            test_dir     = "plots/test/tabular"
            os.makedirs(metrics_dir, exist_ok=True)
            os.makedirs(model_dir, exist_ok=True)
            os.makedirs(training_dir, exist_ok=True)
            os.makedirs(test_dir, exist_ok=True)

            # === Save metrics ===
            metrics_path = os.path.join(metrics_dir, f"metrics_{ticker}_{event_type.lower()}.csv")
            save_metrics_csv(
                metrics_path,
                [event_type, ticker, "XGBoost", f"{rmse:.4f}", f"{mae:.4f}", f"{r2:.4f}", f"{mape:.4f}", f"{max_err:.4f}"],
                header=["event_type", "ticker", "model", "rmse", "mae", "r2", "mape", "max_err"]
            )

            # === Save model ===
            model_path = os.path.join(model_dir, f"{event_type}_{ticker}_xgb.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(model, f)

            # === Save training plots ===
            plot_training_history(history, "xgboost", ticker, event_type, save_dir=training_dir)
            plot_predictions(idx, y_true, y_pred, "xgboost", ticker, event_type, save_dir=test_dir)

            # === Save AAR & CAAR truth vs pred ===
            car_true = np.cumsum(y_true)
            car_pred = np.cumsum(y_pred)
            results_df = pd.DataFrame({
                'ar_true' : y_true,
                'ar_pred' : y_pred,
                'car_true': car_true,
                'car_pred': car_pred,
            }, index=idx)

            results_df.to_csv(f"{training_dir}/{ticker}_{event_type}_xgb_ar_car.csv")

        except Exception as e:
            print(f"Failed to run model for {ticker}: {e}")
            continue

    return all_results


if __name__ == "__main__":

    # Command-line argument for event selection
    parser = argparse.ArgumentParser(description="Run climate-financial tabular regression analysis.")
    parser.add_argument('--event_type', type=str,
                        help='Event type to filter for cross-event analysis (e.g., Hurricane, Wildfire, Flood).')
    parser.add_argument('--model', type=str,
                        help='ML model to use (e.g., xgboost, linear, random_forest).')

    args = parser.parse_args()
    event_type  = args.event_type

    if event_type not in EVENT_FEATURES:
        raise ValueError(f"Unknown event type: {event_type}. Valid options: {list(EVENT_FEATURES.keys())}")

    data_dir = f"../data/aar_weather_dfs/{event_type}"
    os.makedirs(data_dir, exist_ok=True)

    features    = EVENT_FEATURES.get(event_type, ['temperature'])
    target      = "abnormal_return"

    results = run_tabular_regression(data_dir, event_type, features, target)

    print("\nSummary of results:")
    for ticker, metrics in results.items():
        print(f"{ticker}: RMSE={metrics['RMSE']:.4f}, R2={metrics['R2']:.4f}")
