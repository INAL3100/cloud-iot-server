import requests
import random
import time

URL = "https://cloud-iot-server.onrender.com/data"

sensors = ["SENSOR_1", "SENSOR_2", "SENSOR_3"]

while True:
    for sensor in sensors:
        value = round(random.uniform(20, 35), 1)

        response = requests.post(URL, data={
            "sensor_id": sensor,
            "value": value
        })

        print(sensor, "sent:", value)

    # 30 minutes (use 10 seconds for testing)
    time.sleep(60)
