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
        <style>
            table {
                border-collapse: collapse;
                margin-left: auto;
                margin-right: auto;
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
    </head>
    <body>
    <h1 style="text-align:center;">Sensors Data (IT View)</h1>
    <table>
        <tr>
            <th>Sensor</th>
            <th>Date</th>
            <th>Time</th>
            <th>Reading</th>
            <th>Average</th>
        </tr>
    """

    # Iterate over each sensor's data
    for (sensor, date), readings in data_store.items():
        # Values for this sensor
        times = [t for t, _ in readings]
        values = [v for _, v in readings]
        avg = round(sum(values) / len(values), 2)

        # Add rows for each time-value pair
        for i in range(len(times)):
            # For the first row of each sensor, show sensor and date
            if i == 0:
                page += f"""
                <tr>
                    <td rowspan="{len(times)}">{sensor}</td>
                    <td rowspan="{len(times)}">{date}</td>
                    <td>{times[i]}</td>
                    <td>{values[i]}</td>
                    {"<td rowspan='%d'>%s</td>" % (len(times), avg) if i == len(times) - 1 else ""}
                </tr>
                """
            else:
                # For subsequent rows, show only time and reading
                page += f"""
                <tr>
                    <td>{times[i]}</td>
                    <td>{values[i]}</td>
                    {"<td></td>" if i != len(times) - 1 else ""}
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
