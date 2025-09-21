# -*- coding: utf-8 -*-

"""
Capteur : Utilisation de la Mémoire d'Échange (SWAP)

Ce module mesure l'utilisation de la mémoire d'échange du système.
"""

import psutil
import json

def go_to_gb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Gigabytes."""
    return round(value_in_bytes / (1024**3), 2)

def mesurer():
    """
    Mesure l'utilisation de la SWAP.

    :return: Un dictionnaire contenant les informations sur la SWAP.
    """
    try:
        swap = psutil.swap_memory()

        return {
            "memoire_swap": {
                "usage_pourcentage": swap.percent,
                "utilisee_gb": go_to_gb(swap.used),
                "libre_gb": go_to_gb(swap.free),
                "totale_gb": go_to_gb(swap.total)
            }
        }
    except Exception as e:
        return {"memoire_swap": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Utilisation de la Mémoire SWAP ---")
    donnees = mesurer()
    print(json.dumps(donnees, indent=4))
    print("\nNote : Il est normal que les valeurs soient à 0 si votre RAM n'est pas saturée.")
    print("--- Test terminé. ---")
