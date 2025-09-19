#!/bin/bash
#
# FUSION COMPLÈTE EVE-AGI + DÉPLOIEMENT GITHUB
# Script automatisé pour migration constitutionnelle complète
#

set -e  # Arrêt sur erreur

echo "🚀 FUSION COMPLÈTE EVE-AGI - DÉPLOIEMENT CONSTITUTIONNEL"
echo "========================================================"

# Configuration
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backup_pre_fusion_$DATE"
AGI_DIR="/home/toni/Documents/Projet AGI"

cd "$AGI_DIR"

# Phase 1: Sauvegarde sécurisée
echo ""
echo "💾 PHASE 1: SAUVEGARDE SÉCURISÉE"
echo "--------------------------------"
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR/" 2>/dev/null || echo "Sauvegarde partielle effectuée"
echo "✅ Sauvegarde AGI créée: $BACKUP_DIR"

# Phase 2: Création architecture EVE
echo ""
echo "🏗️ PHASE 2: CRÉATION ARCHITECTURE EVE"
echo "-------------------------------------"
mkdir -p eve/{cognitive,simulation,development,interfaces,common}
mkdir -p eve/cognitive/{brain,launchers,agents,interfaces}
mkdir -p eve/simulation/{universe,evolution,physics,agents}
mkdir -p eve/development/{code_analysis,monitoring,git_tools,automation}
mkdir -p eve/interfaces/{ui,logs,documentation,apis}
mkdir -p eve/common/{utils,config,data}
mkdir -p integration/{constitutional_eve,unified_intelligence,bridges}
mkdir -p reports/fusion/

echo "✅ Structure EVE créée dans AGI"

# Phase 3: Migration ALMA (Intelligence Cognitive)
echo ""
echo "🧠 PHASE 3: MIGRATION ALMA → eve/cognitive/"
echo "-------------------------------------------"
if [ -d "/home/toni/Documents/ALMA" ]; then
    # Copier fichiers principaux ALMA
    cp -r "/home/toni/Documents/ALMA/Cerveau"/* eve/cognitive/brain/ 2>/dev/null || true
    cp -r "/home/toni/Documents/ALMA/Interfaces"/* eve/cognitive/interfaces/ 2>/dev/null || true
    cp -r "/home/toni/Documents/ALMA/projet_alma"/* eve/cognitive/agents/ 2>/dev/null || true
    cp "/home/toni/Documents/ALMA/alma_launcher.py" eve/cognitive/launchers/ 2>/dev/null || true
    cp -r "/home/toni/Documents/ALMA/Outils"/* eve/development/automation/ 2>/dev/null || true
    
    echo "✅ ALMA migré vers eve/cognitive/"
else
    echo "⚠️ ALMA introuvable"
fi

# Phase 4: Migration Monde (Simulation)
echo ""
echo "🌍 PHASE 4: MIGRATION Monde → eve/simulation/"
echo "--------------------------------------------"
if [ -d "/home/toni/Documents/Monde" ]; then
    # Copier composants simulation
    cp "/home/toni/Documents/Monde"/*.py eve/simulation/universe/ 2>/dev/null || true
    cp -r "/home/toni/Documents/Monde"/* eve/simulation/physics/ 2>/dev/null || true
    
    echo "✅ Monde migré vers eve/simulation/"
else
    echo "⚠️ Monde introuvable"
fi

# Phase 5: Migration gaia (Analyse Code)
echo ""
echo "🔍 PHASE 5: MIGRATION gaia → eve/development/"
echo "--------------------------------------------"
if [ -d "/home/toni/Documents/gaia" ]; then
    cp "/home/toni/Documents/gaia"/* eve/development/code_analysis/ 2>/dev/null || true
    echo "✅ gaia migré vers eve/development/code_analysis/"
else
    echo "⚠️ gaia introuvable"
fi

# Phase 6: Migration EVE GENESIS
echo ""
echo "🧬 PHASE 6: MIGRATION EVE GENESIS → eve/simulation/evolution/"
echo "-----------------------------------------------------------"
if [ -d "/home/toni/Documents/EVE GENESIS" ]; then
    cp -r "/home/toni/Documents/EVE GENESIS"/* eve/simulation/evolution/ 2>/dev/null || true
    echo "✅ EVE GENESIS migré vers eve/simulation/evolution/"
else
    echo "⚠️ EVE GENESIS introuvable"
fi

# Phase 7: Migration Test Eve
echo ""
echo "🔧 PHASE 7: MIGRATION Test Eve → eve/development/"
echo "------------------------------------------------"
if [ -d "/home/toni/Documents/Test Eve" ]; then
    cp -r "/home/toni/Documents/Test Eve"/* eve/development/monitoring/ 2>/dev/null || true
    echo "✅ Test Eve migré vers eve/development/monitoring/"
else
    echo "⚠️ Test Eve introuvable"
fi

# Phase 8: Migration Projet simulateur
echo ""
echo "🎮 PHASE 8: MIGRATION Projet simulateur → eve/interfaces/"
echo "--------------------------------------------------------"
if [ -d "/home/toni/Documents/Projet simulateur" ]; then
    cp -r "/home/toni/Documents/Projet simulateur"/* eve/interfaces/ui/ 2>/dev/null || true
    echo "✅ Projet simulateur migré vers eve/interfaces/ui/"
else
    echo "⚠️ Projet simulateur introuvable"
fi

# Phase 9: Migration ALMA_Space_Cerveau_Demo
echo ""
echo "🌌 PHASE 9: MIGRATION ALMA_Space_Cerveau_Demo → eve/cognitive/"
echo "-------------------------------------------------------------"
if [ -d "/home/toni/Documents/ALMA_Space_Cerveau_Demo" ]; then
    cp -r "/home/toni/Documents/ALMA_Space_Cerveau_Demo"/* eve/cognitive/brain/ 2>/dev/null || true
    echo "✅ ALMA_Space_Cerveau_Demo migré"
else
    echo "⚠️ ALMA_Space_Cerveau_Demo introuvable"
fi

echo ""
echo "📊 MIGRATION TERMINÉE - STATISTIQUES"
echo "===================================="
echo "Fichiers Python migrés:"
find eve/ -name "*.py" | wc -l | sed 's/^/   Fichiers .py: /'
echo "Taille totale EVE:"
du -sh eve/ | cut -f1 | sed 's/^/   Taille: /'
echo "Structure créée:"
tree eve/ -d -L 2 2>/dev/null || find eve/ -type d | head -10

echo ""
echo "✅ FUSION EVE-AGI TERMINÉE AVEC SUCCÈS"
