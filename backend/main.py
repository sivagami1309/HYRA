from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Literal

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================
# HYRA - REAL WORLD DATA BACKEND
# ============================================================

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("HYRA")


app = FastAPI(
    title="HYRA Real World Hazard Analysis API",
    version="3.0.0",
    description="Real-world environmental data collection and hazard analysis system",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hyra-jade.vercel.app",
        "http://127.0.0.1:5500",
        "http://localhost:5500",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# TYPES
# ============================================================

RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


# ============================================================
# REQUEST MODEL
# ============================================================

class LocationRequest(BaseModel):
    location: str = Field(
        ...,
        min_length=2,
        max_length=100
    )


# ============================================================
# HTTP CLIENT
# ============================================================

async def get_json(
    url: str,
    params: dict | None = None,
    timeout: int = 20
):

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True
    ) as client:

        response = await client.get(
            url,
            params=params
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# LOCATION
# ============================================================

async def get_location_data(location: str):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    data = await get_json(
        url,
        params
    )

    if not data.get("results"):
        raise ValueError(
            f"Location '{location}' was not found."
        )

    result = data["results"][0]

    return {
        "name": result.get("name"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "elevation": result.get("elevation", 0),
        "country": result.get("country", ""),
        "country_code": result.get("country_code", ""),
        "timezone": result.get("timezone", ""),
        "admin1": result.get("admin1", ""),
        "admin2": result.get("admin2", ""),
    }


# ============================================================
# REAL-TIME / FORECAST WEATHER
# ============================================================

async def get_weather_data(
    latitude: float,
    longitude: float
):

    url = "https://api.open-meteo.com/v1/forecast"

    hourly_variables = [
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "precipitation_probability",
        "precipitation",
        "rain",
        "showers",
        "surface_pressure",
        "pressure_msl",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "visibility",
        "wind_speed_10m",
        "wind_direction_10m",
        "wind_gusts_10m",
        "soil_temperature_0_to_7cm",
        "soil_temperature_7_to_28cm",
        "soil_temperature_28_to_100cm",
        "soil_temperature_100_to_255cm",
        "soil_moisture_0_to_7cm",
        "soil_moisture_7_to_28cm",
        "soil_moisture_28_to_100cm",
        "soil_moisture_100_to_255cm",
        "evapotranspiration",
        "et0_fao_evapotranspiration",
        "vapour_pressure_deficit",
        "cape",
        "weather_code",
    ]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(hourly_variables),
        "forecast_days": 7,
        "past_days": 2,
        "timezone": "auto",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    data = await get_json(
        url,
        params,
        timeout=30
    )

    hourly = data.get("hourly", {})

    times = hourly.get("time", [])

    def clean_values(name):

        return [
            value
            for value in hourly.get(name, [])
            if value is not None
        ]

    precipitation = clean_values("precipitation")
    rain = clean_values("rain")

    soil_07 = clean_values(
        "soil_moisture_0_to_7cm"
    )

    soil_728 = clean_values(
        "soil_moisture_7_to_28cm"
    )

    soil_28100 = clean_values(
        "soil_moisture_28_to_100cm"
    )

    soil_100255 = clean_values(
        "soil_moisture_100_to_255cm"
    )

    temperatures = clean_values(
        "temperature_2m"
    )

    humidity = clean_values(
        "relative_humidity_2m"
    )

    wind = clean_values(
        "wind_speed_10m"
    )

    gusts = clean_values(
        "wind_gusts_10m"
    )

    pressure = clean_values(
        "surface_pressure"
    )

    cloud = clean_values(
        "cloud_cover"
    )

    visibility = clean_values(
        "visibility"
    )

    rain_probability = clean_values(
        "precipitation_probability"
    )

    # --------------------------------------------------------
    # 24 hour data
    # --------------------------------------------------------

    rain_24h = sum(
        precipitation[:24]
    )

    rain_next_24h = sum(
        precipitation[-24:]
    ) if len(precipitation) >= 24 else sum(precipitation)

    maximum_hourly_rain = max(
        rain[:24],
        default=0
    )

    maximum_wind = max(
        wind[:24],
        default=0
    )

    maximum_gust = max(
        gusts[:24],
        default=0
    )

    average_temperature = (
        sum(temperatures[:24]) /
        len(temperatures[:24])
        if temperatures
        else 0
    )

    average_humidity = (
        sum(humidity[:24]) /
        len(humidity[:24])
        if humidity
        else 0
    )

    average_pressure = (
        sum(pressure[:24]) /
        len(pressure[:24])
        if pressure
        else 0
    )

    average_cloud = (
        sum(cloud[:24]) /
        len(cloud[:24])
        if cloud
        else 0
    )

    average_visibility = (
        sum(visibility[:24]) /
        len(visibility[:24])
        if visibility
        else 0
    )

    average_rain_probability = (
        sum(rain_probability[:24]) /
        len(rain_probability[:24])
        if rain_probability
        else 0
    )

    # --------------------------------------------------------
    # Soil
    # --------------------------------------------------------

    def average(values):

        if not values:
            return 0

        return sum(values) / len(values)

    soil_moisture = {
        "0_7cm": round(
            average(soil_07) * 100,
            2
        ),
        "7_28cm": round(
            average(soil_728) * 100,
            2
        ),
        "28_100cm": round(
            average(soil_28100) * 100,
            2
        ),
        "100_255cm": round(
            average(soil_100255) * 100,
            2
        ),
    }

    # --------------------------------------------------------
    # Current values
    # --------------------------------------------------------

    current = {
        "time": times[0] if times else None,

        "temperature_c": round(
            temperatures[0],
            2
        ) if temperatures else None,

        "humidity_percent": round(
            humidity[0],
            2
        ) if humidity else None,

        "wind_speed_kmh": round(
            wind[0],
            2
        ) if wind else None,

        "wind_gust_kmh": round(
            gusts[0],
            2
        ) if gusts else None,

        "surface_pressure_hpa": round(
            pressure[0],
            2
        ) if pressure else None,

        "cloud_cover_percent": round(
            cloud[0],
            2
        ) if cloud else None,

        "visibility_m": round(
            visibility[0],
            2
        ) if visibility else None,

        "precipitation_probability_percent": round(
            rain_probability[0],
            2
        ) if rain_probability else None,
    }

    return {

        "source": "Open-Meteo",

        "forecast_days": 7,

        "current": current,

        "rainfall": {
            "past_and_forecast_total_mm": round(
                sum(precipitation),
                2
            ),

            "past_24h_mm": round(
                rain_24h,
                2
            ),

            "next_24h_mm": round(
                rain_next_24h,
                2
            ),

            "maximum_hourly_rain_mm": round(
                maximum_hourly_rain,
                2
            ),
        },

        "wind": {
            "maximum_24h_kmh": round(
                maximum_wind,
                2
            ),

            "maximum_gust_24h_kmh": round(
                maximum_gust,
                2
            ),
        },

        "atmosphere": {
            "average_temperature_c": round(
                average_temperature,
                2
            ),

            "average_humidity_percent": round(
                average_humidity,
                2
            ),

            "average_surface_pressure_hpa": round(
                average_pressure,
                2
            ),

            "average_cloud_cover_percent": round(
                average_cloud,
                2
            ),

            "average_visibility_m": round(
                average_visibility,
                2
            ),

            "average_rain_probability_percent": round(
                average_rain_probability,
                2
            ),
        },

        "soil": {
            "moisture_percent": soil_moisture
        },

        "raw_hourly": {

            "time": times,

            "temperature_c": hourly.get(
                "temperature_2m",
                []
            ),

            "rainfall_mm": hourly.get(
                "precipitation",
                []
            ),

            "rain_mm": hourly.get(
                "rain",
                []
            ),

            "humidity_percent": hourly.get(
                "relative_humidity_2m",
                []
            ),

            "wind_speed_kmh": hourly.get(
                "wind_speed_10m",
                []
            ),

            "wind_gust_kmh": hourly.get(
                "wind_gusts_10m",
                []
            ),

            "soil_moisture": hourly.get(
                "soil_moisture_0_to_7cm",
                []
            ),

            "pressure_hpa": hourly.get(
                "surface_pressure",
                []
            ),

            "cloud_cover_percent": hourly.get(
                "cloud_cover",
                []
            ),
        },
    }


# ============================================================
# HISTORICAL WEATHER
# ============================================================

async def get_historical_data(
    latitude: float,
    longitude: float
):

    end_date = datetime.utcnow().date()

    start_date = (
        end_date - timedelta(days=30)
    )

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "start_date": start_date.isoformat(),

        "end_date": end_date.isoformat(),

        "daily": ",".join([
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "rain_sum",
            "wind_speed_10m_max",
        ]),

        "timezone": "auto",
    }

    try:

        data = await get_json(
            url,
            params,
            timeout=30
        )

        daily = data.get(
            "daily",
            {}
        )

        rainfall = [
            value
            for value in daily.get(
                "precipitation_sum",
                []
            )
            if value is not None
        ]

        rain = [
            value
            for value in daily.get(
                "rain_sum",
                []
            )
            if value is not None
        ]

        return {

            "source": "Open-Meteo Historical Weather",

            "period_days": 30,

            "start_date": start_date.isoformat(),

            "end_date": end_date.isoformat(),

            "total_precipitation_mm": round(
                sum(rainfall),
                2
            ),

            "total_rain_mm": round(
                sum(rain),
                2
            ),

            "maximum_daily_rain_mm": round(
                max(rainfall, default=0),
                2
            ),

            "daily": daily,
        }

    except Exception as error:

        logger.warning(
            "Historical weather unavailable: %s",
            error
        )

        return {

            "source": "Open-Meteo Historical Weather",

            "available": False,

            "error": str(error),
        }


# ============================================================
# NASA PMM DATA
# ============================================================

async def get_nasa_hazard_data(
    latitude: float,
    longitude: float
):

    url = (
        "https://pmmpublisher.pps.eosdis.nasa.gov/"
        "opensearch"
    )

    today = datetime.utcnow().date()

    start_date = (
        today - timedelta(days=7)
    )

    datasets = [

        "precip_30mn",

        "precip_30mn_3hr",

        "precip_30mn_1d",

        "flood_nowcast",

        "global_landslide_nowcast",

    ]

    results = {}

    for dataset in datasets:

        params = {

            "q": dataset,

            "lat": latitude,

            "lon": longitude,

            "startTime": start_date.isoformat(),

            "endTime": today.isoformat(),

            "limit": 5,
        }

        try:

            data = await get_json(
                url,
                params,
                timeout=30
            )

            results[dataset] = {

                "available": True,

                "data": data,

            }

        except Exception as error:

            results[dataset] = {

                "available": False,

                "error": str(error),

            }

    return {

        "source": "NASA GPM / PMM Publisher",

        "datasets": results,

    }


# ============================================================
# FLOOD RISK
# ============================================================

def calculate_flood_risk(
    rainfall_24h: float,
    rainfall_next_24h: float,
    maximum_hourly_rain: float,
    soil_moisture: float,
    rain_probability: float,
    historical_rainfall: float,
):

    score = 0

    # Recent rainfall
    if rainfall_24h >= 100:
        score += 4
    elif rainfall_24h >= 50:
        score += 3
    elif rainfall_24h >= 20:
        score += 1

    # Forecast rainfall
    if rainfall_next_24h >= 100:
        score += 4
    elif rainfall_next_24h >= 50:
        score += 3
    elif rainfall_next_24h >= 20:
        score += 1

    # Extreme hourly rainfall
    if maximum_hourly_rain >= 50:
        score += 4
    elif maximum_hourly_rain >= 30:
        score += 3
    elif maximum_hourly_rain >= 15:
        score += 1

    # Soil saturation
    if soil_moisture >= 80:
        score += 3
    elif soil_moisture >= 60:
        score += 2
    elif soil_moisture >= 40:
        score += 1

    # Rain probability
    if rain_probability >= 80:
        score += 2
    elif rain_probability >= 60:
        score += 1

    # Recent historical wetness
    if historical_rainfall >= 300:
        score += 2
    elif historical_rainfall >= 150:
        score += 1

    if score >= 12:
        risk = "HIGH"

    elif score >= 6:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return risk, score


# ============================================================
# LANDSLIDE RISK
# ============================================================

def calculate_landslide_risk(
    rainfall_24h: float,
    rainfall_next_24h: float,
    maximum_hourly_rain: float,
    soil_moisture: float,
    elevation: float,
    historical_rainfall: float,
):

    score = 0

    # Rainfall
    if rainfall_24h >= 80:
        score += 3
    elif rainfall_24h >= 40:
        score += 2
    elif rainfall_24h >= 20:
        score += 1

    # Forecast rain
    if rainfall_next_24h >= 80:
        score += 3
    elif rainfall_next_24h >= 40:
        score += 2
    elif rainfall_next_24h >= 20:
        score += 1

    # Intense rain
    if maximum_hourly_rain >= 40:
        score += 3
    elif maximum_hourly_rain >= 25:
        score += 2
    elif maximum_hourly_rain >= 10:
        score += 1

    # Soil saturation
    if soil_moisture >= 80:
        score += 3
    elif soil_moisture >= 60:
        score += 2
    elif soil_moisture >= 40:
        score += 1

    # Elevation
    if elevation >= 1500:
        score += 3
    elif elevation >= 1000:
        score += 2
    elif elevation >= 500:
        score += 1

    # Historical wetness
    if historical_rainfall >= 300:
        score += 2
    elif historical_rainfall >= 150:
        score += 1

    if score >= 12:
        risk = "HIGH"

    elif score >= 6:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return risk, score


# ============================================================
# OVERALL RISK
# ============================================================

def get_overall_risk(
    flood_risk: str,
    landslide_risk: str
):

    if (
        flood_risk == "HIGH"
        or landslide_risk == "HIGH"
    ):

        return "HIGH"

    if (
        flood_risk == "MEDIUM"
        or landslide_risk == "MEDIUM"
    ):

        return "MEDIUM"

    return "LOW"


# ============================================================
# ALERT ENGINE
# ============================================================

def create_alerts(
    location: str,
    overall_risk: str,
    flood_risk: str,
    landslide_risk: str
):

    result = {

        "authority_alert": False,

        "public_alert": False,

        "authority_message": "",

        "public_message": "",

        "notification_status":
            "NOT_SENT",

    }

    if overall_risk == "HIGH":

        result["authority_alert"] = True

        result["public_alert"] = True

        result["authority_message"] = (
            f"HYRA EMERGENCY ALERT: "
            f"High hazard risk detected in {location}. "
            f"Flood risk: {flood_risk}. "
            f"Landslide risk: {landslide_risk}. "
            f"Immediate monitoring and preparedness "
            f"action recommended."
        )

        result["public_message"] = (
            f"HYRA ALERT: High hazard risk detected "
            f"in {location}. Avoid risky areas and "
            f"follow official safety instructions."
        )

        result["notification_status"] = (
            "ALERT_READY"
        )

    elif overall_risk == "MEDIUM":

        result["authority_alert"] = True

        result["public_alert"] = False

        result["authority_message"] = (
            f"HYRA WATCH: Moderate hazard conditions "
            f"detected in {location}. "
            f"Increased monitoring recommended."
        )

        result["public_message"] = (
            f"HYRA WATCH: Moderate hazard conditions "
            f"detected in {location}. "
            f"Monitor official advisories."
        )

        result["notification_status"] = (
            "WATCH_READY"
        )

    return result


# ============================================================
# MAIN PREDICTION API
# ============================================================

@app.post("/predict-location")
async def predict_location(
    payload: LocationRequest
):

    location = payload.location.strip()

    if not location:

        return {

            "success": False,

            "error": "Location cannot be empty."

        }

    try:

        # ----------------------------------------------------
        # 1. LOCATION
        # ----------------------------------------------------

        location_data = await get_location_data(
            location
        )

        latitude = location_data["latitude"]

        longitude = location_data["longitude"]

        elevation = location_data["elevation"]


        # ----------------------------------------------------
        # 2. REAL WEATHER
        # ----------------------------------------------------

        weather = await get_weather_data(
            latitude,
            longitude
        )


        # ----------------------------------------------------
        # 3. HISTORICAL WEATHER
        # ----------------------------------------------------

        historical = await get_historical_data(
            latitude,
            longitude
        )


        # ----------------------------------------------------
        # 4. NASA DATA
        # ----------------------------------------------------

        nasa = await get_nasa_hazard_data(
            latitude,
            longitude
        )


        # ----------------------------------------------------
        # 5. EXTRACT DATA
        # ----------------------------------------------------

        rainfall_24h = weather[
            "rainfall"
        ]["past_24h_mm"]

        rainfall_next_24h = weather[
            "rainfall"
        ]["next_24h_mm"]

        maximum_hourly_rain = weather[
            "rainfall"
        ]["maximum_hourly_rain_mm"]

        soil_layers = weather[
            "soil"
        ]["moisture_percent"]

        soil_moisture = soil_layers[
            "0_7cm"
        ]

        rain_probability = weather[
            "atmosphere"
        ]["average_rain_probability_percent"]

        historical_rainfall = historical.get(
            "total_precipitation_mm",
            0
        )


        # ----------------------------------------------------
        # 6. FLOOD RISK
        # ----------------------------------------------------

        flood_risk, flood_score = (
            calculate_flood_risk(
                rainfall_24h,
                rainfall_next_24h,
                maximum_hourly_rain,
                soil_moisture,
                rain_probability,
                historical_rainfall,
            )
        )


        # ----------------------------------------------------
        # 7. LANDSLIDE RISK
        # ----------------------------------------------------

        landslide_risk, landslide_score = (
            calculate_landslide_risk(
                rainfall_24h,
                rainfall_next_24h,
                maximum_hourly_rain,
                soil_moisture,
                elevation,
                historical_rainfall,
            )
        )


        # ----------------------------------------------------
        # 8. OVERALL
        # ----------------------------------------------------

        overall_risk = get_overall_risk(
            flood_risk,
            landslide_risk
        )


        # ----------------------------------------------------
        # 9. ALERT
        # ----------------------------------------------------

        alerts = create_alerts(
            location_data["name"],
            overall_risk,
            flood_risk,
            landslide_risk
        )


        # ----------------------------------------------------
        # 10. FINAL RESPONSE
        # ----------------------------------------------------

        return {

            "success": True,

            "system": "HYRA",

            "data_timestamp": datetime.utcnow().isoformat(),

            "location": location_data,

            "prediction": {

                "forecast_window":
                    "Next 24 hours",

                "flood_risk":
                    flood_risk,

                "flood_score":
                    flood_score,

                "landslide_risk":
                    landslide_risk,

                "landslide_score":
                    landslide_score,

                "overall_risk":
                    overall_risk,
            },

            "real_world_environment": {

                "weather":
                    weather,

                "historical_weather":
                    historical,

                "nasa":
                    nasa,
            },

            "terrain": {

                "elevation_m":
                    elevation,

            },

            "alerts":
                alerts,

            "data_sources": [

                "Open-Meteo Geocoding",

                "Open-Meteo Forecast",

                "Open-Meteo Historical Weather",

                "NASA GPM / PMM",

            ],

        }

    except Exception as error:

        logger.exception(
            "HYRA prediction failed"
        )

        return {

            "success": False,

            "error": str(error),

        }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "ok",

        "system": "HYRA",

        "version": "3.0.0",

    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "message":
            "HYRA Real World Hazard Analysis API is running.",

        "version":
            "3.0.0",

        "endpoint":
            "/predict-location",

    }