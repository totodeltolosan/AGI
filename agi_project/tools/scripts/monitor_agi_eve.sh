#!/bin/bash
# Monitoring continu AGI-EVE

echo "📊 MONITORING AGI-EVE $(date)"
echo "=============================="

cd "/home/toni/Documents/Projet AGI"

echo "🏛️ Conformité constitutionnelle:"
python run_agi_audit.py --summary 2>/dev/null || echo "Audit indisponible"

echo ""
echo "📁 Structure EVE:"
if [ -d "eve/" ]; then
    find eve/ -name "*.py" | wc -l | sed 's/^/  Fichiers Python EVE: /'
    du -sh eve/ | sed 's/^/  Taille EVE: /'
else
    echo "  ❌ Structure EVE manquante"
fi

echo ""
echo "🔗 Bridges:"
if [ -f "integration/bridges/eve_agi_bridge.py" ]; then
    echo "  ✅ Bridge EVE-AGI opérationnel"
else
    echo "  ❌ Bridge EVE-AGI manquant"
fi

echo ""
echo "🚀 Git Status:"
git status --porcelain | wc -l | sed 's/^/  Fichiers modifiés: /'
git log --oneline -1 | sed 's/^/  Dernier commit: /'
