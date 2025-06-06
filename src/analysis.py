# src/analysis.py
import pandas as pd


def calculate_abnormal_returns(market_returns, sector_returns):
    """
    Compute abnormal returns by subtracting market return from each sector.
    """
    abnormal_returns = sector_returns.subtract(market_returns, axis=0)
    return abnormal_returns


def calculate_car(abnormal_returns):
    """
    Compute cumulative abnormal returns (CAR) by cumulative summation.
    """
    car = abnormal_returns.cumsum()
    return car


def run_regression(weather_df, abnormal_df):
    from sklearn.linear_model import LinearRegression

    results = {}
    common_index = weather_df.index.intersection(abnormal_df.index)
    X = weather_df.loc[common_index].dropna()
    for col in abnormal_df.columns:
        y = abnormal_df.loc[common_index, col].dropna()
        aligned = X.join(y, how='inner')
        if aligned.empty:
            continue
        model = LinearRegression()
        model.fit(aligned[X.columns], aligned[col])
        score = model.score(aligned[X.columns], aligned[col])
        results[col] = {
            "coef": model.coef_,
            "intercept": model.intercept_,
            "r2": score
        }
    return results
