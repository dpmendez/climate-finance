# Climate-Financial Event Study Toolkit

## 📈 Overview

This project provides a modular and extensible **event study framework** to analyze how **climate disasters** (hurricanes, wildfires, floods, winter storms, etc.) affect **financial markets**, especially sector-specific ETFs.

The goal is to **quantify and forecast abnormal stock returns** in response to these events using historical market and weather data, with both classical (CAPM-style) and machine learning (XGBoost and LSTM) models.

---

## 🌪️ Use Cases

* Quantify sector-specific market responses to various disaster types.
* Forecast short-term market volatility driven by extreme weather.
* Visualize event-driven anomalies and model accuracy across sectors.
* Extend to future scenarios and simulate market stress testing due to climate events.

---

## ✅ Project Status

### 📂 Modules Implemented

| Module        | Description                                                                                                                       |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `events.py`   | Contains metadata for historical and combined disaster events. Supports flexible grouping by disaster type (e.g. all hurricanes). |
| `weather.py`  | Fetches weather variables from Visual Crossing API based on disaster location and window. Tailors variables to event type.        |
| `market.py`   | Downloads market and sector ETF data using `yfinance`. Cleans and aligns price data across sectors.                               |
| `returns.py`  | Computes abnormal and cumulative abnormal returns (CAR) using either naive or regression-based approaches.                        |
| `models.py`   | Trains and evaluates forecasting models (XGBoost, LSTM) for sectoral returns using weather as input.                              |
| `viz.py`      | Generates visualizations of stock prices, abnormal returns, CAR, model predictions, and feature importances.                      |
| `analysis.py` | Main orchestrator: selects events, runs data pipeline, fits models, and produces outputs for single or combined events.           |

---

### 🔄 Key Enhancements (v0.2.0)

#### Combined Events

We can now analyze groups of events of the same type (e.g. all hurricanes) by passing a grouped key (e.g. "hurricanes") to the pipeline. This affects:

* Return model computation: the regression for CAPM-style AR is trained across the full set of combined events.
* Abnormal return calculation: AR is computed per-sector per-day across all event timelines.
* Allows for cross-event learning and generalization.

#### 📊 Visualization (new in viz.py)

Centralized plotting functions include:

* Stock price evolution around event windows.
* Abnormal and cumulative abnormal returns per sector.
* Model performance: predicted vs actual returns, RMSE, and R².
* XGBoost feature importances for weather variables.
* LSTM predictions and training loss curves.
    
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

Each event (or group of events) is defined by:

* `event_key`: string identifier (e.g. "harvey_2017", "wildfires", "hurricanes")
* `lat, lon`: disaster center coordinates
* `start_date`, end_date: analysis window
* `sector_tickers`: relevant ETFs by sector
* `weather_vars`: key weather metrics (e.g. windspeed, precip, temp)

Users can switch between event keys in events.py and easily extend the dataset with future disasters.

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

## 🚀 How to Run

1. Set your Visual Crossing API key.
2. Choose an event (event_key) or group (event_type).
3. Run:

```python
python run_analysis.py --event_key helene_2024
```

4. Outputs include:
* Abnormal and cumulative return plots
* Model performance metrics
* Saved model predictions and training logs

---

## 🛠️ To Do

- [X] Export event summaries as reports
- [ ] Incorporate confidence intervals on predictions
- [ ] Optimize model parameters
- [ ] Build interactive dashboard using Dash or Streamlit
- [ ] Add social/environmental impact overlays (e.g., population affected, federal relief, etc.)
