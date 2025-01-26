import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

markets = ["A", "B", "C", "D", "E"]
period = 2  # default period, can be updated via API

# Function to preprocess and label data
def preprocess_and_label_data(market, period):
    data_dir = f"TrainingData/Period{str(period)}/{market}/"
    
    all_files = os.listdir(data_dir)
    
    market_data_files = [file for file in all_files if "market_data" in file and file.endswith(".csv")]
    trade_data_files = [file for file in all_files if "trade_data" in file and file.endswith(".csv")]
    
    bid_ask_data = pd.concat([pd.read_csv(os.path.join(data_dir, file)) for file in market_data_files], ignore_index=True)
    price_volume_data = pd.read_csv(os.path.join(data_dir, trade_data_files[0]))
    
    bid_ask_df = pd.DataFrame(bid_ask_data, columns=["bidVolume", "bidPrice", "askVolume", "askPrice", "timestamp"])
    price_volume_df = pd.DataFrame(price_volume_data, columns=["price", "volume", "timestamp"])

    bid_ask_df['timestamp'] = pd.to_datetime(bid_ask_df['timestamp'], errors='coerce')
    price_volume_df['timestamp'] = pd.to_datetime(price_volume_df['timestamp'], errors='coerce')

    bid_ask_df = bid_ask_df.dropna(subset=['timestamp'])
    price_volume_df = price_volume_df.dropna(subset=['timestamp'])

    bid_ask_df = bid_ask_df.sort_values('timestamp')
    price_volume_df = price_volume_df.sort_values('timestamp')

    merged_df = pd.merge_asof(price_volume_df, bid_ask_df, on='timestamp', direction='backward')

    merged_df['smoothed_price'] = merged_df['price'].rolling(window=10, min_periods=1).mean()
    merged_df['spread'] = merged_df['askPrice'] - merged_df['bidPrice']
    merged_df['momentum'] = merged_df['smoothed_price'] - merged_df['smoothed_price'].shift(1)
    merged_df['volume_ratio'] = merged_df['bidVolume'] / (merged_df['askVolume'] + 1e-6)

    def label_entry(row):
        if row['momentum'] > 0 and row['volume_ratio'] > 1:
            return "Buy"
        elif row['momentum'] < 0 and row['volume_ratio'] < 1:
            return "Sell"
        else:
            return "Hold"

    merged_df['label'] = merged_df.apply(label_entry, axis=1)

    return merged_df

# Function to train or test the model
def train_or_test_model(market, period, mode="train"):
    merged_df = preprocess_and_label_data(market, period)
    
    features = merged_df[['spread', 'momentum', 'volume_ratio']]
    labels = merged_df['label']
    
    labels_encoded = labels.map({"Buy": 0, "Sell": 1, "Hold": 2}).values

    X_train, X_test, y_train, y_test = train_test_split(features, labels_encoded, test_size=0.2, random_state=42)

    model = RandomForestClassifier()

    if mode == "train":
        model.fit(X_train, y_train)
        return f"Model trained for market {market}, period {period}"
    elif mode == "test":
        y_pred = model.predict(X_test)
        return classification_report(y_test, y_pred)
