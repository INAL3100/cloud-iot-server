import requests
import time
import random

# Your Flask server URL
URL = "http://127.0.0.1:5000/data"
API_KEY = "NEXA_SENS_DEVICE_KEY"

# Sensors and their zones
SENSORS = ["SENSOR_1", "SENSOR_2", "SENSOR_3"]

def send_sensor_data(sensor_id, value):
    data = {
        "sensor_id": sensor_id,
        "value": value
    }
    headers = {
        "X-API-KEY": API_KEY
    }
    response = requests.post(URL, data=data, headers=headers)
    if response.status_code == 200:
        print(f"Sent {value} to {sensor_id} ✅")
    else:
        print(f"Failed to send {sensor_id} ❌ Status: {response.status_code}")

if __name__ == "__main__":
    print("Starting sensor simulation...")
    try:
        while True:
            for sensor in SENSORS:
                # Random value between 20 and 50 to test ON/OFF logic
                value = random.uniform(20, 50)
                send_sensor_data(sensor, value)
            time.sleep(5)  # wait 5 seconds before next batch
    except KeyboardInterrupt:
        print("Simulation stopped.")
