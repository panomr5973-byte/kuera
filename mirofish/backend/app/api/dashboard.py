"""
Mirofish AI - Dashboard API
Overview dan summary data
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import (
    Farm, Pond, Sensor, SensorReading, Alert,
    get_db, DeviceStatus, AlertStatus
)

router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get overall dashboard summary."""
    # Count statistics
    total_farms = db.query(Farm).count()
    total_ponds = db.query(Pond).count()
    active_ponds = db.query(Pond).filter(Pond.status == DeviceStatus.ACTIVE).count()
    total_sensors = db.query(Sensor).count()
    active_alerts = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).count()
    
    # Recent readings count (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_readings = db.query(SensorReading).filter(
        SensorReading.recorded_at >= yesterday
    ).count()
    
    # Alerts by severity
    critical_alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.ACTIVE,
        Alert.severity == "critical"
    ).count()
    
    warning_alerts = db.query(Alert).filter(
        Alert.status == AlertStatus.ACTIVE,
        Alert.severity == "warning"
    ).count()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overview": {
            "total_farms": total_farms,
            "total_ponds": total_ponds,
            "active_ponds": active_ponds,
            "total_sensors": total_sensors,
            "active_alerts": active_alerts,
            "readings_24h": recent_readings
        },
        "alerts": {
            "critical": critical_alerts,
            "warning": warning_alerts,
            "total_active": active_alerts
        },
        "system_health": {
            "status": "healthy" if critical_alerts == 0 else "degraded",
            "ponds_online": f"{active_ponds}/{total_ponds}"
        }
    }


@router.get("/pond/{pond_id}/status")
def get_pond_dashboard(pond_id: str, db: Session = Depends(get_db)):
    """Get detailed dashboard for a specific pond."""
    pond = db.query(Pond).filter(Pond.id == pond_id).first()
    if not pond:
        raise HTTPException(status_code=404, detail="Pond not found")
    
    # Get latest readings
    sensors = db.query(Sensor).filter(Sensor.pond_id == pond_id).all()
    
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
                "timestamp": reading.recorded_at.isoformat(),
                "status": check_threshold(sensor_type, reading.value, pond)
            }
    
    # Get active alerts
    active_alerts = db.query(Alert).filter(
        Alert.pond_id == pond_id,
        Alert.status == AlertStatus.ACTIVE
    ).all()
    
    alerts_list = [
        {
            "id": a.id,
            "severity": a.severity.value if a.severity else None,
            "parameter": a.parameter,
            "message": a.message,
            "created_at": a.created_at.isoformat()
        }
        for a in active_alerts
    ]
    
    # Calculate trend (last hour vs previous hour)
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)
    
    trends = {}
    for sensor in sensors:
        recent = db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor.id,
            SensorReading.recorded_at >= one_hour_ago
        ).all()
        
        previous = db.query(SensorReading).filter(
            SensorReading.sensor_id == sensor.id,
            SensorReading.recorded_at >= two_hours_ago,
            SensorReading.recorded_at < one_hour_ago
        ).all()
        
        if recent and previous:
            recent_avg = sum(r.value for r in recent) / len(recent)
            previous_avg = sum(p.value for p in previous) / len(previous)
            
            sensor_type = sensor.type.value if sensor.type else "unknown"
            change = recent_avg - previous_avg
            change_percent = (change / previous_avg * 100) if previous_avg != 0 else 0
            
            trends[sensor_type] = {
                "direction": "up" if change > 0 else "down",
                "change": round(change, 2),
                "change_percent": round(change_percent, 1)
            }
    
    return {
        "pond": {
            "id": pond.id,
            "name": pond.name,
            "fish_type": pond.fish_type,
            "fish_count": pond.fish_count,
            "status": pond.status.value if pond.status else None
        },
        "latest_readings": latest_readings,
        "active_alerts": alerts_list,
        "trends": trends,
        "recommendations": generate_recommendations(latest_readings, alerts_list)
    }


