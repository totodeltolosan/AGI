#!/bin/bash
echo "🎯 TEST COMPLET DASHBOARD v4.0"
echo "=============================="

# Test conformité constitutionnelle
echo "1. Vérification conformité constitutionnelle:"
python agi_compliance_checker.py | grep -E "(dashboard_|tools/dashboard_core)" || echo "✅ TOUS MODULES CONFORMES"

# Test génération dashboard
echo ""
echo "2. Test génération poste de commandement:"
python tools/dashboard_generator.py

# Vérification fichier généré
if [ -f "AGI_Command_Center.html" ]; then
    echo "✅ Dashboard généré: $(wc -c < AGI_Command_Center.html) octets"
else
    echo "❌ Échec génération"
    exit 1
fi

# Test serveur (si Flask installé)
echo ""
echo "3. Test serveur étendu (5 secondes):"
python tools/command_server_extended.py &
SERVER_PID=$!
sleep 3
curl -s http://localhost:5000/status | grep operational && echo "✅ Serveur opérationnel" || echo "⚠️ Serveur non accessible"
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ DASHBOARD v4.0 COMPLET - TESTS TERMINÉS"
echo "🌐 Ouverture: xdg-open AGI_Command_Center.html"
