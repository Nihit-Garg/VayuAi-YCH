import pandas as pd
import joblib
import os
from services.smoke_model_service import SmokeModelService

DATA_PATH = "data/mq2_sample_data.csv"
MODEL_PATH = "smoke_model.pkl"

def predict_next_n(n=5):
    print(f"--- Generating next {n} predictions ---")
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print("Error: Data file not found.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Ensure expected columns exist
    required_cols = ['mq2_raw', 'pm25', 'co', 'voc', 'temperature', 'humidity']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: Dataset missing required columns. Found: {df.columns}")
        return

    # Convert last 10 rows to list of dicts
    data = df[required_cols].tail(10).to_dict('records')
    
    # 2. Initialize Service
    try:
        service = SmokeModelService(MODEL_PATH)
    except FileNotFoundError:
        print("Error: Model not found. Train it first.")
        return

    print(f"Initial Context (Last 3 MQ2 readings): {[d['mq2_raw'] for d in data[-3:]]}")
    
    current_window = data.copy()
    predictions = []

    # 3. Iterative Prediction
    for i in range(n):
        # Predict next value
        next_val = service.predict(current_window)
        predictions.append(next_val)
        
        print(f"Step {i+1}: Predicted MQ2={next_val:.2f}")
        
        # Create next mock reading (Holding other env vars constant for short-term forecast)
        last_reading = current_window[-1].copy()
        next_reading = {
            'mq2_raw': next_val,
            'pm25': last_reading['pm25'],
            'co': last_reading['co'],
            'voc': last_reading['voc'],
            'temperature': last_reading['temperature'],
            'humidity': last_reading['humidity']
        }
        
        # Update specific correlated values slightly if MQ2 rises/falls significantly (Simulation)
        if next_val > last_reading['mq2_raw'] + 5:
            # Smoke rising -> PM2.5 & CO likely rising
            next_reading['pm25'] += 1
            next_reading['co'] += 0.5
        elif next_val < last_reading['mq2_raw'] - 5:
            # Smoke clearing
            next_reading['pm25'] = max(0, next_reading['pm25'] - 1)
            next_reading['co'] = max(0, next_reading['co'] - 0.5)

        # Slide window
        current_window.append(next_reading)
        current_window.pop(0)

    print("\n--- Final Results ---")
    print(f"Next 5 Predicted MQ2 Values: {[round(x, 2) for x in predictions]}")

if __name__ == "__main__":
    predict_next_n(5)
