#!/bin/bash
set -e
echo "🛠️ RÉPARATION STRUCTURE AGI-EVE CRITIQUE"
echo "========================================"

AGI_DIR="/home/toni/Documents/Projet AGI"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backup_critical_repair_$DATE"

cd "$AGI_DIR"

echo "💾 SAUVEGARDE CRITIQUE"
mkdir -p "$BACKUP_DIR"
cp -r . "$BACKUP_DIR/" 2>/dev/null || echo "Sauvegarde partielle effectuée"
echo "✅ Sauvegarde: $BACKUP_DIR"

echo ""
echo "🔧 RÉPARATION STRUCTURE INTEGRATION"
mkdir -p integration/{constitutional_eve,unified_intelligence,bridges}
mkdir -p integration/constitutional_eve/{core,validators,interfaces}
mkdir -p integration/unified_intelligence/{ai_core,knowledge_base,decision_engine}
mkdir -p integration/bridges/{eve_agi,constitutional,monitoring}

touch integration/__init__.py
touch integration/constitutional_eve/__init__.py
touch integration/unified_intelligence/__init__.py
touch integration/bridges/__init__.py

echo "✅ Structure integration/ réparée"

echo ""
echo "🏗️ CRÉATION STRUCTURE EVE COMPLÈTE"
mkdir -p eve/{cognitive,simulation,development,interfaces,common}
mkdir -p eve/cognitive/{brain,launchers,agents,interfaces}
mkdir -p eve/simulation/{universe,evolution,physics,agents}
mkdir -p eve/development/{code_analysis,monitoring,git_tools,automation}
mkdir -p eve/interfaces/{ui,logs,documentation,apis}
mkdir -p eve/common/{utils,config,data}

find eve/ -type d -exec touch {}/__init__.py \;
echo "✅ Structure EVE créée complètement"

echo ""
echo "📊 RÉPARATION RÉPERTOIRES REPORTS"
mkdir -p reports/{fusion,audit,compliance,deployment,recovery,migration}
mkdir -p reports/fusion/{pre,post,migration}
mkdir -p reports/audit/{daily,critical,summary}

echo "✅ Répertoires reports créés"

echo ""
echo "🤖 PRÉPARATION GITHUB ACTIONS"
mkdir -p .github/{workflows,templates,scripts}
mkdir -p .github/workflows/{ci,cd,audit,deployment}

echo "✅ Structure GitHub Actions préparée"

chmod -R 755 integration/ eve/ .github/ reports/
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ RÉPARATION STRUCTURE TERMINÉE AVEC SUCCÈS"
