# Climate-Financial Event Study Toolkit

## 📈 Overview

This project builds a modular and extensible **event study framework** to analyze how **climate disasters** (hurricanes, wildfires, floods, winter storms, etc.) impact **financial markets**, particularly **sector-specific stock returns**. 

The core objective is to **quantify and forecast abnormal stock returns in response to extreme climate events**, using historical stock and weather data, with the aid of machine learning models (XGBoost and LSTM).

---

## 🌪️ Use Cases

* Understand how different sectors react to various disaster types.
* Forecast stock behavior using relevant weather variables.
* Compare actual vs predicted sectoral response to extreme weather.
* Extend to future scenarios and simulate market stress testing due to climate events.

---

## ✅ Project Status

### 📂 Modules Implemented

| Module                | Description                                                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `events.py`           | Contains metadata and location/date info for multiple historical disaster events. Now includes sector-specific tickers per event.     |
| `weather.py`          | Fetches weather data from Visual Crossing API. Dynamically pulls relevant weather variables based on event type.                      |
| `market.py`           | Fetches stock price and volume data using `yfinance`. Returns structured sector and market dataframes.                                |
| `returns.py`          | Computes abnormal and cumulative abnormal returns (CAR). Includes both naive and regression-based computation.                        |
| `models.py`           | Trains and evaluates XGBoost and LSTM models to forecast abnormal returns from weather data.                                          |
| `analysis.py`         | Main pipeline: selects an event, loads data, computes abnormal returns, prepares features, and trains models. Also includes plotting. |

---

## 🔍 Abnormal Return Methodology

Two methods are implemented:

* **Naive approach**:

  $$\text{Abnormal Return} = R_t - \overline{R}$$

* **Market-adjusted (CAPM-style) approach**:

  $$\text{AR}_ {\text{sector}} = R_{\text{sector}} - (\alpha + \beta \cdot R_{\text{market}})$$

where $\alpha$, $\beta$ are learned from OLS regression during the estimation window.

CAR is calculated as the cumulative sum of daily abnormal returns.

---

## ⚙️ Inputs and Configuration

Each event is defined by:

* Name and type
* Geolocation (`lat`, `lon`)
* Start and end date of the analysis window
* Sector tickers impacted
* Weather variables relevant to disaster type (automatically selected)

Users can select an event key (`event_key`) and run the pipeline for any disaster in `events.py`.

---

## 📊 Example Events

```python
EVENTS = {
  "harvey_2017": {...},
  "maria_2017": {...},
  "wildfires_west_2020": {...},
  "winter_storm_uri_2021": {...},
  "maui_2023": {...},
  ...
}
```

Each entry includes disaster metadata, sector tickers, and estimated losses.

---

## 🔋 Dependencies

* `pandas`, `numpy`, `matplotlib`, `seaborn`
* `scikit-learn`, `xgboost`
* `tensorflow` or `keras` for LSTM
* `yfinance` for stock data
* Visual Crossing Weather API key (required)

---

## 🛠️ To Do

- [ ] Incorporate confidence intervals on predictions
- [ ] Build interactive dashboard using Dash or Streamlit
- [ ] Add social/environmental impact overlays (e.g., population affected, federal relief, etc.)
- [ ] Export event summaries as reports
