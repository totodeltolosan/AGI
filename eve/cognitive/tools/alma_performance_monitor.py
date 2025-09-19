# /home/toni/Documents/ALMA/Outils/alma_performance_monitor.py

"""
---
name: alma_performance_monitor.py
version: 0.1.0-alpha # Squelette initial avec collecte de données psutil et affichage basique
author: Toni & Gemini AI
description: Tableau de bord graphique pour le monitoring des ressources des modules ALMA.
role: Visualiser la performance CPU/RAM des composants ALMA en temps réel.
type_execution: gui_app
état: en développement
last_update: 2025-05-27 # Création du squelette V0.1.0
dossier: Outils
tags: [V20, alma, performance, monitoring, gui, tkinter, psutil, matplotlib, pandas]
dependencies: [tkinter, psutil]
optional_dependencies: [matplotlib, seaborn, pandas] # Pour les graphiques futurs
---
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import os
import sys
from pathlib import Path
import json
import logging
import threading
import time
from typing import Dict, Any, Optional, List

# --- Gestion des Dépendances Optionnelles ---
PSUTIL_AVAILABLE = False
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    # Un message d'erreur sera affiché dans __main__ si psutil est crucial et manquant
    pass

# Les imports pour Matplotlib, Seaborn, Pandas seront ajoutés quand nous les utiliserons.

# --- Définition des Constantes du Module ---
APP_NAME_MONITOR = "ALMA - Moniteur de Performance"
VERSION_MONITOR = "0.1.0-alpha"
DEFAULT_REFRESH_INTERVAL_MS = 5000 # Intervalle de rafraîchissement UI par défaut (5 secondes)
PID_STATUS_FILENAME = "alma_pids_status.json" # Nom du fichier généré par alma_launcher.py
# --- Fin des Constantes du Module ---

# --- Configuration du Logger pour ce Module ---
logger = logging.getLogger(APP_NAME_MONITOR)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    _ch_monitor = logging.StreamHandler(sys.stdout)
    _formatter_monitor = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)-8s - %(threadName)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    _ch_monitor.setFormatter(_formatter_monitor)
    logger.addHandler(_ch_monitor)
    logger.info(f"Logger pour {APP_NAME_MONITOR} v{VERSION_MONITOR} initialisé.")
# --- Fin Logger Configuration ---

# --- Configuration de ALMA_BASE_DIR ---
ALMA_BASE_DIR_DEFAULT_FALLBACK_MON = Path("/home/toni/Documents/ALMA").resolve()
_alma_base_dir_determined_mon = False
ALMA_BASE_DIR: Path

try:
    if '__file__' in globals() and globals()['__file__'] is not None:
        current_script_path_mon = Path(__file__).resolve()
        potential_alma_base_dir_mon = current_script_path_mon.parent.parent
        if (potential_alma_base_dir_mon / "Cerveau").is_dir() and \
           (potential_alma_base_dir_mon / "Connaissance").is_dir() and \
           (potential_alma_base_dir_mon / "Outils").is_dir() and \
           (potential_alma_base_dir_mon / "venv").is_dir():
            ALMA_BASE_DIR = potential_alma_base_dir_mon
            logger.info(f"ALMA_BASE_DIR déduit du chemin du script : {ALMA_BASE_DIR}")
            _alma_base_dir_determined_mon = True
        else:
            logger.debug(f"Déduction de ALMA_BASE_DIR via __file__ a échoué la validation de structure.")
    else:
        logger.debug("__file__ non défini ou None, impossible de déduire ALMA_BASE_DIR.")
except Exception as e_file_deduction_mon:
    logger.debug(f"Exception lors de la déduction de ALMA_BASE_DIR via __file__: {e_file_deduction_mon}")

if not _alma_base_dir_determined_mon:
    try:
        env_alma_base_dir_str_mon = os.environ["ALMA_BASE_DIR"]
        potential_alma_base_dir_mon = Path(env_alma_base_dir_str_mon).resolve()
        if (potential_alma_base_dir_mon / "Cerveau").is_dir() and \
           (potential_alma_base_dir_mon / "Connaissance").is_dir():
            ALMA_BASE_DIR = potential_alma_base_dir_mon
            logger.info(f"ALMA_BASE_DIR récupéré depuis l'environnement : {ALMA_BASE_DIR}")
            _alma_base_dir_determined_mon = True
        else:
            logger.warning(f"ALMA_BASE_DIR de l'environnement ('{env_alma_base_dir_str_mon}') semble incorrect.")
    except KeyError:
        logger.info("Variable d'environnement ALMA_BASE_DIR non définie.")
    except Exception as e_env_deduction_mon:
        logger.debug(f"Exception lors de la lecture de ALMA_BASE_DIR: {e_env_deduction_mon}")

if not _alma_base_dir_determined_mon:
    ALMA_BASE_DIR = ALMA_BASE_DIR_DEFAULT_FALLBACK_MON
    logger.warning(f"ALMA_BASE_DIR non déterminé. Utilisation du fallback : {ALMA_BASE_DIR}")
    if not (ALMA_BASE_DIR / "Cerveau").is_dir() or not (ALMA_BASE_DIR / "Connaissance").is_dir():
        critical_error_msg_mon = f"Fallback ALMA_BASE_DIR ({ALMA_BASE_DIR}) invalide. Vérifiez la structure ou définissez ALMA_BASE_DIR."
        logger.critical(critical_error_msg_mon)
        # Tenter une messagebox si Tkinter est importable
        try:
            root_temp_error_mon = tk.Tk(); root_temp_error_mon.withdraw()
            tk.messagebox.showerror(f"{APP_NAME_MONITOR} - Erreur Critique", critical_error_msg_mon)
            root_temp_error_mon.destroy()
        except Exception: pass
        sys.exit(1)
# --- Fin Configuration ALMA_BASE_DIR ---

# --- Définition des Chemins Clés ---
LOGS_DIR_ALMA = ALMA_BASE_DIR / "logs"
PID_STATUS_FILE_PATH = LOGS_DIR_ALMA / PID_STATUS_FILENAME
# --- Fin Définition des Chemins Clés ---

# La classe PerformanceMonitorApp et le bloc __main__ viendront après.
# --- Classe Principale de l'Application GUI ---
class PerformanceMonitorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME_MONITOR} v{VERSION_MONITOR}")
        self.root.geometry("800x600") # Taille initiale
        self.root.minsize(600, 400)

        self.logger = logger # Utiliser le logger du module

        if not PSUTIL_AVAILABLE:
            self.logger.critical("La bibliothèque 'psutil' est requise mais n'a pas pu être importée. Le moniteur de performance ne peut pas fonctionner.")
            messagebox.showerror("Dépendance Manquante", "La bibliothèque 'psutil' est introuvable. Veuillez l'installer (pip install psutil) pour utiliser ce moniteur.")
            self.root.destroy()
            sys.exit(1)

        # Données de performance (partagées entre le thread de collecte et le thread UI)
        self.performance_data: Dict[str, Dict[str, Any]] = {} # Clé: name_key du module, Valeur: {pid, cpu, ram_mb, label, status}
        self.performance_data_lock = threading.Lock() # Pour protéger l'accès à self.performance_data

        # État du thread de collecte
        self.data_collector_thread: Optional[threading.Thread] = None
        self.stop_data_collector_event = threading.Event()

        # Configuration UI
        self.refresh_interval_ms = DEFAULT_REFRESH_INTERVAL_MS

        self._setup_ui_base()
        self.start_data_collection()

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.logger.info("PerformanceMonitorApp initialisée.")

    def _setup_ui_base(self):
        """Configure la structure de base de l'interface utilisateur."""
        self.logger.debug("Configuration de l'UI de base...")

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Titre
        title_label = ttk.Label(main_frame, text=APP_NAME_MONITOR, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 15))

        # Panneau de Contrôle (pour l'instant, juste un placeholder)
        control_panel = ttk.LabelFrame(main_frame, text="Contrôles & Options", padding="10")
        control_panel.pack(fill=tk.X, pady=5)
        ttk.Label(control_panel, text="(Futurs contrôles: sélection modules, refresh, type de graphique)").pack()

        # Zone d'Affichage des Données (pour l'instant, des labels pour les données brutes)
        self.data_display_frame = ttk.LabelFrame(main_frame, text="Données de Performance (Brutes)", padding="10")
        self.data_display_frame.pack(expand=True, fill=tk.BOTH, pady=10)

        # Créer des labels pour chaque module potentiel (sera mis à jour dynamiquement)
        # Pour ce squelette, on ne les crée pas dynamiquement ici, mais on aura une méthode pour les mettre à jour.
        self.module_labels: Dict[str, ttk.Label] = {} # Clé: name_key, Valeur: ttk.Label

        self.logger.debug("UI de base configurée.")

    def _update_performance_display(self):
        """Met à jour l'affichage des données de performance dans l'UI (labels pour l'instant)."""
        with self.performance_data_lock:
            # Copier pour éviter les problèmes de modification pendant l'itération si le thread met à jour
            current_data_snapshot = self.performance_data.copy()

        # Nettoyer les anciens labels si des modules ont disparu
        labels_to_remove = [name_key for name_key in self.module_labels if name_key not in current_data_snapshot]
        for name_key in labels_to_remove:
            if self.module_labels[name_key].winfo_exists():
                self.module_labels[name_key].destroy()
            del self.module_labels[name_key]

        # Mettre à jour ou créer les labels pour les données actuelles
        row_idx = 0
        for name_key, data in sorted(current_data_snapshot.items()):
            pid = data.get('pid', 'N/A')
            cpu = data.get('cpu_percent', 'N/A')
            ram_mb = data.get('ram_mb', 'N/A')
            status = data.get('status', 'Inconnu')
            label_text = data.get('script_label', name_key) # Utiliser le label du script si dispo

            display_text = f"{label_text} (PID: {pid}) - CPU: {cpu}%, RAM: {ram_mb} MB - Statut: {status}"

            if name_key not in self.module_labels:
                self.module_labels[name_key] = ttk.Label(self.data_display_frame, text=display_text, font=("Segoe UI", 9))
                self.module_labels[name_key].grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
            else:
                if self.module_labels[name_key].winfo_exists():
                    self.module_labels[name_key].config(text=display_text)

            # Changer la couleur du texte en fonction du statut (simplifié)
            color = "grey"
            if status == "Actif": color = "green"
            elif status == "Arrêté": color = "red"
            elif status == "PID non trouvé": color = "orange"

            if self.module_labels[name_key].winfo_exists():
                 self.module_labels[name_key].config(foreground=color)

            row_idx += 1

        # Planifier le prochain rafraîchissement de l'UI
        if not self.stop_data_collector_event.is_set():
            self.root.after(self.refresh_interval_ms, self._update_performance_display)


    def _data_collection_loop(self):
        """Boucle exécutée dans un thread séparé pour collecter les données de performance."""
        self.logger.info("Thread de collecte de données démarré.")

        while not self.stop_data_collector_event.is_set():
            active_pids_map: Dict[str, Dict[str, Any]] = {} # name_key -> {pid, script_label}

            # 1. Lire le fichier alma_pids_status.json
            if PID_STATUS_FILE_PATH.exists() and PID_STATUS_FILE_PATH.is_file():
                try:
                    with open(PID_STATUS_FILE_PATH, 'r', encoding='utf-8') as f:
                        active_pids_map_from_file = json.load(f)
                    if isinstance(active_pids_map_from_file, dict):
                        active_pids_map = active_pids_map_from_file
                except json.JSONDecodeError:
                    self.logger.warning(f"Erreur de décodage JSON pour {PID_STATUS_FILE_PATH}.")
                except Exception as e_read_pid:
                    self.logger.error(f"Impossible de lire {PID_STATUS_FILE_PATH}: {e_read_pid}")
            else:
                self.logger.debug(f"{PID_STATUS_FILE_PATH} non trouvé. Aucun processus ALMA à surveiller.")

            new_performance_data: Dict[str, Dict[str, Any]] = {}
            for name_key, pid_info in active_pids_map.items():
                pid = pid_info.get("pid")
                script_label = pid_info.get("script_label", name_key)
                if pid is None:
                    new_performance_data[name_key] = {"pid": "N/A", "cpu_percent": "N/A", "ram_mb": "N/A", "script_label": script_label, "status": "PID Manquant"}
                    continue

                try:
                    if psutil.pid_exists(pid):
                        process = psutil.Process(pid)
                        with process.oneshot(): # Optimisation pour plusieurs appels psutil
                            cpu = process.cpu_percent(interval=0.1) # Intervalle court non bloquant
                            ram_rss_bytes = process.memory_info().rss
                        ram_mb = round(ram_rss_bytes / (1024 * 1024), 2)
                        new_performance_data[name_key] = {"pid": pid, "cpu_percent": cpu, "ram_mb": ram_mb, "script_label": script_label, "status": "Actif"}
                    else:
                        new_performance_data[name_key] = {"pid": pid, "cpu_percent": "N/A", "ram_mb": "N/A", "script_label": script_label, "status": "PID non trouvé"}
                except psutil.NoSuchProcess:
                    new_performance_data[name_key] = {"pid": pid, "cpu_percent": "N/A", "ram_mb": "N/A", "script_label": script_label, "status": "Arrêté"}
                except psutil.AccessDenied:
                    new_performance_data[name_key] = {"pid": pid, "cpu_percent": "N/A", "ram_mb": "N/A", "script_label": script_label, "status": "Accès Refusé"}
                except Exception as e_psutil:
                    self.logger.error(f"Erreur psutil pour PID {pid} ({name_key}): {e_psutil}")
                    new_performance_data[name_key] = {"pid": pid, "cpu_percent": "ERR", "ram_mb": "ERR", "script_label": script_label, "status": "Erreur psutil"}

            # Mettre à jour la structure de données partagée
            with self.performance_data_lock:
                self.performance_data = new_performance_data

            # Attendre avant la prochaine collecte
            # L'intervalle de collecte de données peut être plus fréquent que le rafraîchissement UI
            time.sleep(max(1, self.refresh_interval_ms / 1000 / 2)) # Ex: toutes les 2.5s si UI refresh toutes les 5s

        self.logger.info("Thread de collecte de données arrêté.")

    def start_data_collection(self):
        """Démarre le thread de collecte de données si psutil est disponible."""
        if not PSUTIL_AVAILABLE:
            self.logger.error("psutil n'est pas disponible. Le thread de collecte de données ne peut pas démarrer.")
            return

        if self.data_collector_thread is None or not self.data_collector_thread.is_alive():
            self.stop_data_collector_event.clear()
            self.data_collector_thread = threading.Thread(target=self._data_collection_loop, daemon=True, name="AlmaPerfDataCollector")
            self.data_collector_thread.start()
            # Démarrer le rafraîchissement de l'UI
            self.root.after(100, self._update_performance_display) # Premier appel un peu différé
        else:
            self.logger.warning("Tentative de démarrer le thread de collecte alors qu'il est déjà actif.")

    def _on_closing(self):
        """Gère la fermeture de la fenêtre."""
        self.logger.info("Fermeture du Moniteur de Performance demandée.")
        self.stop_data_collector_event.set() # Signaler au thread de s'arrêter
        if self.data_collector_thread and self.data_collector_thread.is_alive():
            self.logger.debug("Attente de la fin du thread de collecte de données...")
            self.data_collector_thread.join(timeout=3) # Attendre un peu
            if self.data_collector_thread.is_alive():
                self.logger.warning("Le thread de collecte de données n'a pas pu être arrêté proprement dans le délai.")

        self.logger.info("Moniteur de Performance fermé.")
        self.root.destroy()

