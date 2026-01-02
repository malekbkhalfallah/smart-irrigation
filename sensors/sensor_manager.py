"""
Manager central pour tous les capteurs - HARDWARE RÉEL
"""
import time
import logging
from typing import Dict, Any, List, Optional
from config.settings import config

logger = logging.getLogger(__name__)

class SensorManager:
    """Gère tous les capteurs du système - HARDWARE RÉEL"""
    
    def __init__(self):
        # Dictionnaire pour stocker toutes les instances de capteurs
        self.sensors = {}
        # Liste des capteurs disponibles
        self.available_sensors = []
        # Initialisation
        self.initialize_sensors()
    
    def initialize_sensors(self):
        """Initialise tous les capteurs avec leurs pins GPIO - HARDWARE RÉEL"""
        try:
            print("\n🔧 INITIALISATION CAPTEURS HARDWARE RÉEL")
            print("=" * 40)
            
            # Import des classes de capteurs
            from .dht22_sensor import DHT22Sensor as DHT22Sensor
            from .soil_moisture_sensor import SoilMoistureSensor
            from .raindrop_sensor import RaindropSensor
            from .water_level_sensor import WaterLevelSensor
            
            # Configuration des pins
            # DHT22 - température/humidité
            print(f"🌡️  DHT22 -> GPIO{config.gpio.DHT22_PIN}")
            self.sensors['dht22'] = DHT22Sensor(pin=config.gpio.DHT22_PIN)
            
            # Capteur d'humidité du sol
            print(f"💧 Humidité Sol -> GPIO{config.gpio.SOIL_MOISTURE_PIN}")
            self.sensors['soil'] = SoilMoistureSensor(pin=config.gpio.SOIL_MOISTURE_PIN)
            
            # Capteur de pluie
            print(f"🌧️  Pluie -> GPIO{config.gpio.RAINDROP_PIN}")
            self.sensors['rain'] = RaindropSensor(pin=config.gpio.RAINDROP_PIN)
            
            # Capteur de niveau d'eau
            print(f"💦 Niveau Eau -> GPIO{config.gpio.WATER_LEVEL_PIN}")
            self.sensors['water'] = WaterLevelSensor(pin=config.gpio.WATER_LEVEL_PIN)
            
            # Mise à jour de la liste des capteurs disponibles
            self.available_sensors = list(self.sensors.keys())
            
            print("=" * 40)
            logger.info(f"✅ Capteurs initialisés: {self.available_sensors} - HARDWARE RÉEL")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation capteurs: {str(e)}")
            raise
    
    def read_all(self) -> Dict[str, Any]:
        """
        Lit toutes les valeurs des capteurs - HARDWARE RÉEL
        Returns: dict avec timestamp et données de tous les capteurs
        """
        readings = {
            "timestamp": time.time(),
            "sensors": {},
            "success": False,
            "healthy_sensors": 0,
            "total_sensors": len(self.sensors)
        }
        
        try:
            # Lecture de chaque capteur
            for name, sensor in self.sensors.items():
                data = sensor.read()
                readings["sensors"][name] = data
                
                if data is not None:
                    readings["healthy_sensors"] += 1
            
            # Vérification si au moins un capteur a répondu
            valid_readings = sum(
                1 for data in readings["sensors"].values() 
                if data is not None
            )
            
            readings["success"] = valid_readings > 0
            
            if readings["success"]:
                logger.debug(f"📊 Lecture capteurs réussie: {valid_readings}/{len(self.sensors)}")
            else:
                logger.warning("⚠️ Aucun capteur n'a retourné de données valides")
            
            return readings
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture capteurs: {str(e)}")
            return readings
    
    def get_sensor_status(self) -> Dict[str, Any]:
        """
        Retourne le statut de santé de tous les capteurs
        Returns: dict avec état de chaque capteur
        """
        status = {}
        for name, sensor in self.sensors.items():
            status[name] = sensor.get_status()
        return status
    
    def get_specific_sensor(self, name: str):
        """
        Retourne une instance spécifique de capteur
        Utile pour accéder directement à un capteur
        """
        return self.sensors.get(name)
    
    def read_sensor(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Lit un capteur spécifique
        """
        sensor = self.get_specific_sensor(name)
        if sensor:
            return sensor.read()
        return None
    
    def is_system_healthy(self) -> bool:
        """
        Vérifie si tous les capteurs sont sains
        """
        for name, sensor in self.sensors.items():
            if not sensor.is_healthy():
                logger.warning(f"⚠️ Capteur {name} défaillant")
                return False
        return True
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """
        Retourne un rapport complet de santé du système
        """
        report = {
            "timestamp": time.time(),
            "total_sensors": len(self.sensors),
            "healthy_sensors": 0,
            "sensors": {}
        }
        
        for name, sensor in self.sensors.items():
            is_healthy = sensor.is_healthy()
            report["sensors"][name] = {
                "healthy": is_healthy,
                "error_count": sensor.error_count,
                "last_read": sensor.last_read_time
            }
            if is_healthy:
                report["healthy_sensors"] += 1
        
        report["all_healthy"] = (report["healthy_sensors"] == report["total_sensors"])
        
        return report
    
    def cleanup(self):
        """Nettoie toutes les ressources des capteurs"""
        for name, sensor in self.sensors.items():
            try:
                sensor.cleanup()
                logger.debug(f"Capteur {name} nettoyé")
            except Exception as e:
                logger.error(f"❌ Erreur nettoyage capteur {name}: {str(e)}")
        
        logger.info("✅ Tous les capteurs nettoyés")

# Instance globale unique
sensor_manager = SensorManager()