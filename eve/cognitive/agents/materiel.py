# -*- coding: utf-8 -*-
"""
materiel.py (v2.0 - Profileur Intelligent avec Cache et Détection GPU)

Module de perception d'Alma.
Collecte les informations matérielles statiques de manière performante
en utilisant un système de cache et une détection GPU améliorée.
"""

import platform
import psutil
import cpuinfo
import json
import os
import time
import subprocess
from datetime import timedelta

# --- Constantes de Configuration ---
CACHE_FILE = 'profil_materiel.json'
# Le profil matériel change très rarement. Un cache de 7 jours est raisonnable.
CACHE_DURATION_SECONDS = timedelta(days=7).total_seconds()


class _ProfileurMateriel:
    """
    Classe interne qui gère la logique de collecte des informations matérielles.
    L'encapsulation permet de garder le code organisé.
    """
    def _obtenir_os(self):
        try:
            return {
                "systeme": platform.system(),
                "version": platform.release(),
                "architecture": platform.architecture()[0],
                "nom_machine": platform.node()
            }
        except Exception as e: return {"erreur": str(e)}

    def _obtenir_cpu(self):
        try:
            info_brute = cpuinfo.get_cpu_info()
            return {
                "nom": info_brute.get('brand_raw', 'N/A'),
                "coeurs_physiques": psutil.cpu_count(logical=False),
                "coeurs_logiques": psutil.cpu_count(logical=True),
                "frequence_max_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else 'N/A'
            }
        except Exception as e: return {"erreur": str(e)}

    def _obtenir_memoire_totale(self):
        try:
            ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
            return {"ram_totale_gb": ram_gb}
        except Exception as e: return {"erreur": str(e)}

    def _obtenir_disques(self):
        try:
            partitions = psutil.disk_partitions()
            info_disques = []
            for p in partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    info_disques.append({
                        "peripherique": p.device,
                        "point_montage": p.mountpoint,
                        "taille_totale_gb": round(usage.total / (1024**3), 2)
                    })
                except (PermissionError, FileNotFoundError): continue
            return {"disques": info_disques}
        except Exception as e: return {"erreur": str(e)}

    def _detecter_gpu_nvidia(self):
        """Tente de détecter un GPU NVIDIA via la commande nvidia-smi."""
        try:
            # Commande pour obtenir le nom du GPU, sans en-tête et au format CSV
            cmd = "nvidia-smi --query-gpu=gpu_name --format=csv,noheader"
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, check=True)
            gpu_name = result.stdout.strip()
            return {"gpu_principal": gpu_name} if gpu_name else None
        except (FileNotFoundError, subprocess.CalledProcessError):
            # FileNotFoundError: nvidia-smi n'est pas installé ou pas dans le PATH
            # CalledProcessError: la commande a échoué
            return None
        except Exception:
            return None

    def _obtenir_gpu(self):
        """Fonction principale de détection GPU, extensible."""
        # On essaie d'abord la méthode la plus fiable pour les GPU dédiés
        gpu_nvidia = self._detecter_gpu_nvidia()
        if gpu_nvidia:
            return gpu_nvidia

        # En fallback, on peut ajouter d'autres méthodes ici (pour AMD, Intel, etc.)
        return {"gpu_principal": "Détection non implémentée ou GPU non-NVIDIA"}

    def generer_profil_complet(self):
        """Rassemble toutes les informations matérielles."""
        return {
            "os": self._obtenir_os(),
            "cpu": self._obtenir_cpu(),
            "memoire": self._obtenir_memoire_totale(),
            "stockage": self._obtenir_disques(),
            "gpu": self._obtenir_gpu()
        }

def obtenir_profil_materiel_complet():
    """
    Fonction publique qui retourne le profil matériel complet, en utilisant un cache.
    C'est le seul point d'entrée pour les autres modules.
    """
    # 1. Vérifier si un cache valide existe
    if os.path.exists(CACHE_FILE):
        cache_age = time.time() - os.path.getmtime(CACHE_FILE)
        if cache_age < CACHE_DURATION_SECONDS:
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("[Alerte Matériel] Cache corrompu. Lancement d'une nouvelle analyse.")

    # 2. Si pas de cache valide, lancer une nouvelle analyse
    print("[Info Matériel] Génération d'un nouveau profil matériel (cette opération n'a lieu qu'une fois par semaine).")
    profileur = _ProfileurMateriel()
    profil = profileur.generer_profil_complet()
    profil["derniere_analyse"] = time.time()

    # 3. Sauvegarder le nouveau profil dans le cache
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profil, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"[Erreur Matériel] Impossible de sauvegarder le cache : {e}")

    return profil

# --- Bloc de test ---
if __name__ == "__main__":
    print("--- Test du module de profilage matériel (v2.0) ---")

    print("\n1. Premier appel (devrait être plus lent et créer/mettre à jour le cache)...")
    start_time = time.time()
    profil1 = obtenir_profil_materiel_complet()
    end_time = time.time()
    print(f"   Terminé en {end_time - start_time:.4f} secondes.")

    print("\n   Profil Matériel Détecté :\n")
    print(json.dumps(profil1, indent=2, ensure_ascii=False))

    print("\n2. Deuxième appel (devrait être instantané grâce au cache)...")
    start_time = time.time()
    profil2 = obtenir_profil_materiel_complet()
    end_time = time.time()
    print(f"   Terminé en {end_time - start_time:.4f} secondes.")
    print("   SUCCÈS : Le profil a été chargé instantanément depuis le cache.")

    print("\n--- Test de materiel.py terminé ---")
