import torch
import pickle
import numpy as np
import pandas as pd
from model import SpendingAutoencoder, SpendingLSTM
from database import get_all_transactions, get_monthly_totals

def load_autoencoder():
    with open("models/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("models/threshold.pkl", "rb") as f:
        threshold = pickle.load(f)
    with open ("models/label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    model = SpendingAutoencoder()
    model.load_state_dict(torch.load("models/autoencoder.pt"))
    model.eval()
    return model, scaler, label_encoder, threshold

def detect_anomalies():
    model, scaler, label_encoder, threshold = load_autoencoder()
    df_transactions = pd.DataFrame(get_all_transactions())
    df_transactions = df_transactions[df_transactions["type"]=="expense"]
    df_transactions["date"] = pd.to_datetime(df_transactions["date"])
    df_transactions["category_encoded"] = df_transactions["category"].apply(
        lambda c: label_encoder.transform([c])[0] if c in label_encoder.classes_ else -1
    )
    df_transactions["day_of_week"] = df_transactions["date"].dt.dayofweek
    df_transactions["day_of_month"] = df_transactions["date"].dt.day
    df_transactions["month"] = df_transactions["date"].dt.month
    features = np.column_stack([
        df_transactions["amount"], 
        df_transactions["category_encoded"],
        df_transactions["day_of_week"],
        df_transactions["day_of_month"],
        df_transactions["month"]
    ])
    tensor  = torch.tensor(scaler.transform(features), dtype= torch.float32)
    with torch.no_grad():
        errors = model.reconstruction_error(tensor).numpy()
        df_transactions["anomaly_score"] = errors
        df_transactions["is_anomaly"] = df_transactions["anomaly_score"] > threshold
        anomalies = df_transactions[df_transactions["is_anomaly"]==True][["date", "description", "category", "amount", "type", "anomaly_score"]].to_dict("records")
        return anomalies
    
def forecast_next_month():
    lstm_model = SpendingLSTM()
    lstm_model.load_state_dict(torch.load("models/lstm.pt"))
    lstm_model.eval()
    with open("models/lstm_scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    monthly = get_monthly_totals()
    last_3 = [m["total_monthly_expenses"] for m in monthly[-3:]]
    scaled = scaler.transform(np.array(last_3).reshape(-1, 1)).flatten()
    lstm_input = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
    with torch.no_grad():
        predicted_scaled = lstm_model(lstm_input).item()
        predicted_expense = scaler.inverse_transform([[predicted_scaled]])
        return predicted_expense[0][0]
    
if __name__ == "__main__":
    anomalies = detect_anomalies()
    print("Anomalies detected:")
    for a in anomalies:
        print(a)
    
    next_month_expense = forecast_next_month()
    print(f"Predicted total expenses for next month: {next_month_expense:.2f}")