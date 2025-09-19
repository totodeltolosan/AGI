# -*- coding: utf-8 -*-

"""
Capteur : Temps d'utilisation du CPU

Ce module analyse comment le temps du processeur est réparti entre
les différentes tâches (utilisateur, système, inactivité, etc.).
"""

import psutil
import json
import time

def analyser():
    """
    Analyse la répartition du temps CPU sur un intervalle d'une seconde.

    :return: Un dictionnaire contenant les pourcentages de temps.
    """
    try:
        # Renvoie un objet spécial avec des attributs pour chaque catégorie de temps
        temps_cpu = psutil.cpu_times_percent(interval=1)

        return {
            "cpu_temps_systeme": {
                "temps_utilisateur_pourcentage": temps_cpu.user,
                "temps_systeme_pourcentage": temps_cpu.system,
                "temps_inactif_pourcentage": temps_cpu.idle
            }
        }
    except Exception as e:
        return {"cpu_temps_systeme": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Temps d'utilisation du CPU ---")
    print("Appuyez sur CTRL+C pour arrêter.")

    try:
        while True:
            donnees = analyser()
            print(json.dumps(donnees, indent=4))
    except KeyboardInterrupt:
        print("\n--- Test terminé. ---")
