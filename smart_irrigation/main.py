from src.supabase_client import SupabaseClient
from src.predictor import Predictor
import time
import schedule
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_new_readings():
    """Process new sensor readings and update predictions"""
    logging.info("\nProcessing new readings...")

    # Initialize clients
    supabase = SupabaseClient()
    predictor = Predictor()

    try:
        # Get readings without predictions
        readings = supabase.get_readings_without_predictions()

        if readings is not None and not readings.empty:
            logging.info(f"\nFound {len(readings)} new readings to process")

            # Print input data for debugging
            logging.info("\nInput Data Sample:")
            logging.info(readings.head())

            try:
                # Make predictions
                predictions = predictor.predict(readings)

                # Create results dataframe
                results = pd.DataFrame({
                    'ID': readings['id'],
                    'Temperature': readings['temperature_2m_mean'],
                    'Humidity': readings['apparent_temperature_mean'],
                    'Is Raining': readings['isRain'],
                    'Predicted_Evapotranspiration': predictions
                })

                # Add delay between updates to prevent rate limiting
                for _, row in results.iterrows():
                    try:
                        prediction_value = float(row['Predicted_Evapotranspiration'])
                        logging.info(f"\nUpdating prediction for ID: {row['ID']}")
                        logging.info(f"Input values: Temp={row['Temperature']}°C, "
                                     f"Humidity={row['Humidity']}%, "
                                     f"IsRaining={row['Is Raining']}")
                        logging.info(f"Predicted value: {prediction_value:.4f} mm/day")

                        # Update database
                        supabase.update_prediction(row['ID'], prediction_value)
                        time.sleep(0.5)  # Add small delay between updates

                    except Exception as e:
                        logging.error(f"Error updating prediction for ID {row['ID']}: {str(e)}")
                        continue

                logging.info("\nCompleted processing all readings")

            except Exception as e:
                logging.error(f"Error during prediction: {str(e)}")
        else:
            logging.info("No new readings to process")

    except Exception as e:
        logging.error(f"Error in process_new_readings: {str(e)}")


def main():
    logging.info("Starting Smart Irrigation Prediction Service")

    # Run immediately on startup
    process_new_readings()

    # Schedule the job to run every 5 minutes
    schedule.every(5).minutes.do(process_new_readings)

    # Keep the script running
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")


if __name__ == "__main__":
    main()