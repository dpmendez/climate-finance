import yfinance as yf
import pandas as pd

def fetch_market_data(tickers, start_date, end_date):
    data = {}
    for symbol, label in tickers.items():
        df = yf.download(symbol, start=start_date, end=end_date)

        if not df.empty:
            price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            df['Return'] = df[price_col].pct_change()

            df = df[[price_col, 'Return', 'Volume']].rename(columns={price_col: label})
            # store processed df in the dictionary, with 'label' as the key
            data[label] = df

    return data
