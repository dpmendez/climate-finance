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
    df = df.dropna(subset=feature_cols + [target_col])
    X = df[features].values
    y = df[target].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    test_index = df.index[len(X_train):]  # ensure index alignment with X_test
    return rmse, preds, test_index, y_test


def train_lstm_model(df, features, target):
    df = df.dropna(subset=feature_cols + [target_col])
    X = df[features].values
    y = df[target].values

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X) # scale so values lie between 0 and 1

    window_size = 5
    X_seq = []
    y_seq = []
    for i in range(window_size, len(X_scaled)):
        X_seq.append(X_scaled[i-window_size:i])
        y_seq.append(y[i])

    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    train_size = int(len(X_seq) * 0.8)
    X_train, X_test, y_train, y_test = train_test_split(
        X_seq, y_seq, test_size=0.2, shuffle=False
    )

    # account for the initial shift due to the sliding window
    test_index = df.index[window_size + train_size:]

    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(window_size, X_seq.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

    model.fit(X_train, y_train, epochs=20, batch_size=8, verbose=0)
    preds = model.predict(X_test).flatten()

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    return rmse, preds, test_index, y_test