# Le bloc if __name__ == "__main__": viendra après.
# --- Point d'Entrée Principal du Script ---
if __name__ == "__main__":
    # Le logger global du module a déjà été configuré au début du script (Bloc 1)
    logger.info(f"--- Lancement de {APP_NAME_MONITOR} v{VERSION_MONITOR} ---")

    # Vérification critique de ALMA_BASE_DIR (déjà faite dans le Bloc 1,
    # mais une double vérification ici avant de lancer la GUI est une bonne pratique)
    if "ALMA_BASE_DIR" not in globals() or not ALMA_BASE_DIR.is_dir() or \
       not (ALMA_BASE_DIR / "Cerveau").is_dir() or \
       not (ALMA_BASE_DIR / "Connaissance").is_dir():
        critical_error_msg_main_mon = f"ALMA_BASE_DIR ({ALMA_BASE_DIR if 'ALMA_BASE_DIR' in globals() else 'NON DÉFINI'}) n'est pas configuré correctement ou la structure du projet est corrompue. Arrêt de {APP_NAME_MONITOR}."
        logger.critical(critical_error_msg_main_mon)
        try:
            root_temp_error_main_mon = tk.Tk(); root_temp_error_main_mon.withdraw()
            tk.messagebox.showerror(f"{APP_NAME_MONITOR} - Erreur Configuration Critique", critical_error_msg_main_mon)
            root_temp_error_main_mon.destroy()
        except tk.TclError: pass # Au cas où Tkinter lui-même aurait un problème
        except Exception: pass # Autres erreurs potentielles avec messagebox
        sys.exit(1)
    else:
        logger.info(f"Utilisation de ALMA_BASE_DIR: {ALMA_BASE_DIR}")

    # Vérification de la disponibilité de psutil (crucial pour ce module)
    if not PSUTIL_AVAILABLE:
        critical_error_psutil = (
            f"La bibliothèque 'psutil' est indispensable pour le Moniteur de Performance mais n'a pas pu être importée.\n"
            f"Veuillez l'installer (ex: pip install psutil) et réessayer.\n\n"
            f"{APP_NAME_MONITOR} ne peut pas continuer."
        )
        logger.critical(critical_error_psutil)
        try:
            root_temp_error_psutil = tk.Tk(); root_temp_error_psutil.withdraw()
            tk.messagebox.showerror(f"{APP_NAME_MONITOR} - Dépendance Critique Manquante", critical_error_psutil)
            root_temp_error_psutil.destroy()
        except tk.TclError: pass
        except Exception: pass
        sys.exit(1)
    else:
        logger.info("Bibliothèque 'psutil' disponible et prête à l'emploi.")

    # Vérification de l'existence du fichier PID_STATUS_FILE_PATH (informatif, le moniteur peut démarrer même s'il est vide ou absent au début)
    if not PID_STATUS_FILE_PATH.exists():
        logger.warning(f"Le fichier de statut des PIDs ALMA ({PID_STATUS_FILE_PATH}) n'existe pas encore. Le moniteur affichera 'Aucun processus' jusqu'à ce que le lanceur ALMA le crée.")
    else:
        logger.info(f"Fichier de statut des PIDs ALMA trouvé à : {PID_STATUS_FILE_PATH}")


    root_window_main_mon: Optional[tk.Tk] = None # Pour le bloc finally
    app_instance_mon: Optional[PerformanceMonitorApp] = None
    try:
        logger.debug("Création de la fenêtre Tkinter principale pour le Moniteur...")
        root_window_main_mon = tk.Tk()

        logger.debug("Instanciation de PerformanceMonitorApp...")
        app_instance_mon = PerformanceMonitorApp(root_window_main_mon) # L'__init__ démarre la collecte

        logger.info("Lancement de la boucle principale Tkinter (mainloop) pour le Moniteur...")
        root_window_main_mon.mainloop()

        # Ce log sera atteint après la fermeture de la fenêtre principale
        logger.info(f"{APP_NAME_MONITOR} terminé proprement après fermeture de la fenêtre.")

    except tk.TclError as e_tcl_main:
        # Erreur spécifique à Tkinter, souvent si l'environnement graphique n'est pas disponible
        logger.critical(f"Erreur TclError majeure lors de l'initialisation ou de l'exécution de l'interface Tkinter: {e_tcl_main}", exc_info=True)
        print(f"ERREUR GRAPHIQUE: {APP_NAME_MONITOR} n'a pas pu démarrer en raison d'un problème Tkinter. Assurez-vous qu'un environnement graphique est disponible.", file=sys.stderr)
        sys.exit(1)
    except Exception as e_main_app_runtime_mon:
        logger.critical(f"Erreur fatale inattendue dans l'exécution principale de {APP_NAME_MONITOR}: {e_main_app_runtime_mon}", exc_info=True)
        # Tenter une dernière messagebox si possible
        try:
            if root_window_main_mon and root_window_main_mon.winfo_exists():
                tk.messagebox.showerror(f"{APP_NAME_MONITOR} - Erreur Fatale", f"Une erreur fatale est survenue:\n{type(e_main_app_runtime_mon).__name__}: {e_main_app_runtime_mon}", parent=root_window_main_mon)
            else: # Si la racine n'a pas été créée
                root_temp_fatal = tk.Tk(); root_temp_fatal.withdraw()
                tk.messagebox.showerror(f"{APP_NAME_MONITOR} - Erreur Fatale", f"Une erreur fatale est survenue avant même la création de la fenêtre principale:\n{type(e_main_app_runtime_mon).__name__}: {e_main_app_runtime_mon}")
                root_temp_fatal.destroy()
        except Exception: pass # Éviter une erreur dans le handler d'erreur
        sys.exit(1)
    finally:
        # S'assurer que le thread de collecte est bien arrêté si l'application se termine anormalement
        # avant que _on_closing ne soit appelé (ex: par une exception dans mainloop ou avant).
        if app_instance_mon and hasattr(app_instance_mon, 'stop_data_collector_event'):
            if not app_instance_mon.stop_data_collector_event.is_set():
                logger.info("Nettoyage final: Signal d'arrêt envoyé au thread de collecte de données.")
                app_instance_mon.stop_data_collector_event.set()
            if app_instance_mon.data_collector_thread and app_instance_mon.data_collector_thread.is_alive():
                logger.info("Nettoyage final: Attente de la fin du thread de collecte (max 1s)...")
                app_instance_mon.data_collector_thread.join(timeout=1.0)
                if app_instance_mon.data_collector_thread.is_alive():
                     logger.warning("Nettoyage final: Le thread de collecte de données est toujours actif après le timeout.")

        logger.info(f"--- {APP_NAME_MONITOR} v{VERSION_MONITOR} - Fin d'exécution ---")
        logging.shutdown() # Bonne pratique pour fermer les handlers de logging
