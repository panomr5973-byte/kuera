"""
Mirofish AI - Alerts API
Manajemen notifikasi dan alert
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import Alert, Pond, Sensor, get_db, AlertStatus, AlertSeverity

router = APIRouter()


class AlertAcknowledge(BaseModel):
    acknowledged_by: str


class AlertResponse(BaseModel):
    id: str
    pond_id: str
    sensor_id: Optional[str]
    severity: str
    status: str
    parameter: str
    threshold_value: Optional[float]
    actual_value: Optional[float]
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    pond_id: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^(active|acknowledged|resolved)$"),
    severity: Optional[str] = Query(None, pattern="^(critical|warning|info)$"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    """List alerts with filtering."""
    query = db.query(Alert)
    
    if pond_id:
        query = query.filter(Alert.pond_id == pond_id)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return alerts


@router.get("/active")
def get_active_alerts(
    pond_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get active alerts summary."""
    query = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE)
    
    if pond_id:
        query = query.filter(Alert.pond_id == pond_id)
    
    alerts = query.all()
    
    # Group by severity
    critical = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
    warning = [a for a in alerts if a.severity == AlertSeverity.WARNING]
    info = [a for a in alerts if a.severity == AlertSeverity.INFO]
    
    return {
        "total_active": len(alerts),
        "critical_count": len(critical),
        "warning_count": len(warning),
        "info_count": len(info),
        "alerts": [
            {
                "id": a.id,
                "pond_id": a.pond_id,
                "parameter": a.parameter,
                "message": a.message,
                "severity": a.severity.value if a.severity else None,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts[:20]  # Return first 20
        ]
    }


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get alert details."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: str,
    ack_data: AlertAcknowledge,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by = ack_data.acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {
        "message": "Alert acknowledged",
        "alert_id": alert_id,
        "acknowledged_by": ack_data.acknowledged_by
    }


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    """Resolve an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {
        "message": "Alert resolved",
        "alert_id": alert_id
    }


@router.get("/history/summary")
def get_alert_history_summary(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get alert history summary."""
    query = db.query(Alert)
    
    if from_date:
        query = query.filter(Alert.created_at >= from_date)
    if to_date:
        query = query.filter(Alert.created_at <= to_date)
    
    alerts = query.all()
    
    # Calculate statistics
    total = len(alerts)
    by_severity = {}
    by_status = {}
    by_parameter = {}
    
    for alert in alerts:
        # By severity
        sev = alert.severity.value if alert.severity else "unknown"
        by_severity[sev] = by_severity.get(sev, 0) + 1
        
        # By status
        stat = alert.status.value if alert.status else "unknown"
        by_status[stat] = by_status.get(stat, 0) + 1
        
        # By parameter
        param = alert.parameter or "unknown"
        by_parameter[param] = by_parameter.get(param, 0) + 1
    
    return {
        "total_alerts": total,
        "period": {
            "from": from_date.isoformat() if from_date else None,
            "to": to_date.isoformat() if to_date else None
        },
        "by_severity": by_severity,
        "by_status": by_status,
        "by_parameter": by_parameter
    }
