#!/usr/bin/env python3
"""
VERSION INTELLIGENTE - Avec recommandations d'arrosage
"""

import time
import lgpio

class SmartSoilSensor:
    def __init__(self, pin=23):
        self.pin = pin
        self.chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(self.chip, pin)
        
        # Historique pour détection de tendance
        self.history = []
        self.max_history = 10
        
        print("🌱 CAPTEUR HUMIDITÉ SOL INTELLIGENT")
        print("📍 GPIO23 | 0=HUMIDE, 1=SEC")
    
    def read_state(self):
        """Lire l'état actuel"""
        value = lgpio.gpio_read(self.chip, self.pin)
        
        # Ajouter à l'historique
        self.history.append(value)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return value
    
    def get_trend(self):
        """Analyser la tendance"""
        if len(self.history) < 3:
            return "STABLE"
        
        # Compter les changements récents
        recent = self.history[-3:]
        changes = sum(1 for i in range(1, len(recent)) if recent[i] != recent[i-1])
        
        if changes >= 2:
            return "VARIABLE"
        elif all(v == 0 for v in recent):
            return "HUMIDE_STABLE" 
        elif all(v == 1 for v in recent):
            return "SEC_STABLE"
        else:
            return "STABLE"
    
    def get_recommendation(self, value, trend):
        """Obtenir une recommandation intelligente"""
        if value == 0:  # HUMIDE
            if trend == "HUMIDE_STABLE":
                return "✅ Humidité optimale - Maintenir"
            else:
                return "✅ Terre humide - Pas besoin d'arrosage"
        else:  # SEC
            if trend == "SEC_STABLE":
                return "🚨 BESOIN URGENT D'ARROSAGE - Terre très sèche"
            else:
                return "💦 Terre sèche - Arroser bientôt"
    
    def monitor(self, duration=60):
        """Surveillance continue"""
        print(f"\n🔍 Surveillance pendant {duration} secondes...")
        print("💧 Testez avec différentes conditions:")
        print("   - Eau 💧")
        print("   - Terre humide 🌱") 
        print("   - Terre sèche 🏜️")
        print("   - Air sec 💨")
        print("-" * 50)
        
        try:
            for i in range(duration):
                value = self.read_state()
                trend = self.get_trend()
                recommendation = self.get_recommendation(value, trend)
                
                # Émoji selon l'état
                emoji = "💧" if value == 0 else "🏜️"
                state = "HUMIDE" if value == 0 else "SEC"
                
                print(f"⏱️  {i+1}s: {emoji} {state} | {recommendation}")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Surveillance arrêtée")
    
    def quick_test(self):
        """Test rapide de 10 secondes"""
        print("\n⚡ TEST RAPIDE (10 secondes)")
        print("Testez rapidement le capteur...")
        
        for i in range(10):
            value = self.read_state()
            state = "HUMIDE" if value == 0 else "SEC"
            print(f"{i+1}s: {state} (valeur: {value})")
            time.sleep(1)
    
    def cleanup(self):
        lgpio.gpiochip_close(self.chip)

# Menu simple
def main():
    sensor = SmartSoilSensor(23)
    
    try:
        while True:
            print("\n🌱 MENU SIMPLE")
            print("1. 🔍 Surveillance continue")
            print("2. ⚡ Test rapide") 
            print("3. 🚪 Quitter")
            
            choix = input("Choix (1-3): ")
            
            if choix == "1":
                sensor.monitor(60)
            elif choix == "2":
                sensor.quick_test()
            elif choix == "3":
                print("👋 Au revoir!")
                break
            else:
                print("❌ Choix invalide")
                
    finally:
        sensor.cleanup()

if __name__ == "__main__":
    main()