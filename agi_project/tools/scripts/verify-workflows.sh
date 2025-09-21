#!/bin/bash

echo "🔍 Vérification complète des 25 workflows GitHub Actions..."
echo ""

# Liste des 25 workflows attendus
expected_workflows=(
    "constitutional-governance.yml"
    "quality-assurance.yml" 
    "security-advanced.yml"
    "performance-optimization.yml"
    "cross-module-integration.yml"
    "automated-deployment.yml"
    "eve-cognitive-validation.yml"
    "alma-compatibility.yml"
    "cognitive-benchmarks.yml"
    "brain-core-monitoring.yml"
    "cognitive-integration.yml"
    "universe-simulation.yml"
    "monde-integration.yml"
    "eve-genesis-validation.yml"
    "emergence-monitor.yml"
    "gaia-code-analysis.yml"
    "test-eve-monitoring.yml"
    "git-integration-advanced.yml"
    "dev-automation-pipeline.yml"
    "code-generation-validation.yml"
    "ui-interface-validation.yml"
    "logs-management.yml"
    "documentation-generation.yml"
    "master-orchestrator.yml"
    "continuous-monitoring.yml"
    "system-health-dashboard.yml"
)

workflows_dir=".github/workflows"
missing_workflows=()
invalid_workflows=()
incomplete_workflows=()
valid_workflows=()

echo "📁 Vérification dossier workflows..."
if [ ! -d "$workflows_dir" ]; then
    echo "❌ ERREUR: Dossier $workflows_dir n'existe pas !"
    echo "   Créer le dossier: mkdir -p $workflows_dir"
    exit 1
fi

echo "✅ Dossier $workflows_dir trouvé"
echo ""

echo "📋 Vérification présence des 25 workflows..."
for workflow in "${expected_workflows[@]}"; do
    workflow_path="$workflows_dir/$workflow"
    
    if [ -f "$workflow_path" ]; then
        echo "✅ $workflow"
        valid_workflows+=("$workflow")
    else
        echo "❌ $workflow - MANQUANT"
        missing_workflows+=("$workflow")
    fi
done

echo ""
echo "📊 RÉSULTATS VÉRIFICATION PRÉSENCE:"
echo "   ✅ Présents: ${#valid_workflows[@]}/25"
echo "   ❌ Manquants: ${#missing_workflows[@]}/25"
echo ""

