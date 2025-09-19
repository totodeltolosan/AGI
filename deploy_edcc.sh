#!/bin/bash
#
# SCRIPT PRINCIPAL DE DÉPLOIEMENT DE L'EDCC
# Orchestre l'installation de l'Écosystème de Développement à Conscience Constitutionnelle.
#

echo "🚀 Démarrage du déploiement de l'EDCC..."
echo ""

# Vérification des prérequis
if ! command -v git &> /dev/null
then
    echo "❌ ERREUR: Git n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

echo "✅ Prérequis validés."
echo ""

echo ">>> ÉTAPE 1 : Configuration de l'espace de travail VS Code..."
bash scripts/setup/01_setup_vscode_workspace.sh
echo ""

echo ">>> ÉTAPE 2 : Création des workflows GitHub Actions..."
bash scripts/setup/02_create_github_workflows.sh
echo ""

echo "🎉 Déploiement des configurations automatiques terminé."
echo ""
echo "🔴 ACTION MANUELLE REQUISE 🔴"
echo "Vous devez maintenant suivre les instructions du guide de configuration manuelle."
echo "Pour afficher le guide, exécutez la commande suivante :"
echo "cat docs/GITHUB_SETUP_GUIDE.md"
echo ""
echo "Une fois ces étapes manuelles terminées, n'oubliez pas de commiter les changements :"
echo "git add ."
echo "git commit -m \"feat(env): Deploy Constitutional Development Ecosystem\""
echo "git push"
