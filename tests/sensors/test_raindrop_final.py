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
    print("⚠️  Note: Le capteur peut être à logique inversée")
    
    try:
        # Initialisation
        chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(chip, 27)
        print("✅ Capteur de pluie initialisé")
        
        # Test initial
        initial_value = lgpio.gpio_read(chip, 27)
        print(f"📊 Valeur initiale au repos: {initial_value}")
        print("0 = Pluie détectée | 1 = Pas de pluie")
        
        dry_count = 0
        rain_count = 0
        
        print("\n🔍 Surveillance pendant 30 secondes...")
        print("💧 Simulez la pluie en mouillant les capteurs")
        print("-" * 40)
        
        for i in range(30):
            # Lecture du capteur
            sensor_value = lgpio.gpio_read(chip, 27)
            
            # Essayez d'inverser la logique si nécessaire
            # Option 1: Logique normale (décommenter celle qui marche)
            # rain_detected = sensor_value == 0  # 0 = pluie
            # Option 2: Logique inversée
            rain_detected = sensor_value == 1  # 1 = pluie (inversé)
            
            if rain_detected:
                rain_count += 1
                status = "🌧️  PLUIE DÉTECTÉE"
            else:
                dry_count += 1
                status = "☀️  PAS DE PLUIE"
            
            print(f"⏱️  {i+1}s: {status} (Valeur brute: {sensor_value})")
            time.sleep(1)
        
        # Nettoyage
        lgpio.gpiochip_close(chip)
        
        # Résultats
        print(f"\n📊 RÉSULTATS:")
        print(f"   Valeur initiale: {initial_value}")
        print(f"   ☀️  Temps sec: {dry_count}s")
        print(f"   🌧️  Temps pluie: {rain_count}s")
        
        if dry_count == 30 and initial_value == 0:
            print("\n⚠️  SITUATION: Le capteur indique toujours 'pluie'")
            print("   1. Essayez d'inverser les fils du capteur")
            print("   2. Vérifiez le potentiomètre sur le module")
            print("   3. Testez avec la logique inversée dans le code")
            return False
        elif rain_count > 0 and dry_count > 0:
            print("🎉 Capteur de pluie FONCTIONNE! (mais logique peut-être inversée)")
            return True
        else:
            print("💡 Aucun changement détecté")
            print("   Essayez de mouiller les capteurs ou d'ajuster le potentiomètre")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = test_raindrop_final()
    if success:
        print("\n🚀 Capteur de pluie validé pour le projet")
    else:
        print("\n🔧 Des ajustements sont nécessaires")