import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class DataProcessor:
    def __init__(self, data_path):
        self.target = None
        self.features = None
        self.data_path = data_path
        self.scaler = StandardScaler()

    def load_data(self):
        """Load and perform initial processing of the data"""
        # Read the CSV file
        df = pd.read_csv(self.data_path)

        # Drop rows with NaN values
        df = df.dropna()

        print(f"Shape after dropping NaN values: {df.shape}")

        # Convert precipitation to binary (0 or 1)
        df['isRain'] = (df['precipitation_sum'] > 0).astype(int)

        # Select features
        self.features = [
            'temperature_2m_mean',
            'isRain',
            'apparent_temperature_mean',  # Adding this as proxy for humidity
        ]

        self.target = 'et0_fao_evapotranspiration'

        # Additional check for NaN values in selected features and target
        selected_columns = self.features + [self.target]
        df = df[selected_columns].dropna()

        print(f"Final shape after selecting features and dropping NaN: {df.shape}")
        print("\nFeature summary:")
        print(df[self.features].describe())

        return df

    def prepare_data(self, test_size=0.2, random_state=42):
        """Prepare data for training"""
        df = self.load_data()

        # Prepare X and y
        X = df[self.features]
        y = df[self.target]

        # Final check for NaN values
        assert not X.isnull().any().any(), "X contains NaN values"
        assert not y.isnull().any(), "y contains NaN values"

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test

    def prepare_sensor_data(self, sensor_data):
        """Prepare real-time sensor data for prediction"""
        # Create