@router.get("/farm/{farm_id}/overview")
def get_farm_overview(farm_id: str, db: Session = Depends(get_db)):
    """Get overview for a farm."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Get all ponds
    ponds = db.query(Pond).filter(Pond.farm_id == farm_id).all()
    
    pond_statuses = []
    for pond in ponds:
        # Get latest readings
        sensors = db.query(Sensor).filter(Sensor.pond_id == pond.id).all()
        
        readings = {}
        for sensor in sensors:
            reading = db.query(SensorReading).filter(
                SensorReading.sensor_id == sensor.id
            ).order_by(SensorReading.recorded_at.desc()).first()
            
            if reading:
                sensor_type = sensor.type.value if sensor.type else "unknown"
                readings[sensor_type] = reading.value
        
        # Count alerts
        alert_count = db.query(Alert).filter(
            Alert.pond_id == pond.id,
            Alert.status == AlertStatus.ACTIVE
        ).count()
        
        # Determine status
        status = "healthy"
        if alert_count > 0:
            status = "warning"
        if any(check_threshold(k, v, pond) == "critical" for k, v in readings.items()):
            status = "critical"
        
        pond_statuses.append({
            "id": pond.id,
            "name": pond.name,
            "status": status,
            "readings": readings,
            "alert_count": alert_count
        })
    
    return {
        "farm": {
            "id": farm.id,
            "name": farm.name,
            "location": farm.location
        },
        "ponds": pond_statuses,
        "summary": {
            "total_ponds": len(ponds),
            "healthy": sum(1 for p in pond_statuses if p["status"] == "healthy"),
            "warning": sum(1 for p in pond_statuses if p["status"] == "warning"),
            "critical": sum(1 for p in pond_statuses if p["status"] == "critical")
        }
    }


def check_threshold(sensor_type: str, value: float, pond) -> str:
    """Check if value is within thresholds."""
    # Use pond-specific thresholds if available, otherwise use defaults
    thresholds = {
        "ph": {"min": pond.ph_min or 6.5, "max": pond.ph_max or 8.5},
        "dissolved_o2": {"min": pond.do_min or 4.0},
        "temperature": {"min": pond.temp_min or 24.0, "max": pond.temp_max or 30.0},
        "ammonia": {"max": pond.ammonia_max or 0.1}
    }
    
    sensor_thresholds = thresholds.get(sensor_type, {})
    
    if "min" in sensor_thresholds and value < sensor_thresholds["min"]:
        return "critical" if value < sensor_thresholds["min"] * 0.8 else "warning"
    
    if "max" in sensor_thresholds and value > sensor_thresholds["max"]:
        return "critical" if value > sensor_thresholds["max"] * 1.2 else "warning"
    
    return "normal"


def generate_recommendations(readings: dict, alerts: list) -> list:
    """Generate recommendations based on readings and alerts."""
    recommendations = []
    
    # Check pH
    ph_data = readings.get("ph", {})
    if isinstance(ph_data, dict):
        ph_value = ph_data.get("value")
        if ph_value and ph_value < 6.5:
            recommendations.append({
                "priority": "high",
                "action": "Tambahkan kapur (lime) ke kolam untuk menaikkan pH",
                "parameter": "pH",
                "current_value": ph_value
            })
        elif ph_value and ph_value > 8.5:
            recommendations.append({
                "priority": "high",
                "action": "Kurangi pemberian pakan, pertimbangkan pergantian air",
                "parameter": "pH",
                "current_value": ph_value
            })
    
    # Check DO
    do_data = readings.get("dissolved_o2", {})
    if isinstance(do_data, dict):
        do_value = do_data.get("value")
        if do_value and do_value < 4.0:
            recommendations.append({
                "priority": "critical",
                "action": "Segera nyalakan aerator! Kadar oksigen terlalu rendah",
                "parameter": "Dissolved O2",
                "current_value": do_value
            })
    
    # Check temperature
    temp_data = readings.get("temperature", {})
    if isinstance(temp_data, dict):
        temp_value = temp_data.get("value")
        if temp_value and temp_value > 30:
            recommendations.append({
                "priority": "medium",
                "action": "Pertimbangkan penambahan naungan atau aerator",
                "parameter": "Temperature",
                "current_value": temp_value
            })
    
    # Add recommendations from alerts
    for alert in alerts:
        recommendations.append({
            "priority": alert.get("severity", "medium"),
            "action": alert.get("message", "Periksa parameter"),
            "parameter": alert.get("parameter", "unknown"),
            "alert_id": alert.get("id")
        })
    
    return recommendations[:5]  # Return top 5
