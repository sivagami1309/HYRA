# HYRA Architecture

## Overview

HYRA is a local hazard risk assessment MVP. It takes rainfall, soil moisture, temperature, and terrain data and uses a transparent rule-based engine to estimate flood risk, landslide risk, overall risk, and recommended safety actions.

The project is intentionally stateless and does not store user data. It does not require AWS cloud credentials or a database.

## Local request flow

User
↓
HYRA Frontend
↓
SAM Local HTTP API
↓
Lambda-compatible function
↓
HYRA Risk Engine
↓
JSON response
↓
Frontend displays result

## Frontend responsibility

The frontend is a polished HTML, CSS, and JavaScript interface. It captures the user inputs, sends them to the local SAM API, and displays the risk summary and recommended actions.

## SAM Local responsibility

SAM Local provides the local HTTP API and runs the Lambda-compatible function on the developer machine. It simulates the same serverless pattern used in AWS, but without using cloud services.

## Lambda responsibility

The Lambda-compatible function receives the request, validates the fields, calculates the risk, and returns a JSON response. The logic remains simple and easy to explain.

## Risk engine responsibility

The risk engine uses fixed thresholds for rainfall, soil moisture, terrain, and temperature. It is transparent and beginner-friendly, and it is explicitly not a trained ML model.

## Why no database is needed

This app only processes live inputs and returns immediate results. There is no need to store user records, weather history, or account data for an MVP.

## Why this is useful for beginners

SAM Local lets beginners learn AWS Lambda and HTTP API structure without needing a cloud account, a card, or deployment credentials.
