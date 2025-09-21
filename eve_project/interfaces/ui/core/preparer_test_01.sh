#!/bin/bash

# Script de préparation pour le Scénario 01 : Survie Initiale
# Automatise la mise en place de l'environnement de test

echo "=== PRÉPARATION SCÉNARIO 01 : SURVIE INITIALE (10 MINUTES) ==="
echo "Début de la préparation à $(date)"

# ... (les sections 1, 2 et 3 du script restent identiques) ...
if [ ! -f "lanceur.py" ]; then
    echo "ERREUR: lanceur.py non trouvé. Exécutez ce script depuis la racine du projet."
    exit 1
fi
if ! command -v minetest &> /dev/null; then
    echo "ERREUR: Minetest n'est pas installé."
    exit 1
fi
if [ ! -d "env" ]; then
    echo "ERREUR: Environnement virtuel Python non trouvé."
    exit 1
fi
echo "✓ Environnement validé"
source env/bin/activate
echo "✓ Environnement Python activé"
mkdir -p tests/scenario_01/logs tests/scenario_01/data tests/scenario_01/monde
echo "✓ Dossiers de test créés"

# 4. Configuration du monde Minetest
echo "[4/6] Configuration du monde de test..."
cat > tests/scenario_01/monde/world.mt << EOF
gameid = minetest_game
world_name = test_survie_01
enable_damage = true
creative_mode = false
enable_pvp = false
time_speed = 72
server_announce = false
EOF

# Configuration des paramètres du test
cat > tests/scenario_01/config_test.json << EOF
{
    "version_config": "1.0-test",
    "parametres": {
        "simulation": {
            "duree_test_minutes": 10,
            "taille_max_go": 1,
            "facteur_temps_defaut": 1.0,
            "seed_monde": "test_survie_01"
        },
        "test": {
            "heure_spawn": "17:00",
            "biome_spawn": "forest",
            "difficulte": "normal",
            "logging_verbeux": true
        },
        "emotions": {
            "confiance_initiale": 0.5,
            "seuil_jours_adolescence": 1,
            "seuil_jours_adulte": 2
        },
        "criteres_reussite": {
            "duree_survie_min": 10,
            "faim_minimum": 15,
            "sante_minimum": 50,
            "bois_minimum": 20,
            "pierre_minimum": 10,
            "concepts_minimum": 5
        }
    }
}
EOF

echo "✓ Monde de test configuré"

# ... (les sections 5 et 6 du script restent identiques) ...
echo "[5/6] Initialisation des logs de test..."
touch tests/scenario_01/logs/test_execution.log
touch tests/scenario_01/logs/actions_ia.log
touch tests/scenario_01/logs/emotions.log
touch tests/scenario_01/logs/erreurs.log
echo "✓ Logs initialisés"

echo "[6/6] Vérification finale..."
if [ -f "tests/scenario_01/config_test.json" ]; then
    echo "✓ Configuration de test créée"
else
    echo "ERREUR: Échec de création de la configuration"
    exit 1
fi

echo ""
echo "=== PRÉPARATION TERMINÉE ==="
echo "Le test peut maintenant être lancé."