#!/bin/bash
#
# ANALYSE COMPLÈTE ÉCOSYSTÈME EVE + PROJETS CONNEXES
# Découverte structurelle avant fusion avec AGI
#

echo "🔍 ANALYSE ÉCOSYSTÈME EVE - DÉCOUVERTE COMPLÈTE"
echo "==============================================="

# Répertoires à analyser
PROJECTS=(
    "/home/toni/Documents/gaia"
    "/home/toni/Documents/Projet simulateur"  
    "/home/toni/Documents/Test Eve"
    "/home/toni/Documents/ALMA"
    "/home/toni/Documents/Monde"
    "/home/toni/Documents/EVE GENESIS"
    "/home/toni/Documents/EVE"
    "/home/toni/Documents/ALMA_Space_Cerveau_Demo"
)

echo "📊 ANALYSE STRUCTURELLE GLOBALE"
echo "--------------------------------"

for project in "${PROJECTS[@]}"; do
    if [ -d "$project" ]; then
        echo ""
        echo "📁 PROJET: $project"
        echo "   Taille: $(du -sh "$project" | cut -f1)"
        echo "   Fichiers: $(find "$project" -type f | wc -l)"
        echo "   Python: $(find "$project" -name "*.py" | wc -l)"
        echo "   JSON: $(find "$project" -name "*.json" | wc -l)"
        echo "   MD: $(find "$project" -name "*.md" | wc -l)"
        echo "   Répertoires: $(find "$project" -type d | wc -l)"
    else
        echo "❌ MANQUANT: $project"
    fi
done

echo ""
echo "🏗️ ANALYSE ARCHITECTURALE DÉTAILLÉE"
echo "-----------------------------------"

for project in "${PROJECTS[@]}"; do
    if [ -d "$project" ]; then
        echo ""
        echo "🔍 ARCHITECTURE: $(basename "$project")"
        echo "   Structure principale:"
        tree "$project" -L 3 2>/dev/null || ls -la "$project"
        
        echo "   Scripts principaux:"
        find "$project" -maxdepth 2 -name "*.py" -executable 2>/dev/null
        
        echo "   Fichiers configuration:"
        find "$project" -maxdepth 2 \( -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" \) 2>/dev/null
    fi
done

echo ""
echo "📋 ANALYSE CONTENU CRITIQUE"
echo "---------------------------"

for project in "${PROJECTS[@]}"; do
    if [ -d "$project" ]; then
        echo ""
        echo "📄 CONTENU: $(basename "$project")"
        
        # README ou documentation
        echo "   Documentation:"
        find "$project" -maxdepth 2 \( -name "README*" -o -name "*.md" \) 2>/dev/null | head -5
        
        # Scripts principaux
        echo "   Points d'entrée:"
        find "$project" -maxdepth 2 \( -name "main.py" -o -name "app.py" -o -name "run*.py" -o -name "*server*.py" \) 2>/dev/null
        
        # Configuration
        echo "   Configuration:"
        find "$project" -maxdepth 2 \( -name "config*" -o -name "settings*" \) 2>/dev/null
    fi
done
