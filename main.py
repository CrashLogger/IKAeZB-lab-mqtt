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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/position')
def get_position():
    return apiDb.get_latest_location()

@app.route('/api/air')
def get_airquality():
    return apiDb.get_latest_airquality()

@app.route('/api/radiation')
def get_radiation():
    return apiDb.get_latest_radiation()

if __name__ == '__main__':
    locationsub = subscriber(["#"], location_queue, airqual_queue, radiation_queue)
    print("Here!");
    threading.Thread(target=locationsub.start_listening, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port='5001')