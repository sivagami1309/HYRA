# HYRA Backend

This folder contains the FastAPI application and the AWS Lambda-compatible risk engine.

## Local run

From this folder:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Then open:

- http://127.0.0.1:8000/docs

## API endpoint

### POST /predict

Example request:

```json
{
  "location": "Kodaikanal",
  "rainfall": 145,
  "soil_moisture": 82,
  "temperature": 24,
  "terrain": "high"
}
```

Example response:

```json
{
  "location": "Kodaikanal",
  "flood_risk": "HIGH",
  "flood_score": 6,
  "landslide_risk": "HIGH",
  "landslide_score": 8,
  "overall_risk": "HIGH",
  "recommended_actions": [
    "Avoid low-lying and waterlogged roads",
    "Avoid streams, flooded roads and drainage channels",
    "Avoid steep slopes and areas with visible ground movement",
    "Monitor official emergency information",
    "Move toward a safer area if conditions worsen"
  ],
  "risk_factors": {
    "rainfall": 145,
    "soil_moisture": 82,
    "temperature": 24,
    "terrain": "High"
  }
}
```

## Lambda version

The file lambda_function.py is designed for AWS Lambda using the standard Python library only. It accepts a JSON payload and returns API Gateway-compatible response objects.

## Important note

This MVP uses a transparent rule-based risk engine and is not a trained predictive model.
