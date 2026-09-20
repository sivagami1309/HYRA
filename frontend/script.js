const API_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {

    const locationInput = document.getElementById("location");
    const checkButton = document.getElementById("checkRisk");

    checkButton.addEventListener("click", checkRisk);

    locationInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            checkRisk();
        }
    });

    async function checkRisk() {

        const location = locationInput.value.trim();

        if (!location) {
            showError("Please enter a location.");
            return;
        }

        checkButton.disabled = true;
        checkButton.textContent = "ANALYZING...";

        showLoading();

        try {

            const response = await fetch(
                `${API_URL}/predict-location`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        location: location
                    })
                }
            );

            const data = await response.json();

            console.log("HYRA RESPONSE:", data);

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error || "Unable to analyze this location."
                );
            }

            displayDashboard(data);

        } catch (error) {

            console.error(error);
            showError(error.message);

        } finally {

            checkButton.disabled = false;
            checkButton.textContent = "CHECK RISK";

        }
    }
});


/* =========================================
   FIND VALUE FROM NESTED OBJECT
========================================= */

function findValue(object, possibleKeys) {

    if (!object || typeof object !== "object") {
        return null;
    }

    for (const key of possibleKeys) {

        if (
            Object.prototype.hasOwnProperty.call(object, key) &&
            object[key] !== null &&
            object[key] !== undefined &&
            typeof object[key] !== "object"
        ) {
            return object[key];
        }
    }

    for (const key in object) {

        const value = object[key];

        if (value && typeof value === "object") {

            if (Array.isArray(value)) {
                continue;
            }

            const result =
                findValue(value, possibleKeys);

            if (
                result !== null &&
                result !== undefined
            ) {
                return result;
            }
        }
    }

    return null;
}


/* =========================================
   FORMAT VALUE
========================================= */

function formatValue(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "N/A";
    }

    if (typeof value === "number") {

        if (!Number.isFinite(value)) {
            return "N/A";
        }

        return Number.isInteger(value)
            ? value
            : value.toFixed(1);
    }

    return String(value);
}


/* =========================================
   LOCATION NAME
========================================= */

function getLocationName(location) {

    if (typeof location === "string") {
        return location;
    }

    if (!location || typeof location !== "object") {
        return "Unknown Location";
    }

    return (
        location.name ||
        location.display_name ||
        location.city ||
        location.town ||
        location.village ||
        location.locality ||
        "Unknown Location"
    );
}


/* =========================================
   MAIN DASHBOARD
========================================= */

function displayDashboard(data) {

    const output =
        document.getElementById("hyraOutput");

    const prediction =
        data.prediction || {};

    const environment =
        data.real_world_environment || {};

    const weather =
        environment.weather || environment;

    /* ---------- RISK ---------- */

    const floodRisk =
        prediction.flood_risk ||
        prediction.flood ||
        "UNKNOWN";

    const landslideRisk =
        prediction.landslide_risk ||
        prediction.landslide ||
        "UNKNOWN";

    const overallRisk =
        prediction.overall_risk ||
        prediction.overall ||
        "UNKNOWN";


    /* ---------- LOCATION ---------- */

    const locationName =
        getLocationName(data.location);


    /* ---------- ENVIRONMENT VALUES ---------- */

    const temperature = findValue(
        weather,
        [
            "temperature_2m",
            "temperature",
            "temperature_c"
        ]
    );

    const humidity = findValue(
        weather,
        [
            "relative_humidity_2m",
            "relative_humidity",
            "humidity",
            "humidity_percent"
        ]
    );

    const rainfall = findValue(
        weather,
        [
            "total",
            "total_mm",
            "total_rainfall",
            "total_rainfall_mm",
            "rainfall",
            "rainfall_mm"
        ]
    );

    const soilMoisture = findValue(
        weather,
        [
            "average_percent",
            "moisture_percent",
            "soil_moisture_percent",
            "average_moisture",
            "moisture"
        ]
    );

    const wind = findValue(
        weather,
        [
            "wind_speed_10m",
            "wind_speed",
            "max_24h",
            "max_wind_speed",
            "wind_speed_kmh"
        ]
    );

    const cloud = findValue(
        weather,
        [
            "cloud_cover",
            "cloud_cover_percent"
        ]
    );

    const pressure = findValue(
        weather,
        [
            "pressure_msl",
            "pressure",
            "surface_pressure"
        ]
    );

    const visibility = findValue(
        weather,
        [
            "visibility",
            "visibility_m"
        ]
    );

    const rainProbability = findValue(
        weather,
        [
            "precipitation_probability",
            "rain_probability",
            "rain_probability_percent"
        ]
    );


    /* ---------- ALERTS ---------- */

    const alerts =
        data.alerts || {};

    const publicAlert =
        alerts.public_message ||
        alerts.public_alert ||
        "No immediate public alert";

    const authorityAlert =
        alerts.authority_message ||
        alerts.authority_alert ||
        "No authority alert";


    /* ---------- HTML ---------- */

    output.innerHTML = `

        <div class="dashboard">

            <!-- LOCATION -->

            <div class="location-header">

                <div>

                    <span class="small-label">
                        ANALYSIS LOCATION
                    </span>

                    <h2>
                        📍 ${locationName}
                    </h2>

                    <p>
                        Real-world environmental analysis
                    </p>

                </div>

                <div class="status-badge ${riskClass(overallRisk)}">
                    ${formatValue(overallRisk)}
                </div>

            </div>


            <!-- OVERALL RISK -->

            <div class="overall-card ${riskClass(overallRisk)}">

                <div class="overall-icon">
                    ${riskIcon(overallRisk)}
                </div>

                <div>

                    <span class="small-label">
                        OVERALL HAZARD RISK
                    </span>

                    <h1>
                        ${formatValue(overallRisk)}
                    </h1>

                    <p>
                        Combined assessment of flood
                        and landslide conditions.
                    </p>

                </div>

            </div>


            <!-- HAZARDS -->

            <div class="section-title">
                ⚠️ Hazard Assessment
            </div>


            <div class="risk-grid">

                <div class="risk-card">

                    <div class="risk-card-top">

                        <span class="hazard-icon">
                            🌊
                        </span>

                        <span class="risk-pill ${riskClass(floodRisk)}">
                            ${formatValue(floodRisk)}
                        </span>

                    </div>

                    <h3>
                        Flood Risk
                    </h3>

                    <p>
                        Based on rainfall and current
                        environmental conditions.
                    </p>

                </div>


                <div class="risk-card">

                    <div class="risk-card-top">

                        <span class="hazard-icon">
                            ⛰️
                        </span>

                        <span class="risk-pill ${riskClass(landslideRisk)}">
                            ${formatValue(landslideRisk)}
                        </span>

                    </div>

                    <h3>
                        Landslide Risk
                    </h3>

                    <p>
                        Based on soil moisture and
                        environmental conditions.
                    </p>

                </div>

            </div>


            <!-- ENVIRONMENT -->

            <div class="section-title">
                🌦️ Environmental Conditions
            </div>


            <div class="environment-grid">

                ${metricCard(
                    "🌡️",
                    "Temperature",
                    temperature,
                    "°C"
                )}

                ${metricCard(
                    "💧",
                    "Humidity",
                    humidity,
                    "%"
                )}

                ${metricCard(
                    "🌧️",
                    "Rainfall",
                    rainfall,
                    "mm"
                )}

                ${metricCard(
                    "🌱",
                    "Soil Moisture",
                    soilMoisture,
                    "%"
                )}

                ${metricCard(
                    "💨",
                    "Wind Speed",
                    wind,
                    "km/h"
                )}

                ${metricCard(
                    "☁️",
                    "Cloud Cover",
                    cloud,
                    "%"
                )}

            </div>


            <!-- ATMOSPHERE -->

            <div class="section-title">
                🌍 Atmospheric Conditions
            </div>


            <div class="atmosphere-card">

                <div>
                    <span>Pressure</span>

                    <strong>
                        ${formatValue(pressure)} hPa
                    </strong>
                </div>


                <div>
                    <span>Visibility</span>

                    <strong>
                        ${formatValue(visibility)} m
                    </strong>
                </div>


                <div>
                    <span>Rain Probability</span>

                    <strong>
                        ${formatValue(rainProbability)}%
                    </strong>
                </div>

            </div>


            <!-- ALERTS -->

            <div class="section-title">
                🚨 Alert Center
            </div>


            <div class="alert-grid">

                <div class="alert-card">

                    <div class="alert-title">
                        📢 Public Alert
                    </div>

                    <p>
                        ${publicAlert}
                    </p>

                </div>


                <div class="alert-card">

                    <div class="alert-title">
                        🏛️ Authority Alert
                    </div>

                    <p>
                        ${authorityAlert}
                    </p>

                </div>

            </div>


            <!-- SOURCE -->

            <div class="data-source">

                <strong>
                    📡 Data Source
                </strong>

                <p>
                    Real-world weather and environmental
                    data used for this analysis.
                </p>

                <span>
                    HYRA Risk Analysis Engine
                </span>

            </div>

        </div>
    `;

    addDashboardStyles();
}


