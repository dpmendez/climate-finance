import yfinance as yf
import pandas as pd

def fetch_market_data(tickers, start_date, end_date):
    data = {}

    if isinstance(tickers, dict):
        iterator = tickers.items()
    elif isinstance(tickers, list):
        iterator = [(t, t) for t in tickers]
    else:
        raise ValueError("tickers must be a list or dict")

    # Convert list to dict if needed (use symbol as label)
    if isinstance(tickers, list):
        tickers = {symbol: symbol for symbol in tickers}

    for symbol, label in tickers.items():
        print("Downloading yf data for ", symbol)
        df = yf.download(symbol, start=start_date, end=end_date)
 
        if df.empty:
            print(f"No data for {symbol}")
            continue
 
        if not df.empty:
            price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            df['Return'] = df[price_col].pct_change() # NaN at the first row

            df = df[[price_col, 'Return', 'Volume']].rename(columns={price_col: label})
            # store processed df in the dictionary, with 'symbol' as the key
            data[symbol] = df

    return data
