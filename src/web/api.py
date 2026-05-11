"""KUERA AI — Canonical FastAPI (v3.0)

Unified ML API combining the best of:
- real_api_v2.py (robust .pkl loading, predict, feedback)
- production_api.py (batch prediction, health, model metadata)

Entry: python src/web/api.py (port 8000)
"""

import json
import logging
import pickle
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent.parent.parent.resolve()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage
MODELS = {}
MODEL_META = {}
SAMPLES = {}
START_TIME = time.time()


# ─── MODEL LOADING ─────────────────────────────────────────────────────

def load_models():
    """Load all .pkl models from models/."""
    models_dir = BASE_DIR / "models"
    if not models_dir.exists():
        logger.warning("models/ directory not found")
        return
    for pkl_file in models_dir.glob("*.pkl"):
        try:
            with open(pkl_file, "rb") as f:
                model = pickle.load(f)
            model_id = pkl_file.stem
            MODELS[model_id] = model
            # Metadata
            meta_file = pkl_file.parent / "model_metadata.json"
            if meta_file.exists():
                MODEL_META[model_id] = json.loads(meta_file.read_text())
            logger.info("[OK] Loaded model: %s", model_id)
        except Exception as e:
            logger.warning("[WARN] Failed to load %s: %s", pkl_file, e)


def load_samples():
    """Load sample inputs from data/processed/."""
    processed = BASE_DIR / "data" / "processed"
    candidates = ["X_train.csv", "train_processed.csv"]
    for cand in candidates:
        path = processed / cand
        if path.exists():
            try:
                df = pd.read_csv(path)
                if "target" in df.columns:
                    feature_cols = [c for c in df.columns if c != "target"]
                else:
                    feature_cols = list(df.columns)
                sample = df[feature_cols].iloc[0].to_dict()
                SAMPLES["default"] = sample
                logger.info("[OK] Loaded sample with %d features from %s", len(feature_cols), cand)
                return
            except Exception as e:
                logger.warning("[WARN] Failed to load sample: %s", e)


# ─── LIFESPAN ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    load_samples()
    logger.info("[OK] KUERA API v3.0 ready — %d models loaded", len(MODELS))
    yield
    logger.info("[BYE] Shutting down KUERA API")


