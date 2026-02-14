import pandas as pd
import joblib
import os
import datetime
import random
from services.smoke_model_service import SmokeModelService

DATA_PATH = "data/mq2_sample_data.csv"
MODEL_PATH = "smoke_model.pkl"

MODEL_PATH = "smoke_model.pkl"

def get_user_input():
    print("\n--- Interactive Data Entry ---")
    choice = input("Add new data point? (m)anual / (r)andom / (c)luster / (s)kip: ").lower().strip()
    
    if choice in ['s', 'skip', '']: 
        return

    # Load last row to get context for correlated features
    try:
        last_row = pd.read_csv(DATA_PATH).iloc[-1]
    except Exception:
        # Fallback if empty (unlikely)
        last_row = {'mq2_raw': 200, 'pm25': 5, 'co': 5, 'voc': 40, 'temperature': 25, 'humidity': 60}

    new_rows = []
    
    if choice in ['m', 'manual']:
        try:
            val = input("Enter MQ2 value: ")
            new_rows.append(float(val))
        except ValueError:
            print("Invalid number. Skipping.")
            return
            
    elif choice in ['r', 'random']:
        # Generate based on constraints (recent trend + noise)
        base = float(last_row['mq2_raw'])
        if random.random() < 0.1: # 10% chance of random spike
             new_mq2 = random.uniform(600, 900)
             print(f"Generated SPIKE value: {new_mq2:.2f}")
        else:
             change = random.uniform(-20, 20)
             new_mq2 = max(150, base + change) 
             print(f"Generated value: {new_mq2:.2f}")
        new_rows.append(new_mq2)
        
    elif choice in ['c', 'cluster']:
        try:
            target = float(input("Enter Target MQ2 Value (e.g., 900): "))
            count = int(input("Enter Number of Points (e.g., 5): "))
            
            print(f"Generating {count} points around {target}...")
            for _ in range(count):
                # Add some jitter
                val = target + random.uniform(-15, 15)
                new_rows.append(val)
        except ValueError:
            print("Invalid input. Skipping.")
            return
            
    else:
        return

    # Process all new rows
    rows_to_add = []
    current_time = datetime.datetime.now()
    
    for i, mq2_val in enumerate(new_rows):
        # Determine correlated values based on MQ2 intensity
        # High MQ2 (>400) implies fire/smoke -> High PM2.5, High CO
        pm25_base = float(last_row['pm25'])
        co_base = float(last_row['co'])
        
        if mq2_val > 400:
            pm25_base = random.uniform(50, 150) # Spike particulate
            co_base = random.uniform(20, 50)    # Spike CO
        
        row = {
            'timestamp': (current_time + datetime.timedelta(seconds=i)).isoformat(),
            'mq2_raw': mq2_val,
            'pm25': max(0.0, pm25_base + random.uniform(-2, 2)),
            'co': max(0.0, co_base + random.uniform(-1, 1)),
            'voc': max(0.0, float(last_row['voc']) + random.uniform(-5, 5)),
            'temperature': float(last_row['temperature']) + random.uniform(-0.5, 0.5),
            'humidity': float(last_row['humidity']) + random.uniform(-1, 1),
            'event_label': 1 if mq2_val > 400 else 0
        }
        rows_to_add.append(row)
    
    if rows_to_add:
        # Append to CSV
        df = pd.DataFrame(rows_to_add)
        df.to_csv(DATA_PATH, mode='a', header=False, index=False)
        print(f"Added {len(rows_to_add)} data points successfully!\n")

def predict_next_n(n=5):
    get_user_input()
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

    # Convert last 50 rows to list of dicts (matching new WINDOW size)
    data = df[required_cols].tail(50).to_dict('records')
    
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
