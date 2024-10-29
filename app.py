from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import webbrowser
from threading import Timer

app = Flask(__name__)

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

    # Compare each generated value to the average values for the selected age range
    warnings = []
    for col, avg in average_values_for_age.items():
        # Compare and generate warnings
        biometric_data[f'{col} (Comparison)'] = biometric_data[col].apply(
            lambda x: "Within Range" if abs(x - avg) <= (0.1 * avg) else "Out of Range"
        )
        
        # Generate warnings for out-of-range values
        for index, value in biometric_data[col].items():
            if abs(value - avg) > (0.1 * avg):
                warnings.append(f"{col} of {value} is out of range (average: {avg})")

    # Determine if the pilot is fit to fly based on the biometric data
    fit_to_fly = all(biometric_data[f'{col} (Comparison)'].iloc[0] == "Within Range" for col in average_values_for_age.keys())
    summary = "Pilot is Fit to Fly" if fit_to_fly else "Pilot is Not Fit to Fly"

    return render_template('data_table.html', 
                           data=original_data.to_dict(orient='records') if original_data is not None else None,
                           columns=original_data.columns if original_data is not None else None,
                           simulated_data=None, 
                           biometric_data=biometric_data.to_dict(orient='records'),
                           pilot_averages=average_values_for_age, 
                           warnings=warnings, 
                           summary=summary)


def open_browser():
    webbrowser.open("http://127.0.0.1:5000/")

if __name__ == "__main__":
    if not app.debug:
        Timer(1, open_browser).start()
    app.run(debug=True)  # Change to True for debugging
