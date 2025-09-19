#!/bin/bash
# Script de Vérification de Conformité AGI - Version Corrigée
# Exécute l'ensemble des outils de validation de base sur le projet AGI
#
# Usage:
#   ./verification_compliance_script.sh
#   ./verification_compliance_script.sh --target /path/to/project
#   ./verification_compliance_script.sh --full-audit

set -e  # Arrêt du script en cas d'erreur

# Configuration par défaut
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT=""
TARGET_DIR=""
FULL_AUDIT=false
VERBOSE=false
OUTPUT_DIR=""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Fonction d'affichage avec couleurs
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}🏛️  $1${NC}"
}

# Fonction d'aide
show_help() {
    cat << EOF
Script de Vérification de Conformité AGI

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --target DIR        Répertoire à analyser (défaut: auto-détection)
    --full-audit        Exécute l'audit constitutionnel complet
    --output DIR        Répertoire de sortie pour les rapports
    --verbose           Mode verbeux
    --help              Affiche cette aide

EXEMPLES:
    $0                                          # Vérification standard
    $0 --target ./tools/project_initializer/    # Cible spécifique
    $0 --full-audit --output ./reports/         # Audit complet avec rapports

DESCRIPTION:
    Ce script coordonne l'exécution de tous les outils de validation AGI:
    1. Vérification rapide des lignes (quick_check_lines.py)
    2. Audit constitutionnel complet (full_audit.py) si demandé
    3. Génération de rapports de synthèse

EOF
}

# Fonction de détection de la racine du projet
find_project_root() {
    local current_dir="$PWD"

    # Recherche AGI.md ou structure tools/project_initializer
    while [[ "$current_dir" != "/" ]]; do
        if [[ -f "$current_dir/AGI.md" ]] || [[ -d "$current_dir/tools/project_initializer" ]]; then
            echo "$current_dir"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done

    # Si pas trouvé, utilise le répertoire courant
    echo "$PWD"
}

# Fonction de validation de l'environnement
check_environment() {
    log_info "Vérification de l'environnement..."

    # Vérification Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé ou accessible"
        exit 1
    fi

    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_success "Python $python_version détecté"

    # Vérification de la racine du projet
    if [[ -z "$PROJECT_ROOT" ]]; then
        PROJECT_ROOT=$(find_project_root)
        log_info "Racine du projet détectée: $PROJECT_ROOT"
    fi

    # Définition du répertoire cible par défaut
    if [[ -z "$TARGET_DIR" ]]; then
        if [[ -d "$PROJECT_ROOT/tools/project_initializer" ]]; then
            TARGET_DIR="$PROJECT_ROOT/tools/project_initializer"
        else
            TARGET_DIR="$PROJECT_ROOT"
        fi
        log_info "Répertoire cible: $TARGET_DIR"
    fi

    # Vérification de l'existence du répertoire cible
    if [[ ! -d "$TARGET_DIR" ]]; then
        log_error "Répertoire cible inexistant: $TARGET_DIR"
        exit 1
    fi

    # Création du répertoire de sortie si nécessaire
    if [[ -n "$OUTPUT_DIR" ]]; then
        mkdir -p "$OUTPUT_DIR"
        log_success "Répertoire de sortie préparé: $OUTPUT_DIR"
    fi
}

# Fonction de vérification rapide des lignes
run_quick_check() {
    log_header "ÉTAPE 1: Vérification Rapide des 200 Lignes"
    echo "=================================================="

    local quick_check_script="$PROJECT_ROOT/tools/compliance_checker/quick_check_lines.py"
    local csv_output=""

    # Préparation de la sortie CSV
    if [[ -n "$OUTPUT_DIR" ]]; then
        csv_output="$OUTPUT_DIR/quick_check_$(date +%Y%m%d_%H%M%S).csv"
    fi

    # Construction de la commande
    local cmd="python3 $quick_check_script --target $TARGET_DIR"
    if [[ -n "$csv_output" ]]; then
        cmd="$cmd --csv $csv_output"
    fi

    log_info "Exécution: $cmd"

    # Exécution et capture du code de retour
    set +e
    if [[ "$VERBOSE" == "true" ]]; then
        eval "$cmd"
    else
        eval "$cmd" 2>/dev/null
    fi
    local quick_check_result=$?
    set -e

    # Analyse du résultat
    if [[ $quick_check_result -eq 0 ]]; then
        log_success "Vérification rapide: CONFORME"
        return 0
    else
        log_warning "Vérification rapide: VIOLATIONS DÉTECTÉES"
        return 1
    fi
}

