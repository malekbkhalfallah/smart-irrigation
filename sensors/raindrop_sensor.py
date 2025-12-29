"""
Capteur de pluie (digital)
"""
import time
import logging
from typing import Optional, Dict, Any
from .base_sensor import BaseSensor

logger = logging.getLogger(__name__)

class RaindropSensor(BaseSensor):
    """Capteur digital de pluie - 0 = pluie, 1 = sec"""
    
    def __init__(self, pin: int = 27):  # PAS de inverted_logic!
        super().__init__(name="Raindrop", pin=pin)
        self.chip = None
        self.setup_gpio()

    def setup_gpio(self):
        """Configuration GPIO"""
        try:
            import lgpio
            self.chip = lgpio.gpiochip_open(0)
            lgpio.gpio_claim_input(self.chip, self.pin)
            logger.info(f"Raindrop initialisé sur GPIO{self.pin}")
        except ImportError:
            logger.warning("lgpio non disponible - mode simulation")
            self.chip = None
        except Exception as e:
            logger.error(f"Erreur initialisation Raindrop: {e}")
            self.chip = None
    
    def read(self) -> Optional[Dict[str, Any]]:
        """Lecture de l'état pluie - 0 = pluie, 1 = sec"""
        if not self.chip:
            # Mode simulation
            return {
                "rain_detected": False,
                "raw_value": 1,
                "state": "DRY",
                "timestamp": time.time()
            }
            
        try:
            import lgpio
            raw_value = lgpio.gpio_read(self.chip, self.pin)
            
            # 0 = pluie détectée, 1 = sec
            rain_detected = raw_value == 0
            
            return {
                "rain_detected": rain_detected,
                "raw_value": raw_value,
                "state": "RAINING" if rain_detected else "DRY",
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Erreur lecture Raindrop: {e}")
            return None
    
    def cleanup(self):
        """Nettoyage"""
        if self.chip:
            try:
                import lgpio
                lgpio.gpiochip_close(self.chip)
            except:
                pass