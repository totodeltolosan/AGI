# -*- coding: utf-8 -*-

"""
Capteur : État de la Batterie

Ce module vérifie le statut de la batterie.
"""

import psutil
import json
from datetime import timedelta

def verifier():
    """
    Vérifie le pourcentage de la batterie et son état.
    """
    try:
        if hasattr(psutil, "sensors_battery"):
            batterie = psutil.sensors_battery()

            if batterie is None:
                return {"hardware_batterie": {"status": "Aucune batterie détectée"}}

            temps_restant_str = "N/A (sur secteur)"
            if batterie.secsleft and batterie.secsleft > 0:
                temps_restant_str = str(timedelta(seconds=batterie.secsleft))

            return {
                "hardware_batterie": {
                    "pourcentage": batterie.percent,
                    "en_charge": batterie.power_plugged,
                    "temps_restant_estime": temps_restant_str
                }
            }
        else:
            return {"hardware_batterie": {"status": "Non supporté sur cet OS"}}

    except Exception as e:
        return {"hardware_batterie": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : État de la Batterie ---")
    donnees = verifier()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
