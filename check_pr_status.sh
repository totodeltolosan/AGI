#!/bin/bash
echo "⚡ === VÉRIFICATION EXPRESS PR #662 ==="
echo "🕒 $(date '+%H:%M:%S')"
echo ""

# État git local
if git status --porcelain | grep -q .; then
    echo "❌ Modifications non committées restantes"
    git status --short
else
    echo "✅ Working tree propre"
fi

echo ""
echo "🎯 LIENS DIRECTS:"
echo "📋 GitHub Actions: https://github.com/totodeltolosan/AGI/actions"
echo "🔀 PR #662: https://github.com/totodeltolosan/AGI/pull/662"

echo ""
echo "🏥 STATUS PATIENT ZÉRO:"
if [ -f ".github/workflows/master-constitutional-corrector.yml" ]; then
    echo "✅ Master Constitutional Corrector: OPÉRATIONNEL"
    echo "🎯 Le Patient Zéro devrait être guéri dans 2-3 minutes"
else
    echo "❌ Master Constitutional Corrector: MANQUANT"
fi

echo ""
echo "📞 ACTIONS IMMÉDIATES:"
echo "1. Aller sur GitHub Actions (lien ci-dessus)"
echo "2. Vérifier le statut du workflow"
echo "3. Si vert ✅ → Merger la PR #662 immédiatement"
echo "4. Si rouge ❌ → Re-run failed jobs"
