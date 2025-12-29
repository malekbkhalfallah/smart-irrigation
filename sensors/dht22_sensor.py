"""
Capteur DHT22 (température/humidité)
"""
import time
import logging
from typing import Optional, Dict, Any
from .base_sensor import BaseSensor

logger = logging.getLogger(__name__)

class DHT22Sensor(BaseSensor):
    """Capteur de température et humidité DHT22"""
    
    def __init__(self, pin: int = 17):
        super().__init__(name="DHT22", pin=pin)
        self.setup_sensor()
    
    def setup_sensor(self):
        """Initialise le capteur DHT22"""
        try:
            import adafruit_dht
            import board
            
            self.dht_device = adafruit_dht.DHT22(getattr(board, f"D{self.pin}"))
            logger.info(f"DHT22 initialisé sur GPIO{self.pin}")
            
        except ImportError:
            logger.warning("adafruit_dht non disponible - mode simulation")
            self.dht_device = None
        except Exception as e:
            logger.error(f"Erreur initialisation DHT22: {e}")
            self.dht_device = None
    
    def read(self) -> Optional[Dict[str, Any]]:
        """Lecture température et humidité"""
        if not self.dht_device:
            # Mode simulation pour tests
            return {
                "temperature": 22.5,
                "humidity": 65.0,
                "unit": "C",
                "timestamp": time.time()
            }
            
        try:
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity
            
            if temperature is not None and humidity is not None:
                return {
                    "temperature": round(temperature, 1),
                    "humidity": round(humidity, 1),
                    "unit": "C",
                    "timestamp": time.time()
                }
                
        except RuntimeError:
            logger.debug("DHT22: Erreur timing (normal)")
        except Exception as e:
            logger.error(f"Erreur lecture DHT22: {e}")
            
        return None
    
    def cleanup(self):
        """Nettoyage"""
        if hasattr(self, 'dht_device') and self.dht_device:
            try:
                self.dht_device.exit()
            except:
                pass