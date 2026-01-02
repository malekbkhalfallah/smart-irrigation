# sensors/water_level_sensor.py - VERSION CORRIGÉE
import logging
from typing import Optional, Dict, Any
from sensors.base_sensor import BaseSensor
from core.gpio_manager import gpio_central

logger = logging.getLogger(__name__)

class WaterLevelSensor(BaseSensor):
    def __init__(self, pin: int = 23):
        super().__init__(name="WaterLevel", pin=pin)
        logger.info(f"✅ WaterLevel initialisé sur GPIO{pin} - UTILISE GPIO CENTRAL")
    
    def read_raw(self) -> Optional[Dict[str, Any]]:
        try:
            raw_value = gpio_central.read(self.pin)
            
            # ⚠️ LOGIQUE À ADAPTER SELON TON CAPTEUR ⚠️
            # Si ton capteur retourne 1 quand il y a de l'eau, et 0 quand il n'y en a pas
            # Essaie d'inverser si besoin : water_detected = not bool(raw_value)
            
            water_detected = bool(raw_value)  # Essaie d'abord cette logique
            # Si c'est inversé : water_detected = not bool(raw_value)
            
            # Pourcentage basé sur la détection (simplifié)
            water_percent = 100.0 if water_detected else 0.0
            
            return {
                "water_detected": water_detected,
                "water_percent": water_percent,
                "raw_value": raw_value,
                "state": "WATER_OK" if water_detected else "WATER_LOW"
            }
        except Exception as e:
            logger.error(f"❌ Erreur lecture WaterLevel: {str(e)}")
            return None