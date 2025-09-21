#!/bin/bash

echo "🔧 Correction automatique erreurs YAML..."

# Corriger les erreurs communes dans tous les workflows
for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        echo "Correction: $(basename $workflow)"
        
        # Sauvegarder original
        cp "$workflow" "$workflow.backup"
        
        # Corrections communes
        sed -i 's/\r$//' "$workflow"                    # Supprimer retours chariot Windows
        sed -i 's/\t/  /g' "$workflow"                  # Remplacer tabs par espaces
        sed -i '/^$/N;/^\n$/d' "$workflow"              # Supprimer lignes vides multiples
        sed -i 's/[[:space:]]*$//' "$workflow"          # Supprimer espaces en fin de ligne
        
        # Vérifier si correction a résolu le problème
        if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
            echo "  ✅ Corrigé"
            rm "$workflow.backup"
        else
            echo "  ❌ Erreur persistante"
            mv "$workflow.backup" "$workflow"
        fi
    fi
done

echo "✅ Corrections automatiques terminées"
