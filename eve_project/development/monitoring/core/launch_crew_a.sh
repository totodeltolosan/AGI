#!/bin/bash

# =============================================================================
# 🚀 EVE GENESIS CREW A - SCRIPT DE LANCEMENT RAPIDE
# =============================================================================
#
# Ce script automatise le lancement complet du test Crew A
# et vérifie tous les prérequis avant l'exécution
#
# 🤖 Crew A: L'Ingénieur Adaptatif & Supervisable
# 📊 41 Agents | 40 Tâches | 6 Missions Critiques
#
# =============================================================================

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_step() {
    echo -e "${CYAN}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction de vérification d'Ollama
check_ollama() {
    print_step "Vérification d'Ollama..."

    if ! command -v ollama &> /dev/null; then
        print_error "Ollama n'est pas installé"
        echo "Installation d'Ollama requise: https://ollama.ai/"
        return 1
    fi

    # Test de connexion
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama est actif"

        # Vérification des modèles
        models=$(curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = [model['name'] for model in data.get('models', [])]
    print('\\n'.join(models))
except:
    pass
")

        if echo "$models" | grep -q "llama3"; then
            print_success "Modèle llama3 disponible"
            echo -e "${BLUE}📋 Modèles installés:${NC}"
            echo "$models" | head -5 | sed 's/^/   - /'
        else
            print_warning "Modèle llama3 non trouvé"
            echo -e "${BLUE}💾 Installation du modèle llama3:8b...${NC}"
            ollama pull llama3:8b
            if [ $? -eq 0 ]; then
                print_success "Modèle llama3:8b installé"
            else
                print_error "Échec de l'installation du modèle"
                return 1
            fi
        fi
    else
        print_error "Ollama n'est pas accessible sur localhost:11434"
        echo -e "${YELLOW}Démarrage d'Ollama...${NC}"
        echo "Lancez dans un autre terminal: ollama serve"
        echo "Puis relancez ce script"
        return 1
    fi
}

# Fonction de vérification Python
check_python() {
    print_step "Vérification de Python..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé"
        return 1
    fi

    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python $python_version détecté"

    # Vérification de la version minimale
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
        print_success "Version Python compatible (>= 3.10)"
    else
        print_error "Version Python insuffisante (< 3.10)"
        echo "Python 3.10+ requis pour EVE GENESIS"
        return 1
    fi
}

# Fonction de vérification des dépendances
check_dependencies() {
    print_step "Vérification des dépendances Python..."

    # Liste des dépendances critiques
    critical_deps=("pathlib" "json" "subprocess" "threading")
    optional_deps=("psutil" "requests" "crewai")

    # Vérification des dépendances critiques
    for dep in "${critical_deps[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            print_success "Dépendance critique: $dep"
        else
            print_error "Dépendance critique manquante: $dep"
            return 1
        fi
    done

    # Vérification des dépendances optionnelles
    missing_optional=()
    for dep in "${optional_deps[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            print_success "Dépendance optionnelle: $dep"
        else
            print_warning "Dépendance optionnelle manquante: $dep"
            missing_optional+=("$dep")
        fi
    done

    # Installation des dépendances manquantes
    if [ ${#missing_optional[@]} -ne 0 ]; then
        echo -e "${BLUE}📦 Installation des dépendances manquantes...${NC}"
        for dep in "${missing_optional[@]}"; do
            echo "Installation de $dep..."
            pip3 install "$dep" || print_warning "Échec installation $dep"
        done
    fi
}

# Fonction de vérification des ressources système
check_system_resources() {
    print_step "Vérification des ressources système..."

    # RAM disponible
    if command -v free &> /dev/null; then
        ram_gb=$(free -g | awk 'NR==2{printf "%.0f", $7}')
        if [ "$ram_gb" -ge 8 ]; then
            print_success "RAM disponible: ${ram_gb}GB"
        else
            print_warning "RAM limitée: ${ram_gb}GB (8GB+ recommandé)"
        fi
    fi

    # Espace disque
    if command -v df &> /dev/null; then
        disk_gb=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
        if [ "$disk_gb" -ge 10 ]; then
            print_success "Espace disque: ${disk_gb}GB"
        else
            print_warning "Espace disque limité: ${disk_gb}GB (10GB+ recommandé)"
        fi
    fi

    # CPU
    if command -v nproc &> /dev/null; then
        cpu_cores=$(nproc)
        if [ "$cpu_cores" -ge 4 ]; then
            print_success "CPU: ${cpu_cores} cœurs"
        else
            print_warning "CPU limité: ${cpu_cores} cœurs (4+ recommandé)"
        fi
    fi
}

# Fonction de vérification de la structure projet
check_project_structure() {
    print_step "Vérification de la structure projet..."

    if [ -d "crew_a" ]; then
        print_success "Dossier crew_a trouvé"

        # Vérification des fichiers clés
        key_files=(
            "crew_a/src/eve_genesis___crew_a_construction_eveil/main.py"
            "crew_a/src/eve_genesis___crew_a_construction_eveil/config/agents.yaml"
            "crew_a/src/eve_genesis___crew_a_construction_eveil/config/tasks.yaml"
        )

        for file in "${key_files[@]}"; do
            if [ -f "$file" ]; then
                print_success "Fichier trouvé: $(basename $file)"
            else
                print_error "Fichier manquant: $file"
                return 1
            fi
        done

        # Vérification crew.py (doit être remplacé par la version optimisée)
        crew_py="crew_a/src/eve_genesis___crew_a_construction_eveil/crew.py"
        if [ -f "$crew_py" ]; then
            # Vérification si c'est la version optimisée
            if grep -q "FileManagerTool\|SystemMonitorTool" "$crew_py"; then
                print_success "crew.py - Version optimisée détectée"
            else
                print_warning "crew.py - Version originale détectée"
                echo -e "${YELLOW}⚠️ Il est recommandé d'utiliser la version optimisée de crew.py${NC}"
                echo -e "${YELLOW}   Remplacez le contenu par la version de l'artefact${NC}"
            fi
        else
            print_error "crew.py manquant"
            return 1
        fi
    else
        print_error "Dossier crew_a non trouvé"
        echo "Structure de projet EVE GENESIS requise"
        return 1
    fi
}

# Fonction de préparation de l'environnement
prepare_environment() {
    print_step "Préparation de l'environnement..."

    # Création des dossiers nécessaires
    dirs=("logs" "temp" "output" "data/backups" "monitoring")
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        print_success "Dossier créé: $dir"
    done

    # Variables d'environnement
    export EVE_ENV="test"
    export EVE_LOG_LEVEL="INFO"
    export EVE_TEST_MODE="true"
    export PYTHONPATH="$(pwd):$PYTHONPATH"

    print_success "Variables d'environnement configurées"
}

# Fonction de lancement du test
launch_test() {
    print_step "Lancement du test Crew A..."

    # Vérification finale
    if [ ! -f "test_crew_a_complete.py" ]; then
        print_error "Script de test non trouvé: test_crew_a_complete.py"
        echo "Assurez-vous que le script de test est présent dans le répertoire courant"
        return 1
    fi

    echo -e "${BLUE}📊 CONFIGURATION DU TEST:${NC}"
    echo "   - 41 agents spécialisés"
    echo "   - 40 tâches séquentielles"
    echo "   - 6 missions critiques"
    echo "   - Durée estimée: 2-6 heures"
    echo "   - Monitoring en temps réel"

    echo ""
    echo -e "${YELLOW}⚠️ AVERTISSEMENT FINAL:${NC}"
    echo "   - L'exécution sera longue et intensive"
    echo "   - Ne fermez pas le terminal pendant l'exécution"
    echo "   - Surveillez l'usage des ressources"

    echo ""
    read -p "🚀 Confirmer le lancement? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_success "Lancement confirmé"
        echo -e "${PURPLE}🚀 DÉMARRAGE DU TEST EVE GENESIS CREW A${NC}"
        echo ""

        # Lancement avec capture d'écran et logs
        python3 test_crew_a_complete.py 2>&1 | tee "logs/crew_a_execution_$(date +%Y%m%d_%H%M%S).log"

        exit_code=${PIPESTATUS[0]}

        if [ $exit_code -eq 0 ]; then
            print_success "TEST TERMINÉ AVEC SUCCÈS!"
        else
            print_error "TEST ÉCHOUÉ (code: $exit_code)"
        fi

        return $exit_code
    else
        echo -e "${YELLOW}Test annulé par l'utilisateur${NC}"
        return 1
    fi
}

# Fonction principale
main() {
    clear

    print_header "🤖 EVE GENESIS CREW A - LANCEMENT"
    echo -e "${BLUE}🧬 L'Ingénieur Adaptatif & Supervisable${NC}"
    echo -e "${BLUE}📊 41 Agents | 40 Tâches | 6 Missions${NC}"
    echo ""
    echo -e "${CYAN}📅 Démarrage: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""

    # Séquence de vérifications
    local all_checks_passed=true

    check_python || all_checks_passed=false
    echo ""

    check_ollama || all_checks_passed=false
    echo ""

    check_dependencies || all_checks_passed=false
    echo ""

    check_system_resources || all_checks_passed=false
    echo ""

    check_project_structure || all_checks_passed=false
    echo ""

    if [ "$all_checks_passed" = true ]; then
        print_success "TOUTES LES VÉRIFICATIONS RÉUSSIES"
        echo ""

        prepare_environment
        echo ""

        launch_test
        return $?
    else
        print_error "CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ"
        echo ""
        echo -e "${YELLOW}Corrigez les problèmes avant de relancer le script${NC}"
        return 1
    fi
}

# Point d'entrée
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
    exit $?
fi