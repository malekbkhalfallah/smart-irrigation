# sensors/__init__.py - VERSION CORRIGÉE
from .dht22_sensor import DHT22Sensor  # CHANGER ICI
from .soil_moisture_sensor import SoilMoistureSensor
from .raindrop_sensor import RaindropSensor
from .water_level_sensor import WaterLevelSensor
from .sensor_manager import SensorManager

__all__ = [
    'DHT22Sensor',  # CHANGER ICI
    'SoilMoistureSensor', 
    'RaindropSensor',
    'WaterLevelSensor',
    'SensorManager'
]