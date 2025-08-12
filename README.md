# Climate-Financial Event Study Toolkit

## 📈 Overview

This project provides a modular and extensible **event study** framework to analyze how **climate disasters** (hurricanes, wildfires, floods, winter storms, etc.) affect **financial markets**, especially sector-specific ETFs.

The initial goal was to **quantify and forecast abnormal stock returns** in response to these events using historical market and weather data, with both classical (CAPM-style) and machine learning (XGBoost and LSTM) models.

In this branch, the codebase has been **refactored for better structure, output organization, and preparation for a new modeling approach** (tabular regression). While the current event study implementation works, it produces **small test datasets** for some events due to limited aligned weather–market data, which restricts predictive insight.

---

## 🌪️ Use Cases (Current)

* Quantify sector-specific market responses to various disaster types.
* Save and organize model outputs, metrics, and plots into consistent directories.
* Run a **tabular regression** task that consolidates all event-day feature sets into one dataset for regression analysis.
* Maintain reproducible pipelines for both single-event and grouped-event studies.

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
| `tabular_regression.py` |	**New** — builds a unified dataset of weather + market features across events for regression modeling.                  |

---

### 📂 Output Organization **(new)**

Outputs are now saved in dedicated folders with .gitkeep placeholders to keep structure without tracking generated files:

data/       # Raw and processed datasets
metrics/    # Model evaluation metrics
models/     # Saved trained models
plots/      # Generated plots

These folders are tracked empty in Git via .gitkeep and excluded from committing generated files with .gitignore.

---
### 🔄 Key changes in this branch

* Introduced tabular regression pipeline for multi-event, cross-sectional modeling.
* Standardized output directory creation and file saving across scripts.
* Cleaned up metric saving and model export logic.
* Updated .gitignore to keep repo clean from large generated artifacts.
* Tagged version to reflect the limitations of current event study results and prepare for next phase.

---

### ⚠️ Limitations of Current Event Study Approach

* Limited data points in some events after aligning weather and market data.
* Small sample sizes in test sets (sometimes only a few dates) make prediction plots sparse.
* Grouped-event analysis helps but does not fully address data scarcity.
* Abnormal returns currently calculated with daily data only — higher-frequency data (hourly) could offer richer samples.

---

## 🚀 How to Run

1. Set your Visual Crossing API key.
2. Choose an event (event_key) or group (event_type).
3. Run:

**Event Study Analysis**
```python
python run_analysis.py --event_key helene_2024
```
or
**Tabular Regression Analysis**
```python
python tabular_regression.py --event_type Hurricane
```

4. Outputs include:
* Metrics (metrics/)
* Models (models/)
* Plots (plots/)
* Processed datasets (data/)

---

## 🛠️ To Do
- [ ] Explore hourly weather + market data for richer datasets.
- [ ] Expand tabular regression task for individual event impact prediction.
- [ ] Optimize hyperparameters for both classical and ML models.
- [ ] Add interactive dashboard for results exploration.
- [ ] Consider additional non-market impact data sources.
