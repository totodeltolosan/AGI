# generateur_config.py
"""
Génère le fichier de configuration `config.json` à partir d'un dictionnaire
Python. C'est la méthode la plus fiable pour éviter les erreurs de syntaxe JSON.
"""
import json

config_data = {
    "environnement": {
        "taille": 100,
        "ressources_initiales": 0,
        "ressources_par_cycle": 0,
        "nombre_obstacles": 20,
        "taille_obstacle_max": 8,
        "terrain_variable": True,
        "cout_mouvement_difficile": 1.4,
    },
    "cycles_temporels": {
        "saisons_activees": True,
        "duree_saison": 5000,
        "modificateur_ressources_hiver": 0.4,
    },
    "organisme": {
        "population_initiale_vegetal": 600,
        "population_initiale_insecte": 200,
        "population_initiale_animal": 60,
        "energie_initiale": 250,
    },
    "evolution": {
        "cout_de_vie": 1,
        "cout_action": 1,
        "gain_energie_vegetal": 15,
        "gain_energie_insecte": 40,
        "seuil_reproduction": 220,
    },
    "genetique": {
        "mode_reproduction": "asexuee",
        "chance_mutation_genome": 0.9,
        "taux_mutation_poids": 0.15,
        "chance_mutation_type": 0.02,
        "cout_energie_par_poids_neuronal": 0.0002,
    },
    "biologie": {
        "vieillissement_active": True,
        "esperance_vie_min": 600,
        "esperance_vie_max": 1000,
        "duree_gestation": 25,
        "corps_devient_ressource": True,
        "energie_corps": 50,
        "epidemie_activee": False,
        "toxicite_activee": False,
    },
    "predation": {"cout_attaque": 3, "gain_energie_predation": 100},
    "societe": {"chance_mutation_tribu": 0.01},
    "cerveau": {"neurones_entree": 25, "neurones_sortie": 9},
}
try:
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    print("✅ Fichier config.json généré avec succès !")
except IOError as e:
    print(f"❌ Une erreur d'écriture est survenue : {e}")
