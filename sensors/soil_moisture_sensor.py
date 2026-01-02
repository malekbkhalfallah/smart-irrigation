"""
Capteur digital d'humidité du sol - UTILISE GPIO CENTRAL
"""
import logging
from typing import Optional, Dict, Any
from sensors.base_sensor import BaseSensor
from core.gpio_manager import gpio_central

logger = logging.getLogger(__name__)

class SoilMoistureSensor(BaseSensor):
    """Capteur digital d'humidité du sol - UTILISE GPIO CENTRAL"""
    
    def __init__(self, pin: int = 24):
        super().__init__(name="SoilMoisture", pin=pin)
        logger.info(f"✅ SoilMoisture initialisé sur GPIO{pin} - UTILISE GPIO CENTRAL")
    
    def read_raw(self) -> Optional[Dict[str, Any]]:
        """
        Lecture de l'état du sol via GPIO central
        Returns: dict avec état et pourcentage d'humidité
        """
        try:
            # Lecture via GPIO central
            raw_value = gpio_central.read(self.pin)
            # Conversion en booléen: 1 = sec, 0 = humide
            is_dry = bool(raw_value)
            
            # Pourcentage d'humidité (simplifié pour capteur digital)
            # 0% = complètement sec, 100% = complètement humide
            moisture_percent = 0.0 if is_dry else 100.0
            
            return {
                "is_dry": is_dry,
                "moisture_percent": moisture_percent,
                "raw_value": raw_value,
                "state": "DRY" if is_dry else "WET"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture SoilMoisture: {str(e)}")
            return None