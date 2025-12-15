from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# Key = (sensor_id, date)
# Value = list of (time, value)
data_store = {}

@app.route("/data", methods=["POST"])
def receive_data():
    sensor_id = request.form.get("sensor_id")
    value = float(request.form.get("value"))

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")

    key = (sensor_id, date)

    if key not in data_store:
        data_store[key] = []

    data_store[key].append((time, value))

    return "OK", 200

@app.route("/")
def homepage():
    page = """
    <html>
    <head>
        <meta http-equiv="refresh" content="300"> <!-- auto-refresh every 300 seconds -->
        <style>
            table {
                border-collapse: collapse;
                margin: auto;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
        <title>Sensors Dashboard</title>
    </head>
    <body>
    <h1 style="text-align:center;">Sensors Data (Live Dashboard)</h1>
    <table>
        <tr>
            <th>Sensor</th>
            <th>Date</th>
            <th>Time</th>
            <th>Reading</th>
            <th>Average</th>
        </tr>
    """

    for (sensor, date), readings in data_store.items():
        avg = str(round(sum(v for _, v in readings) / len(readings), 2))
        rows = len(readings)

        # FIRST ROW: Sensor, Date, first time/value, Average
        first_time, first_value = readings[0]
        page += f"""
        <tr>
            <td rowspan="{rows}">{sensor}</td>
            <td rowspan="{rows}">{date}</td>
            <td>{first_time}</td>
            <td>{first_value}</td>
            <td rowspan="{rows}">{avg}</td>
        </tr>
        """

        # Remaining rows: only time/value
        for time_, value in readings[1:]:
            page += f"""
            <tr>
                <td>{time_}</td>
                <td>{value}</td>
            </tr>
            """

    page += """
    </table>
    </body>
    </html>
    """

    return page

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
