#!/usr/bin/env python
"""
SelfEvolvingApp - Aplikasi AI yang dapat berkembang mandiri
Integrasi FastAPI dengan komponen self-improvement
"""

import os
import sys
import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Import self-evolving components
from .data_collector import DataCollector
from .evaluator import Evaluator
from .retrainer import AutoRetrain, RetrainConfig

# Optional Ollama integration
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama not available, using fallback mode")

logger = logging.getLogger(__name__)

# ============================================================================
# Pydantic Models
# ============================================================================

class QueryRequest(BaseModel):
    query: str = Field(..., description="User query/input")
    session_id: Optional[str] = None
    metadata: Optional[Dict] = None

class QueryResponse(BaseModel):
    response: str
    model_used: str
    confidence: float
    latency_ms: float
    interaction_id: int
    timestamp: str

class FeedbackRequest(BaseModel):
    interaction_id: int
    feedback: int = Field(..., ge=0, le=1, description="1=good, 0=bad")
    reason: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    interaction_id: int

class RetrainRequest(BaseModel):
    force: bool = False
    model_type: str = "auto"

class StatusResponse(BaseModel):
    status: str
    timestamp: str
    production_model: Optional[str]
    total_interactions: int
    feedback_stats: Dict


# ============================================================================
# SelfEvolvingApp Class
# ============================================================================

