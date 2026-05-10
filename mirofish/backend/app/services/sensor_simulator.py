"""
Mirofish AI - Sensor Simulator
Simulasi data sensor untuk testing tanpa hardware
"""
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class SimulationMode(Enum):
    NORMAL = "normal"
    CRITICAL = "critical"
    FLUCTUATING = "fluctuating"
    DRIFTING = "drifting"


@dataclass
class SensorConfig:
    """Configuration for sensor simulation."""
    base_value: float
    noise_range: float
    drift_per_hour: float = 0.0
    critical_range: Optional[tuple] = None


class SensorSimulator:
    """Simulate sensor readings for aquaculture monitoring."""
    
    # Default configurations for different sensor types
    DEFAULT_CONFIGS = {
        "ph": SensorConfig(
            base_value=7.2,
            noise_range=0.2,
            drift_per_hour=0.01,
            critical_range=(6.0, 9.0)
        ),
        "dissolved_o2": SensorConfig(
            base_value=6.5,
            noise_range=0.5,
            drift_per_hour=-0.1,  # DO tends to decrease
            critical_range=(3.0, 12.0)
        ),
        "temperature": SensorConfig(
            base_value=26.0,
            noise_range=0.8,
            drift_per_hour=0.05,
            critical_range=(22.0, 32.0)
        ),
        "conductivity": SensorConfig(
            base_value=450.0,
            noise_range=20.0,
            drift_per_hour=0.5
        ),
        "turbidity": SensorConfig(
            base_value=5.0,
            noise_range=1.5,
            drift_per_hour=0.2
        ),
        "ammonia": SensorConfig(
            base_value=0.02,
            noise_range=0.005,
            drift_per_hour=0.001,
            critical_range=(0.0, 0.1)
        ),
        "water_level": SensorConfig(
            base_value=100.0,
            noise_range=2.0,
            drift_per_hour=-0.5  # Level may decrease due to evaporation
        )
    }
    
    def __init__(self, mode: SimulationMode = SimulationMode.NORMAL):
        self.mode = mode
        self.current_values: Dict[str, float] = {}
        self.iteration = 0
        
        # Initialize with base values
        for sensor_type, config in self.DEFAULT_CONFIGS.items():
            self.current_values[sensor_type] = config.base_value
    
    def set_mode(self, mode: SimulationMode):
        """Change simulation mode."""
        self.mode = mode
        
        if mode == SimulationMode.CRITICAL:
            # Set values outside normal ranges
            self.current_values["ph"] = 5.5  # Too acidic
            self.current_values["dissolved_o2"] = 2.5  # Too low
            self.current_values["temperature"] = 34.0  # Too high
            self.current_values["ammonia"] = 0.15  # Too high
    
    def generate_reading(self, sensor_type: str, custom_config: Optional[SensorConfig] = None) -> float:
        """Generate a single sensor reading."""
        config = custom_config or self.DEFAULT_CONFIGS.get(sensor_type)
        if not config:
            return 0.0
        
        current = self.current_values.get(sensor_type, config.base_value)
        
        # Apply mode-specific modifications
        if self.mode == SimulationMode.FLUCTUATING:
            noise = random.uniform(-config.noise_range * 2, config.noise_range * 2)
        elif self.mode == SimulationMode.CRITICAL:
            # More extreme values
            noise = random.uniform(-config.noise_range, config.noise_range)
            if sensor_type == "ph":
                current = random.choice([5.2, 9.2])  # Critical pH
            elif sensor_type == "dissolved_o2":
                current = random.uniform(2.0, 3.0)  # Critical DO
        else:
            noise = random.uniform(-config.noise_range, config.noise_range)
        
        # Apply drift
        drift = config.drift_per_hour / 3600  # Per second (if called every second)
        
        # Calculate new value
        new_value = current + noise + drift
        
        # Keep within critical range if defined
        if config.critical_range:
            min_val, max_val = config.critical_range
            new_value = max(min_val, min(max_val, new_value))
        
        # Ensure non-negative for most sensors
        if sensor_type not in ["ph"]:
            new_value = max(0, new_value)
        
        # Update current value
        self.current_values[sensor_type] = new_value
        
        return round(new_value, 2)
    
    def generate_all_readings(self) -> Dict[str, float]:
        """Generate readings for all sensor types."""
        readings = {}
        for sensor_type in self.DEFAULT_CONFIGS.keys():
            readings[sensor_type] = self.generate_reading(sensor_type)
        return readings
    
    def get_status(self, sensor_type: str, value: float) -> str:
        """Get status based on value and thresholds."""
        thresholds = {
            "ph": {"low": 6.5, "high": 8.5},
            "dissolved_o2": {"low": 4.0},
            "temperature": {"low": 24.0, "high": 30.0},
            "ammonia": {"high": 0.1}
        }
        
        sensor_thresholds = thresholds.get(sensor_type, {})
        
        if "low" in sensor_thresholds and value < sensor_thresholds["low"]:
            return "critical" if value < sensor_thresholds["low"] * 0.8 else "warning"
        
        if "high" in sensor_thresholds and value > sensor_thresholds["high"]:
            return "critical" if value > sensor_thresholds["high"] * 1.2 else "warning"
        
        return "normal"


