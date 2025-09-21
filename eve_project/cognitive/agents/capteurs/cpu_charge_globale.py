# -*- coding: utf-8 -*-

"""
Capteur : Charge Globale du CPU

Ce module est un capteur spécialisé pour mesurer le pourcentage
d'utilisation global du processeur.
"""

import psutil
import json
import time

def mesurer():
    """
    Mesure la charge CPU globale sur un intervalle d'une seconde.

    :return: Un dictionnaire contenant la mesure.
             Ex: {'cpu_charge_globale': {'charge_cpu_pourcentage': 12.5}}
    """
    try:
        # L'intervalle de 1 seconde est important pour obtenir une moyenne fiable
        # et non une valeur instantanée qui serait souvent de 0 ou 100.
        charge = psutil.cpu_percent(interval=1)

        # Le dictionnaire retourné utilise le nom du module comme clé principale.
        # C'est ainsi que `activite.py` saura comment assembler les données.
        return {
            "cpu_charge_globale": {
                "charge_cpu_pourcentage": charge
            }
        }
    except Exception as e:
        return {"cpu_charge_globale": {"erreur": str(e)}}

# --- Bloc de test ---
# Permet de tester ce capteur individuellement.
if __name__ == "__main__":
    print("--- Test du capteur : Charge Globale du CPU ---")
    print("Appuyez sur CTRL+C pour arrêter.")

    try:
        while True:
            donnees = mesurer()
            print(json.dumps(donnees, indent=4))
            # La fonction mesurer() inclut déjà une pause de 1s,
            # donc pas besoin d'un time.sleep() supplémentaire ici.
    except KeyboardInterrupt:
        print("\n--- Test terminé. ---")
