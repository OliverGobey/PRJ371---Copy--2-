import pandas as pd
import numpy as np
import webbrowser
from threading import Timer
from flask import jsonify
import random
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_socketio import SocketIO
import sqlite3
from datetime import datetime, timedelta
import os


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to store min, max, and average values
min_max_values = {}
average_values = {}

# Store the original uploaded data to reuse for simulation
original_data = None
biometric_data = None  # New variable to store biometric data

# Average pilot biometric values for comparison
average_pilot_values = {
    'Heart Rate (BPM)': 75,
    'Blood Oxygen (%)': 98,
    'Blood Pressure (Systolic)': 120,
    'Blood Pressure (Diastolic)': 80,
    'Reaction Time (ms)': 250,
    'Hours Slept': 7,
    'Steps Walked Today': 5000
}

# Average biometric values for different age ranges
average_values_by_age = {
    '18-25': {
        'Heart Rate (BPM)': 70,
        'Blood Oxygen (%)': 98,
        'Blood Pressure (Systolic)': 118,
        'Blood Pressure (Diastolic)': 76,
        'Reaction Time (ms)': 240,
        'Hours Slept': 8,
        'Steps Walked Today': 6000
    },
    '26-35': {
        'Heart Rate (BPM)': 72,
        'Blood Oxygen (%)': 97,
        'Blood Pressure (Systolic)': 120,
        'Blood Pressure (Diastolic)': 78,
        'Reaction Time (ms)': 250,
        'Hours Slept': 7,
        'Steps Walked Today': 5500
    },
    '36-50': {
        'Heart Rate (BPM)': 75,
        'Blood Oxygen (%)': 96,
        'Blood Pressure (Systolic)': 125,
        'Blood Pressure (Diastolic)': 80,
        'Reaction Time (ms)': 260,
        'Hours Slept': 6,
        'Steps Walked Today': 5000
    }
}

@app.route('/')
def index():
    global biometric_data
    return render_template('index.html', biometric_data=biometric_data, pilot_averages=average_pilot_values)

@app.route('/simulate', methods=['POST'])
def simulate_data():
    global original_data
    if original_data is None:
        return render_template('data_table.html', error="No original data to simulate from.", biometric_data=None)

    simulated_data = pd.DataFrame(columns=original_data.columns)

    for col in min_max_values.keys():
        min_val, max_val = min_max_values[col]
        if original_data[col].dtype == int:
            simulated_column = np.random.randint(min_val, max_val + 1, len(original_data))
        else:
            simulated_column = np.random.uniform(min_val, max_val, len(original_data)).round(2)

        simulated_data[col] = simulated_column

    return render_template('data_table.html', data=original_data.to_dict(orient='records'), columns=original_data.columns, simulated_data=simulated_data.to_dict(orient='records'), biometric_data=None)

@app.route('/generate_biometrics', methods=['POST'])
def generate_biometrics():
    global biometric_data
    age_range = request.form['age_range']  # Get the selected age range

    # Retrieve average values based on the selected age range
    average_values_for_age = average_values_by_age.get(age_range, {})

    # Generate biometric data
    biometric_data = pd.DataFrame({
        'Heart Rate (BPM)': [np.random.randint(60, 100)],
        'Blood Oxygen (%)': [round(np.random.uniform(95, 100), 1)],
        'Blood Pressure (Systolic)': [np.random.randint(110, 130)],
        'Blood Pressure (Diastolic)': [np.random.randint(70, 85)],
        'Reaction Time (ms)': [round(np.random.uniform(200, 300), 2)],
        'Hours Slept': [np.random.randint(4, 9)],
        'Steps Walked Today': [np.random.randint(3000, 10000)]
    })

    # Set a threshold point system and initialize pilot points
    total_points = 0
    max_points_per_metric = 10  # Max points if metric is within range
    min_points_threshold = 50   # Minimum total points required to be fit to fly
    warnings = []

    # Compare each generated value to the average values for the selected age range
    for col, avg in average_values_for_age.items():
        value = biometric_data[col].iloc[0]
        
        # Calculate if the value is within a 10% range of the average
        if abs(value - avg) <= (0.1 * avg):
            total_points += max_points_per_metric  # Full points for within range
            biometric_data[f'{col} (Comparison)'] = "Within Range"
        else:
            # Half points if slightly out of range, no points if severely out
            points = max_points_per_metric - int(abs(value - avg) / (0.1 * avg) * max_points_per_metric)
            total_points += max(0, points)
            biometric_data[f'{col} (Comparison)'] = "Out of Range"
            warnings.append(f"{col} of {value} is out of range (average: {avg})")

    # Determine if the pilot is fit to fly based on total points
    fit_to_fly = total_points >= min_points_threshold
    summary = "Pilot is Fit to Fly" if fit_to_fly else "Pilot is Not Fit to Fly"

    return render_template('data_table.html', 
                           data=original_data.to_dict(orient='records') if original_data is not None else None,
                           columns=original_data.columns if original_data is not None else None,
                           simulated_data=None, 
                           biometric_data=biometric_data.to_dict(orient='records'),
                           pilot_averages=average_values_for_age, 
                           warnings=warnings, 
                           summary=summary,
                           total_points=total_points,
                           min_points_threshold=min_points_threshold)


