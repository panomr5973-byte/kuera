"""
Mirofish AI - Configuration Module
Optimasi untuk resource terbatas
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings dengan default yang optimal untuk development."""
    
    # App Info
    app_name: str = "Mirofish AI"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database - SQLite untuk resource minimal
    database_url: str = "sqlite+aiosqlite:///./database/mirofish.db"
    database_echo: bool = False
    
    # MQTT - Local broker
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_keepalive: int = 60
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI/ML
    model_path: str = "../models"
    use_local_llm: bool = True
    llm_model_path: str = "../models/llm"
    
    # Simulation
    simulation_enabled: bool = True
    simulation_interval: int = 5
    sensor_data_interval: int = 10
    
    # Alert Thresholds - Default untuk ikan nila/tilapia
    ph_min: float = 6.5
    ph_max: float = 8.5
    do_min: float = 4.0
    temp_min: float = 24.0
    temp_max: float = 30.0
    ammonia_max: float = 0.1
    
    # External APIs
    weather_api_key: Optional[str] = None
    
    # AI Kuera Integration
    kuera_api_url: str = "http://localhost:8000"
    kuera_integration_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
