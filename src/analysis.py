import os
import sys
import numpy as np
import pandas as pd
import pickle

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from config.events import EVENT_FEATURES
from dataset import build_pooled_dataset, get_sector_groups
from models import run_leave_one_event_out, MODEL_REGISTRY
from viz import (
    plot_actual_vs_predicted,
    plot_feature_importance,
    plot_car_by_event,
    plot_cv_metrics_summary,
)


def run_pooled_analysis(event_type, api_key):
    """
    Main analysis orchestrator for pooled tabular regression.

    1. Builds a pooled dataset for all events of the given type
    2. For each sector, runs leave-one-event-out CV with all models
    3. Saves metrics, predictions, models, and plots
    """
    # Build pooled dataset
    pooled_df = build_pooled_dataset(event_type, api_key)

    # Output directory
    output_dir = os.path.join("output", event_type)
    os.makedirs(output_dir, exist_ok=True)

    # Save full pooled dataset
    pooled_path = os.path.join(output_dir, "pooled_dataset.csv")
    pooled_df.to_csv(pooled_path, index=False)
    print(f"\nSaved pooled dataset to {pooled_path}")

    # Determine feature columns (delta_* columns from EVENT_FEATURES)
    raw_features = EVENT_FEATURES.get(event_type, ['temp', 'humidity', 'precip', 'windspeed', 'pressure'])
    delta_features = [f"delta_{f}" for f in raw_features]
    features = ['relative_day'] + [f for f in delta_features if f in pooled_df.columns]
    target = 'ar'

    print(f"\nFeatures: {features}")
    print(f"Target: {target}")

    # Per-sector analysis
    sector_groups = get_sector_groups(pooled_df)
    all_sector_metrics = []

    for sector, sector_df in sector_groups.items():
        n_events = sector_df['event_key'].nunique()
        print(f"\n{'='*60}")
        print(f"Sector: {sector} | {len(sector_df)} rows | {n_events} events")
        print(f"{'='*60}")

        if n_events < 2:
            print(f"  Skipping {sector}: need at least 2 events for leave-one-out CV")
            continue

        # Check that all features exist
        available_features = [f for f in features if f in sector_df.columns]
        if len(available_features) < len(features):
            missing = set(features) - set(available_features)
            print(f"  Warning: missing features {missing}, using {available_features}")
        features_to_use = available_features

        # Drop rows with NaN in features or target
        sector_df = sector_df.dropna(subset=features_to_use + [target])

        # Run leave-one-event-out CV
        fold_results, overall_metrics, final_models = run_leave_one_event_out(
            sector_df, features_to_use, target, event_col='event_key'
        )

        # Print metrics summary
        for model_name, metrics in overall_metrics.items():
            print(f"  {model_name:15s} | RMSE: {metrics['rmse']:.6f} | MAE: {metrics['mae']:.6f} | R2: {metrics['r2']:.4f}")
            all_sector_metrics.append({
                'sector': sector,
                'model': model_name,
                **metrics,
            })

        # --- Save outputs ---

        # Metrics
        metrics_dir = os.path.join(output_dir, "metrics")
        os.makedirs(metrics_dir, exist_ok=True)
        metrics_rows = []
        for fold in fold_results:
            for model_name in MODEL_REGISTRY:
                m = fold[f'metrics_{model_name}']
                metrics_rows.append({
                    'held_out_event': fold['event_key'],
                    'model': model_name,
                    **m,
                })
        # Add overall row
        for model_name, m in overall_metrics.items():
            metrics_rows.append({
                'held_out_event': 'OVERALL',
                'model': model_name,
                **m,
            })
        metrics_df = pd.DataFrame(metrics_rows)
        metrics_df.to_csv(os.path.join(metrics_dir, f"{sector}_cv_metrics.csv"), index=False)

        # Predictions
        preds_dir = os.path.join(output_dir, "predictions")
        os.makedirs(preds_dir, exist_ok=True)
        pred_rows = []
        for fold in fold_results:
            for i in range(len(fold['y_true'])):
                row = {
                    'event_key': fold['event_key'],
                    'relative_day': fold['relative_days'][i],
                    'ar_true': fold['y_true'][i],
                }
                for model_name in MODEL_REGISTRY:
                    row[f'ar_pred_{model_name}'] = fold[f'y_pred_{model_name}'][i]
                pred_rows.append(row)

        preds_df = pd.DataFrame(pred_rows).sort_values(['event_key', 'relative_day'])

        # Compute CAR columns
        for model_name in MODEL_REGISTRY:
            preds_df[f'car_pred_{model_name}'] = preds_df.groupby('event_key')[f'ar_pred_{model_name}'].cumsum()
        preds_df['car_true'] = preds_df.groupby('event_key')['ar_true'].cumsum()

        preds_df.to_csv(os.path.join(preds_dir, f"{sector}_cv_predictions.csv"), index=False)

        # Models
        model_dir = os.path.join(output_dir, "models")
        os.makedirs(model_dir, exist_ok=True)
        for model_name, model in final_models.items():
            model_path = os.path.join(model_dir, f"{sector}_{model_name}.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(model, f)

        # Plots
        plots_dir = os.path.join(output_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)

        # Scatter plots (actual vs predicted) for XGBoost and RF
        all_true = np.concatenate([f['y_true'] for f in fold_results])
        for model_name in ['xgboost', 'random_forest']:
            all_pred = np.concatenate([f[f'y_pred_{model_name}'] for f in fold_results])
            plot_actual_vs_predicted(
                all_true, all_pred, model_name, sector, event_type, plots_dir
            )

        # Feature importance (XGBoost)
        if 'xgboost' in final_models:
            plot_feature_importance(
                final_models['xgboost'], features_to_use, sector, event_type, plots_dir
            )

        # CAR by event
        plot_car_by_event(preds_df, sector, event_type, plots_dir)

    # Cross-model summary plot
    if all_sector_metrics:
        summary_df = pd.DataFrame(all_sector_metrics)
        plots_dir = os.path.join(output_dir, "plots")
        plot_cv_metrics_summary(summary_df, event_type, plots_dir)

    print(f"\n{'='*60}")
    print(f"Analysis complete for {event_type}. Outputs in {output_dir}/")
    print(f"{'='*60}")