@app.route('/real_time_biometrics')
def real_time_biometrics():
    # Initialize biometric data with typical starting values
    biometric_data = {
        'Heart Rate (BPM)': np.random.randint(60, 75),  # Resting heart rate range
        'Blood Oxygen (%)': 98.0,  # Stable, typical baseline for a healthy individual
        'Blood Pressure (Systolic)': np.random.randint(110, 120),
        'Blood Pressure (Diastolic)': np.random.randint(70, 80),
        'Reaction Time (ms)': round(np.random.uniform(250, 300), 2),
        'Hours Slept': 8,  # Fixed for the day
        'Steps Walked Today': np.random.randint(0, 500)  # Start low, to increase over time
    }

    # Heart Rate - small gradual change, only +/- 1 or 2
    heart_rate_change = random.choice([-2, -1, 1, 2])
    biometric_data['Heart Rate (BPM)'] += heart_rate_change
    biometric_data['Heart Rate (BPM)'] = max(60, min(100, biometric_data['Heart Rate (BPM)']))

    # Blood Oxygen - very stable, occasional minor fluctuation
    if random.random() < 0.05:  # Small chance of a minor change
        biometric_data['Blood Oxygen (%)'] += random.choice([-0.1, 0.1])
    biometric_data['Blood Oxygen (%)'] = round(max(95.0, min(100.0, biometric_data['Blood Oxygen (%)'])), 1)

    # Blood Pressure - small fluctuations
    biometric_data['Blood Pressure (Systolic)'] += random.choice([-1, 0, 1])
    biometric_data['Blood Pressure (Diastolic)'] += random.choice([-1, 0, 1])
    biometric_data['Blood Pressure (Systolic)'] = max(110, min(130, biometric_data['Blood Pressure (Systolic)']))
    biometric_data['Blood Pressure (Diastolic)'] = max(70, min(85, biometric_data['Blood Pressure (Diastolic)']))

    # Reaction Time - minor fluctuations
    reaction_time_change = round(random.uniform(-0.5, 0.5), 2)  # Small fluctuation
    biometric_data['Reaction Time (ms)'] += reaction_time_change
    biometric_data['Reaction Time (ms)'] = round(max(200, min(300, biometric_data['Reaction Time (ms)'])), 2)

    # Hours Slept - fixed, no change during the day
    biometric_data['Hours Slept'] = 8

    # Steps Walked Today - only increases throughout the day
    steps_increase = random.randint(0, 50)  # Add a realistic step count increment
    biometric_data['Steps Walked Today'] += steps_increase
    biometric_data['Steps Walked Today'] = min(10000, biometric_data['Steps Walked Today'])  # Cap at 10,000 steps

    return jsonify(biometric_data)


@app.route('/fatigue')
def fatigue():
    return render_template('fatigue.html')

@app.route('/data_table')
def data_table():
    return render_template('data_table.html', biometric_data=biometric_data)

@app.route('/summary')
def summary():
    return render_template('summary.html')    

@app.route("/add-sample-data", methods=["POST"])
def add_sample_data():
    insert_sample_data()  # Function to insert sample data into the database



socketio = SocketIO(app, cors_allowed_origins="*")

import sqlite3

def init_db():
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            heart_rate INTEGER,
            blood_oxygen INTEGER,
            temperature REAL,
            alert TEXT,
            blood_pressure_systolic INTEGER,
            blood_pressure_diastolic INTEGER,
            reaction_time REAL,
            hours_slept INTEGER,
            steps_walked INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def insert_sample_data():
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    
    # Generate sample data
    sample_data = [
        (
            datetime.now() - timedelta(minutes=i * 5),
            random.randint(60, 100),  # Heart rate
            98,  # Stable blood oxygen
            round(random.uniform(36.5, 38.5), 1),  # Temperature
            "High Heart Rate" if random.randint(60, 100) > 95 else
            "Low Blood Oxygen" if 98 < 90 else
            "High Temperature" if round(random.uniform(36.5, 38.5), 1) > 37.5 else None,
            random.randint(110, 120),  # Blood Pressure (Systolic)
            random.randint(70, 80),    # Blood Pressure (Diastolic)
            round(random.uniform(250, 300), 2),  # Reaction Time (ms)
            8,  # Fixed Hours Slept
            random.randint(0, 500)  # Steps Walked Today
        )
        for i in range(30)  # Generate 30 records
    ]
    
    # Insert the sample data into the database
    cursor.executemany('''
        INSERT INTO health_metrics (
            timestamp, 
            heart_rate, 
            blood_oxygen, 
            temperature, 
            alert, 
            blood_pressure_systolic, 
            blood_pressure_diastolic, 
            reaction_time, 
            hours_slept, 
            steps_walked
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    conn.close()
    print("Sample data inserted successfully.")



def get_metrics():
    conn = sqlite3.connect('health_data.db')
    cursor = conn.cursor()
    
    # Fetch all the metrics, including the new fields
    cursor.execute('''
        SELECT 
            timestamp, 
            heart_rate, 
            blood_oxygen, 
            temperature, 
            alert, 
            blood_pressure_systolic, 
            blood_pressure_diastolic, 
            reaction_time, 
            hours_slept, 
            steps_walked 
        FROM health_metrics
    ''')
    
    metrics = cursor.fetchall()
    conn.close()
    return metrics 

@app.route('/metrics', methods=['GET', 'POST'])
def metrics():
    if request.method == 'POST':
        insert_sample_data()
        # After inserting the data, reload the page with updated metrics
        return redirect(url_for('metrics'))

    # Get metrics to display on the page
    metrics_data = get_metrics()
    return render_template('metrics.html', metrics=metrics_data)


@socketio.on("connect")
def handle_connect():
    print("Client connected")


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    init_db()
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
