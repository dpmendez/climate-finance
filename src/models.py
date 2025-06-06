from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

def train_xgboost(df, target_col, feature_cols):
    df = df.dropna(subset=feature_cols + [target_col])
    X = df[feature_cols]
    y = df[target_col]

    # we’re dealing with time series data = take ordered parts of the sample for training and testing.
    train_size = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    model = XGBRegressor()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    return model, preds, y_test, rmse
