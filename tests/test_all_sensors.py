#!/usr/bin/env python3
"""
TEST COMPLET - Tous les capteurs
Version finale pour validation système
"""

import time
import lgpio
import board
import adafruit_dht

def test_led():
    """Test de la LED"""
    print("1. 💡 TEST LED...")
    try:
        chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(chip, 17)
        
        lgpio.gpio_write(chip, 17, 1)
        time.sleep(1)
        lgpio.gpio_write(chip, 17, 0)
        
        lgpio.gpiochip_close(chip)
        print("   ✅ LED fonctionne")
        return True
    except Exception as e:
        print(f"   ❌ LED: {e}")
        return False

def test_dht22():
    """Test du DHT22"""
    print("2. 🌡️  TEST DHT22...")
    try:
        dht_device = adafruit_dht.DHT22(board.D17)
        
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        
        dht_device.exit()
        
        if temperature is not None and humidity is not None:
            print(f"   ✅ DHT22: {temperature:.1f}°C, {humidity:.1f}%")
            return True
        else:
            print("   ❌ DHT22: Données invalides")
            return False
            
    except Exception as e:
        print(f"   ❌ DHT22: {e}")
        return False

def test_raindrop():
    """Test du capteur de pluie"""
    print("3. 🌧️  TEST CAPTEUR DE PLUIE...")
    try:
        chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(chip, 27)
        
        sensor_value = lgpio.gpio_read(chip, 27)
        
        lgpio.gpiochip_close(chip)
        
        print(f"   ✅ Raindrop: Valeur = {sensor_value} (0=pluie, 1=sec)")
        return True
        
    except Exception as e:
        print(f"   ❌ Raindrop: {e}")
        return False

def main():
    """Test complet du système"""
    print("🚀 TEST COMPLET - SYSTÈME IRRIGATION INTELLIGENTE")
    print("=" * 55)
    print("📍 Validation de tous les composants matériels")
    print("🛑 Ctrl+C pour arrêter\n")
    
    results = []
    
    # Tests individuels
    results.append(test_led())
    time.sleep(1)
    
    results.append(test_dht22())
    time.sleep(1)
    
    results.append(test_raindrop())
    
    # Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS:")
    success_count = sum(results)
    total_tests = len(results)
    
    print(f"   ✅ Tests réussis: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 SYSTÈME COMPLET VALIDÉ!")
        print("🚀 Tous les capteurs sont fonctionnels")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("   1. Développement logique d'irrigation")
        print("   2. Application Flutter")
        print("   3. Intégration Firebase")
    else:
        print("💡 Certains composants nécessitent une vérification")

if __name__ == "__main__":
    main()