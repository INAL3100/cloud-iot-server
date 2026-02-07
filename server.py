from flask import Flask, request, render_template, redirect, session
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "nexa_sens_secret"

API_KEY = "NEXA_SENS_DEVICE_KEY"

# -----------------------------
# ZONES & SENSORS
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

# Readings table
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

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# User-zone mapping
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_zones (
    user_id INTEGER,
    zone TEXT
)
""")
conn.commit()

# -----------------------------
# CREATE DEMO USERS (RUN ONCE)
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
        elif uname == "eng2":
            cursor.execute("INSERT OR IGNORE INTO user_zones VALUES (?, ?)", (uid, "Zone 2"))
        elif uname == "eng3":
            cursor.execute("INSERT OR IGNORE INTO user_zones VALUES (?, ?)", (uid, "Zone 3"))
    conn.commit()

create_demo_users()  # ← run once, then comment out if needed

# -----------------------------
# HELPERS
# -----------------------------
def get_user_zones(user_id):
    cursor.execute("SELECT zone FROM user_zones WHERE user_id=?", (user_id,))
    return [z[0] for z in cursor.fetchall()]

# -----------------------------
# LOGIN / LOGOUT
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT id, password, role FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["role"] = user[2]
            return redirect("/")
        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -----------------------------
# RECEIVE SENSOR DATA
# -----------------------------
@app.route("/data", methods=["POST"])
def receive_data():
    if request.headers.get("X-API-KEY") != API_KEY:
        return "Unauthorized", 401

    sensor_id = request.form.get("sensor_id")
    value = float(request.form.get("value"))
    zone = SENSOR_ZONES.get(sensor_id)

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_ = now.strftime("%H:%M:%S")

    cursor.execute(
        "SELECT value, machine_status FROM readings WHERE sensor_id=? ORDER BY id DESC LIMIT 1",
        (sensor_id,)
    )
    last = cursor.fetchone()
    last_value, last_status = last if last else (None, "OFF")

    if value > 40:
        status = "OFF"
    elif last_value and last_value < 25 and value < 25:
        status = "ON"
    else:
        status = last_status

    cursor.execute(
        "INSERT INTO readings VALUES (NULL, ?, ?, ?, ?, ?, ?)",
        (zone, sensor_id, date, time_, value, status)
    )
