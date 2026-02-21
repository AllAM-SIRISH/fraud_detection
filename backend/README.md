# Fraud Detection Backend

FastAPI backend for real-time fraud detection using Isolation Forest.

## Features

- ✅ Synthetic transaction data generation
- ✅ Isolation Forest ML model
- ✅ Real-time fraud prediction
- ✅ RESTful API endpoints
- ✅ Model training on startup
- ✅ In-memory model for instant predictions

## API Endpoints

### GET /health
Check system status and model availability.

### GET /sample-transaction
Get a random sample transaction for testing.

### POST /predict
Predict fraud for a transaction.

Request body:
```json
{
  "amount": 1250.50,
  "transaction_type": "purchase",
  "account_age_days": 365,
  "location_risk_score": 0.15,
  "device_risk_score": 0.08,
  "transaction_hour": 14,
  "past_transactions_24h": 3
}
```

Response:
```json
{
  "prediction": "SAFE",
  "anomaly_score": 0.1234,
  "risk_level": "LOW",
  "explanation": "Transaction appears normal | Low risk profile detected"
}
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## Model Details

- **Algorithm**: Isolation Forest
- **Training Data**: 10,000 normal + 400 fraudulent transactions
- **Features**: Amount, transaction type, account age, risk scores, time, activity
- **Contamination Rate**: 4% (expected fraud rate)

## Data Generation

The system generates realistic synthetic financial data with:

- Normal transactions with realistic patterns
- Fraudulent transactions with suspicious behaviors:
  - High amounts
  - Late-night activity
  - High risk scores
  - Burst activity patterns

## Performance

- Model training: ~2-3 seconds on startup
- Prediction time: <1ms per transaction
- Memory usage: ~50MB (model + data)
