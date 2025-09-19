# -*- coding: utf-8 -*-
"""
historique.py (v2.0 - Enregistreur Haute Performance)

Gère l'écriture des événements labellisés dans le fichier CSV d'historique.
Cette version utilise le module natif 'csv' pour une performance maximale
et une robustesse accrue. Elle est également thread-safe.
"""

import os
import csv
import threading
from datetime import datetime

# --- Constantes ---
HISTORIQUE_CSV = 'historique_alma.csv'

# Verrou pour empêcher les écritures concurrentes et la corruption de données
_log_lock = threading.Lock()

def enregistrer_evenement(donnees_evenement: dict):
    """
    Enregistre un événement complet dans le fichier CSV de manière efficace et sécurisée.

    Cette fonction est conçue pour être appelée une seule fois par événement,
    avec toutes les données déjà présentes, y compris la 'cause_reelle'.

    Args:
        donnees_evenement (dict): Un dictionnaire contenant toutes les données
                                  de l'événement à enregistrer. Les clés du
                                  dictionnaire seront utilisées comme en-tête CSV.
    """
    # On s'assure qu'une seule écriture a lieu à la fois
    with _log_lock:
        try:
            # On détermine si le fichier existe déjà pour savoir s'il faut écrire l'en-tête
            fichier_existe = os.path.exists(HISTORIQUE_CSV)

            # On ouvre le fichier en mode 'append' (ajout) pour ne pas tout réécrire
            with open(HISTORIQUE_CSV, 'a', newline='', encoding='utf-8') as f_csv:

                # Les noms des colonnes sont déterminés dynamiquement par les clés du dict
                header = list(donnees_evenement.keys())

                # On utilise DictWriter pour mapper directement notre dictionnaire au CSV
                writer = csv.DictWriter(f_csv, fieldnames=header)

                # Si le fichier vient d'être créé, on écrit la ligne d'en-tête
                if not fichier_existe:
                    writer.writeheader()

                # On écrit la ligne de données de notre événement
                writer.writerow(donnees_evenement)

            # print(f"[Historique] Événement avec cause '{donnees_evenement.get('cause_reelle')}' enregistré.")
            return True

        except Exception as e:
            print(f"[Erreur Historique] Impossible d'enregistrer l'événement : {e}")
            return False

# --- Bloc de test pour démontrer le fonctionnement ---
if __name__ == "__main__":
    print("--- Test du module Historique (v2.0) ---")

    # On simule un premier événement
    print("\n1. Enregistrement d'un premier événement (création du fichier)...")
    premier_evenement = {
        'timestamp': datetime.now().isoformat(),
        'cpu_charge': 85.5,
        'ram_usage_pourcentage': 60.2,
        'top_processus_nom': 'chrome.exe',
        'environnement_sonore': 'MUSIQUE',
        'diagnostic_initial': 'ANOMALIE CPU',
        'cause_reelle': 'NAVIGATION_WEB'
    }
    enregistrer_evenement(premier_evenement)

    # On simule un deuxième événement
    print("\n2. Enregistrement d'un deuxième événement (ajout au fichier existant)...")
    deuxieme_evenement = {
        'timestamp': datetime.now().isoformat(),
        'cpu_charge': 98.1,
        'ram_usage_pourcentage': 75.8,
        'top_processus_nom': 'cyberpunk.exe',
        'environnement_sonore': 'EXPLOSION',
        'diagnostic_initial': 'ANOMALIE CPU',
        'cause_reelle': 'JEU_VIDEO'
    }
    enregistrer_evenement(deuxieme_evenement)

    print(f"\nTest terminé. Vérifiez le contenu du fichier '{HISTORIQUE_CSV}'.")
