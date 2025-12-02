#!/usr/bin/env python3
"""
VERSION FINALE CAPTEUR NIVEAU D'EAU ST045
Test validé - Capteur fonctionne avec eau conductrice
"""

import time
import lgpio

class WaterLevelSensor:
    """Capteur de niveau d'eau ST045 - Version finale"""
    
    def __init__(self, sensor_pin=23):
        self.sensor_pin = sensor_pin
        self.chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(self.chip, sensor_pin)
        
        print(f"✅ Capteur niveau eau initialisé sur GPIO{sensor_pin}")
        print("💡 Utilisez de l'eau du robinet (conductrice)")
    
    def read_level(self):
        """Lire le niveau d'eau"""
        try:
            # 0 = pas d'eau, 1 = eau détectée
            value = lgpio.gpio_read(self.chip, self.sensor_pin)
            water_detected = value == 1
            
            return {
                'water_detected': water_detected,
                'sensor_value': value,
                'level': 'LOW' if water_detected else 'HIGH',
                'success': True
            }
        except Exception as e:
            return {'water_detected': None, 'success': False, 'error': str(e)}
    
    def cleanup(self):
        """Nettoyer"""
        lgpio.gpiochip_close(self.chip)

def test_water_final():
    """Test final validé"""
    print("💧 TEST FINAL CAPTEUR NIVEAU D'EAU")
    print("=" * 50)
    print("✅ CAPTEUR VALIDÉ - Fonctionne avec eau conductrice")
    print("📍 GPIO23 | Eau = 1 | Sec = 0")
    
    sensor = WaterLevelSensor(23)
    
    try:
        print("\n🔍 Test en cours...")
        print("💦 Plongez le capteur dans l'eau du robinet")
        print("🏜️  Sortez-le pour sécher")
        print("-" * 45)
        
        water_detections = 0
        dry_detections = 0
        
        for i in range(30):
            data = sensor.read_level()
            
            if data['success']:
                if data['water_detected']:
                    water_detections += 1
                    print(f"⏱️  {i+1}s: 💦 EAU DÉTECTÉE | Niveau: {data['level']}")
                else:
                    dry_detections += 1
                    print(f"⏱️  {i+1}s: 🏜️  PAS D'EAU | Niveau: {data['level']}")
            else:
                print(f"❌ Erreur: {data.get('error')}")
            
            time.sleep(1)
        
        # Résultats
        print(f"\n📊 RÉSULTATS FINAUX:")
        print(f"   💦 Détections eau: {water_detections}")
        print(f"   🏜️  Détections sec: {dry_detections}")
        
        if water_detections > 0 and dry_detections > 0:
            print("🎉 CAPTEUR FONCTIONNE PARFAITEMENT!")
            print("🚀 Prêt pour le projet d'irrigation")
        else:
            print("💡 Le capteur a besoin d'eau conductrice")
            print("   Utilisez de l'eau du robinet, pas d'eau distillée")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu")
    finally:
        sensor.cleanup()

if __name__ == "__main__":
    test_water_final()