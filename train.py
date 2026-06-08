import model
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os
from database import get_all_transactions, get_monthly_totals
from model import SpendingAutoencoder, SpendingLSTM

def prepare_autoencoder_data():
    df_transactions = pd.DataFrame(get_all_transactions())
    df_transactions = df_transactions[df_transactions["type"]=="expense"]
    df_transactions["date"] = pd.to_datetime(df_transactions["date"])
    amount =df_transactions["amount"].values
    le = LabelEncoder()
    sc = StandardScaler()
    category = le.fit_transform(df_transactions["category"])
    day_of_week = df_transactions["date"].dt.dayofweek.values
    day_of_month = df_transactions["date"].dt.day.values
    month = df_transactions["date"].dt.month.values
    features = np.column_stack([
        amount.astype(float),
        category.astype(float),
        day_of_week.astype(float),
        day_of_month.astype(float),
        month.astype(float)
    ]).astype(float)
    scaled_features = sc.fit_transform(features)
    tensor = torch.tensor(scaled_features, dtype = torch.float32)

    os.makedirs("models", exist_ok=True)
    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(sc, f)
    with open("models/label_encoder.pkl", "wb") as f:
        pickle.dump(le, f)

    return tensor

def train_autoencoder():
    train_data = prepare_autoencoder_data()
    model = SpendingAutoencoder()
    
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    epochs = 100
    
    for epoch in range(epochs):
        running_loss = 0
        optimizer.zero_grad()
        output = model(train_data)
        loss = criterion(output, train_data)  
        loss.backward()
        optimizer.step()
        running_loss += loss.item()  
        
        if (epoch + 1) % 20 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss:.4f}")
    
    torch.save(model.state_dict(), "models/autoencoder.pt")
    print("Model saved to models/autoencoder.pt")
    errors = model.reconstruction_error(train_data).numpy()
    threshold = float(np.percentile(errors, 95))
    with open("models/threshold.pkl", "wb") as f:
        pickle.dump(threshold, f)
    print(f"Anomaly threshold set at: {threshold:.6f}")
    return model
    
def prepare_lstm_data():
    monthly_totals = pd.DataFrame(get_monthly_totals())
    expenses = monthly_totals["total_monthly_expenses"].values.reshape(-1, 1)  
    lstm_sc = StandardScaler()
    expenses_scaled = lstm_sc.fit_transform(expenses).flatten()
    X, y = [], []
    window = 3
    for i in range(len(expenses_scaled) - window):
        X.append(expenses_scaled[i:i+window])
        y.append(expenses_scaled[i+window])
    
    X = torch.tensor(np.array(X), dtype=torch.float32).unsqueeze(-1)
    y = torch.tensor(np.array(y), dtype=torch.float32).unsqueeze(-1)
    
    os.makedirs("models", exist_ok=True)
    with open("models/lstm_scaler.pkl", "wb") as f:
        pickle.dump(lstm_sc, f)
    
    return X, y

def train_lstm():
    X, y = prepare_lstm_data()
    X_train, X_val, y_train, y_val = train_test_split(X, y, train_size=0.7, random_state=42, shuffle=False)
    model = SpendingLSTM()

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    epochs = 100

    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(X_train)
        loss = criterion(output, y_train)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_output = model(X_val)
            val_loss = criterion(val_output, y_val)
        model.train()

        if (epoch + 1) % 20 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
    
    torch.save(model.state_dict(), "models/lstm.pt")
    print("Model saved to models/lstm.pt")   
    return model

if __name__ == "__main__":
    print("Training autoencoder...")
    train_autoencoder()
    print("Training LSTM...")
    train_lstm()
    print("All models trained!")