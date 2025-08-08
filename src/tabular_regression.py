import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))

import argparse
import pandas as pd
from models import train_xgboost_model
from config.events import EVENTS, EVENT_FEATURES
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
            all_results[ticker] = {
                "RMSE": rmse,
                "MAE": mae,
                "R2": r2,
            }

            output_dir = "plots/training/tabular"
            os.makedirs(output_dir, exist_ok=True)

            plot_training_history(history, "xgboost", ticker, event_type, save_dir=output_dir)
            plot_predictions(idx, y_true, y_pred, "xgboost", ticker, event_type, save_dir=output_dir)

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
    data_folder = f"data/aar_weather_dfs/{event_type}"
    features    = EVENT_FEATURES.get(event_type, ['temperature'])
    target      = "abnormal_return"

    results = run_tabular_regression(data_folder, event_type, features, target)

    print("\nSummary of results:")
    for ticker, metrics in results.items():
        print(f"{ticker}: RMSE={metrics['RMSE']:.4f}, R2={metrics['R2']:.4f}")
