# -*- coding: utf-8 -*-

"""
Capteur : Activité Globale du Réseau

Ce module compte le nombre total de données envoyées et reçues
sur toutes les interfaces réseau depuis le démarrage du système.
"""

import psutil
import json

def go_to_mb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Megabytes."""
    return round(value_in_bytes / (1024**2), 2)

def compter():
    """
    Compte les I/O réseau totaux.

    :return: Un dictionnaire contenant les compteurs d'activité réseau.
    """
    try:
        net_io = psutil.net_io_counters()

        return {
            "reseau_activite_globale": {
                "donnees_envoyees_mb": go_to_mb(net_io.bytes_sent),
                "donnees_recues_mb": go_to_mb(net_io.bytes_recv)
            }
        }
    except Exception as e:
        return {"reseau_activite_globale": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Activité Globale du Réseau ---")
    donnees = compter()
    print(json.dumps(donnees, indent=4))
    print("\nNote : Ces chiffres représentent l'activité totale depuis le démarrage.")
    print("--- Test terminé. ---")
