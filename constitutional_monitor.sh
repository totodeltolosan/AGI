#!/bin/bash
# 📊 Monitoring Constitutionnel Temps Réel

echo "📊 === MONITORING CONSTITUTIONNEL ==="
echo "🔄 Surveillance de l'état GitHub Actions"
echo ""

# Configuration
GITHUB_REPO="totodeltolosan/AGI"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

current_time=$(date '+%H:%M:%S')
current_branch=$(git branch --show-current)

echo -e "${BLUE}🕒 $current_time | 📍 Branche: $current_branch${NC}"
echo ""

# État des branches
echo -e "${YELLOW}🌿 ÉTAT DES BRANCHES:${NC}"
git branch --list | while read branch; do
    if [[ $branch == *"*"* ]]; then
        echo -e "  ${GREEN}📍 $branch (ACTIVE)${NC}"
    else
        echo "  🟡 $branch"
    fi
done

echo ""

# État des workflows critiques
echo -e "${YELLOW}⚙️ WORKFLOWS CRITIQUES:${NC}"
if [ -f ".github/workflows/master-constitutional-corrector.yml" ]; then
    echo -e "  ${GREEN}✅ Master Constitutional Corrector${NC}"
else
    echo -e "  ${RED}❌ Master Constitutional Corrector MANQUANT${NC}"
fi

if [ -f ".github/workflows/fusion_progress_analyzer.yml" ]; then
    echo -e "  ${GREEN}✅ Le Stratège (Fusion Analyzer)${NC}"
else
    echo -e "  ${YELLOW}⚠️  Le Stratège manquant${NC}"
fi

if [ -f ".github/workflows/syntax_autocorrector.yml" ]; then
    echo -e "  ${GREEN}✅ Le Concierge (Auto Corrector)${NC}"
else
    echo -e "  ${YELLOW}⚠️  Le Concierge manquant${NC}"
fi

echo ""

# Sync status
echo -e "${YELLOW}🔄 SYNCHRONISATION:${NC}"
if git status --porcelain | grep -q .; then
    echo -e "  ${RED}❌ Modifications non committées${NC}"
else
    echo -e "  ${GREEN}✅ Working tree propre${NC}"
fi

unpushed=$(git log --oneline @{u}.. 2>/dev/null | wc -l)
if [ $unpushed -gt 0 ]; then
    echo -e "  ${YELLOW}⚠️  $unpushed commit(s) non pushé(s)${NC}"
else
    echo -e "  ${GREEN}✅ Synchronisé avec GitHub${NC}"
fi

echo ""

# Liens directs
echo -e "${BLUE}🔗 LIENS DIRECTS:${NC}"
echo "  📋 GitHub Actions: https://github.com/$GITHUB_REPO/actions"
echo "  🔀 PR #662: https://github.com/$GITHUB_REPO/pull/662"
echo "  🌿 Toutes les branches: https://github.com/$GITHUB_REPO/branches"

echo ""
echo -e "${GREEN}📊 Monitoring terminé - Vérifiez GitHub maintenant !${NC}"
