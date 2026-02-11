import numpy as np
import pandas as pd
import pickle
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    max_error,
)
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb


def compute_metrics(y_true, y_pred):
    """Compute regression metrics. Returns a dict."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return {
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'r2': r2_score(y_true, y_pred),
        'mape': np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100,
        'max_error': max_error(y_true, y_pred),
    }


def train_xgboost(X_train, y_train, X_test, y_test):
    """Train XGBoost regressor. Returns (predictions, model)."""
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test)

    # Use a small validation split from training data for early stopping
    n = len(X_train)
    val_split = int(n * 0.85)
    dtrain_inner = xgb.DMatrix(X_train.iloc[:val_split], label=y_train.iloc[:val_split])
    dval_inner = xgb.DMatrix(X_train.iloc[val_split:], label=y_train.iloc[val_split:])

    params = {
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
    }

    model = xgb.train(
        params,
        dtrain_inner,
        num_boost_round=500,
        evals=[(dtrain_inner, "train"), (dval_inner, "val")],
        early_stopping_rounds=20,
        verbose_eval=False,
    )

    # Retrain on full training set with the best number of rounds
    best_rounds = model.best_iteration + 1
    model = xgb.train(params, dtrain, num_boost_round=best_rounds, verbose_eval=False)

    preds = model.predict(dtest)
    return preds, model


def train_random_forest(X_train, y_train, X_test, y_test):
    """Train Random Forest regressor. Returns (predictions, model)."""
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=5,
        random_state=42,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return preds, model


def train_linear_baseline(X_train, y_train, X_test, y_test):
    """Train OLS linear regression baseline. Returns (predictions, model)."""
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return preds, model


MODEL_REGISTRY = {
    'xgboost': train_xgboost,
    'random_forest': train_random_forest,
    'ols': train_linear_baseline,
}


def run_leave_one_event_out(df, features, target, event_col='event_key'):
    """
    Leave-one-event-out cross-validation.

    For each unique event: train on all OTHER events, predict the held-out event.
    Runs all three models (XGBoost, Random Forest, OLS).

    Returns:
        fold_results: list of dicts, one per fold, with metrics and predictions
        overall_metrics: dict of {model_name: aggregated metrics across all folds}
        final_models: dict of {model_name: model trained on ALL data}
    """
    events = df[event_col].unique()
    fold_results = []

    for held_out_event in events:
        train_mask = df[event_col] != held_out_event
        test_mask = df[event_col] == held_out_event

        X_train = df.loc[train_mask, features]
        y_train = df.loc[train_mask, target]
        X_test = df.loc[test_mask, features]
        y_test = df.loc[test_mask, target]

        if len(X_test) == 0 or len(X_train) == 0:
            continue

        fold = {
            'event_key': held_out_event,
            'test_index': df.loc[test_mask].index,
            'relative_days': df.loc[test_mask, 'relative_day'].values,
            'y_true': y_test.values,
        }

        for model_name, train_fn in MODEL_REGISTRY.items():
            preds, _ = train_fn(X_train, y_train, X_test, y_test)
            fold[f'y_pred_{model_name}'] = preds
            fold[f'metrics_{model_name}'] = compute_metrics(y_test.values, preds)

        fold_results.append(fold)

    # Aggregate metrics across folds
    overall_metrics = {}
    for model_name in MODEL_REGISTRY:
        all_true = np.concatenate([f['y_true'] for f in fold_results])
        all_pred = np.concatenate([f[f'y_pred_{model_name}'] for f in fold_results])
        overall_metrics[model_name] = compute_metrics(all_true, all_pred)

    # Train final models on all data
    X_all = df[features]
    y_all = df[target]
    final_models = {}
    for model_name, train_fn in MODEL_REGISTRY.items():
        _, model = train_fn(X_all, y_all, X_all, y_all)
        final_models[model_name] = model

    return fold_results, overall_metrics, final_models
