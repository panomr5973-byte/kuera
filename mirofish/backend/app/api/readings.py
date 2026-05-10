"""
Mirofish AI - Sensor Readings API
Data dari sensor dan historis
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from app.models.database import SensorReading, Sensor, Pond, get_db, generate_uuid

router = APIRouter()


# Pydantic Models
class ReadingCreate(BaseModel):
    sensor_id: str
    value: float
    unit: Optional[str] = None
    recorded_at: Optional[datetime] = None


class ReadingResponse(BaseModel):
    id: str
    pond_id: str
    sensor_id: str
    value: float
    unit: Optional[str]
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class ReadingStats(BaseModel):
    sensor_type: str
    unit: str
    count: int
    avg: float
    min: float
    max: float
    latest: float


# API Endpoints
@router.get("/pond/{pond_id}", response_model=List[ReadingResponse])
def get_pond_readings(
    pond_id: str,
    sensor_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    aggregate: Optional[str] = Query(None, pattern="^(1m|5m|15m|1h|1d)$"),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get readings for a pond."""
    # Verify pond exists
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Build query
    query = db.query(SensorReading).filter(SensorReading.pond_id == pond_id)
    
    if sensor_type:
        # Join with sensor to filter by type
        query = query.join(Sensor).filter(Sensor.type == sensor_type)
    
    if from_date:
        query = query.filter(SensorReading.recorded_at >= from_date)
    if to_date:
        query = query.filter(SensorReading.recorded_at <= to_date)
    
    readings = query.order_by(SensorReading.recorded_at.desc()).limit(limit).all()
    return readings


@router.get("/pond/{pond_id}/latest")
def get_latest_readings(pond_id: str, db: Session = Depends(get_db)):
    """Get latest readings for all sensors in a pond."""
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    sensors = db.query(Sensor).filter(Sensor.pond_id == pond_id).all()
    
    result = {}
    for sensor in sensors:
        reading = db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor.id
        ).order_by(SensorReading.recorded_at.desc()).first()
        
        sensor_type = sensor.type.value if sensor.type else "unknown"
        
        if reading:
            result[sensor_type] = {
                "value": round(reading.value, 2),
                "unit": reading.unit,
                "recorded_at": reading.recorded_at.isoformat(),
                "sensor_name": sensor.name
            }
        else:
            result[sensor_type] = {
                "value": None,
                "unit": None,
                "recorded_at": None,
                "sensor_name": sensor.name
            }
    
    return {
        "pond_id": pond_id,
        "timestamp": datetime.utcnow().isoformat(),
        "readings": result
    }


@router.get("/pond/{pond_id}/stats")
def get_reading_stats(
    pond_id: str,
    from_date: Optional[datetime] = Query(default=None),
    to_date: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db)
):
    """Get statistics for all sensor types."""
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Default to last 24 hours if no dates provided
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=1)
    if not to_date:
        to_date = datetime.utcnow()
    
    sensors = db.query(Sensor).filter(Sensor.pond_id == pond_id).all()
    
    stats = []
    for sensor in sensors:
        readings = db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor.id,
            SensorReading.recorded_at >= from_date,
            SensorReading.recorded_at <= to_date
        ).all()
        
        if readings:
            values = [r.value for r in readings]
            latest = max(readings, key=lambda r: r.recorded_at)
            
            stats.append({
                "sensor_type": sensor.type.value if sensor.type else "unknown",
                "sensor_name": sensor.name,
                "unit": readings[0].unit if readings else None,
                "count": len(readings),
                "avg": round(sum(values) / len(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "latest": round(latest.value, 2)
            })
    
    return {
        "pond_id": pond_id,
        "period": {
            "from": from_date.isoformat(),
            "to": to_date.isoformat()
        },
        "stats": stats
    }


@router.post("/ingest")
def ingest_reading(reading: ReadingCreate, db: Session = Depends(get_db)):
    """Ingest a new sensor reading (from MQTT or simulation)."""
    # Verify sensor exists
    sensor = db.query(Sensor).filter(Sensor.id == reading.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    db_reading = SensorReading(
        id=generate_uuid(),
        pond_id=sensor.pond_id,
        sensor_id=reading.sensor_id,
        value=reading.value,
        unit=reading.unit or get_default_unit(sensor.type),
        recorded_at=reading.recorded_at or datetime.utcnow()
    )
    
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    
    return db_reading


@router.post("/ingest/batch")
def ingest_readings_batch(readings: List[ReadingCreate], db: Session = Depends(get_db)):
    """Ingest multiple readings at once."""
    created = []
    errors = []
    
    for reading in readings:
        try:
            sensor = db.query(Sensor).filter(Sensor.id == reading.sensor_id).first()
            if not sensor:
                errors.append({"sensor_id": reading.sensor_id, "error": "Sensor not found"})
                continue
            
            db_reading = SensorReading(
                id=generate_uuid(),
                pond_id=sensor.pond_id,
                sensor_id=reading.sensor_id,
                value=reading.value,
                unit=reading.unit or get_default_unit(sensor.type),
                recorded_at=reading.recorded_at or datetime.utcnow()
            )
            
            db.add(db_reading)
            created.append(db_reading)
        
        except Exception as e:
            errors.append({"sensor_id": reading.sensor_id, "error": str(e)})
    
    db.commit()
    
    return {
        "created": len(created),
        "errors": len(errors),
        "error_details": errors if errors else None
    }


def get_default_unit(sensor_type) -> str:
    """Get default unit for sensor type."""
    unit_map = {
        "ph": "pH",
        "dissolved_o2": "mg/L",
        "temperature": "°C",
        "conductivity": "μS/cm",
        "turbidity": "NTU",
        "ammonia": "mg/L",
        "water_level": "cm"
    }
    return unit_map.get(sensor_type.value if sensor_type else "", "")
