# -*- coding: utf-8 -*-
"""Capteur Sonore - Enfant : Base de données des sons"""
import json
import os
# numpy n'est plus nécessaire ici car on ne manipule plus ses objets
# import numpy as np

# Le chemin est maintenant relatif au dossier 'sonore'
DB_SONS_JSON = os.path.join(os.path.dirname(__file__), 'db_sons_alma.json')

def sauvegarder_son(empreinte_mfcc: list, label: str):
    """
    Sauvegarde une empreinte sonore (déjà sous forme de liste) et son label.
    """
    try:
        donnees = []
        # On s'assure que le fichier existe avant de tenter de le lire
        if os.path.exists(DB_SONS_JSON) and os.path.getsize(DB_SONS_JSON) > 0:
            try:
                with open(DB_SONS_JSON, 'r', encoding='utf-8') as f:
                    donnees = json.load(f)
            except json.JSONDecodeError:
                print(f"[Avertissement DB Sonore] Le fichier {DB_SONS_JSON} est corrompu. Il va être réinitialisé.")
                donnees = []

        # --- DÉBUT DE LA CORRECTION ---
        # L'empreinte est déjà une liste, on l'utilise directement.
        donnees.append({
            "label": label,
            "mfcc": empreinte_mfcc
        })
        # --- FIN DE LA CORRECTION ---

        with open(DB_SONS_JSON, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=4)

        print(f"[DB Sonore] Le son '{label}' a été sauvegardé pour l'entraînement.")
        return True
    except Exception as e:
        print(f"[Erreur DB Sonore] Impossible de sauvegarder le son : {e}")
        return False
