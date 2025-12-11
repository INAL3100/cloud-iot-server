from flask import Flask, request

app = Flask(__name__)

latest_value = "No data yet"

@app.route("/data", methods=["POST"])
def receive_data():
    global latest_value
    latest_value = request.data.decode()
    return "OK", 200

@app.route("/")
def homepage():
    return f"""
    <h1>Latest Sensor Value:</h1>
    <h2>{latest_value}</h2>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
