#!/bin/bash
echo "🛑 Arrêt du système unifié..."
pkill -f "python.*main.py" 2>/dev/null && echo "✅ Système arrêté" || echo "⚠️ Système non trouvé"
sleep 2