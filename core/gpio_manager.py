"""
Gestion centralisée des GPIO pour éviter les conflits
"""
import RPi.GPIO as GPIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class GPIOManager:
    """Singleton pour gérer les GPIO"""
    
    _instance: Optional['GPIOManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Initialisation GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self._setup_done = False
        self._pins_in_use = set()
        self._initialized = True
        logger.info("Gestionnaire GPIO initialisé")
    
    def setup_output(self, pin: int, initial: bool = False) -> None:
        """Configure une broche en sortie"""
        if pin in self._pins_in_use:
            logger.warning(f"GPIO {pin} déjà configuré")
            return
            
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, initial)
        self._pins_in_use.add(pin)
        logger.debug(f"GPIO {pin} configuré en sortie (initial: {initial})")
    
    def setup_input(self, pin: int, pull_up_down: int = GPIO.PUD_OFF) -> None:
        """Configure une broche en entrée"""
        if pin in self._pins_in_use:
            logger.warning(f"GPIO {pin} déjà configuré")
            return
            
        GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)
        self._pins_in_use.add(pin)
        logger.debug(f"GPIO {pin} configuré en entrée")
    
    def setup_adc(self, pin: int) -> None:
        """Configure une broche pour ADC (via MCP3008 ou ADS1115)"""
        # Ici tu devras adapter selon ton convertisseur ADC
        # Pour l'instant, on fait simple
        self.setup_input(pin)
        logger.debug(f"GPIO {pin} configuré pour ADC")
    
    def write(self, pin: int, value: bool) -> None:
        """Écrit une valeur sur une sortie"""
        if pin not in self._pins_in_use:
            logger.error(f"GPIO {pin} non configuré!")
            return
            
        GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)
        logger.debug(f"GPIO {pin} -> {'HIGH' if value else 'LOW'}")
    
    def read(self, pin: int) -> bool:
        """Lit une valeur d'entrée digitale"""
        if pin not in self._pins_in_use:
            logger.error(f"GPIO {pin} non configuré!")
            return False
            
        value = GPIO.input(pin)
        logger.debug(f"GPIO {pin} <- {'HIGH' if value else 'LOW'}")
        return bool(value)
    
    def read_analog(self, pin: int) -> float:
        """Lit une valeur analogique (à adapter selon ton ADC)"""
        # Placeholder - à remplacer par ta logique ADC
        # Exemple avec ADS1115 ou MCP3008
        logger.debug(f"Lecture analogique sur GPIO {pin}")
        return 0.0
    
    def cleanup(self) -> None:
        """Nettoie toutes les broches GPIO"""
        GPIO.cleanup()
        self._pins_in_use.clear()
        logger.info("GPIO nettoyés")
    
    def cleanup_pin(self, pin: int) -> None:
        """Nettoie une broche spécifique"""
        GPIO.cleanup(pin)
        if pin in self._pins_in_use:
            self._pins_in_use.remove(pin)
        logger.debug(f"GPIO {pin} nettoyé")

# Instance globale
gpio_manager = GPIOManager()