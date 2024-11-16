const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(bodyParser.json());

// Endpoint to receive heart rate data
app.post('/api/heart-rate', (req, res) => {
    const heartRateData = req.body;
    console.log('Received heart rate data:', heartRateData);
    // Process and store heart rate data as needed
    res.status(201).send('Heart rate data received');
});

// Endpoint to receive stress data
app.post('/api/stress', (req, res) => {
    const stressData = req.body;
    console.log('Received stress data:', stressData);
    // Process and store stress data as needed
    res.status(201).send('Stress data received');
});

// Endpoint to receive SpO2 data
app.post('/api/spo2', (req, res) => {
    const spo2Data = req.body;
    console.log('Received SpO2 data:', spo2Data);
    // Process and store SpO2 data as needed
    res.status(201).send('SpO2 data received');
});

// Endpoint to receive sleep data
app.post('/api/sleep', (req, res) => {
    const sleepData = req.body;
    console.log('Received sleep data:', sleepData);
    // Process and store sleep data as needed
    res.status(201).send('Sleep data received');
});

// Optional: Adding a root route
app.get('/', (req, res) => {
    res.send('Welcome to the Aviation Safety API!');
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on https://localhost:${PORT}`);
});
