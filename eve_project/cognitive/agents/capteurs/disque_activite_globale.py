# -*- coding: utf-8 -*-

"""
Capteur : Activité Globale des Disques

Ce module compte le nombre total d'opérations et de données lues/écrites
sur tous les disques physiques depuis le démarrage du système.
"""

import psutil
import json

def go_to_mb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Megabytes."""
    return round(value_in_bytes / (1024**2), 2)

def compter():
    """
    Compte les opérations I/O totales du disque.

    :return: Un dictionnaire contenant les compteurs d'activité.
    """
    try:
        # psutil.disk_io_counters() retourne les statistiques système globales
        io_counters = psutil.disk_io_counters()

        return {
            "disque_activite_globale": {
                "nombre_lectures": io_counters.read_count,
                "nombre_ecritures": io_counters.write_count,
                "donnees_lues_mb": go_to_mb(io_counters.read_bytes),
                "donnees_ecrites_mb": go_to_mb(io_counters.write_bytes)
            }
        }
    except Exception as e:
        return {"disque_activite_globale": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Activité Globale des Disques ---")
    donnees = compter()
    print(json.dumps(donnees, indent=4))
    print("\nNote : Ces chiffres représentent l'activité totale depuis le démarrage.")
    print("--- Test terminé. ---")
