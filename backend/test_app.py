import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_kodaikanal_high_risk():
    response = client.post(
        "/predict",
        json={
            "location": "Kodaikanal",
            "rainfall": 145,
            "soil_moisture": 82,
            "temperature": 24,
            "terrain": "high",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk"] == "HIGH"
    assert data["flood_risk"] == "HIGH"
    assert data["landslide_risk"] == "HIGH"


def test_low_risk_values():
    response = client.post(
        "/predict",
        json={
            "location": "Rural Valley",
            "rainfall": 20,
            "soil_moisture": 30,
            "temperature": 18,
            "terrain": "low",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk"] == "LOW"
    assert data["flood_risk"] == "LOW"
    assert data["landslide_risk"] == "LOW"


def test_medium_risk_values():
    response = client.post(
        "/predict",
        json={
            "location": "Hillside Town",
            "rainfall": 95,
            "soil_moisture": 70,
            "temperature": 26,
            "terrain": "medium",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk"] == "MEDIUM"
    assert data["flood_risk"] in {"MEDIUM", "LOW"}
    assert data["landslide_risk"] in {"MEDIUM", "LOW"}


def test_invalid_values():
    response = client.post(
        "/predict",
        json={
            "location": "Test",
            "rainfall": -10,
            "soil_moisture": 120,
            "temperature": 45,
            "terrain": "very high",
        },
    )
    assert response.status_code == 422


def test_missing_fields():
    response = client.post(
        "/predict",
        json={
            "location": "Test",
            "rainfall": 20,
            "temperature": 15,
        },
    )
    assert response.status_code == 422
