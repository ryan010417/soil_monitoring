function main(parameter) {
  output = [];

  /* Start your code here */
  // Get data from each sensor
  const dht11_obj = parameter[1]["data"];
  const soil_obj = parameter[2]["data"];
  const rain_obj = parameter[3]["data"];

  // Get the latest readings
  const dht11_idx = parameter[1]["count"]["total"] - 1;
  const soil_idx = parameter[2]["count"]["total"] - 1;
  const rain_idx = parameter[3]["count"]["total"] - 1;

  // Extract sensor values
  const temperature = dht11_obj[dht11_idx]["Temperature"];
  const humidity = dht11_obj[dht11_idx]["Humidity"];
  const moisture = soil_obj[soil_idx]["Soil moisture"];
  const is_raining = rain_obj[rain_idx]["Raining"];

  // Define thresholds
  const moisture_threshold = 30;
  const temp_threshold = 30;
  const humidity_threshold = 85;

  // Check conditions
  const alerts = [];
  if (parseInt(moisture) < moisture_threshold) {
    alerts.push(`Soil Moisture: ${moisture}% (Below ${moisture_threshold}%)`);
  }
  if (parseFloat(temperature) > temp_threshold) {
    alerts.push(`Temperature: ${temperature}°C (Above ${temp_threshold}°C)`);
  }
  if (parseFloat(humidity) > humidity_threshold) {
    alerts.push(`Humidity: ${humidity}% (Above ${humidity_threshold}%)`);
  }
  if (parseInt(is_raining) === 1) {
    alerts.push("Rain Detected");
  }

  if (alerts.length > 0) {
    // Create alert message
    const msgbody = `
        <p><strong>ALERT: Plant Conditions Need Attention!</strong></p>
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
            <li>Rain Status: ${parseInt(is_raining) === 1 ? "Yes" : "No"}</li>
        </ul>
        <br>
        <p>Action Required: Please check your plant conditions.</p>
        <p>This is an automated alert from your Plant Monitoring System.</p>
        `;
    output[1] = "🚨 ALERT: Plant Conditions Need Attention"; // Email subject
    output[2] = msgbody; // Email body
    output[3] = 2; // Priority level
  } else {
    // Create normal status message
    const msgbody = `
        <p><strong>Plant Status Update</strong></p>
        <p>All conditions are normal.</p>
        <br>
        <p><strong>Current Readings:</strong></p>
        <ul>
            <li>Soil Moisture: ${moisture}%</li>
            <li>Temperature: ${temperature}°C</li>
            <li>Humidity: ${humidity}%</li>
            <li>Rain Status: ${parseInt(is_raining) === 1 ? "Yes" : "No"}</li>
        </ul>
        <br>
        <p>This is an automated update from your Plant Monitoring System.</p>
        `;
    output[1] = "✅ Plant Status: All Normal"; // Email subject
    output[2] = msgbody; // Email body
    output[3] = 1; // Normal priority
  }
  /* End your code here */

  return output;
}
