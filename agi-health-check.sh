#!/bin/bash
# ========================================
# DIAGNOSTIC COMPLET PROJET AGI
# ========================================

echo "🏥 DIAGNOSTIC SANTÉ PROJET AGI"
echo "==============================="
echo ""

# Codes couleur
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    if [ "$1" = "OK" ]; then
        echo -e "${GREEN}✅ $2${NC}"
    elif [ "$1" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# 1. SYNCHRONISATION LOCAL/GITHUB
echo "📡 SYNCHRONISATION LOCAL/GITHUB:"
echo "================================="

# Branche actuelle
current_branch=$(git branch --show-current)
echo "Branche actuelle: $current_branch"

# Commits non poussés
unpushed=$(git log --oneline origin/$current_branch..$current_branch 2>/dev/null | wc -l)
if [ $unpushed -eq 0 ]; then
    print_status "OK" "Aucun commit en attente de push"
else
    print_status "WARNING" "$unpushed commits non poussés vers GitHub"
    echo "   Commande: git push origin $current_branch"
fi

# État working directory
if [ -z "$(git status --porcelain)" ]; then
    print_status "OK" "Working directory propre"
else
    print_status "WARNING" "Modifications non commitées détectées"
    git status --porcelain | head -5
fi

echo ""

# 2. ARCHITECTURE WORKFLOWS
echo "🏗️  ARCHITECTURE WORKFLOWS:"
echo "============================"

# Nombre de workflows
workflow_count=$(find .github/workflows -name "*.yml" 2>/dev/null | wc -l)
if [ $workflow_count -eq 71 ]; then
    print_status "OK" "$workflow_count workflows (conforme aux spécifications)"
else
    print_status "ERROR" "$workflow_count workflows (attendu: 71)"
fi

# Handlers Python
handler_count=$(find .github/scripts -name "*.py" 2>/dev/null | wc -l)
if [ $handler_count -ge 50 ]; then
    print_status "OK" "$handler_count handlers Python disponibles"
else
    print_status "WARNING" "$handler_count handlers Python (recommandé: 50+)"
fi

# Vérifier répartition par niveau
echo "Répartition par niveau:"
for level in 00 01 02 04 05 06 07; do
    count=$(find .github/workflows -name "${level}-*.yml" 2>/dev/null | wc -l)
    case $level in
        "00") expected=1 ;;
        "01") expected=1 ;;
        "02") expected=8 ;;
        "04") expected=26 ;;
        "05") expected=26 ;;
        "06") expected=6 ;;
        "07") expected=3 ;;
    esac

    if [ $count -eq $expected ]; then
        echo "  Niveau $level: $count/$expected ✅"
    else
        echo "  Niveau $level: $count/$expected ❌"
    fi
done

echo ""

# 3. AUTOMATISATION
echo "🤖 AUTOMATISATION WORKFLOWS:"
echo "============================="

# Vérifier GitHub CLI
if command -v gh &> /dev/null; then
    print_status "OK" "GitHub CLI installé"

    # Vérifier authentification
    if gh auth status &> /dev/null; then
        print_status "OK" "Authentifié sur GitHub"

        # Workflows automatiques
        auto_workflows=$(grep -l "schedule:" .github/workflows/*.yml 2>/dev/null | wc -l)
        push_workflows=$(grep -l "push:" .github/workflows/*.yml 2>/dev/null | wc -l)
        manual_workflows=$(grep -l "workflow_dispatch" .github/workflows/*.yml 2>/dev/null | wc -l)

        echo "Types de déclencheurs:"
        echo "  Planifiés (cron): $auto_workflows workflows"
        echo "  Push/PR: $push_workflows workflows"
        echo "  Manuels: $manual_workflows workflows"

        if [ $auto_workflows -eq 0 ]; then
            print_status "WARNING" "Aucun workflow planifié - système non automatisé"
            echo "   Recommandation: Ajouter des 'schedule:' dans 01-orchestre.yml"
        else
            print_status "OK" "Automatisation active avec $auto_workflows workflows planifiés"
        fi

        # Exécutions récentes
        echo ""
        echo "Exécutions récentes:"
        gh run list --limit 3 2>/dev/null | head -4 || echo "  Aucune exécution récente"

    else
        print_status "ERROR" "Non authentifié sur GitHub (gh auth login)"
    fi

else
    print_status "ERROR" "GitHub CLI non installé"
    echo "   Installation: https://github.com/cli/cli#installation"
fi

echo ""

# 4. TESTS LOCAUX
echo "🧪 TESTS LOCAUX:"
echo "================"

if [ -f "test-workflows/test_agi_workflows_fixed.py" ]; then
    print_status "OK" "Script de test disponible"

    # Lancer les tests si demandé
    read -p "Lancer les tests maintenant? (y/N): " run_tests
    if [ "$run_tests" = "y" ] || [ "$run_tests" = "Y" ]; then
        echo "Exécution des tests..."
        cd test-workflows
        python3 test_agi_workflows_fixed.py | tail -20
        cd ..
    fi
else
    print_status "WARNING" "Script de test non trouvé"
fi

echo ""

# 5. RECOMMANDATIONS
echo "📋 RECOMMANDATIONS:"
echo "==================="

# Actions recommandées
if [ $unpushed -gt 0 ]; then
    echo "🔄 URGENT: git push origin $current_branch"
fi

if [ $auto_workflows -eq 0 ]; then
    echo "⏰ Ajouter automatisation: modifier 01-orchestre.yml avec schedule:"
    echo "   - cron: '0 6 * * *'  # Audit quotidien 6h UTC"
fi

if ! command -v gh &> /dev/null || ! gh auth status &> /dev/null; then
    echo "🔧 Configurer GitHub CLI pour gestion complète"
fi

# Score global
score=0
total=5

[ $unpushed -eq 0 ] && score=$((score + 1))
[ $workflow_count -eq 71 ] && score=$((score + 1))
[ $handler_count -ge 50 ] && score=$((score + 1))
command -v gh &> /dev/null && gh auth status &> /dev/null && score=$((score + 1))
[ -f "test-workflows/test_agi_workflows_fixed.py" ] && score=$((score + 1))

percentage=$((score * 100 / total))

echo ""
echo "🎯 SCORE SANTÉ GLOBAL: $score/$total ($percentage%)"

if [ $percentage -ge 80 ]; then
    print_status "OK" "Projet en excellente santé"
elif [ $percentage -ge 60 ]; then
    print_status "WARNING" "Projet en bonne santé - quelques améliorations possibles"
else
    print_status "ERROR" "Projet nécessite des corrections"
fi

echo ""
echo "==============================="
echo "Diagnostic terminé"
