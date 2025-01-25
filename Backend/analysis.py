import pandas as pd
import numpy as np

def stock_analysis(data_json):
    """
    Analyzes stock data to predict market trends and detect events.
    
    Parameters:
        data_json (str or list): JSON string or list of dictionaries containing stock market data.
        
    Returns:
        pd.DataFrame: A DataFrame with predictions and detected events for each timestamp.
    """
    # Load data into a DataFrame
    data = pd.DataFrame(data_json)
    
    # Preprocess Data
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data.set_index('timestamp', inplace=True)
    data.replace(0, np.nan, inplace=True)  # Replace zero values with NaN for analysis
    
    # Calculate Metrics
    data['spread'] = data['askPriceAvg'] - data['bidPriceAvg']
    data['volume_imbalance'] = (data['bidVolumeSum'] - data['askVolumeSum']) / (
        data['bidVolumeSum'] + data['askVolumeSum']
    )
    data['momentum'] = data['actualPriceAvg'].rolling(window=3).mean()
    
    # Define Activity Levels
    rolling_mean = data[['bidVolumeSum', 'askVolumeSum']].rolling(window=5).mean()
    data['high_activity'] = (
        (data['bidVolumeSum'] > 1.5 * rolling_mean['bidVolumeSum']) |
        (data['askVolumeSum'] > 1.5 * rolling_mean['askVolumeSum'])
    )
    
    # Predict Trends
    data['bullish_score'] = (
        (data['spread'] < 0.02) & (data['volume_imbalance'] > 0.5) & (data['momentum'] > 0)
    ).astype(int)
    data['bearish_score'] = (
        (data['spread'] < 0.02) & (data['volume_imbalance'] < -0.5) & (data['momentum'] < 0)
    ).astype(int)
    data['predicted_direction'] = np.where(
        data['bullish_score'] > data['bearish_score'], 'Bullish', 'Bearish'
    )
    
    # Detect Events
    data['event'] = np.where(
        (data['high_activity']) & (data['spread'] < 0.01),
        'Breakout',
        np.where(
            ~data['high_activity'] & (data['momentum'].diff().abs() < 0.01),
            'Consolidation',
            'Normal'
        )
    )
    
    # Return the DataFrame with relevant columns
    return data[['spread', 'volume_imbalance', 'momentum', 'predicted_direction', 'event']]

# Example usage
file = "./streamed_data.json"
data_json = pd.read_json(file)

predictions = stock_analysis(data_json)
print(predictions)
