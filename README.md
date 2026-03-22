# Climate-Financial Event Study Toolkit

## 📈 Overview

This project provides a modular and extensible **event study** framework to analyze how **climate disasters** (hurricanes, wildfires, floods, winter storms, etc.) affect **financial markets**, especially sector-specific ETFs.

The initial goal was to **quantify and forecast abnormal stock returns** in response to these events using historical market and weather data, with both classical (CAPM-style) and machine learning (XGBoost and LSTM) models.

The approach uses **tabular regression** to pool observations across multiple events. Each row in the dataset represents one (event, sector, day) tuple, with weather deviation features and abnormal returns computed via a CAPM market model. Models are evaluated using **leave-one-event-out cross-validation (LOEO CV)**, where each fold holds out one event entirely — training on the rest and predicting on the held-out event.

NOTE:
The codebase was **refactored for better structure, output organization, and preparation for the tabular regression modeling approach**. While the previous event study implementation worked, it produced **small test datasets** for some events due to limited aligned weather–market data, which restricted predictive insight.

---

## 🌪️ Use Cases (Current)

* Quantify sector-specific market responses to various disaster types.
* Save and organize model outputs, metrics, and plots into consistent directories.
* Run a **tabular regression** task that consolidates all event-day feature sets into one dataset for regression analysis.
* Maintain reproducible pipelines for both single-event and grouped-event studies.

---

## ✅ Project Status

### 📂 Modules Implemented

| Module | Description |
| --- | --- |
| `config/events.py` | Event metadata (dates, locations, sector ETFs) and feature config per disaster type. |
| `src/weather.py` | Fetches weather variables from the Visual Crossing API; computes deviations from pre-event baseline. |
| `src/market.py` | Downloads market and sector ETF data via `yfinance`. |
| `src/returns.py` | Fits CAPM market model on estimation window; computes abnormal and cumulative abnormal returns. |
| `src/dataset.py` | Builds a pooled tabular dataset across all events of a given type. |
| `src/models.py` | Trains XGBoost, Random Forest, and OLS models with LOEO CV; computes evaluation metrics. |
| `src/viz.py` | Generates scatter plots, feature importance charts, CAR trajectories, and metric summaries. |
| `src/analysis.py` | Main orchestrator: builds the dataset, runs per-sector LOEO CV, and saves all outputs. |

---

### 📂 Outputs

Results are saved under `output/{event_type}/`:

```
output/{event_type}/
├── pooled_dataset.csv                        # Full feature + target dataset
├── metrics/{sector}_cv_metrics.csv           # Per-model, per-fold evaluation metrics
├── predictions/{sector}_cv_predictions.csv   # Actual vs. predicted AR and CAR
├── models/{sector}_{model}.pkl               # Trained model artifacts
└── plots/                                    # Scatter plots, feature importance, CAR trajectories
```

---

### ⚠️ Limitations

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