#!/usr/bin/env python3
"""
Test rapide - évite les imports complexes
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 TEST RAPIDE DU SYSTÈME")
print("=" * 50)

# Test 1: Configuration
try:
    from config.settings import config
    print("✅ Configuration chargée")
    print(f"   Plante: {config.plant.name}")
    print(f"   GPIO Pompe: {config.gpio.PUMP_RELAY_PIN}")
except Exception as e:
    print(f"❌ Erreur config: {e}")

print()

# Test 2: Capteurs
try:
    from sensors.sensor_manager import sensor_manager
    data = sensor_manager.read_all()
    print("✅ Capteurs lus")
    print(f"   Succès: {data['success']}")
    
    if data["success"]:
        soil = data["sensors"].get("soil", {})
        rain = data["sensors"].get("rain", {})
        print(f"   Humidité sol: {soil.get('moisture_percent', 'N/A')}%")
        print(f"   Pluie détectée: {rain.get('rain_detected', 'N/A')}")
        
except Exception as e:
    print(f"❌ Erreur capteurs: {e}")

print()

# Test 3: Logique simplifiée
try:
    from config.settings import config
    
    # Simuler la logique
    if data.get("success"):
        soil = data["sensors"].get("soil", {})
        rain = data["sensors"].get("rain", {})
        water = data["sensors"].get("water_level", {})
        
        soil_moisture = soil.get("moisture_percent", 50)
        rain_detected = rain.get("rain_detected", False)
        water_percent = water.get("water_percent", 0)
        
        print("🧠 LOGIQUE SIMPLIFIÉE:")
        print(f"   1. Sol {soil_moisture}% < {config.plant.min_moisture}% ? {'OUI' if soil_moisture < config.plant.min_moisture else 'NON'}")
        print(f"   2. Pluie détectée ? {'OUI' if rain_detected else 'NON'}")
        print(f"   3. Eau réservoir {water_percent}% > {config.irrigation.MIN_WATER_LEVEL}% ? {'OUI' if water_percent > config.irrigation.MIN_WATER_LEVEL else 'NON'}")
        
        # Décision simple
        should_irrigate = (
            soil_moisture < config.plant.min_moisture and
            not rain_detected and
            water_percent > config.irrigation.MIN_WATER_LEVEL
        )
        
        print(f"\n🎯 DÉCISION: {'IRRIGUER' if should_irrigate else 'ATTENDRE'}")
        
except Exception as e:
    print(f"❌ Erreur logique: {e}")

print("\n✅ Test terminé")