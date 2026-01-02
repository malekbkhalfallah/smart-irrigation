#!/usr/bin/env python3
"""
Test GPIO immédiat
"""
import time
from core.gpio_manager import gpio_central

print("🔧 TEST GPIO DIRECT")
print("=" * 40)

# Test LEDs
print("💡 Test des LEDs...")
gpio_central.test_leds()

# Test lecture capteurs
print("\n📊 Lecture capteurs...")
print(f"💧 Sol: {gpio_central.read(24)}")
print(f"💦 Eau: {gpio_central.read(23)}")
print(f"🌧️ Pluie: {gpio_central.read(27)}")

print("\n✅ Test terminé")