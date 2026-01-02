"""
Gestion centralisée et unique des GPIO pour Raspberry Pi 5 (lgpio) - HARDWARE RÉEL
TOUTES les opérations GPIO doivent passer par cette classe!
"""
import time
import threading
import logging
import sys
from typing import Optional, Dict, Any
from config.settings import config

logger = logging.getLogger(__name__)

# VARIABLE GLOBALE pour suivre l'initialisation
_GPIO_INITIALIZED = False

class GPIOCentralManager:
    """Singleton CENTRAL pour gérer TOUS les GPIO - HARDWARE RÉEL"""
    
    _instance: Optional['GPIOCentralManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # CORRECTION DÉFINITIVE: Vérifier l'initialisation globale
        global _GPIO_INITIALIZED
        
        if _GPIO_INITIALIZED:
            logger.info("✅ Réutilisation de l'instance GPIO existante")
            # Réinitialiser les attributs pour éviter les erreurs
            if not hasattr(self, '_chip'):
                self._chip = None
            if not hasattr(self, '_pin_registry'):
                self._pin_registry = {}
            return
        
        _GPIO_INITIALIZED = True
        
        self._chip = None
        
        # FORCEMENT HARDWARE RÉEL
        try:
            import lgpio
            self._chip = lgpio.gpiochip_open(0)
            logger.info("✅ Chip GPIO central ouvert (lgpio) - HARDWARE RÉEL")
        except ImportError:
            logger.error("❌ lgpio non installé. Exécutez: pip install lgpio")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur ouverture chip GPIO: {e}")
            raise
        
        # Registre des pins et de leurs utilisateurs
        self._pin_registry = {}
        
        # États LEDs
        self._led_states = {
            'red': False,
            'green': False,
            'yellow': False,
            'white': False
        }
        
        # Threads de clignotement
        self._blink_threads = {}
        self._blink_stop_events = {}
        
        # Initialiser le registre
        self._initialize_pin_registry()
        
        # Configurer tous les pins une seule fois
        self._setup_all_pins()
    
    def _initialize_pin_registry(self):
        """Initialise le registre des pins"""
        gpio = config.gpio
        
        # LEDs (sorties)
        self._pin_registry[gpio.LED_RED_PIN] = {"type": "output", "users": ["led_red"], "state": False}
        self._pin_registry[gpio.LED_GREEN_PIN] = {"type": "output", "users": ["led_green"], "state": False}
        self._pin_registry[gpio.LED_YELLOW_PIN] = {"type": "output", "users": ["led_yellow"], "state": False}
        self._pin_registry[gpio.LED_WHITE_PIN] = {"type": "output", "users": ["led_white"], "state": False}
        
        # Capteurs (entrées)
        self._pin_registry[gpio.SOIL_MOISTURE_PIN] = {"type": "input", "users": ["soil_sensor"], "state": None}
        self._pin_registry[gpio.DHT22_PIN] = {"type": "input", "users": ["dht22_sensor"], "state": None}
        self._pin_registry[gpio.RAINDROP_PIN] = {"type": "input", "users": ["rain_sensor"], "state": None}
        self._pin_registry[gpio.WATER_LEVEL_PIN] = {"type": "input", "users": ["water_sensor"], "state": None}
        
        # Actionneurs (sorties)
        self._pin_registry[gpio.PUMP_RELAY_PIN] = {"type": "output", "users": ["water_pump"], "state": False}
    
    def _setup_all_pins(self):
        """Configure tous les pins GPIO une seule fois"""
        print("\n🔧 CONFIGURATION CENTRALE GPIO RÉELLE:")
        print("=" * 40)
        
        import lgpio
        
        for pin, info in self._pin_registry.items():
            try:
                if info["type"] == "output":
                    lgpio.gpio_claim_output(self._chip, pin)
                    lgpio.gpio_write(self._chip, pin, 0)  # Éteint par défaut
                    info["state"] = False
                    print(f"🔌 GPIO{pin:3} -> SORTIE   ({', '.join(info['users'])})")
                elif info["type"] == "input":
                    lgpio.gpio_claim_input(self._chip, pin)
                    print(f"🔌 GPIO{pin:3} -> ENTREE   ({', '.join(info['users'])})")
            except Exception as e:
                logger.warning(f"⚠️ Erreur configuration GPIO{pin}: {e}")
        
        print("=" * 40)
        logger.info("✅ Tous les pins GPIO configurés centralement - HARDWARE RÉEL")
    
    # === API PUBLIQUE ===
    
    def write(self, pin: int, value: bool):
        """Écrit une valeur sur une sortie - HARDWARE RÉEL"""
        if self._chip is None:
            logger.error("❌ Chip GPIO non initialisé")
            return
        
        import lgpio
        try:
            lgpio.gpio_write(self._chip, pin, 1 if value else 0)
            
            if pin in self._pin_registry:
                self._pin_registry[pin]["state"] = value
            
            logger.debug(f"GPIO {pin} → {'HIGH' if value else 'LOW'}")
        except Exception as e:
            logger.error(f"❌ Erreur écriture GPIO{pin}: {e}")
    
    def read(self, pin: int) -> bool:
        """Lit une valeur d'entrée digitale - HARDWARE RÉEL"""
        if self._chip is None:
            logger.error("❌ Chip GPIO non initialisé")
            return False
        
        import lgpio
        try:
            value = bool(lgpio.gpio_read(self._chip, pin))
            
            if pin in self._pin_registry:
                self._pin_registry[pin]["state"] = value
            
            return value
        except Exception as e:
            logger.error(f"❌ Erreur lecture GPIO{pin}: {e}")
            return False
    
    # Méthodes pour les LEDs
    
    def set_led_red(self, state: bool, blink: bool = False, blink_interval: float = 0.5):
        """Contrôle la LED rouge"""
        self._led_states['red'] = state
        pin = config.gpio.LED_RED_PIN
        
        if blink:
            self._start_blink('red', pin, blink_interval)
        else:
            self._stop_blink('red')
            self.write(pin, state)
    
    def set_led_green(self, state: bool):
        """Contrôle la LED verte"""
        self._led_states['green'] = state
        self.write(config.gpio.LED_GREEN_PIN, state)
    
    def set_led_yellow(self, state: bool, blink: bool = False, blink_interval: float = 0.5):
        """Contrôle la LED jaune"""
        self._led_states['yellow'] = state
        pin = config.gpio.LED_YELLOW_PIN
        
        if blink:
            self._start_blink('yellow', pin, blink_interval)
        else:
            self._stop_blink('yellow')
            self.write(pin, state)
    
    def set_led_white(self, state: bool):
        """Contrôle la LED blanche"""
        self._led_states['white'] = state
        self.write(config.gpio.LED_WHITE_PIN, state)
    
    def _start_blink(self, led_name: str, pin: int, interval: float):
        """Démarre le clignotement d'une LED"""
        if led_name in self._blink_threads:
            return
        
        stop_event = threading.Event()
        self._blink_stop_events[led_name] = stop_event
        
        def blink_task():
            while not stop_event.is_set():
                try:
                    self.write(pin, True)
                    stop_event.wait(interval)
                    if stop_event.is_set():
                        break
                    
                    self.write(pin, False)
                    stop_event.wait(interval)
                except Exception as e:
                    logger.error(f"Erreur clignotement LED {led_name}: {e}")
                    break
        
        thread = threading.Thread(target=blink_task, daemon=True, name=f"blink_{led_name}")
        self._blink_threads[led_name] = thread
        thread.start()
    
    def _stop_blink(self, led_name: str):
        """Arrête le clignotement d'une LED"""
        if led_name in self._blink_stop_events:
            self._blink_stop_events[led_name].set()
        
        if led_name in self._blink_threads:
            thread = self._blink_threads[led_name]
            if thread.is_alive():
                thread.join(timeout=1)
            del self._blink_threads[led_name]
        
        if led_name in self._blink_stop_events:
            del self._blink_stop_events[led_name]
    
    # Méthodes utilitaires
    
    def get_pin_state(self, pin: int):
        """Retourne l'état d'un pin"""
        if pin in self._pin_registry:
            return self._pin_registry[pin]["state"]
        return None
    
    def get_led_status(self) -> Dict[str, bool]:
        """Retourne l'état de toutes les LEDs"""
        return self._led_states.copy()
    
    def get_gpio_status(self) -> Dict[str, Any]:
        """Retourne le statut de tous les GPIO"""
        status = {
            'leds': self._led_states.copy(),
            'pins': {}
        }
        
        for pin, info in self._pin_registry.items():
            status['pins'][pin] = {
                'type': info['type'],
                'users': info['users'],
                'state': self.get_pin_state(pin)
            }
        
        return status
    
    def cleanup(self):
        """Nettoie toutes les broches GPIO - HARDWARE RÉEL"""
        global _GPIO_INITIALIZED
        
        # Arrêter tous les clignotements
        for led_name in list(self._blink_threads.keys()):
            self._stop_blink(led_name)
        
        # Éteindre toutes les sorties
        for pin, info in self._pin_registry.items():
            if info["type"] == "output":
                try:
                    self.write(pin, False)
                except:
                    pass
        
        # Fermer le chip
        if self._chip is not None:
            try:
                import lgpio
                lgpio.gpiochip_close(self._chip)
                logger.info("✅ Chip GPIO central fermé - HARDWARE RÉEL")
            except:
                logger.warning("⚠️ Erreur fermeture chip GPIO")
            finally:
                self._chip = None
        
        self._pin_registry.clear()
        _GPIO_INITIALIZED = False
    
    def test_leds(self):
        """Teste toutes les LEDs"""
        logger.info("💡 Test de toutes les LEDs...")
        
        try:
            self.set_led_red(True)
            time.sleep(0.5)
            self.set_led_red(False)
            
            self.set_led_green(True)
            time.sleep(0.5)
            self.set_led_green(False)
            
            self.set_led_yellow(True)
            time.sleep(0.5)
            self.set_led_yellow(False)
            
            self.set_led_white(True)
            time.sleep(0.5)
            self.set_led_white(False)
            
            logger.info("✅ Test LEDs terminé")
        except Exception as e:
            logger.error(f"❌ Erreur test LEDs: {e}")

# Instance globale unique
gpio_central = GPIOCentralManager()