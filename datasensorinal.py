import requests
import time
import random

# -----------------------------
# CHANGE THIS TO YOUR RENDER URL
# -----------------------------
URL = "https://cloud-iot-server.onrender.com/data"
API_KEY = "NEXA_SENS_DEVICE_KEY"  # must match server.py

SENSORS = ["SENSOR_1", "SENSOR_2", "SENSOR_3"]

while True:
    for sensor in SENSORS:
        # Random sensor value between 20 and 50
        value = round(random.uniform(20, 50), 2)

        try:
            response = requests.post(
                URL,
                headers={"X-API-KEY": API_KEY},
                data={
                    "sensor_id": sensor,
                    "value": value
                },
                timeout=5
            )

            if response.status_code == 200:
                print(f"[OK] {sensor} → {value}")
            else:
                print(f"[ERROR] {sensor} → {value} | Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[EXCEPTION] {sensor} → {value} | {e}")

    time.sleep(30)  # send data every 10 seconds
