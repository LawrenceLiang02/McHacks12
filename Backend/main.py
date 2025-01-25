import time
import pandas as pd
from flask import Flask
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

@app.route('/')
def index():
    return "Working"


@sock.route('/stream')
def stream(sock):
    market_data['type'] = 'market'
    trade_data['type'] = 'trade'
    combined_data = pd.concat([market_data, trade_data]).sort_values(by='timestamp')
    
    for _, row in combined_data.iterrows():
        row_json = row.to_json()
        print(f"Sending: {row_json}")
        sock.send(row_json)
        time.sleep(1)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)