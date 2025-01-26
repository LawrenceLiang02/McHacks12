import os
import pandas as pd
from flask import Flask
from flask_sock import Sock
from threading import Thread
import time

# Initialize Flask app and Flask-Sock
app = Flask(__name__)
sock = Sock(app)

# Directory containing the Period1 folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'TrainingData/Period1')

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

def stream_file(sock, file_path, market_name):
    """
    Function to stream the rows (entries) from each file in a market directory.
    """
    try:
        print(f"Reading file: {file_path}")  # Debugging: print the file path

        # Read the CSV file into a DataFrame without a header
        df = pd.read_csv(file_path, header=None)  # Assuming no header in the files
        print(f"DataFrame shape: {df.shape}")
        
        # Get appropriate column names based on the number of columns in the file
        num_columns = df.shape[1]
        column_names = get_column_names(num_columns)
        df.columns = column_names

        # Add the market name to the DataFrame
        df['market'] = market_name

        # Stream each row as a JSON object with a 1-second delay
        for _, row in df.iterrows():
            data = row.to_dict()  # Convert row to dictionary
            print(f"Sending data: {data}")  # Debugging: print the data being sent
            sock.send(data)  # Send data through WebSocket
            time.sleep(1)  # Delay for 1 second between sending each row

    except Exception as e:
        sock.send({"status": "error", "message": f"Error processing file {file_path}: {str(e)}"})

# Route to stream file entries through WebSocket
@sock.route('/stream')
def stream(sock):
    try:
        print("WebSocket connection established")  # Debugging: connection established message
        threads = []  # List to hold the thread references

        # Iterate over all sub-directories in the Period1 directory
        for market in os.listdir(DATA_DIR):
            market_path = os.path.join(DATA_DIR, market)
            if os.path.isdir(market_path):  # Ensure it's a sub-directory
                print(f"Processing market: {market}")  # Debugging: print current market
                
                # Iterate over files in each market folder
                for filename in os.listdir(market_path):
                    try:
                        full_path = os.path.join(market_path, filename)

                        # Ensure the entry is a file (and optionally check for CSV if needed)
                        if os.path.isfile(full_path):  # Ensure it's a file
                            print(f"Found file in market {market}: {filename}")  # Debugging: file is recognized

                            # Start a new thread for each file to stream its rows
                            thread = Thread(target=stream_file, args=(sock, full_path, market))
                            thread.start()
                            threads.append(thread)
                        else:
                            print(f"Skipping directory in market {market}: {filename}")  # Debugging: print if it's a directory
                    except Exception as e:
                        print(f"Error processing file {filename} in market {market}: {str(e)}")  # Debugging: print any errors

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Indicate that the streaming is complete
        sock.send({"status": "complete", "message": "All file entries have been streamed."})

    except Exception as e:
        # Send error details in case of failure
        sock.send({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
