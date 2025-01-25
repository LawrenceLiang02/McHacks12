import time
import pandas as pd
from flask import Flask, json
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

data_path = "./TrainingData/Period1/A"
market_data = pd.read_csv(f'{data_path}/market_data_A_0.csv')
trade_data = pd.read_csv(f'{data_path}/trade_data__A.csv')

market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
trade_data['timestamp'] = pd.to_datetime(trade_data['timestamp'])
market_data = market_data.sort_values(by='timestamp')
trade_data = trade_data.sort_values(by='timestamp')

start_time = pd.Timestamp("08:10:00")
accumulated_data = []

def align_and_aggregate(market_data, trade_data, start_time, group_by='1S'):
    market_data = market_data[market_data['timestamp'] >= start_time]
    trade_data = trade_data[trade_data['timestamp'] >= start_time]

    market_data['grouped_timestamp'] = ((market_data['timestamp'] - start_time).dt.total_seconds() // 1).astype(int)
    trade_data['grouped_timestamp'] = ((trade_data['timestamp'] - start_time).dt.total_seconds() // 1).astype(int)

    market_data['grouped_timestamp'] = start_time + pd.to_timedelta(market_data['grouped_timestamp'], unit='s')
    trade_data['grouped_timestamp'] = start_time + pd.to_timedelta(trade_data['grouped_timestamp'], unit='s')

    market_data['type'] = 'market'
    trade_data['type'] = 'trade'
    combined_data = pd.concat([market_data, trade_data])

    aggregated = combined_data.set_index('grouped_timestamp').resample(group_by).agg({
        'bidVolume': ['sum', 'mean'],
        'askVolume': ['sum', 'mean'],
        'volume': ['sum', 'mean'],
        'bidPrice': ['sum', 'mean'],
        'askPrice': ['sum', 'mean'],
        'price': ['sum', 'mean']
    }).fillna(0).reset_index()

    # Flatten column names
    aggregated.columns = ['_'.join(col).rstrip('_') if isinstance(col, tuple) else col for col in aggregated.columns]

    # Rename columns
    aggregated.rename(columns={
        'grouped_timestamp': 'timestamp',
        'bidVolume_sum': 'bidVolumeSum',
        'bidVolume_mean': 'bidVolumeAvg',
        'askVolume_sum': 'askVolumeSum',
        'askVolume_mean': 'askVolumeAvg',
        'volume_sum': 'actualVolumeSum',
        'volume_mean': 'actualVolumeAvg',
        'bidPrice_sum': 'bidPriceSum',
        'bidPrice_mean': 'bidPriceAvg',
        'askPrice_sum': 'askPriceSum',
        'askPrice_mean': 'askPriceAvg',
        'price_sum': 'actualPriceSum',
        'price_mean': 'actualPriceAvg'
    }, inplace=True)

    # Format timestamp
    aggregated['timestamp'] = aggregated['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return aggregated

combined_data = align_and_aggregate(market_data, trade_data, start_time)

@app.route('/')
def index():
    return "WebSocket server is working"

@sock.route('/stream')
def stream(sock):
    for _, row in combined_data.iterrows():
        row_dict = row.to_dict()
        accumulated_data.append(row_dict)

        row_json = row.to_json()
        print(f"Sending: {row_json}")
        sock.send(row_json)

        with open("streamed_data.json", "w") as json_file:
            json.dump(accumulated_data, json_file, indent=4)
        time.sleep(1)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
