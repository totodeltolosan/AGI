# -*- coding: utf-8 -*-

"""
Capteur : Vitesse des Disques en Temps Réel

Ce module calcule la vitesse de lecture et d'écriture actuelle sur tous
les disques en comparant les compteurs I/O à 1 seconde d'intervalle.
"""

import psutil
import json
import time

def go_to_mb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Megabytes."""
    return round(value_in_bytes / (1024**2), 2)

def calculer():
    """
    Calcule la vitesse de lecture/écriture en Mo/s.

    :return: Un dictionnaire contenant les vitesses calculées.
    """
    try:
        # Première mesure des compteurs
        t1_read_bytes = psutil.disk_io_counters().read_bytes
        t1_write_bytes = psutil.disk_io_counters().write_bytes

        # On attend 1 seconde
        time.sleep(1)

        # Deuxième mesure des compteurs
        t2_read_bytes = psutil.disk_io_counters().read_bytes
        t2_write_bytes = psutil.disk_io_counters().write_bytes

        # Calcul de la différence
        lecture_vitesse_mbs = go_to_mb(t2_read_bytes - t1_read_bytes)
        ecriture_vitesse_mbs = go_to_mb(t2_write_bytes - t1_write_bytes)

        return {
            "disque_vitesse": {
                "lecture_mo_par_seconde": lecture_vitesse_mbs,
                "ecriture_mo_par_seconde": ecriture_vitesse_mbs
            }
        }
    except Exception as e:
        return {"disque_vitesse": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Vitesse des Disques en Temps Réel ---")
    print("Appuyez sur CTRL+C pour arrêter.")

    try:
        while True:
            donnees = calculer()
            print(json.dumps(donnees, indent=4))
    except KeyboardInterrupt:
        print("\n--- Test terminé. ---")
