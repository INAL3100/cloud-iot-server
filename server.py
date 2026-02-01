from flask import Flask, request, render_template
from datetime import datetime
import sqlite3

app = Flask(__name__)

# -----------------------------
# SENSOR → ZONE
# -----------------------------
SENSOR_ZONES = {
    "SENSOR_1": "Zone 1",
    "SENSOR_2": "Zone 2",
    "SENSOR_3": "Zone 3",
}

ZONES = ["Zone 1", "Zone 2", "Zone 3"]

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("sensors.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone TEXT,
    sensor_id TEXT,
    date TEXT,
    time TEXT,
    value REAL,
    machine_status TEXT DEFAULT 'OFF'
)
""")
conn.commit()

# -----------------------------
# RECEIVE SENSOR DATA
# -----------------------------
@app.route("/data", methods=["POST"])
def receive_data():
    sensor_id = request.form.get("sensor_id")
    value = float(request.form.get("value"))
    zone = SENSOR_ZONES.get(sensor_id)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_ = now.strftime("%H:%M:%S")

    # -----------------------------
    # MACHINE LOGIC
    # ON if last two readings <25, OFF if >40
    cursor.execute("SELECT value, machine_status FROM readings WHERE sensor_id=? ORDER BY id DESC LIMIT 1", (sensor_id,))
    last = cursor.fetchone()
    last_value, last_status = last if last else (None, "OFF")

    if value > 40:
        machine_status = "OFF"
    elif last_value is not None and last_value < 25 and value < 25:
        machine_status = "ON"
    else:
        machine_status = last_status
    # -----------------------------

    cursor.execute(
        "INSERT INTO readings (zone, sensor_id, date, time, value, machine_status) VALUES (?, ?, ?, ?, ?, ?)",
        (zone, sensor_id, date, time_, value, machine_status)
    )
    conn.commit()

    return "OK", 200

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html", zones=ZONES)

# -----------------------------
# ZONE PAGE
# -----------------------------
@app.route("/zone/<zone_name>")
def zone_page(zone_name):
    selected_date = request.args.get("date") or datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT sensor_id, date, time, value, machine_status
        FROM readings
        WHERE zone = ? AND date = ?
        ORDER BY sensor_id, time
    """, (zone_name, selected_date))

    rows = cursor.fetchall()
    data = {}
    for sensor_id, date, time_, value, status in rows:
        data.setdefault(sensor_id, []).append((date, time_, value, status))

    return render_template(
        "zone.html",
        zone=zone_name,
        data=data,
        selected_date=selected_date
    )

if __name__ == "__main__":
    app.run(debug=True)
