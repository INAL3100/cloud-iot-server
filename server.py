from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# Store all readings in memory
data_list = []

@app.route("/data", methods=["POST"])
def receive_data():
    sensor_id = request.form.get("sensor_id")
    value = request.form.get("value")

    now = datetime.now()

    data_list.append({
        "sensor": sensor_id,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "value": float(value)
    })

    return "OK", 200


@app.route("/")
def homepage():
    page = "<h1>Sensor Data (IT View)</h1>"

    # Table
    page += "<table border='1' cellpadding='5'>"
    page += "<tr><th>Sensor</th><th>Date</th><th>Time</th><th>Value</th></tr>"

    sums = {}
    counts = {}

    for d in data_list:
        page += f"<tr><td>{d['sensor']}</td><td>{d['date']}</td><td>{d['time']}</td><td>{d['value']}</td></tr>"

        sensor = d["sensor"]
        sums[sensor] = sums.get(sensor, 0) + d["value"]
        counts[sensor] = counts.get(sensor, 0) + 1

    page += "</table>"

    # Averages
    page += "<h2>Average per Sensor</h2><table border='1' cellpadding='5'>"
    page += "<tr><th>Sensor</th><th>Average</th></tr>"

    for sensor in sums:
        avg = round(sums[sensor] / counts[sensor], 2)
        page += f"<tr><td>{sensor}</td><td>{avg}</td></tr>"

    page += "</table>"

    return page


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
