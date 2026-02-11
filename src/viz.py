import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


def plot_actual_vs_predicted(y_true, y_pred, model_name, sector, event_type, save_dir):
    """Scatter plot of actual vs predicted AR with 45-degree reference line."""
    os.makedirs(save_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(y_true, y_pred, alpha=0.5, s=20)

    # 45-degree reference line
    lims = [
        min(min(y_true), min(y_pred)),
        max(max(y_true), max(y_pred)),
    ]
    ax.plot(lims, lims, 'r--', alpha=0.7, linewidth=1)

    r2 = r2_score(y_true, y_pred)
    ax.set_title(f"{model_name} | {sector} ({event_type})\nR² = {r2:.4f}")
    ax.set_xlabel("Actual AR")
    ax.set_ylabel("Predicted AR")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"{sector}_scatter_{model_name}.png"), dpi=150)
    plt.close()


def plot_feature_importance(model, feature_names, sector, event_type, save_dir):
    """Bar chart of XGBoost feature importances."""
    os.makedirs(save_dir, exist_ok=True)

    importance = model.get_score(importance_type='gain')
    # Map xgboost feature names (f0, f1, ...) back to actual names
    mapped = {}
    for i, name in enumerate(feature_names):
        key = f"f{i}"
        if key in importance:
            mapped[name] = importance[key]
        elif name in importance:
            mapped[name] = importance[name]

    if not mapped:
        return

    names = list(mapped.keys())
    values = list(mapped.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(names, values)
    ax.set_title(f"Feature Importance (Gain) | {sector} ({event_type})")
    ax.set_xlabel("Gain")

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"{sector}_importance_xgb.png"), dpi=150)
    plt.close()


def plot_car_by_event(predictions_df, sector, event_type, save_dir):
    """
    Plot predicted vs actual CAR trajectories for each held-out event.
    One subplot per event.
    """
    os.makedirs(save_dir, exist_ok=True)

    events = predictions_df['event_key'].unique()
    n_events = len(events)
    cols = min(3, n_events)
    rows = (n_events + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows), squeeze=False)

    for idx, event_key in enumerate(events):
        ax = axes[idx // cols][idx % cols]
        event_data = predictions_df[predictions_df['event_key'] == event_key].sort_values('relative_day')

        days = event_data['relative_day'].values
        ax.plot(days, event_data['car_true'].values, 'k-', linewidth=2, label='Actual')
        ax.plot(days, event_data['car_pred_xgboost'].values, 'b--', linewidth=1, label='XGBoost')
        ax.plot(days, event_data['car_pred_random_forest'].values, 'g--', linewidth=1, label='RF')
        ax.plot(days, event_data['car_pred_ols'].values, 'r:', linewidth=1, label='OLS')

        ax.axvline(x=0, color='gray', linestyle=':', alpha=0.5)
        ax.set_title(event_key, fontsize=10)
        ax.set_xlabel("Relative Day")
        ax.set_ylabel("CAR")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(n_events, rows * cols):
        axes[idx // cols][idx % cols].set_visible(False)

    fig.suptitle(f"CAR Trajectories | {sector} ({event_type})", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"{sector}_car_by_event.png"), dpi=150)
    plt.close()


def plot_cv_metrics_summary(summary_df, event_type, save_dir):
    """
    Bar chart comparing models across sectors for key metrics.
    summary_df has columns: sector, model, rmse, mae, r2, ...
    """
    os.makedirs(save_dir, exist_ok=True)

    metrics_to_plot = ['rmse', 'mae', 'r2']
    fig, axes = plt.subplots(1, len(metrics_to_plot), figsize=(6 * len(metrics_to_plot), 5))

    for i, metric in enumerate(metrics_to_plot):
        ax = axes[i]
        pivot = summary_df.pivot(index='sector', columns='model', values=metric)
        pivot.plot(kind='bar', ax=ax)
        ax.set_title(f"{metric.upper()}")
        ax.set_xlabel("Sector")
        ax.set_ylabel(metric.upper())
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle(f"Model Comparison | {event_type}", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"cv_metrics_summary.png"), dpi=150)
    plt.close()