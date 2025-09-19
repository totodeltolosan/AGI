# -*- coding: utf-8 -*-

"""
Capteur : Utilisation de l'Espace Disque

Ce module mesure le pourcentage d'utilisation de l'espace de stockage
pour chaque partition de disque principale.
"""

import psutil
import json

def go_to_gb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Gigabytes."""
    return round(value_in_bytes / (1024**3), 2)

def mesurer():
    """
    Liste les partitions et mesure leur utilisation.

    :return: Un dictionnaire contenant une liste d'informations par partition.
    """
    partitions_info = []
    try:
        # On récupère toutes les partitions
        partitions = psutil.disk_partitions()
        for partition in partitions:
            # On ignore les systèmes de fichiers "spéciaux" et souvent temporaires comme squashfs
            if 'loop' in partition.device or partition.fstype == 'squashfs':
                continue

            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions_info.append({
                    "point_montage": partition.mountpoint,
                    "systeme_fichiers": partition.fstype,
                    "usage_pourcentage": usage.percent,
                    "total_gb": go_to_gb(usage.total),
                    "utilise_gb": go_to_gb(usage.used)
                })
            except (PermissionError, FileNotFoundError):
                # On ignore les partitions inaccessibles (ex: lecteur CD vide)
                continue

        return {"disque_usage": {"partitions": partitions_info}}

    except Exception as e:
        return {"disque_usage": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Utilisation de l'Espace Disque ---")
    donnees = mesurer()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
