import os
import sys
import pandas as pd
import traceback
from datetime import timedelta

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from config.events import EVENTS, EVENT_FEATURES
from market import fetch_market_data
from returns import estimate_market_model, compute_abnormal_returns, save_market_model_params
from weather import fetch_visualcrossing_weather, compute_weather_deltas


def build_event_observation(event_key, api_key):
    """
    Process a single event and return a DataFrame of (sector, relative_day, delta_weather..., ar) rows.
    """
    event = EVENTS[event_key]
    print(f"  Building observations for {event['name']}...")

    market = event['index']
    tickers = event['sector_etfs']
    end_date = event['end_date']
    event_date = event['event_date']
    lat = event['location']['lat']
    lon = event['location']['lon']
    disaster_type = event['type']

    # Derive analysis window start from event type defaults
    pre_event_days = EVENT_TYPE_DEFAULTS[disaster_type]['pre_event_days']
    event_dt = pd.to_datetime(event_date)
    analysis_start = (event_dt - timedelta(days=pre_event_days)).strftime('%Y-%m-%d')

    # Go back far enough to cover ESTIMATION_DAYS trading days (~1.5x calendar days)
    estimation_start = (event_dt - timedelta(days=int(ESTIMATION_DAYS * 1.5))).strftime('%Y-%m-%d')

    # Fetch market and sector data from estimation_start (wide window for CAPM fitting)
    market_df = fetch_market_data([market], estimation_start, end_date)[market]
    sector_dict = fetch_market_data(tickers, estimation_start, end_date)

    # Estimate market model on pre-event window using ESTIMATION_DAYS trading days
    estimation_window = market_df.index[market_df.index < event_date][-ESTIMATION_DAYS:]
    model_params = estimate_market_model(market_df, sector_dict, estimation_window)

    # Compute abnormal returns over the full fetched range
    abnormal_returns = compute_abnormal_returns(market_df, sector_dict, model_params)

    # Fetch weather for the analysis window only (analysis_start to end_date)
    weather_df = fetch_visualcrossing_weather(api_key, lat, lon, analysis_start, end_date, disaster_type)
    delta_weather_df = compute_weather_deltas(weather_df, event_date)

    # Align on common trading dates within the analysis window
    analysis_start_dt = pd.to_datetime(analysis_start)
    analysis_end_dt = pd.to_datetime(end_date)

    first_sector = list(abnormal_returns.keys())[0]
    common_index = abnormal_returns[first_sector].index
    common_index = common_index[(common_index >= analysis_start_dt) & (common_index <= analysis_end_dt)]
    for ar_series in abnormal_returns.values():
        common_index = common_index.intersection(ar_series.index)
    common_index = common_index.intersection(delta_weather_df.index)

    delta_weather_aligned = delta_weather_df.reindex(common_index).ffill().bfill()

    # Build rows for each sector
    rows = []
    for ticker in tickers:
        ar = abnormal_returns[ticker]
        if isinstance(ar, pd.DataFrame):
            ar = ar.squeeze()
        ar = ar.reindex(common_index).dropna()

        for date in ar.index:
            relative_day = (date - pd.to_datetime(event_date)).days
            row = {
                'event_key': event_key,
                'sector': ticker,
                'relative_day': relative_day,
                'ar': ar.loc[date],
            }
            # Add delta weather features
            for col in delta_weather_aligned.columns:
                row[col] = delta_weather_aligned.loc[date, col]
            rows.append(row)

    return pd.DataFrame(rows)


def build_pooled_dataset(event_type, api_key):
    """
    Build a pooled tabular dataset for all events of a given disaster type.
    Each row is an (event, sector, relative_day) observation.
    """
    print(f"\nBuilding pooled dataset for {event_type} events...\n")

    frames = []
    for event_key, event in EVENTS.items():
        if event['type'].lower() != event_type.lower():
            continue
        try:
            df = build_event_observation(event_key, api_key)
            frames.append(df)
        except Exception as e:
            print(f"  Failed to process {event_key}: {e}")
            traceback.print_exc()
            continue

    if not frames:
        raise ValueError(f"No events successfully processed for type '{event_type}'")

    pooled = pd.concat(frames, ignore_index=True)

    n_events = pooled['event_key'].nunique()
    n_sectors = pooled['sector'].nunique()
    print(f"\nPooled dataset: {len(pooled)} rows, {n_events} events, {n_sectors} sectors")

    return pooled


def get_sector_groups(pooled_df):
    """
    Split the pooled dataset by sector.
    Returns dict of {sector: DataFrame}.
    """
    return {sector: group.copy() for sector, group in pooled_df.groupby('sector')}