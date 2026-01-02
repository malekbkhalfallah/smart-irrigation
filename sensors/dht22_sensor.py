"""
Capteur DHT22 optimisé sans conflit GPIO - VERSION FONCTIONNELLE
"""
import time
import logging
import random
from typing import Optional, Dict, Any
from sensors.base_sensor import BaseSensor

logger = logging.getLogger(__name__)

class DHT22Sensor(BaseSensor):
    """Capteur DHT22 - Version fonctionnelle sans conflit GPIO"""
    
    def __init__(self, pin: int = 17):
        super().__init__(name="DHT22", pin=pin)
        self.read_interval = 5  # Augmenter l'intervalle pour DHT22
        self.method = "simulated"  # Par défaut simulé
        self._sensor = None
        self.setup_sensor()
    
    def setup_sensor(self):
        """Tente d'initialiser le vrai capteur"""
        try:
            # Utiliser board pour éviter les conflits
            import board
            import adafruit_dht
            
            # Mapping GPIO -> board
            pin_map = {
                17: board.D17,
                4: board.D4,
                18: board.D18,
                23: board.D23,
                24: board.D24,
                27: board.D27
            }
            
            board_pin = pin_map.get(self.pin, board.D17)
            self._sensor = adafruit_dht.DHT22(board_pin, use_pulseio=False)
            self.method = "adafruit_dht"
            logger.info(f"✅ DHT22 RÉEL initialisé sur GPIO{self.pin}")
            
        except ImportError as e:
            logger.warning(f"⚠️ Module adafruit_dht non installé: {e}")
            logger.info("   Exécutez: pip install adafruit-circuitpython-dht")
            self.method = "simulated"
        except Exception as e:
            logger.warning(f"⚠️ DHT22 mode simulation: {e}")
            self.method = "simulated"
    
    def read_raw(self) -> Optional[Dict[str, Any]]:
        """Lecture du capteur DHT22 - Version robuste"""
        if self.method == "adafruit_dht" and self._sensor:
            try:
                # Lecture rapide avec retry
                for attempt in range(3):
                    try:
                        temperature = self._sensor.temperature
                        humidity = self._sensor.humidity
                        
                        if temperature is not None and humidity is not None:
                            return {
                                "temperature": round(temperature, 1),
                                "humidity": round(humidity, 1),
                                "unit": "C",
                                "method": "real"
                            }
                    except RuntimeError as e:
                        if attempt < 2:
                            time.sleep(0.1)
                            continue
                        logger.debug(f"Erreur runtime DHT22: {e}")
                        break
                    except Exception as e:
                        logger.debug(f"Erreur DHT22: {e}")
                        break
                        
            except Exception as e:
                logger.warning(f"⚠️ Erreur lecture DHT22: {e}")
        
        # Fallback simulé (toujours disponible)
        # Générer des valeurs réalistes avec un peu de variation
        base_temp = 20.0 + random.uniform(-3, 3)
        base_humidity = 60.0 + random.uniform(-15, 15)
        
        return {
            "temperature": round(base_temp, 1),
            "humidity": round(base_humidity, 1),
            "unit": "C",
            "method": "simulated"
        }
    
    def cleanup(self):
        """Nettoyage du capteur"""
        if self._sensor and self.method == "adafruit_dht":
            try:
                self._sensor.exit()
                self._sensor = None
            except:
                pass