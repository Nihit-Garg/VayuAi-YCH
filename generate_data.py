import numpy as np
import pandas as pd

OUTPUT_FILE = "data/mq2_sample_data.csv"
TARGET_SIZE = 3000

def generate_mq2_pattern(n=3000):
    """
    Generates synthetic MQ2 data mimicking real smoke events.
    Pattern: Baseline -> Rise -> Peak -> Decay -> Baseline
    """
    np.random.seed(42)
    baseline = 220
    data = []

    for t in range(n):
        cycle = t % 1000  # Longer cycle for more variety
        
        # 1. Baseline (Clean Air)
        if cycle < 300:
            value = baseline + np.random.normal(0, 5)
            
        # 2. Fast Rise (Smoke detected)
        elif cycle < 350:
            # Linear rise from baseline to ~900
            progress = (cycle - 300) / 50
            value = baseline + (progress * (900 - baseline)) + np.random.normal(0, 15)
            
        # 3. Peak Plateau (Fire/Smoke sustained)
        elif cycle < 500:
            value = 900 + np.random.normal(0, 25)
            
        # 4. Slow Decay (Ventilation/Dissipation)
        elif cycle < 800:
            # Decay from 900 back to baseline
            progress = (cycle - 500) / 300
            value = 900 - (progress * (900 - baseline)) + np.random.normal(0, 15)
            
        # 5. Return to Baseline
        else:
            value = baseline + np.random.normal(0, 5)
            
        # Clip to realistic ADC values (0-1024)
        value = max(0, min(1023, value))
        data.append(int(value))
        
    return data

def main():
    print(f"Generating {TARGET_SIZE} data points...")
    values = generate_mq2_pattern(TARGET_SIZE)
    
    df = pd.DataFrame({
        "timestamp": range(len(values)),
        "raw_adc": values
    })
    
    print(f"Saving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
