# HYRA – Local Hazard Risk & Action Assistant

## 1. Project name

HYRA

## 2. Problem

Local communities often need a quick and simple way to understand nearby environmental risk. Basic information such as rainfall, soil moisture, and terrain can signal danger from flooding or landslides, but many people do not have an easy tool to interpret these conditions.

## 3. Solution

HYRA provides a simple MVP that analyzes local conditions and produces a risk summary with practical safety guidance. It is designed to help people understand environmental risk in a fast, readable, and beginner-friendly way.

## 4. Features

- Flood risk calculation
- Landslide risk calculation
- Overall risk summary
- Risk factor breakdown
- Recommended safety actions
- Responsive web interface
- AWS SAM Local serverless runtime
- Stateless architecture

## 5. Technology stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python + AWS Lambda-compatible function
- Local AWS stack: AWS SAM CLI + SAM Local
- Risk engine: rule-based logic

## 6. Why no AWS cloud account is required

This project is designed to run fully on your Windows laptop. You do not need an AWS account, UPI, debit card, or credit card to run the app locally with AWS SAM Local.

## 7. Local setup for Windows PowerShell

### 1. Install Python 3.12

Install Python 3.12 from python.org.

### 2. Create a virtual environment

```powershell
cd HYRA-Hackathon
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

### 4. Install AWS SAM CLI

```powershell
winget install --id Amazon.SAM-CLI --source winget -e
```

Then confirm it works:

```powershell
sam --version
```

### 5. Start the local Lambda HTTP API

From the project root:

```powershell
cd HYRA-Hackathon
sam build
sam local start-api --host 127.0.0.1 --port 3000
```

The local API will run at:

```text
http://127.0.0.1:3000
```

### 6. Test the POST /predict route

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:3000/predict -ContentType "application/json" -Body '{"location":"Kodaikanal","rainfall":145,"soil_moisture":82,"temperature":24,"terrain":"high"}'
```

### 7. Open the frontend

Open the HTML file in a browser:

```text
frontend\index.html
```

## 8. Example request

```json
{
  "location": "Kodaikanal",
  "rainfall": 145,
  "soil_moisture": 82,
  "temperature": 24,
  "terrain": "high"
}
```

## 9. Example response

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

## 10. Local AWS SAM architecture

User
↓
HYRA Frontend
↓
SAM Local HTTP API
↓
AWS Lambda-compatible function
↓
HYRA Risk Engine
↓
JSON Response
↓
Frontend displays result

## 11. Why this still fits AWS work

The code uses the same Lambda-style pattern used in real AWS deployments, but it runs locally on your computer. This makes it a strong beginner-friendly way to learn serverless architecture without needing cloud access.

## 12. Important note

This MVP uses a transparent rule-based risk engine and is not a trained predictive model. It is intended for beginner learning and local prototype testing.

## 13. Quick PowerShell command list

```powershell
cd HYRA-Hackathon
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
sam build
sam local start-api --host 127.0.0.1 --port 3000
```

## 14. Security note

This project does not include AWS account credentials, AWS access keys, AWS secret keys, API keys, or passwords.

## 15. Beginner summary

1. Install Python 3.12
2. Create a virtual environment
3. Install dependencies
4. Install AWS SAM CLI
5. Start SAM Local
6. Test POST /predict
7. Open the frontend

No AWS account is required for this local build.
