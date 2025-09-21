#!/bin/bash
#
# SCRIPT D'INSTALLATION GUIDÉ POUR L'ESPACE DE TRAVAIL VS CODE
# Ce script configure l'IDE pour qu'il soit conscient de la constitution AGI.
#

echo "--- Étape 1/3 : Création de la configuration de l'espace de travail (.vscode) ---"
mkdir -p .vscode
echo "[OK] Répertoire .vscode créé."
echo ""

# --- Création de settings.json ---
echo "--- Étape 2/3 : Configuration des paramètres (settings.json) ---"
echo "Configuration de l'interpréteur Python, du formatage, et préparation du linter constitutionnel..."
cat << 'EOSH' > .vscode/settings.json
{
    // Lie l'IDE à notre environnement virtuel. C'est une règle absolue.
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    
    // Assure un code propre et uniforme à chaque sauvegarde.
    "editor.formatOnSave": true,
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,

    // Directive future : prépare VS Code à reconnaître notre linter personnalisé.
    // Cette section deviendra active une fois l'extension développée.
    "linter-ia-god.configFile": "${workspaceFolder}/iaGOD.json",
    "linter-ia-god.enabled": true
}
EOSH
echo "[OK] Fichier .vscode/settings.json créé et configuré."
echo ""

# --- Création de extensions.json ---
echo "--- Étape 3/3 : Recommandation des extensions (extensions.json) ---"
echo "Configuration des extensions recommandées pour assurer un environnement de travail homogène..."
cat << 'EOE' > .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylint",
        "eamodio.gitlens",
        "github.vscode-pull-request-github",
        "ms-vscode-remote.remote-ssh",
        "redhat.vscode-yaml" // Essentiel pour éditer iaGOD.json et les fichiers LIHN
    ]
}
EOE
echo "[OK] Fichier .vscode/extensions.json créé."
echo ""
echo "✅ Configuration de l'espace de travail VS Code terminée."
