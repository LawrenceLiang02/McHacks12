import time
import pandas as pd
import numpy as np

def get_spread(data):
    return data['askPriceAvg'] - data['bidPriceAvg']

def get_volume_impalance(data):
    total_volume = data['bidVolumeSum'] + data['askVolumeSum']
    #print(str(data['bidVolumeSum'] - data['askVolumeSum']) + " / " + str(total_volume) + " = " + str((data['bidVolumeSum'] - data['askVolumeSum']) / total_volume))
    if total_volume == 0:
        return 0
    return (data['bidVolumeSum'] - data['askVolumeSum']) / total_volume

def get_momentum(data):
    return data['actualPriceAvg'].rolling(window=3).mean()

def predict_stock(latest, historical):
    required_columns = {'askPriceAvg', 'bidPriceAvg', 'bidVolumeSum', 'askVolumeSum', 'actualPriceAvg'}
    if not required_columns.issubset(historical.columns):
        raise ValueError(f"Missing required columns: {required_columns - set(historical.columns)}")

    historical = historical.copy()
    historical['spread'] = historical.apply(get_spread, axis=1)
    historical['volume_imbalance'] = historical.apply(get_volume_impalance, axis=1)
    historical['momentum'] = get_momentum(historical)

    # Get metrics for the latest record
    spread = get_spread(latest)
    volume_imbalance = get_volume_impalance(latest)
    momentum = historical['momentum'].iloc[-1]

    # Define thresholds
    spread_threshold = 0.0005
    volume_imbalance_threshold = 0
    momentum_threshold = 0.02

    # Decision logic
    if (
        spread > spread_threshold
        and volume_imbalance > volume_imbalance_threshold
    ):
        return f"BUY | {spread} | {momentum} | {volume_imbalance}"
    elif (
        spread < -spread_threshold
        and volume_imbalance < -volume_imbalance_threshold
    ):
        return f"SELL | {spread} | {momentum} | {volume_imbalance}"
    else:
        return f"HOLD | {spread} | {momentum} | {volume_imbalance}"

file = "./streamed_data.json"
data_json = pd.read_json(file)

for i in range(1, len(data_json)):  # Start from the second record to compare with previous data
    latest = data_json.iloc[i]  # Current record
    historical = data_json.iloc[:i]  # All previous records
    
    try:
        decision = predict_stock(latest, historical)
        print(f"Timestamp: {latest['timestamp']} | Decision: {decision}")
    except ValueError as e:
        print(f"Skipping data at index {i} due to missing fields: {e}")
    except Exception as e:
        print(f"An error occurred at index {i}: {e}")
