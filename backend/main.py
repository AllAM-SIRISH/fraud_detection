from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_generator import TransactionDataGenerator
from model import FraudDetectionModel

# Initialize FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection system using Isolation Forest",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global variables
model = None
data_generator = None

def initialize_system():
    """Initialize model and data generator"""
    global model, data_generator
    
    if model is not None and data_generator is not None:
        return
    
    print("=" * 50)
    print("Initializing Fraud Detection System...")
    print("=" * 50)
    
    try:
        # Initialize data generator
        print("Initializing data generator...")
        data_generator = TransactionDataGenerator(seed=42)
        
        # Generate training dataset
        print("Generating training dataset...")
        df = data_generator.generate_dataset()
        
        # Initialize and train model
        print("Initializing fraud detection model...")
        model = FraudDetectionModel()
        
        print("Training model on generated dataset...")
        model.train(df)
        
        print("=" * 50)
        print("✅ Fraud Detection System is ready!")
        print("✅ Model trained and loaded in memory")
        print("✅ API endpoints available")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during initialization: {str(e)}")
        raise

# Pydantic models for API
class TransactionRequest(BaseModel):
    amount: float
    transaction_type: str
    account_age_days: int
    location_risk_score: float
    device_risk_score: float
    transaction_hour: int
    past_transactions_24h: int

class PredictionResponse(BaseModel):
    prediction: str
    anomaly_score: float
    risk_level: str
    explanation: str

class HealthResponse(BaseModel):
    status: str
    model_trained: bool
    message: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        initialize_system()
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            model_trained=False,
            message=f"Initialization error: {str(e)}"
        )
    
    if model is None or not model.is_trained:
        return HealthResponse(
            status="unhealthy",
            model_trained=False,
            message="Model not trained"
        )
    
    return HealthResponse(
        status="healthy",
        model_trained=True,
        message="Fraud detection system is operational"
    )

@app.get("/sample-transaction")
async def get_sample_transaction():
    """Get a random sample transaction for testing"""
    try:
        initialize_system()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System initialization failed: {str(e)}")
    
    try:
        # Randomly decide if we want a normal or fraudulent transaction
        import random
        is_fraudulent = random.choice([None, None, None, True, False])  # Bias towards normal
        
        sample = data_generator.get_sample_transaction(is_fraudulent=is_fraudulent)
        
        # Remove the is_anomaly field (this is ground truth, not for prediction)
        sample.pop('is_anomaly', None)
        
        return sample
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: TransactionRequest):
    """Predict if a transaction is fraudulent"""
    try:
        initialize_system()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System initialization failed: {str(e)}")
    
    try:
        # Convert Pydantic model to dict
        transaction_dict = transaction.dict()
        
        # Make prediction
        prediction = model.predict(transaction_dict)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making prediction: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Fraud Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "sample_transaction": "/sample-transaction",
            "predict": "/predict (POST)"
        },
        "model": "Isolation Forest",
        "status": "operational" if model and model.is_trained else "initializing"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
