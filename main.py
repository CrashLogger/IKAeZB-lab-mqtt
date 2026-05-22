from queue import Queue
import threading
from datetime import *
from model.subscriber import subscriber
from flask import *

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
    if not location_queue.empty():
        latest_data = location_queue.get()
        return jsonify(latest_data)
    return jsonify({})  # Return empty object when queue is empty

@app.route('/api/air')
def get_airquality():
    # Get the latest data from the dumbass queue
    if not airqual_queue.empty():
        latest_data = airqual_queue.get()
    return jsonify(latest_data)

@app.route('/api/radiation')
def get_radiation():
    # Get the latest data from the dumbass queue
    if not radiation_queue.empty():
        latest_data = radiation_queue.get()
    return jsonify(latest_data)
    

if __name__ == '__main__':
    locationsub = subscriber(["#"], location_queue, airqual_queue, radiation_queue)
    print("Here!");
    threading.Thread(target=locationsub.start_listening, daemon=True).start()
    app.run(debug=True, host='0.0.0.0')