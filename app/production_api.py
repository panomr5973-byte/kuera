"""
Production API - Complete Implementation
========================================
API production-ready dengan:
- Authentication
- Rate limiting
- Error handling
- Logging
- Batch processing
- Model versioning
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import pickle
import json
import logging
import time
import hashlib
from datetime import datetime
from pathlib import Path
import asyncio
from functools import lru_cache
import redis
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
Path('logs').mkdir(exist_ok=True)

# Security
security = HTTPBearer()
API_KEYS = {
    "sk-production-123456789": {"role": "admin", "rate_limit": 1000},
    "sk-test-987654321": {"role": "test", "rate_limit": 100},
}

# Rate limiting storage (use Redis in production)
request_counts = {}

# Model storage
models = {}
model_metadata = {}


# ============== LIFESPAN MANAGEMENT ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("="*60)
    logger.info("STARTING PRODUCTION API")
    logger.info("="*60)
    
    # Load all models on startup
    load_models()
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down API...")
    models.clear()


app = FastAPI(
    title="AI Production API",
    description="Enterprise-grade ML API with authentication, monitoring, and batch processing",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== MODEL MANAGEMENT ==============

def load_models():
    """Load all available models"""
    global models, model_metadata
    
    model_files = list(Path('models').glob('*.pkl'))
    
    for model_file in model_files:
        try:
            with open(model_file, 'rb') as f:
                model = pickle.load(f)
            
            model_name = model_file.stem
            models[model_name] = model
            
            # Load metadata if exists
            meta_file = model_file.parent / 'model_metadata.json'
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    model_metadata[model_name] = json.load(f)
            
            logger.info(f"Loaded model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load {model_file}: {e}")
    
    logger.info(f"Total models loaded: {len(models)}")


@lru_cache(maxsize=128)
def get_model(model_name: str = "best_model_logistic_regression"):
    """Get cached model"""
    if model_name not in models:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    return models[model_name]


# ============== AUTHENTICATION & RATE LIMITING ==============

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token"""
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return API_KEYS[token]


def check_rate_limit(api_key: str, role_config: dict):
    """Simple rate limiting"""
    now = time.time()
    window = 60  # 1 minute window
    
    if api_key not in request_counts:
        request_counts[api_key] = []
    
    # Remove old requests
    request_counts[api_key] = [t for t in request_counts[api_key] if now - t < window]
    
    # Check limit
    if len(request_counts[api_key]) >= role_config['rate_limit']:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Limit: {role_config['rate_limit']} requests/minute"
        )
    
    request_counts[api_key].append(now)


# ============== REQUEST/RESPONSE MODELS ==============

class SinglePredictionRequest(BaseModel):
    features: Dict[str, Any] = Field(..., description="Feature values as dictionary")
    model_name: Optional[str] = "best_model_logistic_regression"
    request_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": {
                    "age": 35,
                    "gender": "Male",
                    "tenure_months": 24,
                    "monthly_charges": 65.5
                },
                "model_name": "best_model_logistic_regression"
            }
        }


class BatchPredictionRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(..., description="List of feature dictionaries")
    model_name: Optional[str] = "best_model_logistic_regression"
    
    class Config:
        json_schema_extra = {
            "example": {
                "records": [
                    {"age": 35, "gender": "Male", "tenure_months": 24},
                    {"age": 45, "gender": "Female", "tenure_months": 12}
                ]
            }
        }


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    confidence: str  # High, Medium, Low
    model_name: str
    model_version: str
    latency_ms: float
    timestamp: str
    request_id: Optional[str] = None


class BatchPredictionResponse(BaseModel):
    predictions: List[int]
    probabilities: List[float]
    model_name: str
    total_records: int
    latency_ms: float
    timestamp: str


class ModelInfo(BaseModel):
    name: str
    type: str
    version: str
    features: int
    accuracy: float
    last_trained: str
    status: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: int
    uptime_seconds: float
    version: str
    timestamp: str


# ============== PREDICTION FUNCTIONS ==============

def preprocess_features(features: Dict[str, Any], model) -> np.ndarray:
    """Preprocess features for model input"""
    # Convert dict to array in correct order
    # This is simplified - in production, use the same preprocessing as training
    
    expected_features = getattr(model, 'feature_names_in_', None)
    
    if expected_features is not None:
        # Ensure correct feature order
        values = [features.get(f, 0) for f in expected_features]
    else:
        values = list(features.values())
    
    # Handle categorical variables (simplified)
    processed = []
    for v in values:
        if isinstance(v, str):
            # Simple hash encoding for strings
            processed.append(hash(v) % 1000)
        else:
            processed.append(float(v) if v is not None else 0)
    
    return np.array(processed).reshape(1, -1)


def get_confidence_level(probability: float) -> str:
    """Get confidence level string"""
    if probability >= 0.8:
        return "High"
    elif probability >= 0.6:
        return "Medium"
    else:
        return "Low"


