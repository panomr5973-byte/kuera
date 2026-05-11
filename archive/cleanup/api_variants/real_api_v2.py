#!/usr/bin/env python
"""
Real API v2 - Fixed untuk compatibility
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import pickle
import sqlite3
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load models
MODELS = {}

def load_models():
    """Load all available models"""
    models_dir = Path("models")
    if not models_dir.exists():
        return
    
    for pkl_file in models_dir.glob("*.pkl"):
        try:
            with open(pkl_file, 'rb') as f:
                model = pickle.load(f)
            model_id = pkl_file.stem
            MODELS[model_id] = model
            logger.info(f"[OK] Loaded model: {model_id}")
        except Exception as e:
            logger.warning(f"[WARN] Failed to load {pkl_file}: {e}")

# Load sample data
SAMPLES = {}

def load_samples():
    """Load sample inputs dari processed data"""
    processed_dir = Path("data/processed")
    
    # Try X_train.csv
    if (processed_dir / "X_train.csv").exists():
        df = pd.read_csv(processed_dir / "X_train.csv")
        sample = df.iloc[0].to_dict()
        SAMPLES['default'] = sample
        logger.info(f"[OK] Loaded sample with {len(df.columns)} features from X_train")
        return
    
    if (processed_dir / "train_processed.csv").exists():
        df = pd.read_csv(processed_dir / "train_processed.csv")
        target_cols = ['target', 'label', 'y', 'class']
        feature_cols = [c for c in df.columns if c not in target_cols]
        sample = df[feature_cols].iloc[0].to_dict()
        SAMPLES['default'] = sample
        logger.info(f"[OK] Loaded sample with {len(feature_cols)} features")

# Pydantic Models
class PredictRequest(BaseModel):
    model_id: str
    input_data: Optional[Dict] = None
    session_id: Optional[str] = None

class PredictResponse(BaseModel):
    prediction: int
    confidence: float
    model_used: str
    timestamp: str

class FeedbackRequest(BaseModel):
    interaction_id: int
    feedback: int
    reason: Optional[str] = None

# Initialize
collector = None

def init_collector():
    """Initialize data collector"""
    global collector
    try:
        from self_evolving.data_collector import DataCollector
        collector = DataCollector()
        logger.info("[OK] Data collector initialized")
    except Exception as e:
        logger.warning(f"[WARN] Data collector failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan"""
    load_models()
    load_samples()
    init_collector()
    logger.info("[OK] Real API v2 ready!")
    yield
    if collector:
        collector.close()

app = FastAPI(
    title="Real AI API v2",
    version="2.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "app": "Real AI API v2",
        "models": list(MODELS.keys()),
        "samples_available": list(SAMPLES.keys())
    }

@app.get("/health")
async def health():
    return {
        "status": "running",
        "models": len(MODELS),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models")
async def list_models():
    return {"models": list(MODELS.keys())}

@app.get("/sample")
async def get_sample():
    """Get sample input data"""
    if 'default' in SAMPLES:
        return SAMPLES['default']
    return {"error": "No sample available"}

@app.post("/predict")
async def predict(request: PredictRequest):
    """Predict dengan model real"""
    if request.model_id not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model {request.model_id} not found")
    
    model = MODELS[request.model_id]
    
    # Use provided data atau sample
    input_data = request.input_data or SAMPLES.get('default', {})
    
    if not input_data:
        raise HTTPException(status_code=400, detail="No input data and no sample available")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame([input_data])
        df = df.fillna(0)
        
        # Predict
        prediction = int(model.predict(df)[0])
        
        # Confidence
        confidence = 0.5
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(df)[0]
            confidence = float(np.max(proba))
        
        # Log interaction
        interaction_id = None
        if collector:
            try:
                interaction_id = collector.log_interaction(
                    user_input=json.dumps(input_data),
                    ai_response=json.dumps({'prediction': prediction, 'confidence': confidence}),
                    model_used=request.model_id,
                    session_id=request.session_id,
                    confidence=confidence
                )
            except Exception as e:
                logger.warning(f"[WARN] Failed to log: {e}")
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'model_used': request.model_id,
            'interaction_id': interaction_id,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    """Submit feedback"""
    if not collector:
        raise HTTPException(status_code=503, detail="Collector not available")
    
    try:
        collector.update_feedback(request.interaction_id, request.feedback, request.reason)
        return {'status': 'success', 'interaction_id': request.interaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("="*60)
    print("REAL AI API v2")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8001)
