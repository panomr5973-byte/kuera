"""
Mirofish AI - Main Application
Smart Aquaculture System - Minimal Version
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import get_settings
from app.models.database import init_db
from app.api import farms, ponds, sensors, readings, alerts, dashboard, simulation


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Start simulation if enabled
    if settings.simulation_enabled:
        print("🎮 Sensor simulation enabled")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Smart Aquaculture System - Minimal Resource Version",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(farms.router, prefix="/api/v1/farms", tags=["Farms"])
app.include_router(ponds.router, prefix="/api/v1/ponds", tags=["Ponds"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["Sensors"])
app.include_router(readings.router, prefix="/api/v1/readings", tags=["Readings"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "database": "connected",
            "simulation": "enabled" if settings.simulation_enabled else "disabled"
        }
    }


@app.get("/api/v1/status")
async def system_status():
    """Get detailed system status."""
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug
        },
        "features": {
            "simulation": settings.simulation_enabled,
            "mqtt": settings.mqtt_broker_host is not None,
            "weather_api": settings.weather_api_key is not None,
            "ai_kuera_integration": settings.kuera_integration_enabled
        },
        "thresholds": {
            "ph": {"min": settings.ph_min, "max": settings.ph_max},
            "dissolved_o2": {"min": settings.do_min},
            "temperature": {"min": settings.temp_min, "max": settings.temp_max},
            "ammonia": {"max": settings.ammonia_max}
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else 2
    )
