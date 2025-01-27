import os
import pandas as pd
import pickle  # For loading the trained model
from flask import Flask
from flask_sock import Sock
from threading import Thread
import time
import numpy as np
# Initialize Flask app and Flask-Sock
app = Flask(__name__)
sock = Sock(app)

# Directory containing the Period1 folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'TrainingData/Period2')

# Path to the pre-trained machine learning model
MODEL_PATH = os.path.join(BASE_DIR, 'ModelOutput/trained_model.pkl')

# Load the pre-trained model
try:
    with open(MODEL_PATH, 'rb') as model_file:
        model = pickle.load(model_file)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Failed to load model: {e}")
    model = None

# Define column mappings for various formats
COLUMN_MAPPINGS = {
    5: ['bidVolume', 'bidPrice', 'askVolume', 'askPrice', 'timestamp'],  # Expected full format
    3: ['price', 'volume', 'timestamp'],  # Simplified format
    # Add more mappings as needed for other column counts
}

def get_column_names(num_columns):
    """
    Get column names based on the number of columns in the data.
    """
    return COLUMN_MAPPINGS.get(num_columns, [f'col{i}' for i in range(num_columns)])  # Default to generic column names

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

def predict_action(row):
    """
    Predict the action (hold, buy, or sell) for a given row.
    """
    if model:
        try:
            # Convert row to DataFrame (if it's a pandas Series)
            row_df = pd.DataFrame([row]) 

            # Feature engineering
            row_df['spread'] = row_df['askPrice'] - row_df['bidPrice']

            row_df['volume_ratio'] = row_df['bidVolume'] / (row_df['askVolume'] + 1e-6)
            
            # Calculate average price for a given second
            row_df['timestamp_second'] = row_df['timestamp'].dt.floor('s')  # Round down timestamp to the nearest second
            avg_price_per_second = row_df.groupby('timestamp_second')['price'].mean().reset_index(name='avg_price_per_second')
            
            # Merge the average price back into the row
            row_df = pd.merge(row_df, avg_price_per_second, on='timestamp_second', how='left')

            # Ensure all required features are present
            required_features = ['smoothed_price', 'spread', 'momentum', 'volume_ratio', 'avg_price_per_second']
            features = row_df[required_features].values.reshape(1, -1)

            # Convert features to DataFrame to ensure feature names match the model
            features_df = pd.DataFrame(features, columns=required_features)

            # Get the model's prediction (e.g., 0, 1, or 2)
            prediction = model.predict(features_df)
            result = str(prediction[0])
            print(f"Raw model prediction: {result}")  # Debugging the raw prediction

            return result

        except Exception as e:
            print(f"Prediction error: {e}")
            return "error"  # In case of unexpected prediction error

    else:
        return "unknown"  # Default action if the model isn't loaded


def stream_file(sock, file_path, market_name):
    """
    Function to stream the rows (entries) from each file in a market directory.
    """
    try:
        print(f"Reading file: {file_path}")

        # Read and merge the CSV files as before
        merged_df = preprocess_and_label_data(market_name, period=2)

        # Predict and stream each row as a JSON object with a 1-second delay
        for _, row in merged_df.iterrows():
            row_dict = row.to_dict()  # Convert row to dictionary
            row_dict['action'] = predict_action(row)  # Add the predicted action
            row_dict['market'] = market_name
            print(f"Sending data: {row_dict}")  # Debugging: print the data being sent
            sock.send(row_dict)  # Send data through WebSocket
            time.sleep(1)  # Delay for 1 second between sending each row

    except Exception as e:
        sock.send({"status": "error", "message": f"Error processing file {file_path}: {str(e)}"})

# Route to stream file entries through WebSocket
@sock.route('/stream')
def stream(sock):
    try:
        print("WebSocket connection established")
        threads = []

        # Iterate over all sub-directories in the Period2 directory
        for market in os.listdir(DATA_DIR):
            market_path = os.path.join(DATA_DIR, market)
            if os.path.isdir(market_path):
                thread = Thread(target=stream_file, args=(sock, market_path, market))
                thread.start()
                threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        sock.send({"status": "complete", "message": "All file entries have been streamed."})

    except Exception as e:
        sock.send({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
