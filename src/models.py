import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
    max_error,
)
from sklearn.model_selection import train_test_split
import xgboost as xgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler


def train_xgboost_model(df, features, target):
    df = df.dropna(subset=features + [target])
    
    df = df.sort_index()

    # Keep DataFrames for index handling
    X = df[features]
    y = df[target]

    # Sequential split, like in LSTM
    n = len(df)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)

    X_train = X.iloc[:train_end]
    y_train = y.iloc[:train_end]

    X_val = X.iloc[train_end:val_end]
    y_val = y.iloc[train_end:val_end]

    X_test = X.iloc[val_end:]
    y_test = y.iloc[val_end:]

    # Store indexes
    idx_train = X_train.index
    idx_test = X_test.index

    # Train
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    dtest_train = xgb.DMatrix(X_train)
    dtest_test = xgb.DMatrix(X_test)

    evals_result = {}
    params = {
        "objective": "reg:squarederror",
        "eval_metric": "rmse"
    }

    model = xgb.train(
        params,
        dtrain,
        num_boost_round=500,
        evals=[(dtrain, "train"), (xgb.DMatrix(X_val, label=y_val), "val")],
        early_stopping_rounds=10,
        evals_result=evals_result,
        verbose_eval=False
    )

    # Predictions
    preds_train = model.predict(dtest_train)
    preds_test = model.predict(dtest_test)

    # Metrics on test
    rmse = np.sqrt(mean_squared_error(y_test.values, preds_test))
    mae = mean_absolute_error(y_test.values, preds_test)
    r2 = r2_score(y_test.values, preds_test)
    mape = np.mean(np.abs((y_test.values - preds_test) / np.maximum(np.abs(y_test.values), 1e-8))) * 100
    max_err = max_error(y_test.values, preds_test)

    # Return everything neatly
    return {
        "metrics": {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "mape": mape,
            "max_err": max_err
        },
        "history": evals_result,
        "model": model,
        "train": {
            "index": idx_train,
            "y_true": y_train.values,
            "y_pred": preds_train
        },
        "test": {
            "index": idx_test,
            "y_true": y_test.values,
            "y_pred": preds_test
        }
    }

def train_lstm_model(df, features, target):
    df = df.dropna(subset=features + [target])
    X = df[features].values
    y = df[target].values

    # Scale
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X) # scale so values lie between 0 and 1

    # Sliding window
    window_size = 5
    X_seq, y_seq = [], []
    for i in range(window_size, len(X_scaled)):
        X_seq.append(X_scaled[i - window_size:i])
        y_seq.append(y[i])

    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    # Split
    n = len(X_seq)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)

    X_train, y_train = X_seq[:train_end], y_seq[:train_end]
    X_val, y_val = X_seq[train_end:val_end], y_seq[train_end:val_end]
    X_test, y_test = X_seq[val_end:], y_seq[val_end:]

    # Index offset due to sliding window
    test_index = df.index[window_size + val_end:]

    model = Sequential([
        LSTM(50, activation='relu', input_shape=(window_size, X_seq.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

    history = model.fit(X_train, y_train,
                        validation_data=(X_val, y_val),
                        epochs=20,
                        batch_size=8,
                        verbose=0)

    preds = model.predict(X_test).flatten()
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    mape = np.mean(np.abs((y_test - preds) / np.maximum(np.abs(y_test), 1e-8))) * 100
    max_err = max_error(y_test, preds)

    # Return everything neatly
    return {
        "metrics": {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "mape": mape,
            "max_err": max_err
        },
        "history": history,
        "model": model,
        "train": {
            "index": idx_train,
            "y_true": y_train.values,
            "y_pred": preds_train
        },
        "test": {
            "index": idx_test,
            "y_true": y_test.values,
            "y_pred": preds_test
        }
    }