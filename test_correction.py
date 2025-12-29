#!/usr/bin/env python3
"""
Test après correction capteur pluie
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from sensors.sensor_manager import sensor_manager

print("🧪 TEST APRÈS CORRECTION CAPTEUR PLUIE")
print("=" * 50)

# Recharger le manager de capteurs
sensor_manager.sensors['rain'] = None
sensor_manager.initialize_sensors()

# Lire les capteurs
data = sensor_manager.read_all()
print("📊 Données capteurs CORRIGÉES:")

for name, sensor_data in data["sensors"].items():
    if sensor_data:
        if name == "rain":
            print(f"  🌧️  {name}:")
            print(f"     Pluie détectée: {sensor_data.get('rain_detected')}")
            print(f"     Valeur brute: {sensor_data.get('raw_value')}")
            print(f"     État: {sensor_data.get('state')}")
            print(f"     → Doit être: False (pas de pluie)")
        elif name == "water_level":
            print(f"  💧 {name}:")
            print(f"     Eau détectée: {sensor_data.get('water_detected')}")
            print(f"     Pourcentage: {sensor_data.get('water_percent')}%")
            print(f"     → Normal: False (réservoir vide)")
        else:
            print(f"  ✅ {name}: {sensor_data}")

# Test logique
print("\n🧠 SIMULATION SCÉNARIO COMPLET:")
print("(Ajoute de l'eau dans le réservoir pour tester l'irrigation)")

soil = data["sensors"].get("soil", {})
rain = data["sensors"].get("rain", {})
water = data["sensors"].get("water_level", {})

soil_moisture = soil.get("moisture_percent", 100)
rain_detected = rain.get("rain_detected", False)
water_percent = water.get("water_percent", 0)

print(f"\nConditions actuelles:")
print(f"  1. Humidité sol: {soil_moisture}% {'🔴 TROP SEC' if soil_moisture < 40 else '✅ OK'}")
print(f"  2. Pluie: {'🔴 DÉTECTÉE' if rain_detected else '✅ PAS DE PLUIE'}")
print(f"  3. Eau réservoir: {water_percent}% {'🔴 INSUFFISANT' if water_percent < 20 else '✅ SUFFISANT'}")

print("\n🎯 Pour tester l'irrigation automatique:")
print("   - Humidité sol doit être < 40%")
print("   - Pas de pluie détectée")
print("   - Eau réservoir > 20%")
print("\n🔧 Test manuel possible via API: POST /api/irrigate")