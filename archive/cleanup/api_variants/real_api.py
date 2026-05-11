#!/usr/bin/env python
"""
Real API - Production API dengan data dan prediksi REAL
Menggunakan model yang sudah dilatih dan dataset real
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from self_evolving.real_predictor import RealPredictor
from self_evolving.data_collector import DataCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class PredictRequest(BaseModel):
    model_id: str = Field(..., description="Model ID untuk prediksi")
    input_data: Dict = Field(..., description="Feature values untuk prediksi")
    dataset: Optional[str] = Field(None, description="Dataset referensi (churn/fraud/sales/credit)")
    session_id: Optional[str] = None

class PredictResponse(BaseModel):
    prediction: int
    prediction_label: str
    confidence: float
    confidence_pct: str
    model_used: str
    feature_importance: Optional[Dict]
    interaction_id: Optional[int]
    timestamp: str

class DatasetInfo(BaseModel):
    name: str
    rows: int
    columns: int
    sample: Dict

class FeedbackRequest(BaseModel):
    interaction_id: int
    feedback: int = Field(..., ge=0, le=1, description="1=correct, 0=incorrect")
    true_label: Optional[int] = Field(None, description="Ground truth jika diketahui")
    reason: Optional[str] = None

# Global instances
predictor: Optional[RealPredictor] = None
collector: Optional[DataCollector] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    global predictor, collector
    
    logger.info("[INIT] Loading Real API...")
    
    # Initialize predictor dengan data real
    predictor = RealPredictor()
    
    # Initialize data collector
    collector = DataCollector()
    
    logger.info("[OK] Real API ready with REAL data and models!")
    yield
    
    # Cleanup
    if collector:
        collector.close()
    logger.info("[OK] Real API shutdown")

app = FastAPI(
    title="Real AI Prediction API",
    description="API dengan prediksi REAL menggunakan data dan model nyata",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "app": "Real AI Prediction API",
        "version": "2.0.0",
        "features": ["real_predictions", "feedback_loop", "model_comparison"],
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check dengan info real"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(predictor.models) if predictor else 0,
        "datasets_loaded": len(predictor.datasets) if predictor else 0,
        "total_interactions": collector.get_feedback_stats().get('total_feedback', 0) if collector else 0
    }

@app.get("/models")
async def list_models():
    """List semua model yang tersedia"""
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    models = []
    for model_id in predictor.get_available_models():
        info = predictor.get_model_performance(model_id)
        models.append(info)
    
    return {
        "models": models,
        "total": len(models)
    }

@app.get("/datasets")
async def list_datasets():
    """List semua dataset yang tersedia"""
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    datasets = []
    for name, df in predictor.datasets.items():
        sample = predictor.get_sample_input(name)
        datasets.append({
            "name": name,
            "rows": len(df),
            "columns": len(df.columns),
            "sample": sample
        })
    
    return {"datasets": datasets}

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Prediksi REAL dengan model yang sudah dilatih
    
    Contoh input:
    {
        "model_id": "best_model_logistic_regression",
        "input_data": {"age": 35, "income": 50000, "tenure": 24},
        "dataset": "customer_churn"
    }
    """
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    # Jika input_data kosong, gunakan sample dari dataset
    input_data = request.input_data
    if not input_data and request.dataset:
        input_data = predictor.get_sample_input(request.dataset)
    
    # Prediksi
    result = predictor.predict(request.model_id, input_data)
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    # Log interaction
    if collector:
        interaction_id = collector.log_interaction(
            user_input=json.dumps(input_data),
            ai_response=json.dumps({
                'prediction': result['prediction'],
                'confidence': result['confidence']
            }),
            model_used=request.model_id,
            session_id=request.session_id,
            confidence=result['confidence'],
            metadata={
                'dataset': request.dataset,
                'input_features': result.get('input_features', [])
            }
        )
        result['interaction_id'] = interaction_id
    
    return result

@app.post("/predict/batch")
async def predict_batch(requests: List[PredictRequest]):
    """Batch prediction untuk multiple inputs"""
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    results = []
    for req in requests:
        result = predictor.predict(req.model_id, req.input_data)
        results.append(result)
    
    return {"predictions": results, "count": len(results)}

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback untuk prediksi sebelumnya
    
    Feedback ini akan digunakan untuk:
    1. Menghitung accuracy model
    2. Trigger retraining jika performance turun
    3. Improve model di iterasi berikutnya
    """
    if not collector:
        raise HTTPException(status_code=503, detail="Data collector not initialized")
    
    # Update feedback
    collector.update_feedback(
        interaction_id=request.interaction_id,
        feedback=request.feedback,
        reason=request.reason
    )
    
    # Jika ada true_label, log ke metric
    if request.true_label is not None:
        # Bisa digunakan untuk calculate accuracy
        pass
    
    return {
        "status": "success",
        "interaction_id": request.interaction_id,
        "feedback": request.feedback,
        "message": "Feedback recorded for model improvement"
    }

@app.get("/compare/{model_id1}/{model_id2}")
async def compare_models(model_id1: str, model_id2: str):
    """Bandingkan performa 2 model berdasarkan feedback"""
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    perf1 = predictor.get_model_performance(model_id1)
    perf2 = predictor.get_model_performance(model_id2)
    
    return {
        "model_1": perf1,
        "model_2": perf2,
        "comparison": {
            "better_model": model_id1 if perf1.get('satisfaction_rate', 0) > perf2.get('satisfaction_rate', 0) else model_id2,
            "satisfaction_diff": abs(perf1.get('satisfaction_rate', 0) - perf2.get('satisfaction_rate', 0))
        }
    }

@app.get("/stats")
async def get_stats():
    """Get comprehensive stats"""
    if not predictor or not collector:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    # Model stats
    model_stats = []
    for model_id in predictor.get_available_models():
        perf = predictor.get_model_performance(model_id)
        model_stats.append(perf)
    
    # Feedback stats
    feedback_stats = collector.get_feedback_stats(hours=24*7)  # Last 7 days
    
    # Dataset stats
    dataset_stats = []
    for name, df in predictor.datasets.items():
        dataset_stats.append({
            'name': name,
            'rows': len(df),
            'columns': len(df.columns)
        })
    
    return {
        "models": model_stats,
        "feedback": feedback_stats,
        "datasets": dataset_stats,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("="*60)
    print("REAL AI PREDICTION API")
    print("="*60)
    print("Server: http://localhost:8000")
    print("Docs:   http://localhost:8000/docs")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
