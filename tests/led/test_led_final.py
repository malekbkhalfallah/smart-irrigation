#!/usr/bin/env python3
"""
TEST LED - Version Finale
Valide la communication GPIO avec la Raspberry Pi 5
"""

import time
import lgpio

def test_led_final():
    """Test final de la LED sur GPIO4"""
    print("💡 TEST LED - RASPBERRY PI 5")
    print("=" * 40)
    print("📍 GPIO4 (Broche physique 7)")
    print("🎯 Validation communication GPIO")
    
    try:
        # Initialisation
        chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(chip, 4)
        print("✅ GPIO initialisé")
        
        # Test de clignotement
        print("🔴 Début du test...")
        for i in range(6):
            lgpio.gpio_write(chip, 4, 1)  # ON
            print(f"   Cycle {i+1}: 🔴 ALLUMÉ")
            time.sleep(0.5)
            
            lgpio.gpio_write(chip, 4, 0)  # OFF
            print(f"   Cycle {i+1}: ⚫ ÉTEINT")
            time.sleep(0.5)
        
        # Nettoyage
        lgpio.gpiochip_close(chip)
        
        print("✅ TEST LED RÉUSSI!")
        print("🎉 Communication GPIO validée")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = test_led_final()
    if success:
        print("\n🚀 Raspberry Pi 5 prête pour les capteurs")
    else:
        print("\n💡 Vérifiez le câblage LED")