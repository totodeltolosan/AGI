# -*- coding: utf-8 -*-

"""
Capteur : Vitesse des Ventilateurs

Ce module tente de lire la vitesse des ventilateurs en tours par minute (RPM).
"""

import psutil
import json

def mesurer():
    """
    Tente de lire la vitesse des ventilateurs.
    """
    try:
        if hasattr(psutil, "sensors_fans"):
            vitesses_ventilateurs = psutil.sensors_fans()
            if not vitesses_ventilateurs:
                return {"hardware_ventilateurs": {"status": "Aucun ventilateur détecté"}}

            # On formate les données pour plus de clarté
            details = []
            for nom_sonde, mesures in vitesses_ventilateurs.items():
                for mesure in mesures:
                    details.append({
                        "nom_sonde": nom_sonde,
                        "label": mesure.label or 'N/A',
                        "vitesse_rpm": mesure.current
                    })
            return {"hardware_ventilateurs": {"details": details}}
        else:
            return {"hardware_ventilateurs": {"status": "Non supporté sur cet OS"}}

    except Exception as e:
        return {"hardware_ventilateurs": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Vitesse des Ventilateurs ---")
    donnees = mesurer()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
