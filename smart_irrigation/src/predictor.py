import joblib
import numpy as np
from config.config import MODEL_PATH, FEATURES


class Predictor:
    def __init__(self):
        self.model = self._load_model()
        self.features = FEATURES

    def _load_model(self):
        """Load the trained XGBoost model"""
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def prepare_features(self, data):
        """Prepare features for prediction"""
        if set(self.features).issubset(data.columns):
            return data[self.features]
        else:
            missing_features = set(self.features) - set(data.columns)
            raise ValueError(f"Missing features: {missing_features}")

    def predict(self, data):
        """Make predictions using the loaded model"""
        try:
            # Prepare features
            X = self.prepare_features(data)

            # Make predictions
            predictions = self.model.predict(X)

            return predictions

        except Exception as e:
            print(f"Error making predictions: {e}")
            return None