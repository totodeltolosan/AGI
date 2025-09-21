#!/bin/bash
#
# AFFICHAGE WORKFLOWS D'AUJOURD'HUI UNIQUEMENT
#

echo "WORKFLOWS GITHUB ACTIONS - AUJOURD'HUI UNIQUEMENT"
echo "================================================"

if command -v gh &> /dev/null; then
    echo "Via GitHub CLI:"
    echo "==============="
    
    # Lister les runs d'aujourd'hui
    TODAY=$(date +%Y-%m-%d)
    echo "Date du jour: $TODAY"
    echo ""
    
    # Top 20 des runs d'aujourd'hui
    gh run list --limit 50 --json status,conclusion,name,createdAt,headBranch \
    --jq ".[] | select(.createdAt | startswith(\"$TODAY\")) | \"[\(.status)] \(.name) - \(.headBranch) - \(.createdAt)\"" \
    | head -20
    
else
    echo "GitHub CLI non disponible"
    echo "========================"
    echo ""
    echo "MANUEL: Allez sur GitHub Actions et filtrez:"
    echo "1. https://github.com/totodeltolosan/AGI/actions"
    echo "2. Cliquez sur 'All workflows' pour voir la liste"
    echo "3. Cherchez 'Continuous Monitoring' dans les résultats récents"
    echo "4. Vérifiez si les dernières exécutions sont VERTES ou ROUGES"
fi

echo ""
echo "WORKFLOW CIBLE A SURVEILLER:"
echo "==========================="
echo "Nom: 'Continuous Monitoring'"
echo "Fichier corrigé: continuous-monitoring.yml"
echo "Erreur précédente: env:: command not found ligne 108"
echo "Correction appliquée: Fichier recréé sans syntaxe env::"
echo ""
echo "RESULTAT ATTENDU:"
echo "✅ Status: SUCCESS (vert)"
echo "❌ Si encore rouge: Erreur différente à investiguer"
