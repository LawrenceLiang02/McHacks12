import pandas as pd
import numpy as np
import os
from chart_plotter import plot_chart

markets = ["A", "B", "C", "D", "E"]
period = 1

for market in markets:
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

    def label_entry(row):
        if row['momentum'] > 0 and row['volume_ratio'] > 1:
            return "Buy"
        elif row['momentum'] < 0 and row['volume_ratio'] < 1:
            return "Sell"
        else:
            return "Hold"

    merged_df['label'] = merged_df.apply(label_entry, axis=1)
    merged_df['market'] = market
    label_counts = merged_df['label'].value_counts()
    print(f"Market {market} Label Distribution:\n{label_counts}")

    merged_df['timestamp'] = merged_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S.') + (merged_df['timestamp'].dt.microsecond / 100).astype(int).astype(str).str.zfill(4)

    output_folder = f"Period{str(period)}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    outputFileName = os.path.join(output_folder, f"{market}.csv")

    output_columns = ['timestamp', 'price', 'volume', 'bidVolume', 'bidPrice', 'askVolume', 'askPrice', 'spread', 'momentum', 'volume_ratio', 'label', 'market']
    merged_df[output_columns].to_csv(outputFileName, index=False)

    print(f"Market {market} labeled data has been saved to {outputFileName}.")

    plot_chart(outputFileName, str(period), f"{market}_plot")

