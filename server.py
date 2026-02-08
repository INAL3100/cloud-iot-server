from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import paho.mqtt.client as mqtt
import threading, time

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB = "database.db"

# ---------- DB ----------
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- AUTH ----------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrap

# ---------- ROUTES ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=?",
            (u,)
        ).fetchone()

        if user and check_password_hash(user["password"], p):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/index")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/index")
@login_required
def index():
    db = get_db()
    zones = db.execute("SELECT * FROM zones").fetchall()
    return render_template("index.html", zones=zones)

@app.route("/zone/<int:zone_id>")
@login_required
def zone(zone_id):
    db = get_db()
    zone = db.execute("SELECT * FROM zones WHERE id=?", (zone_id,)).fetchone()
    return render_template("zone.html", zone=zone)

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        new_pw = generate_password_hash(request.form["password"])
        db = get_db()
        db.execute(
            "UPDATE users SET password=? WHERE id=?",
            (new_pw, session["user_id"])
        )
        db.commit()
        return redirect("/index")

    return render_template("settings.html")

# ---------- LIVE DATA ----------
latest_data = {}

@app.route("/api/readings")
@login_required
def api_readings():
    return jsonify(latest_data)

# ---------- MQTT ----------
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    sensor, value = payload.split(",")

    latest_data[sensor] = {
        "value": value,
        "time": time.strftime("%H:%M:%S"),
        "status": "ON"
    }

def mqtt_loop():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe("nexa/sensors/#")
    client.loop_forever()

threading.Thread(target=mqtt_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
