# -*- coding: utf-8 -*-

"""
Capteur : Top 5 des Processus

Ce module identifie les 5 processus les plus gourmands en CPU.
VERSION 1.1 : Correction du bug 'time' non défini.
"""

import psutil
import json
import time # <-- LA CORRECTION EST ICI

def lister():
    """
    Retourne une liste des 5 processus les plus gourmands en CPU.
    """
    processus = []
    try:
        # On demande à psutil de pré-charger les informations dont on a besoin
        # Le premier appel à cpu_percent() pour un processus retourne 0.0
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                # On force une première lecture pour initialiser le compteur cpu_percent
                p.info['cpu_percent'] = p.cpu_percent(interval=0.1)
                processus.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # On trie la liste par utilisation du CPU, du plus grand au plus petit
        processus_tries = sorted(processus, key=lambda p: p.get('cpu_percent', 0), reverse=True)

        return {"processus_top": {"details": processus_tries[:5]}}

    except Exception as e:
        return {"processus_top": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Top 5 des Processus ---")
    print("Capture des processus actifs...")
    donnees = lister()
    print(json.dumps(donnees, indent=4, ensure_ascii=False))
    print("\n--- Test terminé. ---")
