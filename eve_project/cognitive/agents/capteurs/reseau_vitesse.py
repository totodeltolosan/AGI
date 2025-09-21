# -*- coding: utf-8 -*-

"""
Capteur : Vitesse du Réseau en Temps Réel

Ce module calcule la vitesse d'envoi (upload) et de réception (download)
actuelle sur toutes les interfaces réseau.
"""

import psutil
import json
import time

def go_to_mbit(value_in_bytes):
    """
    Petite fonction pour convertir les bytes en Megabits.
    Les vitesses réseau sont traditionnellement exprimées en bits/s.
    1 Megabit = 125000 bytes (1000*1000 / 8)
    """
    return round((value_in_bytes * 8) / (1000**2), 2)

def calculer():
    """
    Calcule la vitesse d'envoi/réception en Mbit/s.

    :return: Un dictionnaire contenant les vitesses calculées.
    """
    try:
        # Première mesure des compteurs
        t1 = psutil.net_io_counters()

        # On attend 1 seconde
        time.sleep(1)

        # Deuxième mesure des compteurs
        t2 = psutil.net_io_counters()

        # Calcul de la différence et conversion en Mbits/s
        upload_mbs = go_to_mbit(t2.bytes_sent - t1.bytes_sent)
        download_mbs = go_to_mbit(t2.bytes_recv - t1.bytes_recv)

        return {
            "reseau_vitesse": {
                "envoi_mbit_par_seconde": upload_mbs,
                "reception_mbit_par_seconde": download_mbs
            }
        }
    except Exception as e:
        return {"reseau_vitesse": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Vitesse du Réseau en Temps Réel ---")
    print("Appuyez sur CTRL+C pour arrêter.")

    try:
        while True:
            donnees = calculer()
            print(json.dumps(donnees, indent=4))
    except KeyboardInterrupt:
        print("\n--- Test terminé. ---")
