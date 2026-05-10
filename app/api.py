"""
FastAPI Application
===================
Contoh API untuk model serving.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np

app = FastAPI(
    title="AI Project API",
    description="API for ML model serving",
    version="1.0.0"
)

# Request/Response models
class PredictionRequest(BaseModel):
    features: List[float]
    
class PredictionResponse(BaseModel):
    prediction: float
    probability: Optional[float] = None
    model_version: str = "1.0.0"

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AI Project API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Make prediction"""
    try:
        # Placeholder for actual prediction logic
        prediction = np.random.random()
        probability = np.random.random()
        
        return PredictionResponse(
            prediction=float(prediction),
            probability=float(probability)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
