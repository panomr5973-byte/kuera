"""
Mirofish AI - Ponds API
Manajemen kolam/tambak
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.database import (
    Farm, Pond, Sensor, SensorReading, Alert,
    get_db, generate_uuid, DeviceStatus, SensorType
)

router = APIRouter()


# Pydantic Models
class PondBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    volume_liters: Optional[int] = Field(None, gt=0)
    fish_type: Optional[str] = None
    fish_count: int = Field(0, ge=0)


class PondCreate(PondBase):
    farm_id: str


class PondThresholds(BaseModel):
    ph_min: Optional[float] = Field(None, ge=0, le=14)
    ph_max: Optional[float] = Field(None, ge=0, le=14)
    do_min: Optional[float] = Field(None, ge=0)
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    ammonia_max: Optional[float] = Field(None, ge=0)


class PondUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    volume_liters: Optional[int] = Field(None, gt=0)
    fish_type: Optional[str] = None
    fish_count: Optional[int] = Field(None, ge=0)
    status: Optional[DeviceStatus] = None
    thresholds: Optional[PondThresholds] = None


class PondResponse(PondBase):
    id: str
    farm_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PondDetailResponse(PondResponse):
    sensors: List[dict] = []
    latest_readings: dict = {}
    active_alerts: int = 0


# API Endpoints
@router.get("", response_model=List[PondResponse])
def list_ponds(
    farm_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all ponds."""
    query = db.query(Pond)
    
    if farm_id:
        query = query.filter(Pond.farm_id == farm_id)
    if status:
        query = query.filter(Pond.status == status)
    
    ponds = query.offset(skip).limit(limit).all()
    return ponds


@router.post("", response_model=PondResponse, status_code=status.HTTP_201_CREATED)
def create_pond(pond: PondCreate, db: Session = Depends(get_db)):
    """Create a new pond."""
    # Verify farm exists
    farm = db.query(Farm).filter(Farm.id == pond.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    db_pond = Pond(
        id=generate_uuid(),
        farm_id=pond.farm_id,
        name=pond.name,
        volume_liters=pond.volume_liters,
        fish_type=pond.fish_type,
        fish_count=pond.fish_count,
        status=DeviceStatus.ACTIVE
    )
    db.add(db_pond)
    db.commit()
    db.refresh(db_pond)
    
    return db_pond


@router.get("/{pond_id}", response_model=PondDetailResponse)
def get_pond(pond_id: str, db: Session = Depends(get_db)):
    """Get pond details with sensors and latest readings."""
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Get sensors
    sensors = db.query(Sensor).filter(Sensor.pond_id == pond_id).all()
    sensor_list = [
        {
            "id": s.id,
            "type": s.type.value if s.type else None,
            "name": s.name,
            "status": s.status.value if s.status else None
        }
        for s in sensors
    ]
    
    # Get latest readings for each sensor type
    latest_readings = {}
    for sensor in sensors:
        reading = db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor.id
        ).order_by(SensorReading.recorded_at.desc()).first()
        
        if reading:
            sensor_type = sensor.type.value if sensor.type else "unknown"
            latest_readings[sensor_type] = {
                "value": reading.value,
                "unit": reading.unit,
                "recorded_at": reading.recorded_at
            }
    
    # Count active alerts
    active_alerts = db.query(Alert).filter(
        Alert.pond_id == pond_id,
        Alert.status == "active"
    ).count()
    
    return {
        "id": pond.id,
        "farm_id": pond.farm_id,
        "name": pond.name,
        "volume_liters": pond.volume_liters,
        "fish_type": pond.fish_type,
        "fish_count": pond.fish_count,
        "status": pond.status.value if pond.status else None,
        "created_at": pond.created_at,
        "updated_at": pond.updated_at,
        "sensors": sensor_list,
        "latest_readings": latest_readings,
        "active_alerts": active_alerts
    }


@router.put("/{pond_id}", response_model=PondResponse)
def update_pond(pond_id: str, pond_update: PondUpdate, db: Session = Depends(get_db)):
    """Update pond."""
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Update basic fields
    update_data = pond_update.model_dump(exclude_unset=True, exclude={"thresholds"})
    for field, value in update_data.items():
        if field != "thresholds":
            setattr(pond, field, value)
    
    # Update thresholds if provided
    if pond_update.thresholds:
        thresholds = pond_update.thresholds.model_dump(exclude_unset=True)
        for field, value in thresholds.items():
            setattr(pond, field, value)
    
    db.commit()
    db.refresh(pond)
    
    return pond


@router.delete("/{pond_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pond(pond_id: str, db: Session = Depends(get_db)):
    """Delete pond."""
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    db.delete(pond)
    db.commit()
    
    return None


@router.post("/{pond_id}/sensors/initialize")
def initialize_sensors(pond_id: str, db: Session = Depends(get_db)):
    """Initialize default sensors for a pond."""
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Create default sensors
    sensor_types = [
        (SensorType.PH, "pH Sensor", "pH"),
        (SensorType.DISSOLVED_O2, "DO Sensor", "mg/L"),
        (SensorType.TEMPERATURE, "Temperature Sensor", "°C"),
        (SensorType.CONDUCTIVITY, "Conductivity Sensor", "μS/cm"),
    ]
    
    created_sensors = []
    for sensor_type, name, unit in sensor_types:
        # Check if sensor already exists
        existing = db.query(Sensor).filter(
            Sensor.pond_id == pond_id,
            Sensor.type == sensor_type
        ).first()
        
        if not existing:
            sensor = Sensor(
                id=generate_uuid(),
                pond_id=pond_id,
                type=sensor_type,
                name=name,
                model="Generic",
                serial_number=f"{pond_id}_{sensor_type.value}",
                status=DeviceStatus.ACTIVE
            )
            db.add(sensor)
            created_sensors.append({"type": sensor_type.value, "name": name})
    
    db.commit()
    
    return {
        "message": f"Created {len(created_sensors)} sensors",
        "sensors": created_sensors
    }
