import requests
import random
import time

URL = "http://127.0.0.1:5000/data"  # change to your Render URL later
sensors = ["SENSOR_1", "SENSOR_2", "SENSOR_3"]

last_value = {s: None for s in sensors}
last_status = {s: "OFF" for s in sensors}

while True:
    for sensor in sensors:
        value = round(random.uniform(20, 45), 1)

        # Local machine logic simulation
        if value > 40:
            status = "OFF"
        elif last_value[sensor] is not None and last_value[sensor] < 25 and value < 25:
            status = "ON"
        else:
            status = last_status[sensor]

        last_value[sensor] = value
        last_status[sensor] = status

        requests.post(URL, data={"sensor_id": sensor, "value": value})
        print(sensor, value, status)

    time.sleep(30)
