"""
Capteur de niveau d'eau (digital)
"""
import time
import logging
from typing import Optional, Dict, Any
from .base_sensor import BaseSensor

logger = logging.getLogger(__name__)

class WaterLevelSensor(BaseSensor):
    """Capteur digital de niveau d'eau"""
    
    def __init__(self, pin: int = 23):
        super().__init__(name="WaterLevel", pin=pin)
        self.chip = None
        self.setup_gpio()
    
    def setup_gpio(self):
        """Configuration GPIO"""
        try:
            import lgpio
            self.chip = lgpio.gpiochip_open(0)
            lgpio.gpio_claim_input(self.chip, self.pin)
            logger.info(f"WaterLevel initialisé sur GPIO{self.pin}")
        except ImportError:
            logger.warning("lgpio non disponible - mode simulation")
            self.chip = None
        except Exception as e:
            logger.error(f"Erreur initialisation WaterLevel: {e}")
            self.chip = None
    
    def read(self) -> Optional[Dict[str, Any]]:
        """Lecture du niveau d'eau"""
        if not self.chip:
            # Mode simulation
            return {
                "water_detected": True,
                "water_percent": 80.0,
                "raw_value": 1,
                "state": "WATER_OK",
                "timestamp": time.time()
            }
            
        try:
            import lgpio
            raw_value = lgpio.gpio_read(self.chip, self.pin)
            
            # 1 = eau détectée, 0 = pas d'eau
            water_detected = bool(raw_value)
            
            # Convertir en pourcentage (simplifié)
            water_percent = 100.0 if water_detected else 0.0
            
            return {
                "water_detected": water_detected,
                "water_percent": water_percent,
                "raw_value": raw_value,
                "state": "WATER_OK" if water_detected else "WATER_LOW",
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Erreur lecture WaterLevel: {e}")
            return None
    
    def cleanup(self):
        """Nettoyage"""
        if self.chip:
            try:
                import lgpio
                lgpio.gpiochip_close(self.chip)
            except:
                pass