#!/bin/bash
# ==============================================================================
# SCRIPT DE DÉCOUVERTE AUTOMATISÉ DU PROJET AGI (Version Corrigée)
# ==============================================================================
set -e
set -o pipefail

PROJECT_ROOT="/home/toni/Documents/Projet AGI"
OUTPUT_FILE="${PROJECT_ROOT}/AGI_Project_Discovery_Report_COMPLET.md"
GENERATOR_TOOL_PATH="${PROJECT_ROOT}/tools/project_initializer"
GENERATED_SKELETON_PATH="/tmp/agi_discovery_run_$(date +%s)"

{
echo "# RAPPORT DE DÉCOUVERTE COMPLÈTE DU PROJET AGI"
echo " "
echo "**Date de génération :** $(date)"
echo "**Généré depuis :** $(pwd)"
echo "**Répertoire du projet analysé :** ${PROJECT_ROOT}"
echo "***"

# ==============================================================================
# PHASE 1 : ORIENTATION ET VUE D'ENSEMBLE
# ==============================================================================
echo "## PHASE 1 : Orientation et Vue d'Ensemble"
echo " "
echo "### 1.1. Contenu détaillé de la racine du projet"
echo "\`\`\`bash"
ls -la "${PROJECT_ROOT}"
echo "\`\`\`"
echo "***"

echo "### 1.2. Arborescence complète du projet"
if ! command -v tree &> /dev/null; then
    echo "**AVERTISSEMENT :** La commande \`tree\` n'est pas installée."
else
    echo "\`\`\`bash"
    tree "${PROJECT_ROOT}"
    echo "\`\`\`"
fi
echo "***"

echo "### 1.3. Analyse du nombre de lignes par fichier Python (CORRIGÉ)"
echo "\`\`\`bash"
find "${PROJECT_ROOT}" -name "*.py" -print0 | xargs -0 wc -l | sort -nr
echo "\`\`\`"
echo "***"

# ==============================================================================
# PHASE 2 : ANALYSE DES ARTEFACTS CLÉS
# ==============================================================================
echo "## PHASE 2 : Analyse des Artefacts Clés"
echo " "
echo "### 2.1. Contenu de la Constitution : AGI.md"
echo "\`\`\`markdown"
cat "${PROJECT_ROOT}/AGI.md"
echo "\`\`\`"
echo "***"

echo "### 2.2. Contenu du Rapport de Continuité : AGI3.md"
echo "\`\`\`markdown"
cat "${PROJECT_ROOT}/AGI3.md"
echo "\`\`\`"
echo "***"

echo "### 2.3. Contenu du Point d'Entrée du Générateur : project_initializer.py"
echo "\`\`\`python"
cat "${GENERATOR_TOOL_PATH}/project_initializer.py"
echo "\`\`\`"
echo "***"

# ==============================================================================
# PHASE 3 : PLONGÉE DANS LE CODE DU GÉNÉRATEUR
# ==============================================================================
echo "## PHASE 3 : Plongée dans le Code du Générateur (Flux d'Exécution)"
echo " "
FILES_TO_INSPECT=(
    "core/orchestrator.py"
    "parsers/agi_parser.py"
    "config/domains.py"
    "config/python_files.py"
    "file_generators/python_generator.py"
    "file_generators/json_generator.py"
    "file_generators/markdown_generator.py"
    "templates/python_tpl.py"
    "validators/paths.py"
    "utils/agi_logger.py"
)
for file in "${FILES_TO_INSPECT[@]}"; do
    if [ -f "${GENERATOR_TOOL_PATH}/${file}" ]; then
        echo "### 3.x. Contenu de : \`${file}\`"
        echo "\`\`\`python"
        cat "${GENERATOR_TOOL_PATH}/${file}"
        echo "\`\`\`"
        echo "***"
    fi
done

# ==============================================================================
# PHASE 4 : ANALYSE DES DÉPENDANCES
# ==============================================================================
echo "## PHASE 4 : Analyse des Dépendances"
echo " "
echo "### 4.1. Recherche de fichiers de dépendances standards"
echo "\`\`\`bash"
find "${PROJECT_ROOT}" -name "requirements.txt" -o -name "pyproject.toml" || echo "Aucun fichier de dépendances standard trouvé."
echo "\`\`\`"
echo "***"

echo "### 4.2. Déduction des dépendances par analyse des imports"
echo "\`\`\`bash"
grep -rhE "^import |^from " "${GENERATOR_TOOL_PATH}/" | sort | uniq
echo "\`\`\`"
echo "***"

# ==============================================================================
# PHASE 5 : VALIDATION ET EXÉCUTION
# ==============================================================================
echo "## PHASE 5 : Validation et Exécution"
echo " "
echo "### 5.1. Exécution des scripts de validation du projet"
if [ -f "${PROJECT_ROOT}/verification_compliance_script.sh" ]; then
    echo "\`\`\`bash"
    chmod +x "${PROJECT_ROOT}/verification_compliance_script.sh"
    bash "${PROJECT_ROOT}/verification_compliance_script.sh"
    echo "\`\`\`"
fi
if [ -f "${PROJECT_ROOT}/quick_check_lines.py" ]; then
    echo "\`\`\`bash"
    python3 "${PROJECT_ROOT}/quick_check_lines.py" "${GENERATOR_TOOL_PATH}/"
    echo "\`\`\`"
fi
echo "***"

echo "### 5.2. Test de génération du squelette dans un répertoire temporaire"
echo "\`\`\`bash"
python3 "${GENERATOR_TOOL_PATH}/project_initializer.py" --output "${GENERATED_SKELETON_PATH}" --verbose
echo "\`\`\`"
echo "***"

echo "### 5.3. Vérification du squelette généré"
if ! command -v tree &> /dev/null; then
    echo "**AVERTISSEMENT :** La commande \`tree\` n'est pas installée."
    ls -R "${GENERATED_SKELETON_PATH}"
else
    echo "\`\`\`"
    tree "${GENERATED_SKELETON_PATH}"
    echo "\`\`\`"
fi
rm -rf "${GENERATED_SKELETON_PATH}"
echo "Nettoyage du répertoire temporaire effectué."
echo "***"

echo "## FIN DU RAPPORT"

} > "${OUTPUT_FILE}" 2>&1

echo "✅ Rapport de découverte COMPLET généré avec succès."
echo "Le fichier se trouve ici : ${OUTPUT_FILE}"