class PondSimulator:
    """Simulate a complete pond with multiple sensors."""
    
    def __init__(self, pond_id: str, name: str):
        self.pond_id = pond_id
        self.name = name
        self.simulator = SensorSimulator()
        self.running = False
        self.reading_history: List[Dict] = []
        self.max_history = 1000
    
    async def start(self, interval_seconds: int = 10):
        """Start continuous simulation."""
        self.running = True
        
        while self.running:
            readings = self.simulator.generate_all_readings()
            timestamp = datetime.utcnow()
            
            # Add to history
            self.reading_history.append({
                "timestamp": timestamp,
                "readings": readings
            })
            
            # Trim history
            if len(self.reading_history) > self.max_history:
                self.reading_history = self.reading_history[-self.max_history:]
            
            # Wait for next iteration
            await asyncio.sleep(interval_seconds)
    
    def stop(self):
        """Stop simulation."""
        self.running = False
    
    def get_latest_readings(self) -> Dict:
        """Get latest readings."""
        if self.reading_history:
            return self.reading_history[-1]
        return {"timestamp": datetime.utcnow(), "readings": {}}
    
    def get_readings_for_period(self, hours: int = 24) -> List[Dict]:
        """Get readings for the last N hours."""
        cutoff = datetime.utcnow() - __import__('datetime').timedelta(hours=hours)
        return [r for r in self.reading_history if r["timestamp"] > cutoff]


# Global simulator manager
class SimulatorManager:
    """Manage multiple pond simulators."""
    
    def __init__(self):
        self.simulators: Dict[str, PondSimulator] = {}
        self.tasks = []
    
    def create_simulator(self, pond_id: str, name: str) -> PondSimulator:
        """Create a new pond simulator."""
        simulator = PondSimulator(pond_id, name)
        self.simulators[pond_id] = simulator
        return simulator
    
    async def start_all(self, interval_seconds: int = 10):
        """Start all simulators."""
        for simulator in self.simulators.values():
            task = asyncio.create_task(simulator.start(interval_seconds))
            self.tasks.append(task)
    
    def stop_all(self):
        """Stop all simulators."""
        for simulator in self.simulators.values():
            simulator.stop()
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        self.tasks = []
    
    def get_simulator(self, pond_id: str) -> Optional[PondSimulator]:
        """Get simulator by pond ID."""
        return self.simulators.get(pond_id)
    
    def get_all_readings(self) -> Dict[str, Dict]:
        """Get latest readings from all simulators."""
        return {
            pond_id: sim.get_latest_readings()
            for pond_id, sim in self.simulators.items()
        }


# Singleton instance
simulator_manager = SimulatorManager()
