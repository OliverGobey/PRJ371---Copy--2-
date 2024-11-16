import { HeartRateSensor } from "heart-rate";
import { BodyPresenceSensor } from "body-presence";
import { EDA } from "eda";
import * as messaging from "messaging";
import document from "document";

// Check if the sensors are available on the device
let hrm = new HeartRateSensor();
let eda = new EDA();
let bodyPresence = new BodyPresenceSensor();

// Check if sensors are supported
if (HeartRateSensor) {
  hrm = new HeartRateSensor();
  hrm.start();
}
if (BodyPresenceSensor) {
  bodyPresence = new BodyPresenceSensor();
  bodyPresence.start();
}
if (EDA) {
  eda = new EDA();
  eda.start();
}

// Function to send sensor data to the companion
function sendSensorData() {
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN) {
    const data = {
      heartRate: hrm.heartRate || "Unavailable",
      bodyPresence: bodyPresence.present ? "Worn" : "Not Worn",
      stressLevel: eda.reading || "Unavailable",
      timestamp: new Date().toISOString()
    };
    console.log("Sending sensor data:", data); //debug log
    messaging.peerSocket.send(data);
  }
}

// Update and send data periodically
setInterval(sendSensorData, 5000); // Adjust interval as needed

// Event listener for changes in heart rate
hrm.onreading = () => {
  document.getElementById("heart-rate").text = `Heart Rate: ${hrm.heartRate}`;
};

// Event listener for changes in stress level (EDA)
eda.onreading = () => {
  document.getElementById("stress-level").text = `Stress Level: ${eda.reading}`;
};
