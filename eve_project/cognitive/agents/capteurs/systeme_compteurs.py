# -*- coding: utf-8 -*-

"""
Capteur : Compteurs Système

Ce module compte le nombre total de processus et de threads en cours.
"""

import psutil
import json

def compter():
    """
    Compte le nombre total de processus et de threads.
    """
    try:
        pids = psutil.pids()
        total_threads = sum(psutil.Process(pid).num_threads() for pid in pids)

        return {
            "systeme_compteurs": {
                "nombre_processus": len(pids),
                "nombre_threads": total_threads
            }
        }
    except Exception as e:
        return {"systeme_compteurs": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Compteurs Système ---")
    donnees = compter()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
