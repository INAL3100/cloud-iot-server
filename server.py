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
        </style>
    </head>
    <body>
    <h1 style="text-align:center;">Sensor Data (IT View)</h1>
    <table>
        <tr>
            <th>Sensor</th>
            <th>Date</th>
            <th>Readings (Time → Value)</th>
            <th>Average</th>
        </tr>
    """

    for (sensor, date), readings in data_store.items():
        values = [v for _, v in readings]
        avg = round(sum(values) / len(values), 2)

        readings_text = "<br>".join(
            [f"{t} → {v}" for t, v in readings]
        )

        page += f"""
        <tr>
            <td>{sensor}</td>
            <td>{date}</td>
            <td>{readings_text}</td>
            <td>{avg}</td>
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
