# -*- coding: utf-8 -*-

"""
Capteur : Utilisateurs Connectés

Ce module liste les utilisateurs actuellement connectés au système.
"""

import psutil
import json
from datetime import datetime

def lister():
    """
    Liste les utilisateurs connectés.

    :return: Un dictionnaire contenant une liste des utilisateurs.
    """
    try:
        utilisateurs = psutil.users()
        details_utilisateurs = []
        for u in utilisateurs:
            details_utilisateurs.append({
                "nom": u.name,
                "terminal": u.terminal,
                "host": u.host,
                "heure_connexion": datetime.fromtimestamp(u.started).strftime("%Y-%m-%d %H:%M:%S")
            })

        return {"systeme_utilisateurs": {"utilisateurs_connectes": details_utilisateurs}}

    except Exception as e:
        return {"systeme_utilisateurs": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Utilisateurs Connectés ---")
    donnees = lister()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
