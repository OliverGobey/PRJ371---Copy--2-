import * as messaging from "messaging";

// Listener for messages from the device app
messaging.peerSocket.onmessage = async (evt) => {
  const sensorData = evt.data;

  try {
    const response = await fetch("http://localhost:3000", { // Update this to your server URL
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(sensorData),
    });

    if (!response.ok) {
      console.error("Failed to send data:", response.statusText);
    }
  } catch (error) {
    console.error("Error sending data:", error);
  }
};
