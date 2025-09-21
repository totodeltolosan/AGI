# -*- coding: utf-8 -*-
"""
activite.py (v4.0 - Collecteur à Découverte Automatique)

Ce module est le chef d'orchestre de la collecte de données.
Il scanne dynamiquement le dossier 'capteurs/', charge chaque capteur
valide et exécute sa fonction de mesure.
"""

import importlib
import os
from pathlib import Path
import time

# Le seul import statique nécessaire est celui du dossier des capteurs
import capteurs

def collecter_donnees_dynamiques():
    """
    Scanne le dossier 'capteurs', charge dynamiquement chaque module de capteur,
    et appelle sa fonction 'mesurer()' pour rassembler les données.

    Retourne:
        dict: Un dictionnaire contenant les données de tous les capteurs actifs.
    """
    rapport_activite = {}
    # On définit le chemin vers le dossier des capteurs de manière robuste
    chemin_capteurs = Path(capteurs.__file__).parent

    # On parcourt tous les fichiers .py dans le dossier des capteurs
    for fichier_capteur in chemin_capteurs.glob('*.py'):
        nom_module = fichier_capteur.stem

        # On ignore les fichiers spéciaux comme __init__.py
        if nom_module.startswith('__'):
            continue

        try:
            # On construit le nom complet du module pour l'importation (ex: 'capteurs.cpu_charge_globale')
            module_a_importer = f"capteurs.{nom_module}"

            # On importe le module dynamiquement
            capteur_module = importlib.import_module(module_a_importer)

            # CONVENTION : Chaque module de capteur doit avoir une fonction 'mesurer'
            if hasattr(capteur_module, 'mesurer'):
                fonction_mesure = getattr(capteur_module, 'mesurer')

                # On exécute la mesure en la protégeant
                try:
                    donnees_capteur = fonction_mesure()
                    # On s'assure que le retour est bien un dictionnaire
                    if isinstance(donnees_capteur, dict):
                        rapport_activite.update(donnees_capteur)
                    else:
                        rapport_activite[nom_module] = {'erreur': 'Le capteur n\'a pas retourné un dictionnaire.'}

                except Exception as e:
                    # Si la fonction 'mesurer' échoue, on l'enregistre et on continue
                    rapport_activite[nom_module] = {'erreur': str(e)}
            else:
                # Si la convention n'est pas respectée, on le signale
                rapport_activite[nom_module] = {'erreur': 'Fonction "mesurer()" non trouvée.'}

        except Exception as e:
            # Si l'import du module lui-même échoue, on le signale et on continue
            rapport_activite[nom_module] = {'erreur': f'Impossible de charger le module. Erreur: {e}'}

    return rapport_activite

# --- Les anciennes fonctions sont conservées pour référence ou usage futur, mais ne sont plus appelées par le moteur ---

def collecter_donnees_statiques_legacy():
    """Rassemble les données qui ne changent pas (lourd et lent)."""
    # NOTE : Cette fonction est conservée mais n'est plus utilisée par le moteur principal
    # pour améliorer les performances de démarrage.
    try:
        from capteurs import disque_usage, systeme_utilisateurs
        import materiel
        import logiciels

        donnees = {}
        donnees.update(materiel.obtenir_profil_materiel_complet())
        donnees.update(logiciels.lister_applications_installees())
        return donnees
    except Exception as e:
        return {'erreur_statique': str(e)}

# --- Bloc de test pour vérifier le bon fonctionnement du collecteur ---
if __name__ == "__main__":
    print("--- Test du Collecteur à Découverte Automatique (v4.0) ---")
    print("Lancement de la collecte des données dynamiques...")
    start_time = time.time()
    donnees = collecter_donnees_dynamiques()
    end_time = time.time()
    print(f"Collecte terminée en {end_time - start_time:.4f} secondes.")

    print("\n--- Rapport de la Collecte ---")
    import json
    # On utilise json pour un affichage propre du dictionnaire
    print(json.dumps(donnees, indent=4, ensure_ascii=False))

    print("\n--- Vérification des Erreurs ---")
    erreurs = {k: v for k, v in donnees.items() if isinstance(v, dict) and 'erreur' in v}
    if erreurs:
        print("Des erreurs ont été détectées dans les capteurs suivants :")
        for nom_capteur, data in erreurs.items():
            print(f"  - {nom_capteur}: {data['erreur']}")
    else:
        print("Aucune erreur détectée. Tous les capteurs ont répondu correctement.")
