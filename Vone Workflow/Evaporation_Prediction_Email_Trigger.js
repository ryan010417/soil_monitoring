function main(parameter) {
  output = [];

  /* Start your code here */
  // Get the latest data from the `raw_sensors_data` query
  const sensors_data = parameter[1]["data"];
  const idx = parameter[1]["count"]["total"] - 1;

  // Extract sensor values from the latest reading
  const latest_reading = sensors_data[idx];
  const temperature = parseFloat(latest_reading["temperature"]);
  const humidity = parseFloat(latest_reading["humidity"]);
  const moisture = parseInt(latest_reading["soil_moisture"]);
  const is_raining = latest_reading["is_raining"];
  const prediction = parseFloat(latest_reading["prediction"]);

  // Define thresholds
  const moisture_threshold = 30;
  const temp_threshold = 30;
  const humidity_threshold = 85;
  const prediction_threshold = 0.5;

  // Check conditions
  const alerts = [];
  if (moisture < moisture_threshold) {
    alerts.push(`Soil Moisture: ${moisture}% (Below ${moisture_threshold}%)`);
  }
  if (temperature > temp_threshold) {
    alerts.push(`Temperature: ${temperature}°C (Above ${temp_threshold}°C)`);
  }
  if (humidity > humidity_threshold) {
    alerts.push(`Humidity: ${humidity}% (Above ${humidity_threshold}%)`);
  }
  if (is_raining) {
    alerts.push("Rain Detected");
  }
  if (prediction >= 0 && prediction < prediction_threshold) {
    alerts.push(
      `Prediction Value: ${prediction.toFixed(
        2
      )} (Below ${prediction_threshold})`
    );
  }

  if (alerts.length > 0) {
    // Create alert message
    const msgbody = `
        <p><strong>🚨 ALERT: Plant Conditions Need Attention!</strong></p>
        <p>Issues Detected:</p>
        <ul>
            ${alerts.map((alert) => `<li>${alert}</li>`).join("")}
        </ul>
        <br>
        <p><strong>Current Readings:</strong></p>
        <ul>
            <li>Soil Moisture: ${moisture}%</li>
            <li>Temperature: ${temperature}°C</li>
            <li>Humidity: ${humidity}%</li>
            <li>Rain Status: ${is_raining ? "Yes" : "No"}</li>
            <li>Prediction: ${prediction.toFixed(2)}</li>
        </ul>
        <br>
        <p>Action Required: Please check your plant conditions immediately.</p>
        <p>This is an automated alert from your Smart Irrigation System.</p>
        `;
    output[1] = "🚨 ALERT: Plant Conditions Need Attention"; // Email subject
    output[2] = msgbody; // Email body
    output[3] = 2; // Priority level
  } else {
    // Create normal status message
    const msgbody = `
        <p><strong>✅ Plant Status: All Normal</strong></p>
        <p>No issues detected. Your plant conditions are optimal.</p>
        <br>
        <p><strong>Current Readings:</strong></p>
        <ul>
            <li>Soil Moisture: ${moisture}%</li>
            <li>Temperature: ${temperature}°C</li>
            <li>Humidity: ${humidity}%</li>
            <li>Rain Status: ${is_raining ? "Yes" : "No"}</li>
            <li>Prediction: ${prediction.toFixed(2)}</li>
        </ul>
        <br>
        <p>This is an automated update from your Smart Irrigation System.</p>
        `;
    output[1] = "✅ Plant Status: All Normal"; // Email subject
    output[2] = msgbody; // Email body
    output[3] = 1; // Normal priority
  }
  /* End your code here */

  return output;
}
