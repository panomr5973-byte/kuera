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
from fastapi import FastAPI, File, HTTPException, UploadFile, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent.parent.parent.resolve()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage
MODELS = {}
MODEL_PATHS = {}
MODEL_META = {}
SAMPLES = {}
START_TIME = time.time()


def _lazy_load_model(model_id: str):
    """Load a single .pkl model on first use."""
    if model_id in MODELS:
        return MODELS[model_id]
    path = MODEL_PATHS.get(model_id)
    if not path or not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            model = pickle.load(f)
        MODELS[model_id] = model
        # Metadata
        meta_file = path.parent / "model_metadata.json"
        if meta_file.exists():
            MODEL_META[model_id] = json.loads(meta_file.read_text())
        logger.info("[OK] Lazy-loaded model: %s", model_id)
        return model
    except Exception as e:
        logger.warning("[WARN] Failed to lazy-load %s: %s", path, e)
        return None


# ─── MODEL LOADING ─────────────────────────────────────────────────────

def load_models():
    """Scan model filenames at startup; defer actual pickle.load until first use."""
    models_dir = BASE_DIR / "models"
    if not models_dir.exists():
        logger.warning("models/ directory not found")
        return
    for pkl_file in models_dir.glob("*.pkl"):
        model_id = pkl_file.stem
        MODEL_PATHS[model_id] = pkl_file
        logger.info("[OK] Registered model: %s", model_id)


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
        "models_loaded": len(MODEL_PATHS),
        "models": list(MODEL_PATHS.keys()),
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
    for name in MODEL_PATHS:
        meta = MODEL_META.get(name, {})
        result.append({
            "name": name,
            "type": meta.get("model_type", "unknown"),
            "framework": meta.get("framework", "sklearn"),
            "loaded": name in MODELS,
        })
    return {"models": result}


@app.get("/models/{model_name}")
async def get_model_info(model_name: str):
    if model_name not in MODEL_PATHS:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    # Lazy-load metadata if not already loaded
    _lazy_load_model(model_name)
    return {
        "name": model_name,
        "metadata": MODEL_META.get(model_name, {}),
        "loaded": model_name in MODELS,
    }


@app.get("/sample")
async def get_sample():
    if "default" in SAMPLES:
        return SAMPLES["default"]
    raise HTTPException(status_code=404, detail="No sample available")


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if request.model_id not in MODEL_PATHS:
        raise HTTPException(status_code=404, detail=f"Model '{request.model_id}' not found")

    model = _lazy_load_model(request.model_id)
    if model is None:
        raise HTTPException(status_code=500, detail=f"Failed to load model '{request.model_id}'")
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

    if request.model_id not in MODEL_PATHS:
        raise HTTPException(status_code=404, detail=f"Model '{request.model_id}' not found")

    model = _lazy_load_model(request.model_id)
    if model is None:
        raise HTTPException(status_code=500, detail=f"Failed to load model '{request.model_id}'")

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
    if model_id not in MODEL_PATHS:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

    model = _lazy_load_model(model_id)
    if model is None:
        raise HTTPException(status_code=500, detail=f"Failed to load model '{model_id}'")
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


# ─── AUDIT TRAIL ENDPOINTS ─────────────────────────────────────────────

@app.get("/api/audit/history")
async def audit_history(
    jenis: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    from src.core.audit_trail import get_history
    runs = get_history(jenis=jenis, limit=limit, offset=offset)
    return {"status": "success", "count": len(runs), "runs": runs}


@app.get("/api/audit/history/{run_id}")
async def audit_history_detail(run_id: int):
    from src.core.audit_trail import get_run_by_id
    run = get_run_by_id(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Audit run {run_id} not found")
    return {"status": "success", "run": run}


@app.post("/api/audit/export/pdf")
async def audit_export_pdf(data: Dict):
    """Generate PDF report from an audit result summary.
    
    Currently supports keuangan audits. SPI and kinerja will return
    a placeholder PDF or error.
    """
    jenis = data.get("jenis", "").lower()
    summary = data.get("summary", {})
    filename = data.get("filename", "audit_result")
    if not jenis or not summary:
        raise HTTPException(status_code=400, detail="jenis and summary required")
    if jenis != "keuangan":
        raise HTTPException(status_code=501, detail=f"PDF export for '{jenis}' not yet implemented")
    
    try:
        from audit_toolkit import PDFReport
        import pandas as pd
        import tempfile
        
        # Reconstruct a minimal DataFrame from summary for PDF generation
        rows = summary.get("total_bumd", 10)
        df = pd.DataFrame({"placeholder": range(rows)})
        
        # Add ROA columns if available in summary
        if "roa_rendah" in summary:
            df["ROA"] = [5.0] * rows  # placeholder
        
        output_dir = BASE_DIR / "data" / "uploads"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"laporan_audit_{filename}.pdf"
        
        report = PDFReport(title=f"Laporan Audit Keuangan — {filename}")
        report.generate(df, str(output_file))
        
        return {
            "status": "success",
            "output_path": str(output_file),
            "download_url": f"/api/audit/download?file={output_file.name}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/audit/batch")
async def audit_batch(data: Dict):
    """Run audit on multiple files sequentially."""
    jenis = data.get("jenis", "").lower()
    filenames = data.get("filenames", [])
    if not jenis or not filenames:
        raise HTTPException(status_code=400, detail="jenis and filenames required")
    if jenis not in ("keuangan", "spi", "kinerja"):
        raise HTTPException(status_code=400, detail=f"Invalid jenis: {jenis}")
    from src.data.audit_workflow import run_batch_audit
    kwargs = {}
    if jenis == "spi":
        kwargs["nama_entitas"] = data.get("nama_entitas", "Entitas Audit")
    elif jenis == "kinerja":
        kwargs["tahun"] = int(data.get("tahun", 2024))
    result = run_batch_audit(jenis, filenames, **kwargs)
    return result


@app.post("/api/audit/upload")
async def audit_upload(file: UploadFile):
    """Upload Excel file for audit analysis."""
    upload_dir = BASE_DIR / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx and .xls files allowed")
    save_path = upload_dir / file.filename
    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)
    # Auto-analyze
    from src.data.audit_connector import analyze_excel
    analysis = analyze_excel(str(save_path))
    return {
        "status": "success",
        "filename": file.filename,
        "saved_to": str(save_path),
        "analysis": analysis,
    }


@app.get("/api/audit/download")
async def audit_download(file: str = Query(...)):
    """Download an audit output file (PDF or Excel) by filename."""
    uploads_dir = BASE_DIR / "data" / "uploads"
    file_path = uploads_dir / file
    # Security: prevent directory traversal
    try:
        file_path.resolve().relative_to(uploads_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid file path")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )


# ─── MAIN ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("KUERA AI API v3.0")
    print("=" * 60)
    uvicorn.run("src.web.api:app", host="0.0.0.0", port=8000, reload=False)
