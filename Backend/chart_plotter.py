import pandas as pd
import matplotlib.pyplot as plt

def plot_chart(file_path, period, market):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Convert timestamp to datetime format for better plotting
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Drop rows with invalid or missing timestamps
    df = df.dropna(subset=['timestamp'])

    # Plot the price vs timestamp
    plt.figure(figsize=(10, 6))
    plt.plot(df['timestamp'], df['price'], label='Price', color='b', alpha=0.7)  # Price line with some transparency

    # Plot Buy, Sell, and Hold as lines
    plt.plot(df[df['label'] == 'Buy']['timestamp'], df[df['label'] == 'Buy']['price'], color='green', label='Buy', lw=2)  # Green for Buy line
    plt.plot(df[df['label'] == 'Sell']['timestamp'], df[df['label'] == 'Sell']['price'], color='red', label='Sell', lw=2)  # Red for Sell line
    plt.plot(df[df['label'] == 'Hold']['timestamp'], df[df['label'] == 'Hold']['price'], color='orange', label='Hold', lw=2, alpha=0.3)  # Orange for Hold line with less opacity
    # Adding title and labels
    plt.title(f"Price Over Period {period} Company {market}")
    plt.xlabel('Timestamp')
    plt.ylabel('Price')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add a legend to indicate which color corresponds to which label
    plt.legend()

    # Display the plot
    plt.tight_layout()
    plt.show()
