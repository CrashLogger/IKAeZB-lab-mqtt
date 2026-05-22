CREATE TABLE location_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    lat REAL,
    lon REAL,
    altitude REAL,
    roll REAL,
    pitch REAL
);

CREATE TABLE radiation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    rad REAL,
    cps REAL
);

CREATE TABLE meteo_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temp REAL,
    pres REAL,
    humid REAL
);