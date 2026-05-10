"""
Mirofish AI - Database Models
Menggunakan SQLite untuk resource minimal
"""
import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, String, Float, DateTime, Integer, 
    ForeignKey, Enum, Boolean, Text, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

# Get absolute path for database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "mirofish.db")

# Ensure database directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

def generate_uuid() -> str:
    """Generate unique identifier."""
    return str(uuid.uuid4())


class UserRole(PyEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AlertSeverity(PyEnum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(PyEnum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class DeviceStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class User(Base):
    """User model untuk autentikasi."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.OPERATOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farms = relationship("Farm", back_populates="owner")


class Farm(Base):
    """Farm model - representasi lokasi budidaya."""
    __tablename__ = "farms"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    location = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)
    owner_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="farms")
    ponds = relationship("Pond", back_populates="farm")


class Pond(Base):
    """Pond model - representasi kolam/tambak."""
    __tablename__ = "ponds"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    farm_id = Column(String, ForeignKey("farms.id"))
    name = Column(String(255), nullable=False)
    volume_liters = Column(Integer)
    fish_type = Column(String(100))
    fish_count = Column(Integer, default=0)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Thresholds (override global settings)
    ph_min = Column(Float)
    ph_max = Column(Float)
    do_min = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)
    ammonia_max = Column(Float)
    
    # Relationships
    farm = relationship("Farm", back_populates="ponds")
    sensors = relationship("Sensor", back_populates="pond")
    readings = relationship("SensorReading", back_populates="pond")
    alerts = relationship("Alert", back_populates="pond")


class SensorType(PyEnum):
    PH = "ph"
    DISSOLVED_O2 = "dissolved_o2"
    TEMPERATURE = "temperature"
    CONDUCTIVITY = "conductivity"
    TURBIDITY = "turbidity"
    AMMONIA = "ammonia"
    WATER_LEVEL = "water_level"


class Sensor(Base):
    """Sensor model - representasi perangkat sensor."""
    __tablename__ = "sensors"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    pond_id = Column(String, ForeignKey("ponds.id"))
    type = Column(Enum(SensorType), nullable=False)
    name = Column(String(255))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    calibration_date = Column(DateTime)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pond = relationship("Pond", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor")


class SensorReading(Base):
    """SensorReading model - data historis dari sensor."""
    __tablename__ = "sensor_readings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    pond_id = Column(String, ForeignKey("ponds.id"))
    sensor_id = Column(String, ForeignKey("sensors.id"))
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    pond = relationship("Pond", back_populates="readings")
    sensor = relationship("Sensor", back_populates="readings")


class Alert(Base):
    """Alert model - notifikasi ketika parameter di luar threshold."""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    pond_id = Column(String, ForeignKey("ponds.id"))
    sensor_id = Column(String, ForeignKey("sensors.id"))
    severity = Column(Enum(AlertSeverity), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    parameter = Column(String(50), nullable=False)
    threshold_value = Column(Float)
    actual_value = Column(Float)
    message = Column(Text)
    acknowledged_by = Column(String, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pond = relationship("Pond", back_populates="alerts")


class SimulationConfig(Base):
    """SimulationConfig model - konfigurasi untuk simulasi."""
    __tablename__ = "simulation_configs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    pond_id = Column(String, ForeignKey("ponds.id"))
    is_active = Column(Boolean, default=False)
    ph_base = Column(Float, default=7.0)
    do_base = Column(Float, default=6.0)
    temp_base = Column(Float, default=26.0)
    noise_factor = Column(Float, default=0.1)
    drift_direction = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database setup untuk SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
