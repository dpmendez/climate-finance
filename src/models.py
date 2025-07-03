import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler


def train_xgboost_model(df, features, target):
    df = df.dropna(subset=features + [target])
    
    # Keep DataFrames for index handling
    X = df[features]
    y = df[target]

    # Sequential split, like in LSTM
    train_size = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
    test_index = X_test.index  # preserves correct datetime index

    # Convert to arrays for model input
    model = XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X_train.values, y_train.values)
    preds = model.predict(X_test.values)

    rmse = np.sqrt(mean_squared_error(y_test.values, preds))
    return rmse, preds, test_index, y_test.values, model


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
    train_size = int(len(X_seq) * 0.8)
    X_train, X_test = X_seq[:train_size], X_seq[train_size:]
    y_train, y_test = y_seq[:train_size], y_seq[train_size:]

    # Index offset due to sliding window
    test_index = df.index[window_size + train_size:]

    model = Sequential([
        LSTM(50, activation='relu', input_shape=(window_size, X_seq.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    model.fit(X_train, y_train, epochs=20, batch_size=8, verbose=0)

    preds = model.predict(X_test).flatten()
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    return rmse, preds, test_index, y_test, model