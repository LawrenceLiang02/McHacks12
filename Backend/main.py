import os
import pandas as pd
from flask import Flask
from flask_sock import Sock

# Initialize Flask app and Flask-Sock
app = Flask(__name__)
sock = Sock(app)

# Directory containing the Period1 folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Period1')

# Route to stream CSV data through WebSocket
@sock.route('/stream')
def stream(sock):
    try:
        # Iterate over all CSV files in the Period1 directory
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.csv'):  # Ensure only CSV files are read
                file_path = os.path.join(DATA_DIR, filename)
                # Read the CSV file into a DataFrame
                df = pd.read_csv(file_path)

                # Stream each row as a JSON object
                for _, row in df.iterrows():
                    data = row.to_dict()  # Convert row to dictionary
                    sock.send(data)  # Send the data through the WebSocket

        # Close the socket after sending all data
        sock.send({"status": "complete", "message": "Streaming completed."})
    except Exception as e:
        # Send error details in case of failure
        sock.send({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
