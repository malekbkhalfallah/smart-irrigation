"""
Test GPIO simple sans conflits
"""
import time
import RPi.GPIO as GPIO

print("🧪 TEST GPIO ISOLÉ")
print("=" * 50)

# Liste des pins utilisés
pins = [17, 23, 24, 26, 27]
GPIO.setmode(GPIO.BCM)

for pin in pins:
    try:
        GPIO.setup(pin, GPIO.IN)
        print(f"GPIO{pin}: ✅ Configuré en INPUT")
    except Exception as e:
        print(f"GPIO{pin}: ❌ Erreur: {e}")

# Test lecture
print("\n📊 Lecture pins:")
for pin in pins:
    try:
        value = GPIO.input(pin)
        print(f"GPIO{pin}: {value}")
    except:
        print(f"GPIO{pin}: Erreur lecture")

GPIO.cleanup()
print("\n✅ Test terminé - GPIO nettoyés")
