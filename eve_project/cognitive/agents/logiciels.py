# -*- coding: utf-8 -*-
"""
logiciels.py (v2.0 - Inventaire Intelligent avec Cache)

Module de perception d'Alma.
Objectif : Lister les logiciels installés de manière performante en utilisant
un système de cache pour éviter les analyses système répétitives et lentes.
"""

import platform
import subprocess
import json
import os
import time
from datetime import timedelta

# --- Constantes de Configuration ---
CACHE_FILE = 'inventaire_logiciels.json'
# Le cache est considéré comme valide pendant 24 heures
CACHE_DURATION_SECONDS = timedelta(hours=24).total_seconds()

def _lister_windows():
    """Exécute la commande PowerShell pour lister les logiciels sur Windows."""
    cmd = 'powershell "Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion, Publisher | Where-Object {$_.DisplayName -ne $null} | ConvertTo-Json -Compress"'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='ignore')

    if not result.stdout:
        return []

    # Le résultat est une série d'objets JSON, on les met dans une liste
    json_str = f"[{','.join(result.stdout.strip().splitlines())}]"
    raw_apps = json.loads(json_str)

    apps = []
    for app in raw_apps:
        apps.append({
            "nom": app.get('DisplayName'),
            "version": app.get('DisplayVersion', 'N/A'),
            "editeur": app.get('Publisher', 'N/A')
        })
    return apps

def _lister_linux_debian():
    """Utilise dpkg pour lister les paquets sur les systèmes basés sur Debian."""
    cmd = "dpkg-query -W -f='${Package},${Version},${Maintainer}\\n'"
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    apps = []
    for line in result.stdout.strip().splitlines():
        parts = line.split(',', 2) # On split au max 2 fois pour gérer les virgules dans les noms
        if len(parts) == 3:
            apps.append({"nom": parts[0], "version": parts[1], "editeur": parts[2]})
    return apps

def _lister_macos():
    """Liste les applications du dossier /Applications sur macOS."""
    cmd = 'ls /Applications'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    apps = []
    for line in result.stdout.strip().splitlines():
        if line.endswith(".app"):
            apps.append({"nom": line.replace('.app', ''), "version": "N/A", "editeur": "N/A"})
    return apps

def lister_applications_installees():
    """
    Tente de lister les applications installées en utilisant un cache.
    Si un cache récent et valide existe, il est retourné instantanément.
    Sinon, une nouvelle analyse est lancée et le cache est mis à jour.
    """
    # 1. Vérifier si un cache valide existe
    if os.path.exists(CACHE_FILE):
        cache_age = time.time() - os.path.getmtime(CACHE_FILE)
        if cache_age < CACHE_DURATION_SECONDS:
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    # print("[Info Logiciels] Utilisation du cache récent.")
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("[Alerte Logiciels] Cache corrompu. Lancement d'une nouvelle analyse.")

    # 2. Si pas de cache valide, lancer l'analyse système
    systeme = platform.system()
    apps = []

    try:
        if systeme == "Windows":
            apps = _lister_windows()
        elif systeme == "Linux":
            # Ici, on pourrait ajouter des logiques pour d'autres gestionnaires de paquets (rpm, pacman...)
            apps = _lister_linux_debian()
        elif systeme == "Darwin":
            apps = _lister_macos()
        else:
            return {"erreur": f"Système d'exploitation '{systeme}' non supporté."}

        inventaire = {"applications": apps, "nombre_trouve": len(apps), "derniere_analyse": time.time()}

        # 3. Sauvegarder le nouvel inventaire dans le cache
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(inventaire, f, indent=4)

        return inventaire

    except FileNotFoundError as e:
        return {"erreur": f"Commande introuvable sur '{systeme}': {e}"}
    except Exception as e:
        return {"erreur": f"Erreur inattendue lors de l'analyse : {e}"}

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du module d'inventaire des logiciels (v2.0) ---")

    print("\n1. Premier appel (devrait être lent et créer/mettre à jour le cache)...")
    start_time = time.time()
    inventaire1 = lister_applications_installees()
    end_time = time.time()
    print(f"   Terminé en {end_time - start_time:.2f} secondes.")

    if "erreur" in inventaire1:
        print(f"   ERREUR : {inventaire1['erreur']}")
    else:
        print(f"   SUCCÈS : {inventaire1.get('nombre_trouve', 0)} applications trouvées.")

    print("\n2. Deuxième appel (devrait être instantané grâce au cache)...")
    start_time = time.time()
    inventaire2 = lister_applications_installees()
    end_time = time.time()
    print(f"   Terminé en {end_time - start_time:.4f} secondes.")

    if "erreur" in inventaire2:
        print(f"   ERREUR : {inventaire2['erreur']}")
    else:
        print(f"   SUCCÈS : {inventaire2.get('nombre_trouve', 0)} applications trouvées depuis le cache.")
        print("\n--- Extrait de l'inventaire (20 premiers) ---")
        for app in inventaire2.get("applications", [])[:20]:
            print(f"  - {app['nom']} (Version: {app.get('version', 'N/A')})")
        if inventaire2.get('nombre_trouve', 0) > 20:
            print("  ...")

    print("\n--- Test de logiciels.py terminé ---")
