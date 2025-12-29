#!/usr/bin/env python3
"""
Test simple du système
"""
import sys
import os

# Ajoute le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sensors.sensor_manager import sensor_manager
    print("✅ Modules importés avec succès")
    
    # Test des capteurs
    data = sensor_manager.read_all()
    print(f"📊 Données capteurs: {data}")
    
    if data["success"]:
        print("🎉 Système fonctionnel !")
        for name, sensor_data in data["sensors"].items():
            if sensor_data:
                print(f"  {name}: {sensor_data}")
    else:
        print("⚠️  Certains capteurs ne répondent pas")
        
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    print("\nSolution rapide :")
    print("1. Installe les dépendances minimales :")
    print("   pip install Flask requests")
    print("2. Le système passera en mode simulation")
    
except Exception as e:
    print(f"❌ Erreur: {e}")