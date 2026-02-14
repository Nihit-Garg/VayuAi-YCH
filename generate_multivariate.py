import numpy as np
import pandas as pd
import datetime
import random

OUTPUT_FILE = "data/mq2_sample_data.csv"
TARGET_SIZE = 5000

def generate_multivariate_data(n=5000):
    """
    Generates synthetic multivariate sensor data with RANDOMIZED events.
    Uses a state machine to transition between Normal, Rise, Peak, and Decay phases.
    """
    np.random.seed(None) # Ensure true randomness each run
    
    # Baselines
    base_mq2 = 220
    base_pm25 = 15
    base_co = 10
    base_voc = 50
    base_temp = 25.0
    base_humidity = 60.0

    data = {
        "timestamp": [],
        "mq2_raw": [],
        "pm25": [],
        "co": [],
        "voc": [],
        "temperature": [],
        "humidity": [],
        "event_label": []
    }
    
    start_time = datetime.datetime.utcnow()
    
    # State Machine
    state = "NORMAL"
    state_duration = 0
    current_intensity = 0.0
    
    # Random parameters for the current event
    target_intensity = 0.0
    rise_speed = 0.005
    decay_speed = 0.005

    for t in range(n):
        # State Transitions
        if state_duration <= 0:
            if state == "NORMAL":
                # Chance to start a fire event
                if random.random() < 0.02: # 2% chance per step to start event
                    state = "RISE"
                    state_duration = random.randint(50, 200) # Random rise duration
                    target_intensity = random.uniform(0.5, 1.2) # Random severity
                    rise_speed = target_intensity / state_duration
                else:
                    state_duration = random.randint(10, 50) # Stay normal for a bit
            
            elif state == "RISE":
                state = "PEAK"
                state_duration = random.randint(50, 150) # Random peak duration
            
            elif state == "PEAK":
                state = "DECAY"
                state_duration = random.randint(100, 300) # Random decay duration
                decay_speed = current_intensity / state_duration
                
            elif state == "DECAY":
                state = "NORMAL"
                state_duration = random.randint(200, 500) # Cooldown
                current_intensity = 0 # Ensure reset

        # Update Intensity based on State
        if state == "NORMAL":
            current_intensity = 0
        elif state == "RISE":
            current_intensity += rise_speed
        elif state == "PEAK":
            pass # constant at target
        elif state == "DECAY":
            current_intensity -= decay_speed
            
        current_intensity = max(0, min(1.5, current_intensity)) # Clamp
        
        state_duration -= 1

        # Generation logic (apply intensity)
        noise = lambda s: np.random.normal(0, s)
        
        # MQ2 (Smoke/Gas)
        mq2_val = base_mq2 + (current_intensity * 700) + noise(15)
        
        # PM2.5 (Particulates)
        pm25_val = base_pm25 + (current_intensity * 400) + noise(8)
        
        # CO (Carbon Monoxide)
        co_val = base_co + (current_intensity * 300) + noise(5)
        
        # VOC
        voc_val = base_voc + (current_intensity * 500) + noise(20)
        
        # Temperature (Rises)
        temp_val = base_temp + (current_intensity * 15) + noise(0.8)
        
        # Humidity (Drops)
        hum_val = base_humidity - (current_intensity * 20) + noise(1.5)
        
        # Append
        data["timestamp"].append((start_time + datetime.timedelta(seconds=t)).isoformat())
        data["mq2_raw"].append(int(mq2_val))
        data["pm25"].append(max(0, pm25_val))
        data["co"].append(max(0, co_val))
        data["voc"].append(max(0, voc_val))
        data["temperature"].append(round(temp_val, 1))
        data["humidity"].append(max(0, min(100, round(hum_val, 1))))
        data["event_label"].append(1 if current_intensity > 0.3 else 0)

    df = pd.DataFrame(data)
    print(f"Saving {len(df)} randomized records to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    generate_multivariate_data(TARGET_SIZE)
