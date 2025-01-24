import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Model Configuration
MODEL_PATH = 'models/optimized_xgboost.joblib'

# Feature Configuration
FEATURES = [
    'temperature_2m_mean',  # mapped from temperature
    'isRain',              # mapped from is_raining
    'apparent_temperature_mean'  # mapped from humidity
]

# Database Configuration
TABLE_NAME = 'raw_sensors_data'

# Schema Configuration
SCHEMA = {
    'temperature': 'float',
    'humidity': 'float',
    'soil_moisture': 'integer',
    'is_raining': 'boolean',
    'timestamp': 'timestamptz',
    'prediction': 'float'
}