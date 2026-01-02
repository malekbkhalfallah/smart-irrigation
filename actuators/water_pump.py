"""
Contrôle de la pompe à eau via relais - UTILISE GPIO CENTRAL
"""
import time
import logging
from typing import Optional
from config.settings import config
from core.gpio_manager import gpio_central

logger = logging.getLogger(__name__)

class WaterPump:
    """Contrôle de la pompe à eau via relais - UTILISE GPIO CENTRAL"""
    
    def __init__(self):
        self.pin = config.gpio.PUMP_RELAY_PIN
        self.is_running = False
        self.total_run_time = 0
        self.last_activation = None
        self.default_duration = config.irrigation.IRRIGATION_DURATION
        
        logger.info(f"✅ Pompe initialisée sur GPIO{self.pin} - UTILISE GPIO CENTRAL")
    
    def start(self, duration: Optional[int] = None) -> bool:
        """
        Démarre la pompe via GPIO central
        """
        if self.is_running:
            logger.warning("⚠️ Pompe déjà en fonctionnement")
            return False
        
        if duration is None:
            duration = self.default_duration
        
        try:
            logger.info(f"🚰 Démarrage pompe pour {duration} secondes...")
            
            # Activation via GPIO central
            gpio_central.write(self.pin, True)
            
            self.is_running = True
            self.last_activation = time.time()
            
            logger.info(f"✅ Pompe démarrée pour {duration} secondes")
            
            if duration > 0:
                logger.info(f"⏳ Attente {duration} secondes...")
                time.sleep(duration)
                self.stop()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage pompe: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """Arrête immédiatement la pompe via GPIO central"""
        if not self.is_running:
            logger.debug("Pompe déjà arrêtée")
            return True
        
        try:
            gpio_central.write(self.pin, False)
            
            self.is_running = False
            
            if self.last_activation:
                run_time = time.time() - self.last_activation
                self.total_run_time += run_time
                logger.info(f"✅ Pompe arrêtée après {run_time:.1f} secondes")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt pompe: {str(e)}")
            return False
    
    def get_status(self) -> dict:
        return {
            "is_running": self.is_running,
            "total_run_time": self.total_run_time,
            "last_activation": self.last_activation,
            "pin": self.pin,
            "default_duration": self.default_duration
        }
    
    def cleanup(self):
        """Arrête la pompe si nécessaire"""
        if self.is_running:
            logger.info("🛑 Arrêt d'urgence de la pompe...")
            self.stop()

# Instance globale unique
water_pump = WaterPump()