/* =========================================
   METRIC CARD
========================================= */

function metricCard(icon, title, value, unit) {

    return `

        <div class="metric-card">

            <div class="metric-icon">
                ${icon}
            </div>

            <div class="metric-info">

                <span>
                    ${title}
                </span>

                <strong>
                    ${formatValue(value)}
                    <small>${unit}</small>
                </strong>

            </div>

        </div>

    `;
}


/* =========================================
   RISK CLASS
========================================= */

function riskClass(risk) {

    const value =
        String(risk || "").toLowerCase();

    if (
        value.includes("critical") ||
        value.includes("extreme")
    ) {
        return "risk-critical";
    }

    if (
        value.includes("high") ||
        value.includes("severe")
    ) {
        return "risk-high";
    }

    if (
        value.includes("moderate") ||
        value.includes("medium")
    ) {
        return "risk-moderate";
    }

    if (
        value.includes("low")
    ) {
        return "risk-low";
    }

    return "risk-unknown";
}


/* =========================================
   RISK ICON
========================================= */

function riskIcon(risk) {

    const value =
        String(risk || "").toLowerCase();

    if (
        value.includes("critical") ||
        value.includes("extreme")
    ) {
        return "🚨";
    }

    if (
        value.includes("high") ||
        value.includes("severe")
    ) {
        return "🔴";
    }

    if (
        value.includes("moderate") ||
        value.includes("medium")
    ) {
        return "🟡";
    }

    if (
        value.includes("low")
    ) {
        return "🟢";
    }

    return "⚠️";
}


/* =========================================
   LOADING
========================================= */

function showLoading() {

    const output =
        document.getElementById("hyraOutput");

    output.innerHTML = `

        <div class="loading-card">

            <div class="loader"></div>

            <h3>
                Analyzing Environmental Conditions
            </h3>

            <p>
                Fetching real-world environmental data...
            </p>

        </div>
    `;

    addDashboardStyles();
}


/* =========================================
   ERROR
========================================= */

function showError(message) {

    const output =
        document.getElementById("hyraOutput");

    output.innerHTML = `

        <div class="error-card">

            <h3>
                ❌ Analysis Failed
            </h3>

            <p>
                ${message}
            </p>

            <button onclick="location.reload()">
                TRY AGAIN
            </button>

        </div>
    `;

    addDashboardStyles();
}


/* =========================================
   CSS
========================================= */

