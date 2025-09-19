# -*- coding: utf-8 -*-

"""
Capteur : Uptime (Durée de fonctionnement) du Système

Ce module calcule depuis combien de temps le système est démarré.
"""

import psutil
import json
from datetime import datetime, timedelta

def calculer():
    """
    Calcule la durée de fonctionnement du système.

    :return: Un dictionnaire contenant la durée de fonctionnement formatée.
    """
    try:
        # psutil.boot_time() retourne le timestamp du démarrage
        temps_demarrage = datetime.fromtimestamp(psutil.boot_time())
        # On calcule la différence avec l'heure actuelle
        uptime = datetime.now() - temps_demarrage

        # On formate le résultat pour une meilleure lisibilité
        jours = uptime.days
        heures, reste = divmod(uptime.seconds, 3600)
        minutes, secondes = divmod(reste, 60)

        return {
            "systeme_uptime": {
                "jours": jours,
                "heures": heures,
                "minutes": minutes,
                "secondes": secondes,
                "texte_lisible": f"{jours}j {heures}h {minutes}m {secondes}s"
            }
        }
    except Exception as e:
        return {"systeme_uptime": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Uptime du Système ---")
    donnees = calculer()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
