import pandas as pd
import numpy as np
import os
from chart_plotter import plot_chart

market, period = "E", 1
outputFileName = f"graph_period{str(period)}_{market}.csv"
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

merged_df = pd.merge_asof(
    price_volume_df,
    bid_ask_df,
    on='timestamp',
    direction='backward'
)

merged_df['smoothed_price'] = merged_df['price'].rolling(window=10, min_periods=1).mean()

merged_df['spread'] = merged_df['askPrice'] - merged_df['bidPrice']
merged_df['momentum'] = merged_df['smoothed_price'] - merged_df['smoothed_price'].shift(1)

merged_df['volume_ratio'] = merged_df['bidVolume'] / (merged_df['askVolume'] + 1e-6)

mean_spread = merged_df['spread'].mean()
std_spread = merged_df['spread'].std()
mean_momentum = merged_df['momentum'].mean()
std_momentum = merged_df['momentum'].std()

spread_threshold = mean_spread + 0.2 * std_spread
momentum_threshold = 0.8 * std_momentum
buy_volume_threshold = 1.2
sell_volume_threshold = 0.6

def label_entry(row):
    if row['spread'] < spread_threshold:
        if row['momentum'] > momentum_threshold and row['volume_ratio'] > buy_volume_threshold:
            return "Buy"
        elif row['momentum'] < -momentum_threshold and row['volume_ratio'] < sell_volume_threshold:
            return "Sell"
    return "Hold"

merged_df['label'] = merged_df.apply(label_entry, axis=1)

label_counts = merged_df['label'].value_counts()
print(f"Label Distribution:\n{label_counts}")

merged_df['timestamp'] = merged_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S.') + (merged_df['timestamp'].dt.microsecond / 100).astype(int).astype(str).str.zfill(4)

output_columns = ['timestamp', 'price', 'volume', 'bidVolume', 'bidPrice', 'askVolume', 'askPrice', 'spread', 'momentum', 'volume_ratio', 'label']
merged_df[output_columns].to_csv(f'{outputFileName}', index=False)

print(f"The labeled data has been saved to {outputFileName}.")

plot_chart(outputFileName)
