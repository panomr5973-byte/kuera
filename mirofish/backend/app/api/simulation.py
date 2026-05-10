"""
Mirofish AI - Simulation API
Control sensor simulation
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import Pond, get_db
from app.services.sensor_simulator import (
    simulator_manager, SensorSimulator, SimulationMode
)

router = APIRouter()


class SimulationConfig(BaseModel):
    mode: str = "normal"  # normal, critical, fluctuating, drifting
    interval_seconds: int = 10


class SimulationResponse(BaseModel):
    pond_id: str
    status: str
    mode: str
    latest_readings: dict


@router.post("/start/{pond_id}")
def start_simulation(
    pond_id: str,
    config: SimulationConfig,
    db: Session = Depends(get_db)
):
    """Start simulation for a pond."""
    # Verify pond exists
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Create or get simulator
    simulator = simulator_manager.get_simulator(pond_id)
    if not simulator:
        simulator = simulator_manager.create_simulator(pond_id, pond.name)
    
    # Set mode
    try:
        mode = SimulationMode(config.mode)
        simulator.simulator.set_mode(mode)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {config.mode}")
    
    # Start simulation (in background)
    import asyncio
    asyncio.create_task(simulator.start(config.interval_seconds))
    
    return {
        "message": "Simulation started",
        "pond_id": pond_id,
        "mode": config.mode,
        "interval_seconds": config.interval_seconds
    }


@router.post("/stop/{pond_id}")
def stop_simulation(pond_id: str):
    """Stop simulation for a pond."""
    simulator = simulator_manager.get_simulator(pond_id)
    if not simulator:
        raise HTTPException(status_code=404, detail="Simulator not found for this pond")
    
    simulator.stop()
    
    return {
        "message": "Simulation stopped",
        "pond_id": pond_id
    }


@router.get("/status/{pond_id}")
def get_simulation_status(pond_id: str):
    """Get simulation status and latest readings."""
    simulator = simulator_manager.get_simulator(pond_id)
    if not simulator:
        raise HTTPException(status_code=404, detail="Simulator not found for this pond")
    
    return {
        "pond_id": pond_id,
        "running": simulator.running,
        "mode": simulator.simulator.mode.value,
        "latest_readings": simulator.get_latest_readings(),
        "history_count": len(simulator.reading_history)
    }


@router.post("/mode/{pond_id}")
def set_simulation_mode(
    pond_id: str,
    mode: str = Query(..., pattern="^(normal|critical|fluctuating|drifting)$")
):
    """Change simulation mode."""
    simulator = simulator_manager.get_simulator(pond_id)
    if not simulator:
        raise HTTPException(status_code=404, detail="Simulator not found for this pond")
    
    try:
        sim_mode = SimulationMode(mode)
        simulator.simulator.set_mode(sim_mode)
        
        return {
            "message": f"Mode changed to {mode}",
            "pond_id": pond_id,
            "mode": mode
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")


@router.get("/generate/{pond_id}")
def generate_single_reading(pond_id: str, sensor_type: Optional[str] = None):
    """Generate a single reading (for testing)."""
    simulator = simulator_manager.get_simulator(pond_id)
    if not simulator:
        # Create temporary simulator
        sim = SensorSimulator()
    else:
        sim = simulator.simulator
    
    if sensor_type:
        value = sim.generate_reading(sensor_type)
        status = sim.get_status(sensor_type, value)
        return {
            "pond_id": pond_id,
            "sensor_type": sensor_type,
            "value": value,
            "status": status
        }
    else:
        readings = sim.generate_all_readings()
        return {
            "pond_id": pond_id,
            "readings": readings,
            "status": {
                k: sim.get_status(k, v) for k, v in readings.items()
            }
        }


@router.get("/all")
def get_all_simulations():
    """Get status of all simulations."""
    return {
        "active_simulations": len(simulator_manager.simulators),
        "simulators": [
            {
                "pond_id": pond_id,
                "name": sim.name,
                "running": sim.running,
                "mode": sim.simulator.mode.value
            }
            for pond_id, sim in simulator_manager.simulators.items()
        ]
    }


@router.post("/stop-all")
def stop_all_simulations():
    """Stop all simulations."""
    simulator_manager.stop_all()
    return {"message": "All simulations stopped"}
