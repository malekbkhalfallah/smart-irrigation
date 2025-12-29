"""
Manager pour tous les capteurs
"""
import time
import logging
from typing import Dict, Any, Optional
from config.settings import config

# Import dynamique pour éviter erreurs si libs manquantes
try:
    from .dht22_sensor import DHT22Sensor
    from .soil_moisture_sensor import SoilMoistureSensor
    from .raindrop_sensor import RaindropSensor
    from .water_level_sensor import WaterLevelSensor
    SENSORS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Import sensors failed: {e}")
    SENSORS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SensorManager:
    """Gère tous les capteurs du système"""
    
    def __init__(self):
        self.sensors = {}
        self.initialize_sensors()
    
    def initialize_sensors(self):
        """Initialise tous les capteurs"""
        if not SENSORS_AVAILABLE:
            logger.warning("Mode simulation - capteurs non disponibles")
            return
            
        try:
            # DHT22
            self.sensors['dht22'] = DHT22Sensor(config.gpio.DHT22_PIN)
            
            # Capteur sol
            self.sensors['soil'] = SoilMoistureSensor(config.gpio.SOIL_MOISTURE_PIN)
            
            # Capteur pluie
            self.sensors['rain'] = RaindropSensor(config.gpio.RAINDROP_DIGITAL_PIN)
            
            # Capteur niveau eau
            self.sensors['water_level'] = WaterLevelSensor(config.gpio.WATER_LEVEL_PIN)
            
            logger.info("Tous les capteurs initialisés")
            
        except Exception as e:
            logger.error(f"Erreur initialisation capteurs: {e}")
    
    def read_all(self) -> Dict[str, Any]:
        """Lit toutes les valeurs des capteurs"""
        readings = {
            "timestamp": time.time(),
            "sensors": {},
            "success": False
        }
        
        try:
            for name, sensor in self.sensors.items():
                data = sensor.read_safe()
                readings["sensors"][name] = data
            
            # Vérifier si au moins un capteur a répondu
            valid_readings = sum(1 for data in readings["sensors"].values() if data is not None)
            readings["success"] = valid_readings > 0
            
            return readings
            
        except Exception as e:
            logger.error(f"Erreur lecture capteurs: {e}")
            return readings
    
    def get_sensor_status(self) -> Dict[str, Any]:
        """Retourne le statut de tous les capteurs"""
        status = {}
        for name, sensor in self.sensors.items():
            status[name] = {
                "name": sensor.name,
                "healthy": sensor.is_healthy(),
                "error_count": sensor.error_count,
                "last_value": sensor.last_value
            }
        return status
    
    def cleanup(self):
        """Nettoie tous les capteurs"""
        for sensor in self.sensors.values():
            try:
                sensor.cleanup()
            except Exception as e:
                logger.error(f"Erreur nettoyage capteur: {e}")
        logger.info("Tous les capteurs nettoyés")

# Instance globale
sensor_manager = SensorManager()