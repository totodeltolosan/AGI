#!/bin/bash
echo "🎯 AGI Workflows Tester - Lancement rapide"
echo "======================================="

# Vérification prérequis
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 requis"
    exit 1
fi

if ! python3 -c "import rich, click" &> /dev/null; then
    echo "📦 Installation dépendances..."
    pip install rich click requests
fi

# Menu interactif
echo ""
echo "🎯 Choisissez votre test:"
echo "1. 🔧 Test complet (tous niveaux)"
echo "2. 🎨 Test Nettoyeurs (Niveau 7)"
echo "3. ⚡ Test Travailleurs (Niveau 6)" 
echo "4. 🏭 Test Ouvriers (Niveau 4)"
echo "5. ✅ Test Qualiticiens (Niveau 5)"
echo "6. 🎼 Test Orchestre (Niveau 1)"
echo "7. 🔍 Test workflow spécifique"
echo ""

read -p "Votre choix (1-7): " choice

case $choice in
    1)
        echo "🚀 Lancement test complet..."
        python3 test_agi_workflows.py
        ;;
    2)
        echo "🎨 Test Nettoyeurs..."
        python3 test_agi_workflows.py --level 7
        ;;
    3)
        echo "⚡ Test Travailleurs..."
        python3 test_agi_workflows.py --level 6
        ;;
    4)
        echo "🏭 Test Ouvriers..."
        python3 test_agi_workflows.py --level 4
        ;;
    5)
        echo "✅ Test Qualiticiens..."
        python3 test_agi_workflows.py --level 5 --sequential
        ;;
    6)
        echo "🎼 Test Orchestre..."
        python3 test_agi_workflows.py --level 1
        ;;
    7)
        read -p "Nom du workflow à tester: " workflow_name
        python3 test_agi_workflows.py --workflow "$workflow_name"
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "📊 Tests terminés! Consultez le dossier reports/ pour les résultats détaillés."