app = FastAPI(
    title="KUERA AI API",
    description="Canonical ML API for KUERA — predictions, batch processing, audit workflow",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── PYDANTIC MODELS ───────────────────────────────────────────────────

class PredictRequest(BaseModel):
    model_id: str = "best_model_logistic_regression"
    input_data: Optional[Dict] = None
    session_id: Optional[str] = None


class PredictResponse(BaseModel):
    prediction: int
    confidence: float
    model_used: str
    timestamp: str


class BatchPredictRequest(BaseModel):
    model_id: str = "best_model_logistic_regression"
    inputs: List[Dict]


class BatchPredictResponse(BaseModel):
    predictions: List[int]
    confidences: List[float]
    model_used: str
    count: int
    timestamp: str


class FeedbackRequest(BaseModel):
    interaction_id: int
    feedback: int = Field(..., ge=-1, le=1, description="-1=bad, 0=neutral, 1=good")
    reason: Optional[str] = None


# ─── ML ENDPOINTS ──────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "app": "KUERA AI API",
        "version": "3.0.0",
        "models_loaded": len(MODELS),
        "models": list(MODELS.keys()),
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "models_loaded": len(MODELS),
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/models")
async def list_models():
    result = []
    for name in MODELS:
        meta = MODEL_META.get(name, {})
        result.append({
            "name": name,
            "type": meta.get("model_type", "unknown"),
            "framework": meta.get("framework", "sklearn"),
        })
    return {"models": result}


@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    if model_name not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    return {
        "name": model_name,
        "metadata": MODEL_META.get(model_name, {}),
    }


@app.get("/sample")
async def get_sample():
    if "default" in SAMPLES:
        return SAMPLES["default"]
    raise HTTPException(status_code=404, detail="No sample available")


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if request.model_id not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model '{request.model_id}' not found")

    model = MODELS[request.model_id]
    input_data = request.input_data or SAMPLES.get("default")

    if not input_data:
        raise HTTPException(status_code=400, detail="No input data and no sample available")

    try:
        df = pd.DataFrame([input_data]).fillna(0)
        prediction = int(model.predict(df)[0])
        confidence = 0.5
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(df)[0]
            confidence = float(np.max(proba))
        return PredictResponse(
            prediction=prediction,
            confidence=confidence,
            model_used=request.model_id,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", response_model=BatchPredictResponse)
async def predict_batch(request: BatchPredictRequest):
    if not request.inputs:
        raise HTTPException(status_code=400, detail="No input data provided")

    if request.model_id not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model '{request.model_id}' not found")

    model = MODELS[request.model_id]

    try:
        df = pd.DataFrame(request.inputs).fillna(0)
        predictions = [int(p) for p in model.predict(df)]
        confidences = []
        if hasattr(model, "predict_proba"):
            for proba in model.predict_proba(df):
                confidences.append(float(np.max(proba)))
        else:
            confidences = [0.5] * len(predictions)

        return BatchPredictResponse(
            predictions=predictions,
            confidences=confidences,
            model_used=request.model_id,
            count=len(predictions),
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/file")
async def predict_file(file: UploadFile, model_id: str = "best_model_logistic_regression"):
    """Upload CSV/Excel and get batch predictions."""
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

    model = MODELS[model_id]
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(status_code=400, detail="Only .csv and .xlsx supported")

        df = df.fillna(0)
        predictions = [int(p) for p in model.predict(df)]
        return {
            "model_used": model_id,
            "predictions": predictions,
            "count": len(predictions),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    """Submit feedback for an interaction."""
    # In v3, feedback is logged to memory/ via logger_engine if available
    try:
        from src.core.logger_engine import log_activity
        log_activity(
            f"Feedback received: interaction={request.interaction_id}, rating={request.feedback}",
            {"reason": request.reason or "N/A"},
        )
    except Exception:
        pass
    return {"status": "success", "interaction_id": request.interaction_id}


# ─── AUDIT WORKFLOW ENDPOINTS ──────────────────────────────────────────

@app.get("/api/audit/templates")
async def audit_templates():
    from src.data.audit_workflow import list_templates
    return {"templates": list_templates()}


@app.post("/api/audit/analyze")
async def audit_analyze(data: Dict):
    from src.data.audit_connector import analyze_excel
    filepath = data.get("filepath", "")
    if not filepath:
        raise HTTPException(status_code=400, detail="filepath required")
    result = analyze_excel(filepath)
    return result


@app.post("/api/audit/run")
async def audit_run(data: Dict):
    from src.data.audit_connector import run_audit
    jenis = data.get("jenis", "").lower()
    filename = data.get("filename", "")
    if not jenis or not filename:
        raise HTTPException(status_code=400, detail="jenis and filename required")
    if jenis not in ("keuangan", "spi", "kinerja"):
        raise HTTPException(status_code=400, detail=f"Invalid jenis: {jenis}")
    upload_dir = BASE_DIR / "data" / "uploads"
    filepath = str(upload_dir / filename)
    kwargs = {}
    if jenis == "spi":
        kwargs["nama_entitas"] = data.get("nama_entitas", "Entitas Audit")
    elif jenis == "kinerja":
        kwargs["tahun"] = int(data.get("tahun", 2024))
    result = run_audit(jenis, filepath, **kwargs)
    return result


@app.post("/api/audit/chart")
async def audit_chart(data: Dict):
    from src.data.audit_workflow import generate_chart_data, AuditResult
    jenis = data.get("jenis", "").lower()
    summary = data.get("summary", {})
    if not jenis or not summary:
        raise HTTPException(status_code=400, detail="jenis and summary required")
    try:
        result = AuditResult(jenis=jenis, status="success", file_input="", file_output=None, summary=summary)
        charts = generate_chart_data(result)
        return {"status": "success", "charts": charts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── FORSA BUMDes ENDPOINTS ────────────────────────────────────────────

@app.get("/api/audit/forsa/status")
async def forsa_status():
    from src.data.forsa_connector import get_forsa_status
    return get_forsa_status()


@app.post("/api/audit/forsa/run")
async def forsa_run(data: Dict):
    from src.data.forsa_connector import run_forsa_audit
    mode = str(data.get("mode", "2"))
    result = run_forsa_audit(mode=mode)
    return result


@app.get("/api/audit/forsa/files")
async def forsa_files():
    from src.data.forsa_connector import ForsaBridge
    bridge = ForsaBridge()
    files = bridge.list_output_files()
    return {"files": files}


# ─── MAIN ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("KUERA AI API v3.0")
    print("=" * 60)
    uvicorn.run("src.web.api:app", host="0.0.0.0", port=8000, reload=False)
