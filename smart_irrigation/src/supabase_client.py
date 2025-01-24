import logging

from supabase import create_client
import pandas as pd
from config.config import SUPABASE_URL, SUPABASE_KEY, TABLE_NAME


class SupabaseClient:
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    def get_latest_readings(self, limit=100):
        """Fetch latest sensor readings from Supabase"""
        try:
            response = self.supabase.table(TABLE_NAME) \
                .select('id, temperature, humidity, soil_moisture, is_raining, timestamp') \
                .order('timestamp', desc=True) \
                .limit(limit) \
                .execute()

            # Convert to DataFrame
            df = pd.DataFrame(response.data)

            # Map to required feature names
            df = df.rename(columns={
                'temperature': 'temperature_2m_mean',
                'is_raining': 'isRain',
                'humidity': 'apparent_temperature_mean'  # Using humidity as proxy
            })

            return df

        except Exception as e:
            print(f"Error fetching data from Supabase: {e}")
            return None

    def update_prediction(self, reading_id, prediction):
        """Update the prediction for a specific reading"""
        try:
            # Validate prediction value
            if not isinstance(prediction, (int, float)):
                raise ValueError(f"Invalid prediction value type: {type(prediction)}")

            # Validate reading_id
            if not reading_id:
                raise ValueError("Invalid reading_id")

            response = self.supabase.table(TABLE_NAME) \
                .update({'prediction': float(prediction)}) \
                .eq('id', reading_id) \
                .execute()

            if response.data:
                logging.info(f"Successfully updated prediction for reading {reading_id}")
                return True
            else:
                logging.error(f"No data updated for reading {reading_id}")
                return False

        except Exception as e:
            logging.error(f"Error updating prediction in Supabase for reading {reading_id}: {str(e)}")
            return False

    def get_readings_without_predictions(self, limit=100):
        """Fetch readings that don't have predictions yet"""
        try:
            response = self.supabase.table(TABLE_NAME) \
                .select('id, temperature, humidity, soil_moisture, is_raining') \
                .is_('prediction', 'null') \
                .order('timestamp', desc=True) \
                .limit(limit) \
                .execute()

            if response.data:
                df = pd.DataFrame(response.data)
                # Rename columns to match model features
                df = df.rename(columns={
                    'temperature': 'temperature_2m_mean',
                    'is_raining': 'isRain',
                    'humidity': 'apparent_temperature_mean'
                })
                return df
            return None

        except Exception as e:
            print(f"Error fetching unpredicted data: {e}")
            return None

    def insert_reading(self, temperature, humidity, soil_moisture, is_raining):
        """Insert a new sensor reading"""
        try:
            data = {
                'temperature': temperature,
                'humidity': humidity,
                'soil_moisture': soil_moisture,
                'is_raining': is_raining
            }
            response = self.supabase.table(TABLE_NAME).insert(data).execute()
            print("Successfully inserted new reading")
            return response.data
        except Exception as e:
            print(f"Error inserting new reading: {e}")
            return None