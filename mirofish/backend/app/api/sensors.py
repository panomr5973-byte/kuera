"""
Mirofish AI - Sensors API
Manajemen sensor devices
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.database import Sensor, Pond, SensorReading, get_db, generate_uuid, DeviceStatus, SensorType

router = APIRouter()


class SensorBase(BaseModel):
    type: str
    name: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None


class SensorCreate(SensorBase):
    pond_id: str


class SensorUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None
    calibration_date: Optional[datetime] = None


class SensorResponse(SensorBase):
    id: str
    pond_id: str
    status: str
    calibration_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SensorDetailResponse(SensorResponse):
    latest_reading: Optional[dict] = None
    reading_count: int = 0


@router.get("", response_model=List[SensorResponse])
def list_sensors(
    pond_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all sensors."""
    query = db.query(Sensor)
    
    if pond_id:
        query = query.filter(Sensor.pond_id == pond_id)
    if sensor_type:
        query = query.filter(Sensor.type == sensor_type)
    if status:
        query = query.filter(Sensor.status == status)
    
    sensors = query.all()
    return sensors


@router.post("", response_model=SensorResponse, status_code=201)
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """Create a new sensor."""
    # Verify pond exists
    pond = db.query(Pond).filter(Pond.id == sensor.pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Validate sensor type
    try:
        sensor_type = SensorType(sensor.type)
    except ValueError:
        valid_types = [t.value for t in SensorType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sensor type. Valid types: {valid_types}"
        )
    
    db_sensor = Sensor(
        id=generate_uuid(),
        pond_id=sensor.pond_id,
        type=sensor_type,
        name=sensor.name or f"{sensor.type} Sensor",
        model=sensor.model or "Generic",
        serial_number=sensor.serial_number or f"AUTO_{generate_uuid()[:8]}",
        status=DeviceStatus.ACTIVE
    )
    
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor


@router.get("/{sensor_id}", response_model=SensorDetailResponse)
def get_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Get sensor details with latest reading."""
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Get latest reading
    latest = db.query(SensorReading).filter(
        SensorReading.sensor_id == sensor_id
    ).order_by(SensorReading.recorded_at.desc()).first()
    
    # Count readings
    reading_count = db.query(SensorReading).filter(
        SensorReading.sensor_id == sensor_id
    ).count()
    
    result = {
        "id": sensor.id,
        "pond_id": sensor.pond_id,
        "type": sensor.type.value if sensor.type else None,
        "name": sensor.name,
        "model": sensor.model,
        "serial_number": sensor.serial_number,
        "status": sensor.status.value if sensor.status else None,
        "calibration_date": sensor.calibration_date,
        "created_at": sensor.created_at,
        "latest_reading": {
            "value": latest.value,
            "unit": latest.unit,
            "recorded_at": latest.recorded_at.isoformat()
        } if latest else None,
        "reading_count": reading_count
    }
    
    return result


@router.put("/{sensor_id}", response_model=SensorResponse)
def update_sensor(sensor_id: str, sensor_update: SensorUpdate, db: Session = Depends(get_db)):
    """Update sensor."""
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    update_data = sensor_update.model_dump(exclude_unset=True)
    
    # Handle status conversion
    if "status" in update_data and update_data["status"]:
        try:
            update_data["status"] = DeviceStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status value")
    
    for field, value in update_data.items():
        setattr(sensor, field, value)
    
    db.commit()
    db.refresh(sensor)
    
    return sensor


@router.delete("/{sensor_id}", status_code=204)
def delete_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Delete sensor."""
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    db.delete(sensor)
    db.commit()
    
    return None


@router.post("/{sensor_id}/calibrate")
def calibrate_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Mark sensor as calibrated."""
    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    sensor.calibration_date = datetime.utcnow()
    db.commit()
    db.refresh(sensor)
    
    return {
        "message": "Sensor calibrated",
        "sensor_id": sensor_id,
        "calibration_date": sensor.calibration_date.isoformat()
    }
