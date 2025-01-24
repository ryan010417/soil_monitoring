#include "VOneMqttClient.h"
#include "SupabaseClient.h"
#include <DHT.h>

// Soil Moisture Mapping
int MinMoistureValue = 4095;
int MaxMoistureValue = 2060;
int MinMoisture = 0;
int MaxMoisture = 100;
int Moisture = 0;

// Define device IDs
const char* SOIL_MOISTURE_ID = "159cd689-3e65-468c-925a-a3d7f23c466f";    // Your soil moisture sensor ID
const char* DHT11_ID = "87a90331-1f6a-4c25-9260-3bd44f991485";            // Your DHT11 sensor ID
const char* RAIN_SENSOR_ID = "8e38ae77-a2e0-4e82-aad1-3b44a0bc1be2";      // Rain sensor ID

// Pin Definitions
const int MOISTURE_PIN = 7;    // Soil moisture sensor
const int DHT_PIN = 42;        // DHT11 sensor
const int GREEN_LED_PIN = 9;   // Green LED for good conditions
const int RED_LED_PIN = 5;     // Red LED for alerts
const int RAIN_PIN = 6;        // Rain sensor pin

// Initialize sensors
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);
// Supabase Configuration
const char* SUPABASE_URL = "https://zcpbbsewwlkfdaqaykjn.supabase.co";
const char* SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpjcGJic2V3d2xrZmRhcWF5a2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY4NjMzODAsImV4cCI6MjA1MjQzOTM4MH0.F57-GHy6mdrjBLsTdbTcg2dQsL8_VDrMiliNg5nT070";

// Create an instance of VOneMqttClient
VOneMqttClient voneClient;
SupabaseClient supabaseClient(SUPABASE_URL, SUPABASE_KEY);

// Last message time
unsigned long lastMsgTime = 0;

// Variables for sensor readings
struct SensorData {
  int moistureRaw;
  int moisturePercentage;
  float temperature;
  float humidity;
  bool isRaining;    // Added for rain sensor
} sensorData;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  
  // Setup pins
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(RAIN_PIN, INPUT);
  
  // Initial LED test
  digitalWrite(GREEN_LED_PIN, HIGH);
  digitalWrite(RED_LED_PIN, HIGH);
  delay(1000);
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  
  dht.begin();
  setup_wifi();
  voneClient.setup();

  Serial.println("==========================================");
  Serial.println("Smart Plant Monitoring System");
  Serial.println("==========================================");
}

void updateLEDs() {
  // Check soil moisture condition
  if (sensorData.moisturePercentage <= 30) {
    digitalWrite(RED_LED_PIN, HIGH);   // Turn on red LED
    digitalWrite(GREEN_LED_PIN, LOW); // Ensure green LED is off
  } else {
    digitalWrite(RED_LED_PIN, LOW);   // Turn off red LED
    digitalWrite(GREEN_LED_PIN, HIGH); // Turn on green LED for normal conditions
  }
}

