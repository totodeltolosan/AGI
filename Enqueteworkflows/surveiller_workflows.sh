#!/bin/bash

# --- CONFIGURATION ---
REPO="totodeltolosan/AGI"
BRANCH="agi-main"
LOG_FILE="/home/toni/Documents/Projet AGI/Enqueteworkflows/workflow_run.log"

# --- SCRIPT ---
echo "==================================================================="
echo "🔎 Script de Surveillance des Workflows pour le projet AGI (v2)"
echo "==================================================================="
echo "Dépôt   : $REPO"
echo "Branche : $BRANCH"
echo "Logs    : $LOG_FILE"
echo "-------------------------------------------------------------------"

# Vider le fichier de log précédent
> "$LOG_FILE"

# Étape 1: Obtenir l'ID du dernier workflow comme point de référence.
# S'il n'y en a pas, on initialise à 0.
LATEST_RUN_ID_BEFORE_START=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json databaseId --jq '.[0].databaseId' || echo "0")
if [[ -z "$LATEST_RUN_ID_BEFORE_START" ]]; then
    LATEST_RUN_ID_BEFORE_START="0"
fi

echo "[$(date +%T)] ⏳ Point de référence établi. Dernier ID de run : $LATEST_RUN_ID_BEFORE_START"
echo "[$(date +%T)] ⏳ En attente d'une NOUVELLE exécution sur la branche '$BRANCH'..."
echo "[$(date +%T)] Astuce : Faites un 'git push' dans un autre terminal pour déclencher."

NEW_RUN_ID=""
# Étape 2: Boucler jusqu'à trouver un workflow avec un ID plus récent.
while true; do
    # On cherche le dernier run qui est soit en cours, soit en attente, soit terminé
    CANDIDATE_RUN_ID=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json databaseId --jq '.[0].databaseId' || echo "0")
    
    # On vérifie si l'ID trouvé est plus récent que notre point de référence
    if [[ "$CANDIDATE_RUN_ID" -gt "$LATEST_RUN_ID_BEFORE_START" ]]; then
        NEW_RUN_ID=$CANDIDATE_RUN_ID
        echo
        echo "[$(date +%T)] ✅ NOUVEAU workflow détecté ! ID de l'exécution : $NEW_RUN_ID"
        echo "[$(date +%T)] 📡 Connexion au flux de logs en direct..."
        echo "-------------------------------------------------------------------"
        break
    fi
    # Affiche un point pour montrer que le script est en vie et attend
    printf "."
    sleep 5
done

# Étape 3: Surveiller l'exécution du nouveau workflow en direct et sauvegarder les logs.
gh run watch "$NEW_RUN_ID" --repo "$REPO" --exit-status | tee "$LOG_FILE"

# Récupérer le statut final de l'exécution
CONCLUSION=$(gh run view "$NEW_RUN_ID" --repo "$REPO" --json conclusion --jq '.conclusion')

echo "-------------------------------------------------------------------"
if [[ "$CONCLUSION" == "success" ]]; then
    echo "[$(date +%T)] ✅ SUCCÈS : Le workflow (ID: $NEW_RUN_ID) a terminé avec succès."
else
    echo "[$(date +%T)] ❌ ÉCHEC : Le workflow (ID: $NEW_RUN_ID) a échoué avec le statut : $CONCLUSION."
fi
echo "Logs complets sauvegardés dans : $LOG_FILE"
echo "==================================================================="

