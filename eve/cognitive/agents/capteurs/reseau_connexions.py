# -*- coding: utf-8 -*-

"""
Capteur : Connexions Réseau Actives

Ce module compte le nombre de connexions réseau, en les groupant
par leur statut (établie, en attente, etc.).
"""

import psutil
import json
from collections import Counter

def compter():
    """
    Compte le nombre de connexions réseau par statut.

    :return: Un dictionnaire contenant les compteurs de connexions.
    """
    try:
        # psutil.net_connections() retourne une longue liste de toutes les connexions
        connexions = psutil.net_connections()

        # On utilise un compteur pour grouper facilement les connexions par leur statut
        statuts_compteur = Counter(c.status for c in connexions)

        return {
            "reseau_connexions": {
                "total_connexions": len(connexions),
                "details_par_statut": dict(statuts_compteur)
            }
        }
    except Exception as e:
        return {"reseau_connexions": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Connexions Réseau Actives ---")
    donnees = compter()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
