import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

WINDOW = 10  # Reduced window size for faster reaction with smaller dataset
MODEL_PATH = "smoke_model.pkl"
DATA_PATH = "data/mq2_sample_data.csv"

np.random.seed(42)


# -------------------------------------------------
# 1. Load & Augment Data
# -------------------------------------------------
def load_and_augment_data(n_augmentations=50):
    """
    Loads real MQ2 data and augments it by adding noise and shifting.
    """
    if not os.path.exists(DATA_PATH):
        print(f"Warning: {DATA_PATH} not found. Generating purely synthetic data.")
        return generate_synthetic_data()

    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    base_signal = df['raw_adc'].values
    
    augmented_data = []
    
    # Original data
    augmented_data.extend(base_signal)
    
    # Augmentations
    for _ in range(n_augmentations):
        # 1. Add random noise
        noise = np.random.normal(0, 5, len(base_signal))
        noisy_signal = base_signal + noise
        
        # 2. Random amplitude scaling (0.9x to 1.1x)
        scale = np.random.uniform(0.9, 1.1)
        scaled_signal = noisy_signal * scale
        
        augmented_data.extend(scaled_signal)
        
    return np.array(augmented_data)


def generate_synthetic_data(n=8000):
    """Fallback synthetic generator matched to MQ2 profile"""
    baseline = 220
    data = []

    for t in range(n):
        cycle = t % 700 
        
        # Simulate the profile from the CSV (Peak around 900, baseline 200)
        if cycle < 200:
            value = baseline + np.random.normal(0, 5)
        elif cycle < 250:
            # fast rise
            value = baseline + (cycle - 200) * 14 + np.random.normal(0, 10)
        elif cycle < 300:
            # peak plateau
            value = 900 + np.random.normal(0, 15)
        elif cycle < 450:
            # slow decay
            value = 900 - (cycle - 300) * 4.5 + np.random.normal(0, 10)
        else:
            value = baseline + np.random.normal(0, 5)
            
        data.append(value)
        
    return np.array(data)


# -------------------------------------------------
# 2. Feature Engineering
# -------------------------------------------------
# -------------------------------------------------
# 2. Feature Engineering (Multivariate)
# -------------------------------------------------
def extract_features(window_df):
    """
    Extracts features from a window of multivariate data.
    Input: DataFrame window with columns [mq2_raw, pm25, co, voc, temperature, humidity]
    """
    features = []
    
    # Iterate over each column to extract stats
    for col in ['mq2_raw', 'pm25', 'co', 'voc', 'temperature', 'humidity']:
        x = window_df[col].values
        
        # Basic Stats
        features.append(np.mean(x))
        features.append(np.max(x))
        features.append(x[-1]) # Last value
        
        # Trend (Slope)
        if len(x) > 1:
            slope = np.polyfit(range(len(x)), x, 1)[0]
        else:
            slope = 0
        features.append(slope)
        
        # Delta
        if len(x) >= 3:
            features.append(x[-1] - x[-3])
        else:
            features.append(0)

    return np.array(features)


# -------------------------------------------------
# 3. Create Dataset
# -------------------------------------------------
def create_dataset(df):
    X, y = [], []
    values = df[['mq2_raw', 'pm25', 'co', 'voc', 'temperature', 'humidity']]
    target = df['mq2_raw'].values # Predicting next MQ2 value as proxy for smoke density

    for i in range(len(values) - WINDOW - 1):
        window_df = values.iloc[i:i + WINDOW]
        target_val = target[i + WINDOW]

        X.append(extract_features(window_df))
        y.append(target_val)

    return np.array(X), np.array(y)


# -------------------------------------------------
# 4. Train Model
# -------------------------------------------------
def train():
    print("Preparing Multivariate data...")
    
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return

    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Drop timestamp and event_label for training inputs if present
    # We use all sensor columns
    print(f"Columns: {df.columns}")
    
    print(f"Total data points: {len(df)}")
    print("Creating training dataset...")
    X, y = create_dataset(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=True, random_state=42
    )

    print(f"Training XGBoost model on {X_train.shape[1]} features...")

    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(X_train, y_train)

    print("Evaluating model...")

    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"MAE: {mae:.2f}")
    print(f"R2 Score: {r2:.4f}")

    with open("metrics.txt", "w") as f:
        f.write(f"MAE: {mae:.2f}\nR2: {r2:.4f}")

    joblib.dump(model, MODEL_PATH)

    print(f"Model saved as {MODEL_PATH}")


if __name__ == "__main__":
    train()
