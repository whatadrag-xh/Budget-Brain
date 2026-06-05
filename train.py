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
    le = LabelEncoder()
    sc = StandardScaler()
    df_transactions["date"] = pd.to_datetime(df_transactions["date"])
    amount =df_transactions["amount"]
    category = le.fit_transform(df_transactions["category"])
    day_of_week = df_transactions["date"].dt.dayofweek
    day_of_month = df_transactions["date"].dt.day
    month = df_transactions["date"].dt.month
    features = np.column_stack([amount, category, day_of_week, day_of_month, month])
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
    

