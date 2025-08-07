import os
import pandas as pd
from models import train_xgboost_model

# Define your feature and target columns here
FEATURE_COLS = ["temperature", "wind_speed", "pressure", "precipitation"]
TARGET_COL = "abnormal_return"


def run_tabular_regression(data_dir, features=FEATURE_COLS, target=TARGET_COL):
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
            os.makedirs(training_dir, exist_ok=True)

            plot_training_history(history_xgb, "xgboost", ticker, event_type, save_dir=output_dir)
            plot_predictions(idx, y_true, y_pred, "xgboost", ticker, event_type, save_dir=output_dir)

        except Exception as e:
            print(f"Failed to run model for {ticker}: {e}")
            continue

    return all_results


if __name__ == "__main__":

    data_folder = "data/aar_weather_dfs/Wildfire"  # Change to match the event type
    results = run_tabular_regression(data_folder)

    print("\nSummary of results:")
    for ticker, metrics in results.items():
        print(f"{ticker}: RMSE={metrics['RMSE']:.4f}, R2={metrics['R2']:.4f}")
