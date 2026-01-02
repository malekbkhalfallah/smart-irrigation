#!/bin/bash
# Script de démarrage automatique du système d'irrigation

echo "🚀 Démarrage du système d'irrigation intelligent..."
echo "================================================"

# Se mettre dans le bon répertoire
cd /home/pi/irrigation_project

# Activer l'environnement virtuel
source venv/bin/activate

# Ajouter le répertoire courant au PYTHONPATH
export PYTHONPATH="/home/pi/irrigation_project:$PYTHONPATH"

# Arrêter tout processus existant sur le port 5000
echo "🛑 Arrêt des processus existants..."
pkill -f "python.*api.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
sleep 2

# Attendre que le réseau soit disponible
echo "🌐 Attente du réseau..."
sleep 3

# Démarrer le serveur API en arrière-plan
echo "🌐 Démarrage du serveur API..."
python web_server/api.py &
API_PID=$!
sleep 5

# Vérifier que l'API démarre
echo "📡 Vérification de l'API..."
if curl -s http://localhost:5000/api/test > /dev/null; then
    echo "✅ API démarrée"
else
    echo "⚠️ API en attente - réessayer..."
    sleep 2
    curl -s http://localhost:5000/api/test > /dev/null && echo "✅ API maintenant démarrée" || echo "❌ API non disponible"
fi

# Démarrer le système d'irrigation principal avec délai
echo "🌱 Démarrage du système d'irrigation..."
sleep 3  # Attendre que l'API initialise complètement GPIO
python main.py &
MAIN_PID=$!

# Attendre un peu pour l'initialisation
sleep 3

# Afficher les PIDs pour référence
echo "📝 Process IDs:"
echo "   API Server: $API_PID"
echo "   Main System: $MAIN_PID"

# Afficher l'URL d'accès
IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo ""
echo "✅ Système démarré avec succès!"
echo "📡 API disponible sur: http://$IP_ADDRESS:5000"
echo "🔧 Test: http://$IP_ADDRESS:5000/api/test"
echo "💻 Interface web: http://$IP_ADDRESS:5000"
echo ""
echo "📋 Commandes utiles:"
echo "   ./stop_system.sh        # Arrêter proprement"
echo "   curl http://localhost:5000/api/sensors  # Voir les capteurs"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter tous les processus"
echo "================================================"

# Attendre Ctrl+C
trap 'echo ""; echo "Arrêt demandé..."; kill $API_PID $MAIN_PID 2>/dev/null; exit 0' INT
wait