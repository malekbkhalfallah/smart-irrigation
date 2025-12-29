"""
Capteur d'humidité du sol (digital)
"""
import time
import logging
from typing import Optional, Dict, Any
from .base_sensor import BaseSensor

logger = logging.getLogger(__name__)

class SoilMoistureSensor(BaseSensor):
    """Capteur digital d'humidité du sol"""
    
    def __init__(self, pin: int = 24):
        super().__init__(name="SoilMoisture", pin=pin)
        self.chip = None
        self.setup_gpio()
    
    def setup_gpio(self):
        """Configuration GPIO"""
        try:
            import lgpio
            self.chip = lgpio.gpiochip_open(0)
            lgpio.gpio_claim_input(self.chip, self.pin)
            logger.info(f"SoilMoisture initialisé sur GPIO{self.pin}")
        except ImportError:
            logger.warning("lgpio non disponible - mode simulation")
            self.chip = None
        except Exception as e:
            logger.error(f"Erreur initialisation SoilMoisture: {e}")
            self.chip = None
    
    def read(self) -> Optional[Dict[str, Any]]:
        """Lecture de l'état du sol"""
        if not self.chip:
            # Mode simulation
            return {
                "is_dry": False,
                "moisture_percent": 65.0,
                "raw_value": 0,
                "state": "WET",
                "timestamp": time.time()
            }
            
        try:
            import lgpio
            # 0 = humide, 1 = sec
            raw_value = lgpio.gpio_read(self.chip, self.pin)
            is_dry = bool(raw_value)
            
            # Convertir en pourcentage pour la logique
            moisture_percent = 0.0 if is_dry else 100.0
            
            return {
                "is_dry": is_dry,
                "moisture_percent": moisture_percent,
                "raw_value": raw_value,
                "state": "DRY" if is_dry else "WET",
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Erreur lecture SoilMoisture: {e}")
            return None
    
    def cleanup(self):
        """Nettoyage"""
        if self.chip:
            try:
                import lgpio
                lgpio.gpiochip_close(self.chip)
            except:
                pass