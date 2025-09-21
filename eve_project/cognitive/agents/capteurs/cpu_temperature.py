# -*- coding: utf-8 -*-

"""
Capteur : Température du CPU

Ce module tente de lire la température des sondes thermiques associées au CPU.
La disponibilité de ces informations est très dépendante du matériel et de l'OS.
"""

import psutil
import json
import time

def mesurer():
    """
    Tente de lire la température de la sonde 'coretemp', la plus commune pour les CPU.

    :return: Un dictionnaire contenant la température ou un statut.
    """
    try:
        # psutil.sensors_temperatures() retourne un dictionnaire de toutes les sondes.
        # Ex: {'coretemp': [shwtemp(label='', current=55.0, high=82.0, critical=92.0)], ...}
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()

            # On cherche en priorité la sonde 'coretemp' qui correspond aux coeurs du CPU.
            if 'coretemp' in temps:
                # On prend la première mesure de cette sonde (souvent la température globale du package)
                temp_cpu = temps['coretemp'][0].current
                return {
                    "cpu_temperature": {
                        "temperature_celsius": temp_cpu
                    }
                }
            else:
                # Si 'coretemp' n'est pas trouvé, on signale que la sonde est absente.
                return {"cpu_temperature": {"status": "Sonde CPU non trouvée"}}
        else:
            # Si la fonction n'existe pas sur l'OS (rare)
            return {"cpu_temperature": {"status": "Non supporté sur cet OS"}}

    except Exception as e:
        return {"cpu_temperature": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Température du CPU ---")
    donnees = mesurer()
    print(json.dumps(donnees, indent=4))
    print("\nNote : Il est normal que le résultat soit 'Sonde non trouvée' ou 'Non supporté'")
    print("si votre système ne donne pas facilement accès à ces informations.")
    print("\n--- Test terminé. ---")