function addDashboardStyles() {

    if (
        document.getElementById(
            "hyraDashboardStyles"
        )
    ) {
        return;
    }

    const style =
        document.createElement("style");

    style.id =
        "hyraDashboardStyles";

    style.innerHTML = `

        #hyraOutput {
            width: 100%;
        }

        .dashboard {
            margin-top: 30px;
        }

        .location-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 5px 20px rgba(0,0,0,.08);
        }

        .location-header h2 {
            margin: 5px 0;
        }

        .location-header p {
            margin: 0;
            color: #777;
        }

        .small-label {
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
            color: #777;
        }

        .status-badge {
            padding: 12px 20px;
            border-radius: 30px;
            font-weight: bold;
        }

        .overall-card {
            margin-top: 20px;
            padding: 30px;
            border-radius: 18px;
            display: flex;
            align-items: center;
            gap: 20px;
            background: white;
            box-shadow: 0 5px 20px rgba(0,0,0,.08);
        }

        .overall-card h1 {
            margin: 5px 0;
            font-size: 34px;
        }

        .overall-card p {
            margin: 0;
            color: #666;
        }

        .overall-icon {
            font-size: 48px;
        }

        .section-title {
            font-size: 20px;
            font-weight: bold;
            margin: 30px 0 15px;
        }

        .risk-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 18px;
        }

        .risk-card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 5px 20px rgba(0,0,0,.07);
        }

        .risk-card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .hazard-icon {
            font-size: 35px;
        }

        .risk-card h3 {
            margin: 18px 0 8px;
        }

        .risk-card p {
            color: #666;
            margin: 0;
        }

        .risk-pill {
            padding: 7px 14px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 13px;
        }

        .environment-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }

        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            gap: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,.06);
        }

        .metric-icon {
            font-size: 30px;
        }

        .metric-info span {
            display: block;
            color: #777;
            font-size: 13px;
        }

        .metric-info strong {
            display: block;
            margin-top: 5px;
            font-size: 21px;
        }

        .metric-info small {
            font-size: 12px;
            color: #777;
        }

        .atmosphere-card {
            background: white;
            padding: 22px;
            border-radius: 15px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,.06);
        }

        .atmosphere-card span {
            display: block;
            color: #777;
            font-size: 13px;
        }

        .atmosphere-card strong {
            display: block;
            margin-top: 6px;
        }

        .alert-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 18px;
        }

        .alert-card {
            background: white;
            padding: 22px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,.06);
        }

        .alert-title {
            font-weight: bold;
            margin-bottom: 12px;
        }

        .alert-card p {
            color: #555;
            margin: 0;
        }

        .data-source {
            margin-top: 25px;
            padding: 20px;
            background: #eef5ff;
            border-radius: 14px;
        }

        .data-source p {
            margin: 6px 0;
            color: #555;
        }

        .data-source span {
            font-size: 12px;
            color: #777;
        }

        .risk-low {
            background: #e8f7ed;
            color: #197a3d;
        }

        .risk-moderate {
            background: #fff4d6;
            color: #9a6a00;
        }

        .risk-high {
            background: #ffe5e5;
            color: #c62828;
        }

        .risk-critical {
            background: #f3d9ff;
            color: #8e24aa;
        }

        .risk-unknown {
            background: #eeeeee;
            color: #555;
        }

        .loading-card {
            margin-top: 30px;
            background: white;
            padding: 40px;
            text-align: center;
            border-radius: 16px;
        }

        .loader {
            width: 45px;
            height: 45px;
            border: 5px solid #ddd;
            border-top: 5px solid #1976d2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: auto;
        }

        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }

        .error-card {
            margin-top: 30px;
            padding: 25px;
            background: #fff0f0;
            border-radius: 15px;
        }

        @media (max-width: 700px) {

            .location-header {
                flex-direction: column;
                align-items: flex-start;
            }

            .risk-grid,
            .alert-grid,
            .environment-grid,
            .atmosphere-card {
                grid-template-columns: 1fr;
            }

            .overall-card {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    `;

    document.head.appendChild(style);
}