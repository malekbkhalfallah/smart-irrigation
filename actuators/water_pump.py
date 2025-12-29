"""
Contrôle de la pompe à eau via relais
"""
import time
import logging
from typing import Optional
from config.settings import config

logger = logging.getLogger(__name__)

class WaterPump:
    """Contrôle de la pompe à eau"""
    
    def __init__(self, pin: int = 26):
        self.pin = pin
        self.chip = None
        self.is_running = False
        self.total_run_time = 0  # en secondes
        self.last_activation = None
        self.initialize()
    
    def initialize(self):
        """Initialise le GPIO pour la pompe"""
        try:
            import lgpio
            self.chip = lgpio.gpiochip_open(0)
            lgpio.gpio_claim_output(self.chip, self.pin)
            # Désactivé par défaut (relais normalement ouvert)
            lgpio.gpio_write(self.chip, self.pin, 0)
            logger.info(f"Pompe initialisée sur GPIO{self.pin}")
        except ImportError:
            logger.warning("lgpio non disponible - mode simulation")
            self.chip = None
        except Exception as e:
            logger.error(f"Erreur initialisation pompe: {e}")
            self.chip = None
    
    def start(self, duration: Optional[int] = None) -> bool:
        """
        Démarre la pompe
        Args:
            duration: durée en secondes (si None, démarre manuellement)
        Returns:
            True si réussi
        """
        if self.chip is None:
            logger.warning("Mode simulation - pompe démarrée")
            self.is_running = True
            self.last_activation = time.time()
            return True
        
        try:
            import lgpio
            # Activer le relais (1 = activé pour relais normalement ouvert)
            lgpio.gpio_write(self.chip, self.pin, 1)
            self.is_running = True
            self.last_activation = time.time()
            logger.info(f"Pompe démarrée (durée: {duration}s)")
            
            # Si durée spécifiée, arrêt automatique
            if duration:
                time.sleep(duration)
                self.stop()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage pompe: {e}")
            return False
    
    def stop(self) -> bool:
        """Arrête la pompe"""
        if self.chip is None:
            logger.warning("Mode simulation - pompe arrêtée")
            self.is_running = False
            return True
        
        try:
            import lgpio
            lgpio.gpio_write(self.chip, self.pin, 0)
            self.is_running = False
            
            # Calculer temps d'activation
            if self.last_activation:
                run_time = time.time() - self.last_activation
                self.total_run_time += run_time
                logger.info(f"Pompe arrêtée (durée: {run_time:.1f}s)")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur arrêt pompe: {e}")
            return False
    
    def get_status(self) -> dict:
        """Retourne le statut de la pompe"""
        return {
            "is_running": self.is_running,
            "total_run_time": self.total_run_time,
            "last_activation": self.last_activation,
            "pin": self.pin
        }
    
    def cleanup(self):
        """Nettoie et arrête la pompe"""
        if self.is_running:
            self.stop()
        if self.chip:
            try:
                import lgpio
                lgpio.gpiochip_close(self.chip)
            except:
                pass
        logger.info("Pompe nettoyée")

# Instance globale
water_pump = WaterPump(config.gpio.PUMP_RELAY_PIN)