void readAllSensors() {
  // Read Soil Moisture
  sensorData.moistureRaw = analogRead(MOISTURE_PIN);
  Serial.print("Raw Moisture Value: ");
  Serial.println(sensorData.moistureRaw);
  
  sensorData.moistureRaw = constrain(sensorData.moistureRaw, MaxMoistureValue, MinMoistureValue);
  sensorData.moisturePercentage = map(sensorData.moistureRaw, MinMoistureValue, MaxMoistureValue, MinMoisture, MaxMoisture);
  
  // Read Temperature and Humidity
  sensorData.humidity = dht.readHumidity();
  sensorData.temperature = dht.readTemperature();
  
  // Read Rain Sensor
  sensorData.isRaining = !digitalRead(RAIN_PIN);  // Inverted because sensor gives LOW when wet
  
  // Check if DHT reading failed
  if (isnan(sensorData.temperature) || isnan(sensorData.humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    voneClient.publishDeviceStatusEvent(DHT11_ID, false);
    digitalWrite(RED_LED_PIN, HIGH);
    digitalWrite(GREEN_LED_PIN, LOW);
    return;
  }
  
  voneClient.publishDeviceStatusEvent(DHT11_ID, true);
  voneClient.publishDeviceStatusEvent(RAIN_SENSOR_ID, true);
  updateLEDs();
}

void sendToVOne() {
  // Publish soil moisture data
  voneClient.publishTelemetryData(SOIL_MOISTURE_ID, "Soil moisture", sensorData.moisturePercentage);
  
  // Create JSON object for DHT11 data
  JSONVar dhtPayload;    
  dhtPayload["Humidity"] = sensorData.humidity;
  dhtPayload["Temperature"] = sensorData.temperature;
  voneClient.publishTelemetryData(DHT11_ID, dhtPayload);
  
  // Publish rain sensor data
  voneClient.publishTelemetryData(RAIN_SENSOR_ID, "Raining", sensorData.isRaining);
}

void printReadings() {
  Serial.println("\n----------------------------------------");
  
  // Moisture Status
  Serial.print("Soil Moisture: ");
  Serial.print(sensorData.moisturePercentage);
  Serial.println("%");
  Serial.print("Soil Status: ");
  if (sensorData.moisturePercentage <= 10) {
    Serial.println("Very Dry - Urgent Watering Required!");
  } else if (sensorData.moisturePercentage <= 30) {
    Serial.println("Dry - Watering Needed");
  } else if (sensorData.moisturePercentage <= 60) {
    Serial.println("Optimal Moisture");
  } else {
    Serial.println("Wet - No Watering Needed");
  }
  
  // Temperature and Humidity
  Serial.print("Air Temperature: ");
  Serial.print(sensorData.temperature, 1);
  Serial.println("°C");
  
  Serial.print("Air Humidity: ");
  Serial.print(sensorData.humidity, 1);
  Serial.println("%");
  
  // Rain Status
  Serial.print("Rain Status: ");
  Serial.println(sensorData.isRaining ? "RAINING!" : "No Rain");
  
  // Environmental Status
  Serial.print("Environment Status: ");
  if (sensorData.temperature > 30) {
    Serial.println("Warning: Temperature too high!");
  } else if (sensorData.humidity > 85) {
    Serial.println("Warning: Humidity too high!");
  } else if (sensorData.isRaining) {
    Serial.println("Warning: Rain detected!");
  } else {
    Serial.println("Optimal Growing Conditions");
  }
}

void sendToSupabase() {
    bool success = supabaseClient.sendSensorData(
        sensorData.temperature,
        sensorData.humidity,
        sensorData.moisturePercentage,
        sensorData.isRaining
    );

    if (success) {
        Serial.println("Data sent to Supabase successfully");
    } else {
        Serial.println("Failed to send data to Supabase");
    }
}

void loop() {
    if (!voneClient.connected()) {
        voneClient.reconnect();
        voneClient.publishDeviceStatusEvent(SOIL_MOISTURE_ID, true);
        voneClient.publishDeviceStatusEvent(DHT11_ID, true);
        voneClient.publishDeviceStatusEvent(RAIN_SENSOR_ID, true);
        
        // Flash both LEDs to indicate reconnection attempt
        for(int i = 0; i < 3; i++) {
            digitalWrite(RED_LED_PIN, HIGH);
            digitalWrite(GREEN_LED_PIN, HIGH);
            delay(100);
            digitalWrite(RED_LED_PIN, LOW);
            digitalWrite(GREEN_LED_PIN, LOW);
            delay(100);
        }
    }
    
    voneClient.loop();

    unsigned long cur = millis();
    if (cur - lastMsgTime > INTERVAL) {
        lastMsgTime = cur;
        
        readAllSensors();
        printReadings();
        sendToVOne();
        sendToSupabase(); // Add Supabase integration here
    }
}