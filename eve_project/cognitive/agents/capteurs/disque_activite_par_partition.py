# -*- coding: utf-8 -*-

"""
Capteur : Activité des Disques par Partition Physique

Ce module détaille le nombre total d'opérations et de données lues/écrites
pour chaque disque physique détecté par le système.
"""

import psutil
import json

def go_to_mb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Megabytes."""
    return round(value_in_bytes / (1024**2), 2)

def compter():
    """
    Compte les opérations I/O pour chaque disque physique.

    :return: Un dictionnaire contenant les détails par disque.
    """
    try:
        # perdisk=True retourne un dictionnaire avec chaque disque physique comme clé.
        # Ex: {'sda': sdiskio(...), 'sdb': sdiskio(...)}
        io_counters_par_disque = psutil.disk_io_counters(perdisk=True)

        details_disques = []
        for disque, compteurs in io_counters_par_disque.items():
            # On ignore les disques "loop" qui sont liés aux snaps de Linux
            if 'loop' in disque:
                continue

            details_disques.append({
                "nom_disque": disque,
                "nombre_lectures": compteurs.read_count,
                "nombre_ecritures": compteurs.write_count,
                "donnees_lues_mb": go_to_mb(compteurs.read_bytes),
                "donnees_ecrites_mb": go_to_mb(compteurs.write_bytes)
            })

        return {
            "disque_activite_par_partition": {
                "details": details_disques
            }
        }
    except Exception as e:
        return {"disque_activite_par_partition": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Activité des Disques par Partition ---")
    donnees = compter()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