# Fonction d'audit constitutionnel complet
run_full_audit() {
    log_header "ÉTAPE 2: Audit Constitutionnel Complet"
    echo "======================================"

    local full_audit_script="$PROJECT_ROOT/tools/compliance_checker/full_audit.py"

    # Vérification de l'existence du script
    if [[ ! -f "$full_audit_script" ]]; then
        log_error "Script d'audit complet non trouvé: $full_audit_script"
        return 1
    fi

    # Préparation des fichiers de sortie
    local json_output=""
    local console_output=""

    if [[ -n "$OUTPUT_DIR" ]]; then
        json_output="$OUTPUT_DIR/full_audit_$(date +%Y%m%d_%H%M%S).json"
        console_output="$OUTPUT_DIR/full_audit_$(date +%Y%m%d_%H%M%S).txt"
    fi

    # Construction de la commande
    local cmd="python3 $full_audit_script --target $TARGET_DIR"
    if [[ "$VERBOSE" == "true" ]]; then
        cmd="$cmd --verbose"
    fi

    log_info "Exécution de l'audit constitutionnel complet..."

    # Exécution et capture
    set +e
    if [[ -n "$console_output" ]]; then
        eval "$cmd" | tee "$console_output"
        local audit_result=${PIPESTATUS[0]}
    else
        eval "$cmd"
        local audit_result=$?
    fi

    # Génération du rapport JSON si demandé
    if [[ -n "$json_output" ]]; then
        local json_cmd="python3 $full_audit_script --target $TARGET_DIR --format json --output $json_output"
        eval "$json_cmd" >/dev/null 2>&1
        log_success "Rapport JSON généré: $json_output"
    fi

    set -e

    # Analyse du résultat
    if [[ $audit_result -eq 0 ]]; then
        log_success "Audit complet: CONFORME À LA CONSTITUTION"
        return 0
    else
        log_warning "Audit complet: NON-CONFORMITÉS DÉTECTÉES"
        return 1
    fi
}

# Fonction de génération du rapport de synthèse
generate_synthesis_report() {
    log_header "ÉTAPE 3: Génération du Rapport de Synthèse"
    echo "============================================="

    local synthesis_file="$OUTPUT_DIR/synthesis_report_$(date +%Y%m%d_%H%M%S).md"

    if [[ -z "$OUTPUT_DIR" ]]; then
        log_info "Pas de répertoire de sortie spécifié, rapport affiché uniquement"
        return 0
    fi

    # Création du rapport de synthèse
    cat > "$synthesis_file" << EOF
# Rapport de Synthèse - Vérification de Conformité AGI

**Date:** $(date '+%d/%m/%Y à %H:%M:%S')
**Projet:** Générateur AGI
**Répertoire analysé:** $TARGET_DIR

## 📊 Résultats de l'Audit

### Vérification Rapide (200 lignes)
- **Statut:** $([[ $quick_result -eq 0 ]] && echo "✅ CONFORME" || echo "❌ VIOLATIONS")
- **Outil:** quick_check_lines.py

### Audit Constitutionnel Complet
- **Statut:** $([[ $full_result -eq 0 ]] && echo "✅ CONFORME" || echo "❌ NON-CONFORME")
- **Outil:** full_audit.py

## 🎯 Verdict Global

EOF

    # Calcul du verdict global
    local global_status="CONFORME"
    if [[ $quick_result -ne 0 ]] || [[ $full_result -ne 0 ]]; then
        global_status="NON-CONFORME"
    fi

    echo "**CONFORMITÉ GÉNÉRALE:** $([[ "$global_status" == "CONFORME" ]] && echo "✅ PROJET CONFORME" || echo "❌ ACTIONS CORRECTIVES REQUISES")" >> "$synthesis_file"

    cat >> "$synthesis_file" << EOF

## 📁 Fichiers Générés

Les rapports détaillés sont disponibles dans:
- \`$OUTPUT_DIR\`

## 🔧 Actions Recommandées

$([[ "$global_status" == "CONFORME" ]] && echo "Aucune action requise. Le projet respecte toutes les directives AGI." || echo "1. Consulter les rapports détaillés
2. Appliquer les corrections recommandées
3. Re-exécuter la vérification
4. Consulter AGI.md pour les directives complètes")

---
*Généré par verification_compliance_script.sh*
EOF

    log_success "Rapport de synthèse généré: $synthesis_file"
}

# Fonction principale
main() {
    # Variables pour les résultats
    local quick_result=0
    local full_result=0

    log_header "SCRIPT DE VÉRIFICATION DE CONFORMITÉ AGI"
    echo "=========================================="
    echo "Version: 2.0 (Corrigée)"
    echo "Date: $(date)"
    echo ""

    # Vérification de l'environnement
    check_environment

    echo ""
    log_info "Début de la vérification de conformité..."
    echo ""

    # Étape 1: Vérification rapide
    run_quick_check
    quick_result=$?

    echo ""

    # Étape 2: Audit complet (si demandé)
    if [[ "$FULL_AUDIT" == "true" ]]; then
        run_full_audit
        full_result=$?
    else
        log_info "Audit complet non demandé (utilisez --full-audit)"
        full_result=0  # Considéré comme neutre
    fi

    echo ""

    # Étape 3: Rapport de synthèse
    if [[ -n "$OUTPUT_DIR" ]]; then
        generate_synthesis_report
    fi

    # Résumé final
    echo ""
    log_header "RÉSUMÉ FINAL"
    echo "============"

    if [[ $quick_result -eq 0 ]]; then
        log_success "Vérification rapide: OK"
    else
        log_error "Vérification rapide: ÉCHEC"
    fi

    if [[ "$FULL_AUDIT" == "true" ]]; then
        if [[ $full_result -eq 0 ]]; then
            log_success "Audit complet: OK"
        else
            log_error "Audit complet: ÉCHEC"
        fi
    fi

    # Code de sortie global
    if [[ $quick_result -eq 0 ]] && [[ $full_result -eq 0 ]]; then
        log_success "🎉 PROJET CONFORME AUX DIRECTIVES AGI"
        exit 0
    else
        log_error "⚠️  ACTIONS CORRECTIVES REQUISES"
        exit 1
    fi
}

# Analyse des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            TARGET_DIR="$2"
            shift 2
            ;;
        --full-audit)
            FULL_AUDIT=true
            shift
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Exécution principale
main