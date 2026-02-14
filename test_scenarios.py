import numpy as np
import joblib
from services.smoke_model_service import SmokeModelService

MODEL_PATH = "smoke_model.pkl"

def run_scenarios():
    print("--- Model Behavior Scenarios ---")
    
    try:
        service = SmokeModelService(MODEL_PATH)
    except FileNotFoundError:
        print("Model not found. Train it first.")
        return

    # Scenario 1: Fire (Rapid Rise)
    # Simulating a sudden increase in all encoded parameters
    fire_input = []
    base_mq2 = 220
    for i in range(10):
        intensity = i * 25
        fire_input.append({
            'mq2_raw': base_mq2 + intensity,
            'pm25': 15 + (intensity * 0.5),
            'co': 10 + (intensity * 0.4),
            'voc': 50 + (intensity * 0.6),
            'temperature': 25 + (i * 0.5),
            'humidity': max(30, 60 - (i * 2))
        })
    
    print("\n[Scenario 1: FIRE / Rapid Rise]")
    print(f"Input Encoded: [Last MQ2={fire_input[-1]['mq2_raw']}, Temp={fire_input[-1]['temperature']}]")
    
    next_val = service.predict(fire_input)
    print(f"Prediction: {next_val:.2f}")
    
    delta = next_val - fire_input[-1]['mq2_raw']
    print(f"Expected Trend: RISING (Delta: +{delta:.2f})")
    
    # Scenario 2: Random / Noise
    random_input = []
    for i in range(10):
        noise = np.random.randint(-5, 5)
        random_input.append({
            'mq2_raw': 220 + noise,
            'pm25': 15 + noise,
            'co': 10 + noise,
            'voc': 50 + noise,
            'temperature': 25.0,
            'humidity': 60.0
        })
    
    print("\n[Scenario 2: RANDOM / Noise]")
    
    next_val = service.predict(random_input)
    print(f"Prediction: {next_val:.2f}")
    
    # In noise, we expect prediction to be near the mean or slightly following last trend
    mq2_values = [r['mq2_raw'] for r in random_input]
    print(f"Mean of MQ2 Input: {np.mean(mq2_values):.2f}")
    
    # Scenario 3: Decay (Fire Extinguished)
    decay_input = []
    for i in range(10):
        intensity = (10 - i) * 20 # Decaying intensity
        decay_input.append({
            'mq2_raw': 220 + intensity,
            'pm25': 15 + (intensity * 0.5),
            'co': 10 + (intensity * 0.4),
            'voc': 50 + (intensity * 0.6),
            'temperature': 35 - (i * 0.5),
            'humidity': 40 + (i * 2)
        })
    
    print("\n[Scenario 3: DECAY / Clearing]")
    
    next_val = service.predict(decay_input)
    print(f"Prediction: {next_val:.2f}")

    delta = next_val - decay_input[-1]['mq2_raw']
    print(f"Expected Trend: FALLING (Delta: {delta:.2f})")

if __name__ == "__main__":
    run_scenarios()