# ============== API ENDPOINTS ==============

@app.get("/", tags=["General"])
def root():
    """Root endpoint"""
    return {
        "name": "AI Production API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "models": "/models"
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if len(models) > 0 else "degraded",
        models_loaded=len(models),
        uptime_seconds=time.time() - start_time,
        version="2.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/models", tags=["Models"])
def list_models():
    """List all available models"""
    return {
        "models": [
            {
                "name": name,
                "metadata": model_metadata.get(name, {})
            }
            for name in models.keys()
        ]
    }


@app.get("/models/{model_name}", response_model=ModelInfo, tags=["Models"])
def get_model_info(model_name: str):
    """Get detailed model information"""
    if model_name not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models[model_name]
    meta = model_metadata.get(model_name, {})
    
    return ModelInfo(
        name=model_name,
        type=type(model).__name__,
        version="1.0.0",
        features=getattr(model, 'n_features_in_', len(getattr(model, 'feature_names_in_', []))),
        accuracy=meta.get('score', 0.0),
        last_trained=meta.get('created_at', 'unknown'),
        status="active"
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(
    request: SinglePredictionRequest,
    background_tasks: BackgroundTasks,
    role_config: dict = Depends(verify_token)
):
    """
    Make a single prediction.
    
    Requires authentication token in header:
    Authorization: Bearer YOUR_API_KEY
    """
    start = time.time()
    
    # Rate limiting
    check_rate_limit(request.model_name or "default", role_config)
    
    try:
        # Get model
        model = get_model(request.model_name)
        
        # Preprocess
        features_array = preprocess_features(request.features, model)
        
        # Predict
        prediction = int(model.predict(features_array)[0])
        probability = float(model.predict_proba(features_array)[0].max())
        
        latency = (time.time() - start) * 1000
        
        # Log prediction
        background_tasks.add_task(
            log_prediction,
            request.model_name,
            request.features,
            prediction,
            probability,
            latency
        )
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            confidence=get_confidence_level(probability),
            model_name=request.model_name,
            model_version="1.0.0",
            latency_ms=round(latency, 2),
            timestamp=datetime.now().isoformat(),
            request_id=request.request_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(
    request: BatchPredictionRequest,
    role_config: dict = Depends(verify_token)
):
    """
    Make batch predictions (up to 1000 records).
    
    Requires authentication token in header:
    Authorization: Bearer YOUR_API_KEY
    """
    start = time.time()
    
    # Rate limiting (batch counts as 1 request but check size)
    check_rate_limit(request.model_name or "default", role_config)
    
    if len(request.records) > 1000:
        raise HTTPException(status_code=400, detail="Maximum 1000 records per batch")
    
    try:
        model = get_model(request.model_name)
        
        predictions = []
        probabilities = []
        
        for record in request.records:
            features_array = preprocess_features(record, model)
            pred = int(model.predict(features_array)[0])
            prob = float(model.predict_proba(features_array)[0].max())
            
            predictions.append(pred)
            probabilities.append(prob)
        
        latency = (time.time() - start) * 1000
        
        return BatchPredictionResponse(
            predictions=predictions,
            probabilities=probabilities,
            model_name=request.model_name,
            total_records=len(request.records),
            latency_ms=round(latency, 2),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/file", tags=["Prediction"])
async def predict_file(
    file: UploadFile = File(...),
    model_name: str = "best_model_logistic_regression",
    role_config: dict = Depends(verify_token)
):
    """
    Upload CSV file for batch prediction.
    
    Returns CSV with predictions added as column.
    """
    check_rate_limit(f"file_{model_name}", role_config)
    
    try:
        # Read CSV
        df = pd.read_csv(file.file)
        
        model = get_model(model_name)
        
        # Predict for each row
        predictions = []
        probabilities = []
        
        for _, row in df.iterrows():
            features_array = preprocess_features(row.to_dict(), model)
            pred = int(model.predict(features_array)[0])
            prob = float(model.predict_proba(features_array)[0].max())
            
            predictions.append(pred)
            probabilities.append(prob)
        
        # Add predictions to dataframe
        df['prediction'] = predictions
        df['confidence'] = probabilities
        
        # Save to buffer
        from io import StringIO
        output = StringIO()
        df.to_csv(output, index=False)
        
        return {
            "filename": f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "content": output.getvalue(),
            "total_rows": len(df),
            "predictions_summary": {
                "class_0": predictions.count(0),
                "class_1": predictions.count(1)
            }
        }
    
    except Exception as e:
        logger.error(f"File prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== BACKGROUND TASKS ==============

def log_prediction(model_name, features, prediction, probability, latency):
    """Log prediction to file for monitoring"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "prediction": prediction,
        "probability": probability,
        "latency_ms": latency
    }
    
    with open('logs/predictions.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


# ============== STARTUP TIME ==============
start_time = time.time()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
