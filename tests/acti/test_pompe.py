#!/usr/bin/env python3

from gpiozero import OutputDevice
import time

# Configuration - même broche
RELAY_GPIO = 17

# Initialisation avec gpiozero
relay = OutputDevice(RELAY_GPIO, active_high=True, initial_value=False)

try:
    print("Test pompe avec gpiozero - Ctrl+C pour arrêter")
    while True:
        print("-> Activation de la pompe (Relais ON)")
        relay.on()  # Active le relais
        time.sleep(2)
        
        print("-> Arrêt de la pompe (Relais OFF)")
        relay.off()  # Désactive le relais
        time.sleep(2)

except KeyboardInterrupt:
    print("\nArrêt du programme par l'utilisateur.")

finally:
    relay.off()  # S'assure que le relais est éteint
    print("Pompe arrêtée, programme terminé.")