if [ ${#missing_workflows[@]} -gt 0 ]; then
    echo "🚨 WORKFLOWS MANQUANTS:"
    for missing in "${missing_workflows[@]}"; do
        echo "   - $missing"
    done
    echo ""
fi

echo "🔍 Vérification syntaxe YAML..."
yaml_errors=0

for workflow in "${valid_workflows[@]}"; do
    workflow_path="$workflows_dir/$workflow"
    
    # Vérification syntaxe YAML basique
    if python3 -c "
import yaml
import sys
try:
    with open('$workflow_path', 'r') as f:
        yaml.safe_load(f)
    print('✅ $workflow - Syntaxe YAML valide')
except yaml.YAMLError as e:
    print('❌ $workflow - Erreur YAML:', str(e))
    sys.exit(1)
except Exception as e:
    print('⚠️ $workflow - Erreur lecture:', str(e))
    sys.exit(1)
" 2>/dev/null; then
        # Syntaxe OK
        :
    else
        echo "❌ $workflow - SYNTAXE YAML INVALIDE"
        invalid_workflows+=("$workflow")
        yaml_errors=$((yaml_errors + 1))
    fi
done

echo ""
echo "📊 RÉSULTATS VÉRIFICATION SYNTAXE:"
echo "   ✅ Syntaxe valide: $((${#valid_workflows[@]} - yaml_errors))"
echo "   ❌ Erreurs YAML: $yaml_errors"
echo ""

if [ ${#invalid_workflows[@]} -gt 0 ]; then
    echo "🚨 WORKFLOWS AVEC ERREURS YAML:"
    for invalid in "${invalid_workflows[@]}"; do
        echo "   - $invalid"
    done
    echo ""
fi

echo "🔍 Vérification structure workflows..."
structure_errors=0

for workflow in "${valid_workflows[@]}"; do
    # Skip si déjà marqué comme invalide
    if [[ " ${invalid_workflows[@]} " =~ " ${workflow} " ]]; then
        continue
    fi
    
    workflow_path="$workflows_dir/$workflow"
    
    # Vérifier éléments essentiels
    has_name=$(grep -q "^name:" "$workflow_path" && echo "true" || echo "false")
    has_on=$(grep -q "^on:" "$workflow_path" && echo "true" || echo "false")
    has_jobs=$(grep -q "^jobs:" "$workflow_path" && echo "true" || echo "false")
    has_steps=$(grep -q "steps:" "$workflow_path" && echo "true" || echo "false")
    
    # Vérifier taille minimale (workflow complet devrait avoir >50 lignes)
    line_count=$(wc -l < "$workflow_path")
    
    if [ "$has_name" = "true" ] && [ "$has_on" = "true" ] && [ "$has_jobs" = "true" ] && [ "$has_steps" = "true" ] && [ $line_count -gt 50 ]; then
        echo "✅ $workflow - Structure complète ($line_count lignes)"
    else
        echo "❌ $workflow - Structure incomplète"
        echo "     Name: $has_name, On: $has_on, Jobs: $has_jobs, Steps: $has_steps, Lignes: $line_count"
        incomplete_workflows+=("$workflow")
        structure_errors=$((structure_errors + 1))
    fi
done

echo ""
echo "📊 RÉSULTATS VÉRIFICATION STRUCTURE:"
echo "   ✅ Structure complète: $(($((${#valid_workflows[@]} - yaml_errors)) - structure_errors))"
echo "   ❌ Structure incomplète: $structure_errors"
echo ""

if [ ${#incomplete_workflows[@]} -gt 0 ]; then
    echo "🚨 WORKFLOWS AVEC STRUCTURE INCOMPLÈTE:"
    for incomplete in "${incomplete_workflows[@]}"; do
        echo "   - $incomplete"
    done
    echo ""
fi

# Vérification fichiers supplémentaires
echo "🔍 Vérification fichiers additionnels..."
extra_files=$(find "$workflows_dir" -name "*.yml" -o -name "*.yaml" | wc -l)
expected_count=25

echo "📊 Fichiers dans $workflows_dir: $extra_files"
echo "📊 Fichiers attendus: $expected_count"

if [ $extra_files -gt $expected_count ]; then
    echo "ℹ️ Fichiers supplémentaires détectés:"
    find "$workflows_dir" -name "*.yml" -o -name "*.yaml" | while read file; do
        basename_file=$(basename "$file")
        if [[ ! " ${expected_workflows[@]} " =~ " ${basename_file} " ]]; then
            echo "   + $basename_file"
        fi
    done
fi

echo ""
echo "🎯 RÉSUMÉ FINAL:"
echo "==============="
total_issues=$((${#missing_workflows[@]} + ${#invalid_workflows[@]} + ${#incomplete_workflows[@]}))

if [ $total_issues -eq 0 ]; then
    echo "✅ PARFAIT: Tous les 25 workflows sont présents et valides !"
    echo "🎉 Configuration GitHub Actions complète et fonctionnelle"
else
    echo "⚠️ PROBLÈMES DÉTECTÉS: $total_issues workflow(s) nécessitent attention"
    echo ""
    echo "🔧 ACTIONS CORRECTIVES SUGGÉRÉES:"
    
    if [ ${#missing_workflows[@]} -gt 0 ]; then
        echo "1. Recréer les workflows manquants:"
        for missing in "${missing_workflows[@]}"; do
            echo "   - $missing"
        done
    fi
    
    if [ ${#invalid_workflows[@]} -gt 0 ]; then
        echo "2. Corriger la syntaxe YAML de:"
        for invalid in "${invalid_workflows[@]}"; do
            echo "   - $invalid"
        done
    fi
    
    if [ ${#incomplete_workflows[@]} -gt 0 ]; then
        echo "3. Compléter la structure de:"
        for incomplete in "${incomplete_workflows[@]}"; do
            echo "   - $incomplete"
        done
    fi
fi

echo ""
echo "✅ Vérification terminée"
