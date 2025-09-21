#!/bin/bash
#
# DIAGNOSTIC COMPLET DES WORKFLOWS GITHUB ACTIONS
#

echo "DIAGNOSTIC WORKFLOWS - BRANCHE AGI"
echo "=================================="

# 1. Vérifier les workflows qui se déclenchent sur agi-main
echo "Workflows qui se déclenchent sur agi-main:"
grep -l "agi-main\|main" .github/workflows/*.yml

# 2. Identifier les workflows avec erreurs potentielles
echo ""
echo "Analyse des patterns d'erreur courants:"

# Vérifier actions obsolètes
echo "Actions potentiellement obsolètes:"
grep -r "@v[123]" .github/workflows/ | grep -v "@v4\|@v5\|@v6"

# Vérifier dépendances manquantes
echo ""
echo "Dépendances potentiellement problématiques:"
grep -r "physics-engine\|deprecated\|install" .github/workflows/ | head -10

# 3. Workflows avec timeouts ou configurations problématiques
echo ""
echo "Workflows sans timeout défini:"
grep -L "timeout-minutes" .github/workflows/*.yml | head -5

# 4. Workflows avec chemins de déclenchement invalides
echo ""
echo "Chemins de déclenchement à vérifier:"
grep -A 5 "paths:" .github/workflows/*.yml | grep -E "eve/|backup_" | head -10

