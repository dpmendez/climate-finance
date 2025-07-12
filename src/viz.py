import os
import matplotlib.pyplot as plt

def plot_predictions(index, actual, lstm_preds, xgb_preds, ticker, event_key):
    plt.figure(figsize=(12, 6))
    plt.plot(index, actual, label='Actual', color='black')
    plt.plot(index, lstm_preds, label='LSTM', linestyle='--')
    plt.plot(index, xgb_preds, label='XGBoost', linestyle=':')
    plt.title(f"Predicted vs Actual Abnormal Returns: {ticker} ({event_key})")
    plt.xlabel("Date")
    plt.ylabel("Abnormal Return")
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def plot_predictions_separately(index_lstm, actual_lstm, preds_lstm,
                                index_xgb, actual_xgb, preds_xgb,
                                ticker, event_key, save_dir="plots"):

    os.makedirs(save_dir, exist_ok=True)

    fig, axs = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    axs[0].plot(index_lstm, actual_lstm, label='Actual', color='black')
    axs[0].plot(index_lstm, preds_lstm, label='LSTM', linestyle='--')
    axs[0].set_title(f"LSTM: {ticker} ({event_key})")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(index_xgb, actual_xgb, label='Actual', color='black')
    axs[1].plot(index_xgb, preds_xgb, label='XGBoost', linestyle=':')
    axs[1].set_title(f"XGBoost: {ticker} ({event_key})")
    axs[1].legend()
    axs[1].grid(True)

    plt.suptitle("Abnormal Return Predictions")
    plt.tight_layout()
    #plt.show()

    save_path = os.path.join(save_dir, f"{ticker}_{event_key}.png")
    plt.savefig(save_path)
    plt.close()

def plot_training_history(history, model_type, ticker, event_key, save_dir="training_plots"):
    """
    Plot training history for LSTM or XGBoost models.

    Parameters:
    - history: dict for XGBoost (evals_result) or Keras History object for LSTM
    - model_type: str, either 'xgboost' or 'lstm'
    - ticker: str, ticker symbol
    - event_key: str, climate event name
    - save_dir: str, directory to save plot
    """
    os.makedirs(save_dir, exist_ok=True)

    plt.figure(figsize=(10, 5))

    if model_type == 'lstm':
        plt.plot(history.history['loss'], label='Train Loss')
        if 'val_loss' in history.history:
            plt.plot(history.history['val_loss'], label='Validation Loss')
    elif model_type == 'xgboost':
        train_metric = history['validation_0']['rmse']
        val_metric = history['validation_1']['rmse']
        plt.plot(train_metric, label='Train RMSE')
        plt.plot(val_metric, label='Validation RMSE')
    else:
        raise ValueError("model_type must be either 'lstm' or 'xgboost'")

    plt.title(f"Training History ({model_type.upper()}) - {ticker} ({event_key})")
    plt.xlabel("Epochs / Boosting Rounds")
    plt.ylabel("Loss / RMSE")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    save_path = os.path.join(save_dir, f"{ticker}_{event_key}_{model_type}_history.png")
    plt.savefig(save_path)
    plt.close()