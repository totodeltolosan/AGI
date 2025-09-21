# -*- coding: utf-8 -*-

"""
Capteur : Utilisation de la Mémoire RAM

Ce module mesure l'utilisation de la mémoire vive (RAM) du système.
"""

import psutil
import json

def go_to_gb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Gigabytes."""
    return round(value_in_bytes / (1024**3), 2)

def mesurer():
    """
    Mesure l'utilisation de la RAM.

    :return: Un dictionnaire contenant les informations sur la RAM.
    """
    try:
        memoire = psutil.virtual_memory()

        return {
            "memoire_ram": {
                "usage_pourcentage": memoire.percent,
                "utilisee_gb": go_to_gb(memoire.used),
                "disponible_gb": go_to_gb(memoire.available),
                "totale_gb": go_to_gb(memoire.total)
            }
        }
    except Exception as e:
        return {"memoire_ram": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Utilisation de la Mémoire RAM ---")
    donnees = mesurer()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
