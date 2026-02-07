import requests
import random
import time

URL = "http://127.0.0.1:5000/data"
HEADERS = {"X-API-KEY": "NEXA_SENS_DEVICE_KEY"}

SENSORS = ["SENSOR_1", "SENSOR_2", "SENSOR_3"]

while True:
    for s in SENSORS:
        value = round(random.uniform(20, 45), 1)
        requests.post(
            URL,
            data={"sensor_id": s, "value": value},
            headers=HEADERS
        )
        print(s, value)
    time.sleep(30)
