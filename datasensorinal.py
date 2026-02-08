import requests
import time
import random

URL = "https://cloud-iot-server.onrender.com/data"
API_KEY = "NEXA_SENS_DEVICE_KEY"

SENSORS = ["SENSOR_1", "SENSOR_2", "SENSOR_3"]

while True:
    for sensor in SENSORS:
        value = round(random.uniform(20, 50), 2)

        response = requests.post(
            URL,
            headers={"X-API-KEY": API_KEY},
            data={
                "sensor_id": sensor,
                "value": value
            }
        )

        print(sensor, value, response.status_code)

    time.sleep(10)
