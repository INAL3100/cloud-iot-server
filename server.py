from flask import Flask, request, render_template, redirect, session
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "nexa_sens_secret"

API_KEY = "NEXA_SENS_DEVICE_KEY"

# -----------------------------
# ZONES & SENSOR MAPPING
# -----------------------------
ZONES = ["Zone 1", "Zone 2", "Zone 3"]

SENSOR_ZONES = {
    "SENSOR_1": "Zone 1",
    "SENSOR_2": "Zone 2",
    "SENSOR_3": "Zone 3",
}

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
    machine_status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_zones (
    user_id INTEGER,
    zone TEXT
)
""")

conn.commit()

# -----------------------------
# DEMO USERS (run once)
# -----------------------------
def create_demo_users():
    users = [
        ("manager", "1234", "manager"),
        ("eng1", "1234", "engineer"),
        ("eng2", "1234", "engineer"),
        ("eng3", "1234", "engineer"),
    ]

    for u, p, r in users:
        cursor.execute(
            "INSERT OR IGNORE INTO users VALUES (NULL, ?, ?, ?)",
            (u, generate_password_hash(p), r)
        )

    conn.commit()

    cursor.execute("SELECT id, username FROM users")
    for uid, uname in cursor.fetchall():
        if uname == "eng1":
            cursor.execute("INSERT OR IGNORE INTO user_zones VALUES (?, ?)", (uid, "Zone 1"))
        if uname == "eng2":
            cursor.execute("INSERT OR IGNORE INTO user_zones VALUES (?, ?)", (uid, "Zone 2"))
        if uname == "eng3":
            cursor.execute("INSERT OR IGNORE INTO user_zones VALUES (?, ?)", (uid, "Zone 3"))

    conn.commit()

create_demo_users()

# -----------------------------
# HELPERS
# -----------------------------
def get_user_zones(user_id):
    cursor.execute(
        "SELECT DISTINCT zone FROM user_zones WHERE user_id=?",
        (user_id,)
    )
    return [z[0] for z in cursor.fetchall()]

# -----------------------------
# LOGIN / LOGOUT
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT id, password, role FROM users WHERE username=?",
            (username,)
        )
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            session["role"] = user[2]
            return redirect("/")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -----------------------------
# SETTINGS
# -----------------------------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        new_username = request.form["username"]
        new_password = generate_password_hash(request.form["password"])

        cursor.execute(
            "UPDATE users SET username=?, password=? WHERE id=?",
            (new_username, new_password, session["user_id"])
        )
        conn.commit()

        session["username"] = new_username
        return redirect("/")

    return render_template("settings.html")

# -----------------------------
# RECEIVE SENSOR DATA
# -----------------------------
@app.route("/data", methods=["POST"])
def receive_data():
    if request.headers.get("X-API-KEY") != API_KEY:
        return "Unauthorized", 401

    sensor_id = request.form["sensor_id"]
    value = float(request.form["value"])
    zone = SENSOR_ZONES.get(sensor_id)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_ = now.strftime("%H:%M:%S")

    cursor.execute("""
        SELECT value, machine_status
        FROM readings
        WHERE sensor_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (sensor_id,))
    last = cursor.fetchone()

    last_value, last_status = last if last else (None, "OFF")

    if value > 40:
        status = "OFF"
    elif last_value and last_value < 25 and value < 25:
        status = "ON"
    else:
        status = last_status

    cursor.execute("""
        INSERT INTO readings
        VALUES (NULL, ?, ?, ?, ?, ?, ?)
    """, (zone, sensor_id, date, time_, value, status))

    conn.commit()
    return "OK", 200

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] == "manager":
        zones = ZONES
    else:
        zones = get_user_zones(session["user_id"])

    return render_template("index.html", zones=zones)

@app.route("/zone/<zone_name>")
def zone_page(zone_name):
    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "manager":
        if zone_name not in get_user_zones(session["user_id"]):
            return "Access denied", 403

    selected_date = request.args.get("date") or datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT sensor_id, time, value, machine_status
        FROM readings
        WHERE zone=? AND date=?
        ORDER BY time
    """, (zone_name, selected_date))

    rows = cursor.fetchall()
    data = {}

    for sensor, time_, value, status in rows:
        data.setdefault(sensor, []).append((time_, value, status))

    return render_template(
        "zone.html",
        zone=zone_name,
        data=data,
        selected_date=selected_date
    )

if __name__ == "__main__":
    app.run(debug=True)
