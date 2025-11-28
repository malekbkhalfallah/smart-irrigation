#!/usr/bin/env python3
"""
TEST RAINDROP MODULE - Version Finale
Capteur de pluie sur GPIO27
"""

import time
import lgpio

def test_raindrop_final():
    """Test final du capteur de pluie"""
    print("🌧️  TEST CAPTEUR DE PLUIE")
    print("=" * 45)
    print("📍 GPIO27 (Broche physique 13)")
    print("💧 Mouillez les capteurs pour tester")
    
    try:
        # Initialisation
        chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(chip, 27)
        print("✅ Capteur de pluie initialisé")
        
        dry_count = 0
        rain_count = 0
        
        print("\n🔍 Surveillance pendant 20 secondes...")
        print("💧 Simulez la pluie en mouillant les capteurs")
        print("-" * 40)
        
        for i in range(20):
            # Lecture du capteur
            sensor_value = lgpio.gpio_read(chip, 27)
            rain_detected = sensor_value == 0  # 0 = pluie détectée
            
            if rain_detected:
                rain_count += 1
                status = "🌧️  PLUIE DÉTECTÉE"
            else:
                dry_count += 1
                status = "☀️  PAS DE PLUIE"
            
            print(f"⏱️  {i+1}s: {status} (Valeur: {sensor_value})")
            time.sleep(1)
        
        # Nettoyage
        lgpio.gpiochip_close(chip)
        
        # Résultats
        print(f"\n📊 RÉSULTATS:")
        print(f"   ☀️  Temps sec: {dry_count}s")
        print(f"   🌧️  Temps pluie: {rain_count}s")
        
        if rain_count > 0:
            print("🎉 Capteur de pluie FONCTIONNE!")
            return True
        else:
            print("💡 Le capteur n'a pas détecté de pluie")
            print("   Essayez de mouiller les capteurs avec de l'eau")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = test_raindrop_final()
    if success:
        print("\n🚀 Capteur de pluie validé pour le projet")