class SelfEvolvingApp:
    """
    Aplikasi AI dengan kemampuan self-improvement
    """
    
    def __init__(
        self,
        db_path: str = "logs/feedback/self_improve.db",
        models_dir: str = "models",
        use_ollama: bool = False,
        ollama_model: str = "llama3.2:1b"
    ):
        self.db_path = db_path
        self.models_dir = models_dir
        self.use_ollama = use_ollama and OLLAMA_AVAILABLE
        self.ollama_model = ollama_model
        
        # Initialize components
        self.collector: Optional[DataCollector] = None
        self.evaluator: Optional[Evaluator] = None
        self.retrainer: Optional[AutoRetrain] = None
        
        # Model cache
        self.current_model = None
        self.current_model_id = None
        
        logger.info("[OK] SelfEvolvingApp initialized")
    
    def initialize(self):
        """Initialize all components"""
        logger.info("[INIT] Initializing components...")
        
        # Data Collector
        self.collector = DataCollector(self.db_path)
        
        # Evaluator (jika ada reference data)
        ref_data = "data/processed/train_processed.csv"
        if os.path.exists(ref_data):
            self.evaluator = Evaluator(ref_data, self.db_path)
        
        # Retrainer
        config = RetrainConfig(min_samples=50, check_interval_hours=24)
        self.retrainer = AutoRetrain(config, self.db_path, self.models_dir)
        
        # Load current production model
        self._load_production_model()
        
        logger.info("[OK] All components initialized")
    
    def _load_production_model(self):
        """Load model yang sedang di production"""
        if self.retrainer:
            prod = self.retrainer.get_production_model()
            if prod:
                import pickle
                with open(prod['model_path'], 'rb') as f:
                    self.current_model = pickle.load(f)
                self.current_model_id = prod['model_id']
                logger.info(f"[OK] Loaded production model: {prod['model_id']}")
    
    def process_query(self, query: str, session_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict:
        """
        Process user query dan log interaction
        
        Returns:
            Dictionary dengan response dan metadata
        """
        start_time = time.time()
        
        # Generate response
        if self.use_ollama and OLLAMA_AVAILABLE:
            try:
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=[{'role': 'user', 'content': query}]
                )
                ai_response = response['message']['content']
                confidence = 0.85  # Placeholder
            except Exception as e:
                logger.error(f"Ollama error: {e}, using fallback")
                ai_response = self._fallback_response(query)
                confidence = 0.5
        else:
            ai_response = self._fallback_response(query)
            confidence = 0.5
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Log interaction
        interaction_id = self.collector.log_interaction(
            user_input=query,
            ai_response=ai_response,
            model_used=self.ollama_model if self.use_ollama else self.current_model_id or "fallback",
            session_id=session_id,
            latency_ms=latency_ms,
            confidence=confidence,
            metadata=metadata
        )
        
        return {
            'response': ai_response,
            'model_used': self.ollama_model if self.use_ollama else self.current_model_id or "fallback",
            'confidence': confidence,
            'latency_ms': latency_ms,
            'interaction_id': interaction_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def _fallback_response(self, query: str) -> str:
        """Fallback response jika AI tidak tersedia"""
        responses = {
            'halo': 'Halo! Saya adalah AI yang sedang belajar.',
            'help': 'Saya dapat membantu dengan pertanyaan umum. Feedback Anda membantu saya berkembang!',
        }
        
        query_lower = query.lower()
        for key, resp in responses.items():
            if key in query_lower:
                return resp
        
        return f"Terima kasih atas pertanyaan: '{query[:50]}...'. Saya sedang mempelajari ini. Mohon berikan feedback!"
    
    def update_feedback(self, interaction_id: int, feedback: int, reason: Optional[str] = None):
        """Update feedback untuk interaction"""
        self.collector.update_feedback(interaction_id, feedback, reason)
    
    def get_status(self) -> Dict:
        """Get current app status"""
        stats = self.collector.get_feedback_stats(hours=24)
        
        # Count total interactions
        conn = self.collector.conn
        cursor = conn.execute("SELECT COUNT(*) FROM interactions")
        total = cursor.fetchone()[0]
        
        return {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'production_model': self.current_model_id,
            'total_interactions': total,
            'feedback_stats': stats
        }
    
    def trigger_retrain(self, force: bool = False) -> Optional[Dict]:
        """Manual trigger retraining"""
        if not self.retrainer:
            return None
        
        return self.retrainer.check_and_trigger_retrain(force=force)
    
    def shutdown(self):
        """Cleanup saat shutdown"""
        if self.collector:
            self.collector.close()
        logger.info("[OK] SelfEvolvingApp shutdown")


# ============================================================================
# FastAPI Application
# ============================================================================

# Global app instance
self_evolving_app: Optional[SelfEvolvingApp] = None

# Security
security = HTTPBearer(auto_error=False)


def create_app() -> FastAPI:
    """Factory function untuk create FastAPI app"""
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan context manager"""
        # Startup
        global self_evolving_app
        self_evolving_app = SelfEvolvingApp(use_ollama=False)
        self_evolving_app.initialize()
        logger.info("[OK] Self-Evolving AI App started!")
        yield
        # Shutdown
        if self_evolving_app:
            self_evolving_app.shutdown()
    
    app = FastAPI(
        title="Self-Evolving AI App",
        description="AI Application dengan kemampuan self-improvement otomatis",
        version="2.0.0",
        lifespan=lifespan
    )
    
    @app.get("/")
    async def root():
        return {
            "app": "Self-Evolving AI",
            "version": "2.0.0",
            "status": "running",
            "docs": "/docs"
        }
    
    @app.get("/health", response_model=StatusResponse)
    async def health():
        """Health check dengan status lengkap"""
        if not self_evolving_app:
            raise HTTPException(status_code=503, detail="App not initialized")
        return self_evolving_app.get_status()
    
    @app.post("/chat", response_model=QueryResponse)
    async def chat(request: QueryRequest):
        """
        Chat dengan AI dan log interaction untuk improvement
        """
        if not self_evolving_app:
            raise HTTPException(status_code=503, detail="App not initialized")
        
        result = self_evolving_app.process_query(
            query=request.query,
            session_id=request.session_id,
            metadata=request.metadata
        )
        return result
    
    @app.post("/feedback", response_model=FeedbackResponse)
    async def feedback(request: FeedbackRequest):
        """
        Berikan feedback untuk interaction sebelumnya
        """
        if not self_evolving_app:
            raise HTTPException(status_code=503, detail="App not initialized")
        
        self_evolving_app.update_feedback(
            request.interaction_id,
            request.feedback,
            request.reason
        )
        
        return {
            'status': 'success',
            'interaction_id': request.interaction_id
        }
    
    @app.post("/admin/retrain")
    async def admin_retrain(request: RetrainRequest):
        """
        Trigger manual retraining (admin only)
        """
        if not self_evolving_app:
            raise HTTPException(status_code=503, detail="App not initialized")
        
        result = self_evolving_app.trigger_retrain(force=request.force)
        
        if result:
            return {
                'status': 'success',
                'result': result
            }
        else:
            return {
                'status': 'skipped',
                'message': 'Not enough data or retrain not triggered'
            }
    
    @app.get("/admin/stats")
    async def admin_stats():
        """Get detailed statistics"""
        if not self_evolving_app:
            raise HTTPException(status_code=503, detail="App not initialized")
        
        # Recent interactions
        recent = self_evolving_app.collector.get_recent_interactions(hours=24)
        
        # Model registry
        registry = self_evolving_app.retrainer.model_registry if self_evolving_app.retrainer else {}
        
        return {
            'interactions_24h': len(recent),
            'feedback_stats': self_evolving_app.collector.get_feedback_stats(hours=24),
            'model_registry': registry,
            'production_model': self_evolving_app.current_model_id
        }
    
    return app


# Create FastAPI app
app = create_app()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*60)
    print("SELF-EVOLVING AI APP")
    print("="*60)
    print("Server: http://localhost:8000")
    print("Docs:   http://localhost:8000/docs")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
