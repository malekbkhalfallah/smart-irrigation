#!/bin/bash
# Script pour arrêter proprement le système

echo "🛑 Arrêt du système d'irrigation..."

# Arrêter tous les processus Python du projet
pkill -f "python.*api.py" 2>/dev/null && echo "✅ API arrêtée" || echo "⚠️ API non trouvée"
pkill -f "python.*main.py" 2>/dev/null && echo "✅ Système principal arrêté" || echo "⚠️ Système non trouvé"

# Attendre un peu
sleep 2

# Nettoyer GPIO si besoin
echo "🧹 Nettoyage GPIO..."
cd /home/pi/irrigation_project
source venv/bin/activate
python -c "
try:
    from core.gpio_manager import gpio_central
    gpio_central.cleanup()
    print('✅ GPIO nettoyé')
except:
    print('⚠️ GPIO déjà nettoyé')
"

echo "✅ Système arrêté"