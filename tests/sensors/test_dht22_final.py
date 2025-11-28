#!/usr/bin/env python3
"""
TEST DHT22 - Version Finale
Capteur température/humidité sur GPIO17
"""

import time
import board
import adafruit_dht

def test_dht22_final():
    """Test final du capteur DHT22"""
    print("🌡️  TEST DHT22 - CAPTEUR TEMPÉRATURE/HUMIDITÉ")
    print("=" * 50)
    print("📍 GPIO17 (Broche physique 11)")
    print("💡 Les erreurs occasionnelles sont normales")
    
    # Initialisation
    dht_device = adafruit_dht.DHT22(board.D17)
    print("✅ DHT22 initialisé")
    
    successful_readings = 0
    total_attempts = 0
    
    try:
        print("\n🔍 Début des lectures...")
        while total_attempts < 10:
            total_attempts += 1
            
            try:
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                
                if temperature is not None and humidity is not None:
                    successful_readings += 1
                    print(f"✅ Lecture {total_attempts}:")
                    print(f"   🌡️  {temperature:.1f}°C")
                    print(f"   💧 {humidity:.1f}%")
                    
                    # Validation des plages
                    if 15 <= temperature <= 35 and 30 <= humidity <= 80:
                        print("   ✅ Plages normales")
                    else:
                        print("   ⚠️  Valeurs hors plage normale")
                        
                else:
                    print(f"❌ Lecture {total_attempts}: Données invalides")
                    
            except RuntimeError:
                print(f"⚠️  Lecture {total_attempts}: Erreur timing")
            except Exception as e:
                print(f"🔴 Lecture {total_attempts}: {e}")
                break
                
            print("-" * 35)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu")
    finally:
        dht_device.exit()
        print("🧹 Capteur nettoyé")
    
    # Résultats
    print(f"\n📊 RÉSULTATS: {successful_readings}/{total_attempts} lectures valides")
    
    if successful_readings >= 3:
        print("🎉 DHT22 FONCTIONNE!")
        return True
    else:
        print("💡 Vérifiez le câblage DHT22")
        return False

if __name__ == "__main__":
    success = test_dht22_final()
    if success:
        print("\n🚀 Capteur DHT22 validé pour le projet")