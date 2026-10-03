// Leaflet setup
const map = L.map('map').setView([43.32, -3.020], 12);

L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        attribution: '&copy; OpenStreetMap contributors'
    }
).addTo(map);

// Vehicle marker
const vehicleMarker = L.marker([43.32, -3.020]).addTo(map);

// Vehicle path
let vehiclePath = [];

const pathLine = L.polyline(
    [],
    {
        color: 'yellow'
    }
).addTo(map);

// Helper
function setField(id, value)
{
    const element = document.getElementById(id);

    if (element)
    {
        element.textContent = value;
    }
}

// MQTT Status Coloring
function updateBrokerStatus()
{
    const broker = document.getElementById("MQT-BROKER");

    if (!broker)
        return;

    const value = broker.textContent.trim().toUpperCase();

    if (value === "DISCONNECTED")
    {
        broker.style.color = "red";
    }
    else
    {
        broker.style.color = "lime";
    }
}

// Update GPS position
function updateVehiclePosition(data)
{


    let lat = parseFloat(data["VEH-LAT"]);
    let lon = parseFloat(data["VEH-LON"]);

    if (isNaN(lat) || isNaN(lon))
    {
        return;
    }

    // Demo GPS spoofing
    lat = 43.267819;
    lon = -2.928508;
    data["VEH-LAT"] = lat;
    data["VEH-LON"] = lon;

    vehicleMarker.setLatLng([lat, lon]);

    vehiclePath.push([lat, lon]);

    pathLine.setLatLngs(vehiclePath);

    map.setView([lat, lon]);
}

// Main telemetry update
function updateTelemetry()
{
    fetch('/tapBridge/api/telemetry')
    .then(response => response.json())
    .then(data =>
    {


        // Map updates

        updateVehiclePosition(data);



        // Update every field automatically

        Object.entries(data).forEach(([key, value]) =>
        {
            setField(key, value);
        });



        // MQTT status colors

        updateBrokerStatus();
    })
    .catch(error =>
    {
        console.error("Telemetry error:", error);
    });
}

// Initial update immediately
updateTelemetry();

// Poll once per second
setInterval(updateTelemetry, 1000);