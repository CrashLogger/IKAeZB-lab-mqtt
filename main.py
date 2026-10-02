from queue import Queue
import threading
from datetime import *
from model.subscriber import subscriber
from flask import *
import sqlite3
from model import apiDb

# env.py fitxategia EZ DA GITHUBERA IGOKO.
# .gitignore fitxategi baten bera ekidituko dugu!

# Initialize a queue for thread-safe data passing because mutexes didn't feel like working.
location_queue = Queue()
radiation_queue = Queue()
airqual_queue = Queue()

location_data = {}
radiation_data = {}
airqual_data = {}

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/ikaebz'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tapBridge/api/position')
def get_position():
    return apiDb.get_latest_location()

@app.route('/tapBridge/api/air')
def get_airquality():
    return apiDb.get_latest_airquality()

@app.route('/tapBridge/api/radiation')
def get_radiation():
    return apiDb.get_latest_radiation()

@app.route("/tapBridge/api/telemetry")
def telemetry():

    conn = sqlite3.connect("data/iot.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, value
        FROM telemetry
    """)

    rows = cursor.fetchall()

    ret = {}

    for topic, value in rows:

        key = topic.split("/")[-1]

        ret[key] = value

    return jsonify(ret)

if __name__ == '__main__':
    locationsub = subscriber()
    print("Here!")
    threading.Thread(target=locationsub.start_listening, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port='5001')
