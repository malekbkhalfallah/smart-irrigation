#!/bin/bash
# Démarrage du système unifié

echo "🚀 Démarrage du système d'irrigation UNIFIÉ..."
echo "================================================"

cd /home/pi/irrigation_project
source venv/bin/activate
export PYTHONPATH="/home/pi/irrigation_project:$PYTHONPATH"

# Arrêter tout processus existant
echo "🛑 Arrêt des processus existants..."
pkill -f "python.*api.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
sleep 2

# Démarrer le système unifié
echo "🌐 Démarrage système unifié (API + Automatisation)..."
python main.py

echo "✅ Système arrêté"