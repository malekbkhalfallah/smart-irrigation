"""
Capteur digital de pluie - UTILISE GPIO CENTRAL
Broche: GPIO27 (pin 13)
Logique: 0 = pluie détectée, 1 = sec
"""
import logging
from typing import Optional, Dict, Any
from sensors.base_sensor import BaseSensor
from core.gpio_manager import gpio_central

logger = logging.getLogger(__name__)

class RaindropSensor(BaseSensor):
    """Capteur digital de pluie - UTILISE GPIO CENTRAL"""
    
    def __init__(self, pin: int = 27):
        super().__init__(name="Raindrop", pin=pin)
        logger.info(f"✅ Raindrop initialisé sur GPIO{pin} - UTILISE GPIO CENTRAL")
    
    def read_raw(self) -> Optional[Dict[str, Any]]:
        """
        Lecture de l'état pluie/sec via GPIO central
        Returns: dict avec état de pluie
        """
        try:
            # Lecture via GPIO central
            raw_value = gpio_central.read(self.pin)
            
            # 0 = pluie détectée (gouttes sur le capteur)
            # 1 = sec (pas de gouttes)
            rain_detected = raw_value == 0
            
            return {
                "rain_detected": rain_detected,
                "raw_value": raw_value,
                "state": "RAINING" if rain_detected else "DRY"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture Raindrop: {str(e)}")
            return None
    
    def cleanup(self):
        """Nettoyage - Le GPIO est géré centralement"""
        pass