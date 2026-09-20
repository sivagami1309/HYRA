import json
import logging

logger = logging.getLogger(__name__)


def calculate_flood_risk(rainfall, soil_moisture):
    rain_points = 1
    if rainfall >= 120:
        rain_points = 3
    elif rainfall >= 70:
        rain_points = 2

    soil_points = 1
    if soil_moisture >= 80:
        soil_points = 3
    elif soil_moisture >= 60:
        soil_points = 2

    score = rain_points + soil_points
    if score >= 6:
        return "HIGH", score
    if score >= 4:
        return "MEDIUM", score
    return "LOW", score


def calculate_landslide_risk(rainfall, soil_moisture, terrain):
    soil_points = 1
    if soil_moisture >= 80:
        soil_points = 3
    elif soil_moisture >= 60:
        soil_points = 2

    terrain_map = {"low": 1, "medium": 2, "high": 3}
    terrain_points = terrain_map.get(str(terrain).lower(), 1)

    rain_points = 0
    if rainfall >= 100:
        rain_points = 2
    elif rainfall >= 50:
        rain_points = 1

    score = soil_points + terrain_points + rain_points
    if score >= 7:
        return "HIGH", score
    if score >= 4:
        return "MEDIUM", score
    return "LOW", score


def overall_risk(flood_risk, landslide_risk):
    if flood_risk == "HIGH" or landslide_risk == "HIGH":
        return "HIGH"
    if flood_risk == "MEDIUM" or landslide_risk == "MEDIUM":
        return "MEDIUM"
    return "LOW"


def build_actions(level):
    actions_map = {
        "HIGH": [
            "Avoid low-lying and waterlogged roads",
            "Avoid streams, flooded roads and drainage channels",
            "Avoid steep slopes and areas with visible ground movement",
            "Monitor official emergency information",
            "Move toward a safer area if conditions worsen",
        ],
        "MEDIUM": [
            "Stay alert to changing weather conditions",
            "Avoid unnecessary travel in risky areas",
            "Prepare for possible evacuation",
            "Monitor local weather conditions",
        ],
        "LOW": [
            "Continue normal activities",
            "Monitor local weather conditions",
        ],
    }
    return actions_map.get(level, actions_map["LOW"])


def lambda_handler(event, context):
    try:
        body = event.get("body")
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body or {}

        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object")

        location = payload.get("location")
        rainfall = payload.get("rainfall")
        soil_moisture = payload.get("soil_moisture")
        terrain = payload.get("terrain")

        if not location or not isinstance(location, str):
            raise ValueError("location is required and must be a string")
        if rainfall is None or soil_moisture is None or terrain is None:
            raise ValueError("rainfall, soil_moisture, and terrain are required")

        rainfall = float(rainfall)
        soil_moisture = float(soil_moisture)
        terrain = str(terrain).strip().lower()

        if not (0 <= rainfall <= 500):
            raise ValueError("rainfall must be between 0 and 500")
        if not (0 <= soil_moisture <= 100):
            raise ValueError("soil_moisture must be between 0 and 100")
        if terrain not in {"low", "medium", "high"}:
            raise ValueError("terrain must be 'low', 'medium', or 'high'")

        flood_risk, flood_score = calculate_flood_risk(rainfall, soil_moisture)
        landslide_risk, landslide_score = calculate_landslide_risk(rainfall, soil_moisture, terrain)
        result = overall_risk(flood_risk, landslide_risk)

        actions = build_actions(result)

        response_payload = {
            "location": location,
            "flood_risk": flood_risk,
            "flood_score": flood_score,
            "landslide_risk": landslide_risk,
            "landslide_score": landslide_score,
            "overall_risk": result,
            "recommended_actions": actions,
            "risk_factors": {
                "rainfall": int(round(rainfall)),
                "soil_moisture": int(round(soil_moisture)),
                "terrain": terrain.title(),
            },
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_payload),
        }
    except ValueError as exc:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(exc)}),
        }
    except Exception as exc:
        logger.exception("Unexpected error in lambda_handler")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }
