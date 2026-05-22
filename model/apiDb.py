import sqlite3
from flask import jsonify

def get_latest_location():
    conn = sqlite3.connect('data/iot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM location_log ORDER BY timestamp DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            "lat": row[2], "lon": row[3], "altitude": row[4],
            "roll": row[5], "pitch": row[6]
        })
    return jsonify({})