# eve_src/config.py
"""Charge et valide la configuration pour l'application."""
import sys
import json

try:
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    print("ERREUR CRITIQUE: Fichier config.json introuvable.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERREUR CRITIQUE: Fichier config.json mal formaté. Détails : {e}")
    sys.exit(1)
