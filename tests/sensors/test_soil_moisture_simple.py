#!/usr/bin/env python3
"""
VERSION ULTRA-SIMPLE - Capteur humidité sol
Affiche directement SEC/HUMIDE sans réglage
"""

import time
import lgpio

print("🌱 CAPTEUR HUMIDITÉ SOL - VERSION SIMPLE")
print("=" * 45)

# Setup GPIO
chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(chip, 24)

print("📍 GPIO24 (Broche 18)")
print("🎯 0 = HUMIDE, 1 = SEC")
print("💧 Testez avec eau/terre/air")
print("🛑 Ctrl+C pour arrêter\n")

try:
    secondes = 0
    while True:
        # Lecture directe
        valeur = lgpio.gpio_read(chip, 24)
        
        if valeur == 0:
            print(f"⏱️  {secondes}s: 💧 HUMIDE - Terre humide")
        else:
            print(f"⏱️  {secondes}s: 🏜️  SEC - Besoin d'arrosage")
        
        secondes += 1
        time.sleep(1)

except KeyboardInterrupt:
    print("\n✅ Test terminé")
finally:
    lgpio.gpiochip_close(chip)