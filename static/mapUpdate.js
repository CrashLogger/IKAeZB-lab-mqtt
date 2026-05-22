// Initialize the map and marker
const map = L.map('map').setView([40.416775, -3.703790], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Add a marker for the Galerna
const GalernaMarker = L.marker([43.43, -3.7]).addTo(map);

// Array to store the Galerna's path
let GalernaPath = [];
// Polyline to draw the path
let pathLine = L.polyline([], {color: 'yellow'}).addTo(map);

// Function to update the Galerna's position
function updatePosition(data) {
    if (!data) {
        console.error("Invalid data:", data);
        return;
    }
    
    if(data.lat && data.lon && !isNaN(data.lat) && !isNaN(data.lon)){
        GalernaMarker.setLatLng([data.lat, data.lon]);

        // Add the new position to the path
        GalernaPath.push([data.lat, data.lon]);
        // Update the polyline with the new path
        pathLine.setLatLngs(GalernaPath);
    }

    document.getElementById('lat').textContent = data.lat.toFixed(7);
    document.getElementById('lon').textContent = data.lon.toFixed(7);
    document.getElementById('altitude').textContent = data.altitude.toFixed(4);
    document.getElementById('roll').textContent = data.roll.toFixed(4);
    document.getElementById('pitch').textContent = data.pitch.toFixed(4);
}

function updateAir(data) {
    if (!data) {
        console.error("Invalid data:", data);
        return;
    }

    document.getElementById('temp').textContent = data.temp.toFixed(2);
    document.getElementById('humid').textContent = data.humid.toFixed(2);
    document.getElementById('pres').textContent = data.pres.toFixed(2);
}

function updateRadiation(data) {
    if (!data) {
        console.error("Invalid data:", data);
        return;
    }

    document.getElementById('cps').textContent = data.rad.toFixed(2);
    document.getElementById('rad').textContent = data.cps.toFixed(2);
}


// Request new data periodically
setInterval(() => {
    fetch('/api/position')
    .then(response => response.json())
    .then(data => {
        if(data.lat && data.lon) {
            updatePosition(data);
            map.setView([data.lat, data.lon]);
        }
    })
    .catch(console.error);

// Air and radiation should NOT try to set map view
fetch('/api/air')
    .then(response => response.json())
    .then(data => updateAir(data))
    .catch(console.error);

fetch('/api/radiation')
    .then(response => response.json())
    .then(data => updateRadiation(data))
    .catch(console.error);
}, 1000);
