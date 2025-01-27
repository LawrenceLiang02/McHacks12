import os
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Function to engineer features for the model
def engineer_features(data):
    data['smoothed_price'] = data['price'].rolling(window=10, min_periods=1).mean()
    data['spread'] = data['askPrice'] - data['bidPrice']
    data['momentum'] = data['smoothed_price'] - data['smoothed_price'].shift(1)
    data['volume_ratio'] = data['bidVolume'] / (data['askVolume'] + 1e-6)
    
    # Calculate average price for a given second
    data['timestamp_second'] = data['timestamp'].dt.floor('s')  # Round down timestamp to the nearest second
    avg_price_per_second = data.groupby('timestamp_second')['price'].mean().reset_index(name='avg_price_per_second')
    
    # Merge the average price back into the original data
    data = pd.merge(data, avg_price_per_second, on='timestamp_second', how='left')
    
    return data

# Labeling function based on momentum and volume ratio
def label_entry(row):
    if row['momentum'] > 0 and row['volume_ratio'] > 1:
        return "Buy"
    elif row['momentum'] < 0 and row['volume_ratio'] < 1:
        return "Sell"
    else:
        return "Hold"

# Prepare the data for training/testing
def prepare_data(data, is_test=False):
    data = engineer_features(data)
    
    # For training, apply the labeling
    if not is_test:
        data['label'] = data.apply(label_entry, axis=1)
        data['label'] = data['label'].astype(str)

    features = data[['smoothed_price', 'spread', 'momentum', 'volume_ratio']]  # Include avg price as a feature
    if is_test:
        return features
    else:
        labels = data['label'].values
        return features, labels

# Function to train and evaluate the model
def train_and_evaluate(merged_df, model, output_folder, test_data=None):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Check if the dataset is empty
    if merged_df.empty:
        print("No data available for training. Exiting.")
        return

    # Prepare training data
    X_train, y_train = prepare_data(merged_df)

    # Check if there are enough samples to split
    if len(X_train) < 2:  # At least 2 samples needed for train/test split
        print("Not enough data for training and validation split. Exiting.")
        return

    # Split into train and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate on validation set
    y_pred = model.predict(X_val)
    print("Classification report on Validation Set:")
    print(classification_report(y_val, y_pred, target_names=["Buy", "Sell", "Hold"]))

    try:
        model_filename = os.path.join(output_folder, 'trained_model.pkl')
        with open(model_filename, 'wb') as model_file:
            pickle.dump(model, model_file)
        print(f"Model saved to {model_filename}")
    except Exception as e:
        print(f"Error saving model: {e}")

    # If test data is provided, evaluate on the test set
    if test_data is not None:
        X_test = prepare_data(test_data, is_test=True)
        y_test_pred = model.predict(X_test)
        test_data['predicted_label'] = y_test_pred

        # Save the predictions to the specified folder
        output_file = os.path.join(output_folder, "predicted_data.csv")
        test_data.to_csv(output_file, index=False)
        print(f"Test data predictions saved to {output_file}.")

# Main execution
model = RandomForestClassifier()  # Model creation

base_data_folder = "TrainingData"
merged_df_all_periods = pd.DataFrame()  # Initialize an empty DataFrame to hold all the combined data
timestamp_format = "%H:%M:%S.%f"

# Loop through all periods and markets dynamically to accumulate data
for period in os.listdir(base_data_folder):
    period_folder = os.path.join(base_data_folder, period)
    
    if os.path.isdir(period_folder):  # Check if it is a valid period folder
        for market in os.listdir(period_folder):
            market_folder = os.path.join(period_folder, market)
            
            if os.path.isdir(market_folder):  # Check if it's a valid market folder
                # Get all relevant market data files