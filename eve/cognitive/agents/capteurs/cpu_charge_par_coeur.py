# -*- coding: utf-8 -*-

"""
Capteur : Charge par Cœur du CPU

Ce module mesure le pourcentage d'utilisation de chaque cœur
individuellement (logique).
"""

import psutil
import json
import time

def mesurer():
    """
    Mesure la charge de chaque cœur CPU sur un intervalle d'une seconde.

    :return: Un dictionnaire contenant une liste des charges.
             Ex: {'cpu_charge_par_coeur': {'charges_pourcentage': [10.2, 5.5, 8.1, 4.0]}}
    """
    try:
        # percpu=True retourne une liste de pourcentages, un pour chaque cœur logique.
        charges_par_coeur = psutil.cpu_percent(interval=1, percpu=True)

        return {
            "cpu_charge_par_coeur": {
                "charges_pourcentage": charges_par_coeur
            }
        }
    except Exception as e:
        return {"cpu_charge_par_coeur": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Charge par Cœur du CPU ---")
    print("Appuyez sur CTRL+C pour arrêter.")

    try:
        while True:
            donnees = mesurer()
            print(json.dumps(donnees, indent=4))
    except KeyboardInterrupt:
        print("\n--- Test terminé. ---")
