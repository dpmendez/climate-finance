from sklearn.linear_model import LinearRegression
import os
import json
import numpy as np
import pandas as pd

# Market model regression to compute normal returns 
def estimate_market_model(market_df, sector_dict, estimation_window):
    """
    Fit the market model on pre-event estimation window for each sector.
    Returns a dictionary of alpha and beta values per sector.
    """
    X = market_df.loc[estimation_window, 'Return'].values.reshape(-1, 1)
    model_params = {}

    for sector, df in sector_dict.items():

        # Handle case where X is a NumPy array — convert to DataFrame
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)

        # Ensure y is a Series with matching length
        y = df.loc[estimation_window, 'Return'].values
        y = pd.Series(y, name="target")

        # Concatenate and drop rows with NaNs
        df_clean = pd.concat([X, y], axis=1).dropna()

        # Separate features and target
        X_clean = df_clean.drop(columns="target")
        y_clean = df_clean["target"]

        model = LinearRegression().fit(X_clean, y_clean)

        model_params[sector] = {
            'alpha': model.intercept_,
            'beta': model.coef_[0]
        }

    return model_params


def save_market_model_params(params, event_key, save_dir="models"):

    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{event_key}_market_lr.json")
    with open(path, "w") as f:
        json.dump(params, f, indent=2)


# Proper method to compute abnormal returns
def compute_abnormal_returns(market_df, sector_dict, model_params):
    """
    Calculate abnormal returns for each sector using estimated market model.
    Returns a dictionary of abnormal return series per sector.
    """
    market_returns = market_df['Return']
    abnormal_returns = {}

    for sector, df in sector_dict.items():
        alpha = model_params[sector]['alpha']
        beta = model_params[sector]['beta']
        expected = alpha + beta * market_returns
        abnormal = df['Return'] - expected
        abnormal_returns[sector] = abnormal

    return abnormal_returns

def compute_car(abnormal_returns_dict):
    """
    Compute cumulative abnormal returns (CAR) for each sector.
    Returns a dictionary of CAR series per sector.
    """
    return {sector: ar.cumsum() for sector, ar in abnormal_returns_dict.items()}


# Non-standard way of computing abnormal returns
def basic_abnormal_return(market_df, index_label):
    # Calculate daily returns and abnormal returns
    # The first row is expected to be NaN
    market_df['return'] = market_df[index_label].pct_change()
    mean_return = market_df['return'].mean()
    market_df['abnormal_return'] = market_df['return'] - mean_return     


def basic_abnormal_returns(market_df, sector_df):
    """
    Compute abnormal returns by subtracting market return from each sector.
    """
    abnormal_returns = sector_df.subtract(market_df, axis=0)
    return abnormal_returns


def basic_car(abnormal_returns):
    """
    Compute cumulative abnormal returns (CAR) by cumulative summation.
    """
    car = abnormal_returns.cumsum()
    return car
