"""
Gestion des LEDs d'état - UTILISE GPIO CENTRAL
"""
import time
import logging
from typing import Dict, Any
from config.settings import config
from core.gpio_manager import gpio_central

logger = logging.getLogger(__name__)

class StatusLED:
    def __init__(self):
        self.current_state = "IDLE"
        logger.info("✅ LEDs d'état initialisées - UTILISE GPIO CENTRAL")
    
    def set_system_state(self, state: str, **kwargs):
        state = state.upper()
        self.current_state = state
        
        if state == "IDLE":
            soil_ok = kwargs.get('soil_ok', False)
            gpio_central.set_led_green(soil_ok)
            gpio_central.set_led_white(kwargs.get('online', False))
            
        elif state == "IRRIGATING":
            gpio_central.set_led_yellow(True, blink=True, blink_interval=0.5)
            logger.info("🟡 Irrigation en cours")
            
        elif state == "ERROR":
            gpio_central.set_led_red(True, blink=True, blink_interval=0.3)
            logger.error("🔴 Erreur système")
            
        elif state == "NO_WATER":
            gpio_central.set_led_red(True)
            logger.warning("🔴 Pas d'eau détecté")
            
        elif state == "OFFLINE":
            gpio_central.set_led_white(False)
            logger.info("⚪ Mode hors ligne")
            
        elif state == "ONLINE":
            gpio_central.set_led_white(True)
            logger.info("⚪ Mode en ligne")
            
        elif state == "SOIL_DRY":
            gpio_central.set_led_green(False)
            logger.warning("💧 Sol trop sec")
            
        elif state == "SOIL_OK":
            gpio_central.set_led_green(True)
            logger.info("💚 Humidité sol optimale")
            
        else:
            logger.warning(f"État inconnu: {state}")
    
    def update_soil_status(self, moisture_percent: float):
        """
        Met à jour la LED verte en fonction de l'humidité du sol
        """
        min_moisture = config.plant.min_moisture
        optimal_moisture = config.plant.optimal_moisture
        
        if moisture_percent >= optimal_moisture:
            self.set_system_state("SOIL_OK")
        elif moisture_percent < min_moisture:
            self.set_system_state("SOIL_DRY")
        else:
            # Humidité entre min et optimal - LED verte allumée
            gpio_central.set_led_green(True)
    
    def test_all_leds(self):
        logger.info("💡 Test de toutes les LEDs...")
        
        gpio_central.set_led_red(True)
        time.sleep(1)
        gpio_central.set_led_red(False)
        
        gpio_central.set_led_green(True)
        time.sleep(1)
        gpio_central.set_led_green(False)
        
        gpio_central.set_led_yellow(True)
        time.sleep(1)
        gpio_central.set_led_yellow(False)
        
        gpio_central.set_led_white(True)
        time.sleep(1)
        gpio_central.set_led_white(False)
        
        logger.info("✅ Test LEDs terminé")
    
    def get_status(self) -> Dict[str, Any]:
        led_status = gpio_central.get_led_status()
        return {
            "current_state": self.current_state,
            "leds": led_status
        }
    def cleanup(self):
        """Éteint toutes les LEDs"""
        from core.gpio_manager import gpio_central
        gpio_central.set_led_red(False)
        gpio_central.set_led_green(False)
        gpio_central.set_led_yellow(False)
        gpio_central.set_led_white(False)   
# Instance globale
status_led = StatusLED()