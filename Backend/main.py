import os
import pandas as pd
from flask import Flask
from flask_sock import Sock
from threading import Thread
from queue import Queue
import time  # Import time module for delay

# Initialize Flask app and Flask-Sock
app = Flask(__name__)
sock = Sock(app)

# Directory containing the Period1 folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Period1')

# Thread-safe Queue to collect data
message_queue = Queue()

def stream_file(message_queue, file_path):
    """
    Function to stream data from a CSV file and push to the message queue.
    """
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Stream each row as a JSON object with a 1-second delay
        for _, row in df.iterrows():
            data = row.to_dict()  # Convert row to dictionary
            message_queue.put(data)  # Put data in the message queue
            time.sleep(1)  # Delay for 1 second between sending each row

        # Put a completion message in the queue
        message_queue.put({"status": "complete", "message": f"Completed streaming from {file_path}"})
    except Exception as e:
        message_queue.put({"status": "error", "message": f"Error in {file_path}: {str(e)}"})

# Route to stream CSV data through WebSocket
@sock.route('/stream')
def stream(sock):
    try:
        threads = []  # List to hold the thread references

        # Iterate over all CSV files in the Period1 directory
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.csv'):  # Ensure only CSV files are processed
                file_path = os.path.join(DATA_DIR, filename)

                # Start a new thread for each file to stream its data
                thread = Thread(target=stream_file, args=(message_queue, file_path))
                thread.start()
                threads.append(thread)

        # Main thread processes the queue and sends data to WebSocket
        while True:
            message = message_queue.get()  # Get data from the queue
            if message:
                sock.send(message)  # Send the data through the WebSocket
            if message.get("status") == "complete" and message_queue.empty():
                break

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Indicate that the streaming is complete
        sock.send({"status": "complete", "message": "All files have been streamed."})

    except Exception as e:
        # Send error details in case of failure
        sock.send({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
