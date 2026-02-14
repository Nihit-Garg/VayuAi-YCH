import numpy as np
import joblib
import os


class SmokeModelService:
    """
    ML inference service for smoke prediction (MQ2 Sensor).
    Uses trained XGBoost model on CO/Smoke analog values.
    """

    def __init__(self, model_path: str = "smoke_model.pkl"):
        self.window_size = 10  # Must match training WINDOW
        self.model_path = model_path
        self.model = self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}. "
                f"Run train_smoke_model.py first."
            )
        return joblib.load(self.model_path)

    def extract_features(self, window_data):
        """
        Convert last 10 readings (dict list) into ML feature vector (30 features).
        MUST match extract_features in smoke_model.py
        Input: List of dicts with keys ['mq2_raw', 'pm25', 'co', 'voc', 'temperature', 'humidity']
        """
        features = []
        
        # Helper to get array for a key
        def get_col(key):
            return np.array([r.get(key, 0) for r in window_data])

        # Iterate over each column to extract stats
        for col in ['mq2_raw', 'pm25', 'co', 'voc', 'temperature', 'humidity']:
            x = get_col(col)
            
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

    def predict(self, readings):
        """
        Predict next MQ2 value based on multivariate context.
        readings: List of dicts or objects with required attributes.
        """
        if len(readings) < self.window_size:
            # Not enough data, return last MQ2 value (naive)
            last_reading = readings[-1] if readings else {}
            # Handle both dict and object access
            val = last_reading.get('mq2', 0) if isinstance(last_reading, dict) else getattr(last_reading, 'co', 0) # Fallback to CO/MQ2
            return float(val)

        window = readings[-self.window_size:]
        
        # Normalize input to list of dicts
        window_dicts = []
        for r in window:
            if isinstance(r, dict):
                window_dicts.append(r)
            else:
                # Assuming Pydantic model or object
                window_dicts.append({
                    'mq2_raw': getattr(r, 'co', 0),    # Mapping CO to MQ2 Raw for model compatibility
                    'pm25': getattr(r, 'pm25', 0),
                    'co': getattr(r, 'co', 0),
                    'voc': getattr(r, 'voc', 0),
                    'temperature': getattr(r, 'temperature', 25.0), # Default if missing
                    'humidity': getattr(r, 'humidity', 50.0)
                })
        
        features = self.extract_features(window_dicts)

        prediction = self.model.predict([features])[0]

        return float(prediction)
