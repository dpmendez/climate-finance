from sklearn.linear_model import LinearRegression
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
        y = df.loc[estimation_window, 'Return'].values
        model = LinearRegression().fit(X, y)
        model_params[sector] = {
            'alpha': model.intercept_,
            'beta': model.coef_[0]
        }

    return model_params

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
