# -*- coding: utf-8 -*-

"""
Capteur : Activité Réseau par Interface

Ce module détaille le total des données envoyées et reçues pour chaque
interface réseau (carte Wi-Fi, port Ethernet, etc.).
"""

import psutil
import json

def go_to_mb(value_in_bytes):
    """Petite fonction pour convertir les bytes en Megabytes."""
    return round(value_in_bytes / (1024**2), 2)

def compter():
    """
    Compte les I/O pour chaque interface réseau.

    :return: Un dictionnaire contenant les détails par interface.
    """
    try:
        # pernic=True retourne un dictionnaire avec chaque interface comme clé.
        io_counters_par_nic = psutil.net_io_counters(pernic=True)

        details_interfaces = []
        for interface, compteurs in io_counters_par_nic.items():
            # On ignore l'interface de 'loopback' (lo) qui ne communique qu'avec la machine elle-même.
            if interface == 'lo':
                continue

            details_interfaces.append({
                "nom_interface": interface,
                "donnees_envoyees_mb": go_to_mb(compteurs.bytes_sent),
                "donnees_recues_mb": go_to_mb(compteurs.bytes_recv)
            })

        return {
            "reseau_activite_par_interface": {
                "details": details_interfaces
            }
        }
    except Exception as e:
        return {"reseau_activite_par_interface": {"erreur": str(e)}}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du capteur : Activité Réseau par Interface ---")
    donnees = compter()
    print(json.dumps(donnees, indent=4))
    print("\n--- Test terminé. ---")
