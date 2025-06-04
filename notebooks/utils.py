import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

START_DATE = "2017-10-01"
END_DATE = "2017-12-15"
DAMREY_DATE = datetime(2017, 11, 4)
EVENT_WINDOW = 15


def compute_sector_cars(sector_tickers, start_date, end_date, event_date):
    sector_returns = {}

    for ticker, name in sector_tickers.items():
        df = yf.download(ticker, start=start_date, end=end_date)

        if df.empty:
            print(f"Warning: No data for {ticker}")
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df.columns]
            adj_col = [col for col in df.columns if 'Adj Close' in col or 'Close' in col][0]
        else:
            adj_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'

        df = df[[adj_col]].rename(columns={adj_col: name})
        df.index = pd.to_datetime(df.index)
        df['return'] = df[name].pct_change()
        mean_ret = df['return'].mean()
        df['abnormal'] = df['return'] - mean_ret

        window_df = df.loc[(df.index >= event_date - pd.Timedelta(days=EVENT_WINDOW)) &
                           (df.index <= event_date + pd.Timedelta(days=EVENT_WINDOW))]

        window_df = window_df.copy()
        window_df['CAR'] = window_df['abnormal'].cumsum()
        sector_returns[name] = window_df['CAR']

    return pd.DataFrame(sector_returns)


def plot_car_comparison(df, event_date):
    plt.figure(figsize=(10, 6))
    for col in df.columns:
        plt.plot(df.index, df[col], label=col)
    plt.axvline(event_date, color='red', linestyle='--', label='Event Date')
    plt.title("CAR Comparison Across Sectors")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Abnormal Return")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()