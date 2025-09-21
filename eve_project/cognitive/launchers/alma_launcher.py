# /home/toni/Documents/ALMA/alma_launcher.py

# --- BLOC 1: IMPORTS ET CONFIGURATIONS GLOBALES INITIALES ---
import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
import subprocess
import os
import sys
from pathlib import Path # Path est ici, pas besoin de l'importer depuis typing
import datetime
import time
import threading
import shutil
import re
import json
import traceback
import logging
from logging.handlers import RotatingFileHandler
import socket
import platform
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, TYPE_CHECKING # TYPE_CHECKING ajouté

# --- Configuration Initiale du Logger (Bootstrap pour les erreurs d'import précoces) ---
# Ce logger est TEMPORAIRE et sert uniquement si les imports principaux ou la config du logger principal échouent.
_bootstrap_logger_name = "ALMA.Launcher.Bootstrap"
_bootstrap_logger = logging.getLogger(_bootstrap_logger_name)
if not _bootstrap_logger.handlers: # Configurer seulement si pas déjà fait (ex: si script est ré-importé)
    _bootstrap_logger.setLevel(logging.INFO) # Niveau INFO pour le bootstrap
    _bootstrap_ch = logging.StreamHandler(sys.stdout)
    _bootstrap_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-7s - %(message)s (bootstrap)')
    _bootstrap_ch.setFormatter(_bootstrap_formatter)
    _bootstrap_logger.addHandler(_bootstrap_ch)
    # _bootstrap_logger.propagate = False # Empêcher la propagation vers le logger racine si on veut l'isoler

# --- Import Conditionnel de Pillow (PIL) ---
PILLOW_AVAILABLE = False
# Utiliser des alias pour éviter les conflits si Image ou ImageTk sont définis à None
PIL_Image = None
PIL_ImageTk = None
try:
    from PIL import Image as ImportedPIL_Image, ImageTk as ImportedPIL_ImageTk
    PIL_Image = ImportedPIL_Image
    PIL_ImageTk = ImportedPIL_ImageTk
    PILLOW_AVAILABLE = True
    _bootstrap_logger.info("Bibliothèque Pillow (PIL) chargée avec succès.")
except ImportError:
    _bootstrap_logger.warning(
        "Bibliothèque Pillow (PIL) non trouvée. Les fonctionnalités d'affichage d'images (icônes, Photo ALMA) seront limitées ou désactivées."
        " Pour l'installer : pip install Pillow"
    )
# --- Fin Import Pillow ---

# --- Imports des Composants UI ---
# On essaie d'importer tous les composants nécessaires.
# ALL_UI_COMPONENTS_LOADED sera True seulement si TOUS réussissent.
ALL_UI_COMPONENTS_LOADED = False # Initialiser à False
try:
    from launcher_ui_components.menu_bar_handler import MenuBarHandler
    from launcher_ui_components.header_toolbar_widgets import HeaderToolbar
    from launcher_ui_components.left_panel_widgets import LeftMonitorPanel
    from launcher_ui_components.center_panel_widgets import CenterInfoPredictionPanel
    from launcher_ui_components.right_panel_widgets import RightGraphPanel
    from launcher_ui_components.module_grid_widgets import ModuleGridPanel
    # from launcher_ui_components.common_widgets import ... # Si vous l'utilisez

    ALL_UI_COMPONENTS_LOADED = True
    _bootstrap_logger.info("Tous les composants UI principaux semblent avoir été importés avec succès.")

except ImportError as e_comp_ui_module:
    err_msg = (
        f"ERREUR CRITIQUE lors de l'import d'un ou plusieurs composants UI du lanceur: {e_comp_ui_module}\n"
        f"Veuillez vérifier que le dossier 'launcher_ui_components' et tous ses fichiers .py "
        f"(menu_bar_handler.py, header_toolbar_widgets.py, etc.) existent, "
        f"sont correctement nommés, et ne contiennent pas d'erreurs de syntaxe empêchant leur import.\n"
        f"Traceback de l'erreur d'import:\n{traceback.format_exc()}"
    )
    _bootstrap_logger.critical(err_msg)
except Exception as e_unexpected_import_module:
    err_msg = (
        f"ERREUR INATTENDUE CRITIQUE lors de l'import des composants UI: {e_unexpected_import_module}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    _bootstrap_logger.critical(err_msg)
# --- Fin Imports des Composants UI ---

# --- DÉFINITION DES CONSTANTES GLOBALES DE THÈME ET STYLE V20 ---
BG_COLOR_APP_BACKGROUND = "#2c3e50"
BG_COLOR_FRAME_MAIN = "#34495e"
BG_COLOR_FRAME_MODULES = "#283747"
BG_COLOR_FRAME_INFO = "#1c2833"

TEXT_COLOR_PRIMARY = "#ecf0f1"
TEXT_COLOR_SECONDARY = "#bdc3c7"
TEXT_COLOR_HEADER = "#ffffff" # Utilisé pour les titres principaux
TEXT_COLOR_ON_ACCENT_PRIMARY = "#ffffff"
TEXT_COLOR_ON_ACCENT_STOP = "#ffffff"
TEXT_COLOR_ON_ACCENT_STOP_ALL = "#ffffff"

COLOR_ACCENT_PRIMARY = "#3498db" # Bleu principal pour les accents
COLOR_BUTTON_DEFAULT_BG = "#5dade2" # Un bleu plus clair pour les boutons par défaut
COLOR_BUTTON_STOP_BG = "#e74c3c" # Rouge pour arrêt
COLOR_BUTTON_STOP_ALL_BG = "#c0392b" # Rouge plus foncé pour arrêt global
COLOR_STATUS_GREEN = "#2ecc71"
COLOR_STATUS_RED = "#e74c3c"
COLOR_STATUS_GREY = "#7f8c8d" # Gris pour inactif/désactivé

FONT_FAMILY_PRIMARY = "Segoe UI" # Police principale souhaitée
FONT_FAMILY_FALLBACK = "TkDefaultFont" # Police de secours Tkinter

# Suffixe _DEF pour indiquer que ce sont les définitions de base des polices
FONT_APP_TITLE_DEF = (FONT_FAMILY_PRIMARY, 16, "bold")
FONT_MODULE_BUTTON_LABEL_DEF = (FONT_FAMILY_PRIMARY, 10, "normal")
FONT_MODULE_BUTTON_TYPE_DEF = (FONT_FAMILY_PRIMARY, 8, "normal", "italic")
FONT_ACTION_BUTTON_DEF = (FONT_FAMILY_PRIMARY, 9, "bold")
FONT_BUTTON_LAUNCH_DEF = (FONT_FAMILY_PRIMARY, 10, "normal") # Pour les boutons de lancement de la grille
FONT_BUTTON_STOP_ALL_DEF = (FONT_FAMILY_PRIMARY, 10, "bold")
FONT_BODY_NORMAL_DEF = (FONT_FAMILY_PRIMARY, 10)
FONT_INFO_BAR_DEF = (FONT_FAMILY_PRIMARY, 9)
FONT_COMBOBOX_DEF = (FONT_FAMILY_PRIMARY, 9)
# --- FIN DÉFINITION DES CONSTANTES GLOBALES DE THÈME ---

# --- Configuration du Logger pour le Lanceur Lui-même ---
# --- Logger Principal (défini ici, configuré dans if __name__ == "__main__" ou après init des chemins) ---
LAUNCHER_VERSION = "2.0.0-alpha.LAYOUT_OK"
APP_NAME_LAUNCHER = "ALMA.LauncherDashboard"
_launcher_default_logger = logging.getLogger(APP_NAME_LAUNCHER) # Obtenir l'instance

# --- Import Conditionnel de PSUTIL (fait après la config du logger dans __main__) ---
PSUTIL_AVAILABLE = False
psutil = None

# --- Détermination de ALMA_BASE_DIR (Logique Améliorée et Journalisée) ---
# Cette logique sera exécutée au moment de l'importation ou au début du if __name__ == "__main__"
# pour que le logger soit déjà configuré. Pour l'instant, on prépare la variable.
ALMA_BASE_DIR: Optional[Path] = None
ALMA_BASE_DIR_DEFAULT_STR = "/home/toni/Documents/ALMA"

# --- Détermination de PYTHON_VENV_EXECUTABLE ---
PYTHON_VENV_EXECUTABLE: Optional[Path] = None

# --- Définition des Chemins pour les Fichiers de Statut et Logs ---
LOGS_DIR: Optional[Path] = None
LAUNCHER_SERVICES_LOGS_DIR: Optional[Path] = None
PID_STATUS_FILE: Optional[Path] = None

# --- Chargement des Configurations Externes (Fichiers YAML) ---
LAUNCHER_CONFIG_PATH: Optional[Path] = None
SCRIPTS_CONFIG: Dict[str, Any] = {} # Configuration des modules/scripts à lancer

LAUNCHER_PATTERNS_PATH: Optional[Path] = None
LAUNCH_PATTERNS: List[Dict[str, Any]] = [] # Configuration des paternes de lancement
PSUTIL_AVAILABLE: bool = False # Initialiser
psutil: Any = None # Initialise

def _initialize_global_paths_and_load_configs_v2( # Renommée pour éviter confusion
    logger_instance: logging.Logger
) -> Tuple[Path, Path, Path, Path, Path, Path, Dict[str, Any], Path, List[Dict[str, Any]]]:
    """
    Détermine ALMA_BASE_DIR, PYTHON_VENV_EXECUTABLE, LOGS_DIR, PID_STATUS_FILE
    et charge (placeholders) SCRIPTS_CONFIG et LAUNCH_PATTERNS.
    Retourne ces valeurs. Lève SystemExit en cas d'erreur critique.
    """
    local_alma_base_dir: Optional[Path] = None
    _alma_base_dir_determined_func = False

    # --- Détermination de ALMA_BASE_DIR ---
    _env_val_func = os.environ.get("ALMA_BASE_DIR")
    if _env_val_func:
        _potential_base_func = Path(_env_val_func).resolve()
        if ((_potential_base_func / "Cerveau").is_dir() and (_potential_base_func / "Outils").is_dir()):
            local_alma_base_dir = _potential_base_func
            _alma_base_dir_determined_func = True
            logger_instance.info(f"ALMA_BASE_DIR par variable d'env: {local_alma_base_dir}")
    if not _alma_base_dir_determined_func:
        try:
            _launcher_script_path_func = Path(__file__).resolve()
            _test_path1_func = _launcher_script_path_func.parent
            if (_test_path1_func / "Cerveau").is_dir() and (_test_path1_func / "Outils").is_dir():
                local_alma_base_dir = _test_path1_func
                _alma_base_dir_determined_func = True
            else:
                _test_path2_func = _launcher_script_path_func.parent.parent
                if (_test_path2_func / "Cerveau").is_dir() and (_test_path2_func / "Outils").is_dir():
                    local_alma_base_dir = _test_path2_func
                    _alma_base_dir_determined_func = True
            if _alma_base_dir_determined_func and local_alma_base_dir: # Log si trouvé par script
                 logger_instance.info(f"ALMA_BASE_DIR déduit du script: {local_alma_base_dir}")
        except NameError: logger_instance.debug("__file__ non défini.")
        except Exception as e: logger_instance.debug(f"Err déduction ALMA_BASE_DIR: {e}")

    if not _alma_base_dir_determined_func or local_alma_base_dir is None:
        local_alma_base_dir = Path(ALMA_BASE_DIR_DEFAULT_STR).resolve()
        logger_instance.warning(f"ALMA_BASE_DIR par défaut: {local_alma_base_dir}")

    final_alma_base_dir = local_alma_base_dir.resolve()
    if not final_alma_base_dir.is_dir():
        logger_instance.critical(f"CRITIQUE: ALMA_BASE_DIR '{final_alma_base_dir}' invalide."); sys.exit(1)
    logger_instance.info(f"ALMA_BASE_DIR final utilisé: {final_alma_base_dir}")

    # --- Détermination de PYTHON_VENV_EXECUTABLE ---
    _python_venv_default_str = str(final_alma_base_dir / "venv" / "bin" / "python")
    local_python_venv_executable: Path
    if Path(_python_venv_default_str).is_file() and os.access(_python_venv_default_str, os.X_OK):
        local_python_venv_executable = Path(_python_venv_default_str)
    else:
        _python_fallback_func = shutil.which("python3") or shutil.which("python")
        if _python_fallback_func: local_python_venv_executable = Path(_python_fallback_func)
        else: logger_instance.critical("Aucun exécutable Python trouvé."); sys.exit(1)
    logger_instance.info(f"Python venv: {local_python_venv_executable}")

    # --- Définition des Chemins pour Logs et Statut ---
    local_logs_dir = final_alma_base_dir / "logs"
    local_launcher_services_logs_dir = local_logs_dir / "launcher_services_logs"
    local_pid_status_file = local_logs_dir / "alma_pids_status.json"
    try:
        local_logs_dir.mkdir(parents=True, exist_ok=True)
        local_launcher_services_logs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e_mkdir_logs_func:
        logger_instance.error(f"Impossible de créer répertoires logs: {e_mkdir_logs_func}", exc_info=True)

    # --- Chargement des Configurations YAML ---
    local_launcher_config_path = final_alma_base_dir / "launcher_config.yaml"
    # TODO: Implémenter la lecture de local_launcher_config_path avec PyYAML
    local_scripts_config = {
        "Cerveau_Placeholder": {"label": "🧠 Cerveau", "icon_path": "Outils/icons_launcher/cerveau.png", "launch_priority": 1, "mode": "module_service", "is_service": True, "script_path_relative": "Cerveau/cerveau.py", "module_name": "Cerveau.cerveau", "args": ["-u"]},
        "Agent_Placeholder": {"label": "📶 AGENT", "icon_path": "Outils/icons_launcher/agent_sniffing.png", "launch_priority": 2, "mode": "module_service", "is_service": True, "script_path_relative": "AGENT/AGENT.py", "module_name": "AGENT.AGENT", "args": []}
    }
    logger_instance.info(f"SCRIPTS_CONFIG (placeholder). Lire depuis {local_launcher_config_path} plus tard.")

    local_launcher_patterns_path = final_alma_base_dir / "launcher_patterns.yaml"
    # TODO: Implémenter la lecture de local_launcher_patterns_path avec PyYAML
    local_launch_patterns = [
        {"name": "PATERNE TEST 1", "description": "Test", "sequence": [{"module_key": "Cerveau_Placeholder", "delay_after_launch_seconds": 5}]}
    ]
    logger_instance.info(f"LAUNCH_PATTERNS (placeholder). Lire depuis {local_launcher_patterns_path} plus tard.")

    return (final_alma_base_dir, local_python_venv_executable,
            local_logs_dir, local_launcher_services_logs_dir, local_pid_status_file,
            local_launcher_config_path, local_scripts_config,
            local_launcher_patterns_path, local_launch_patterns)

# --- Fin de la fonction ---

# --- Appel de la fonction et assignation aux globales DANS LE SCOPE DU MODULE ---
# Ceci doit être fait après la configuration du logger _launcher_default_logger
# et avant que la classe AlmaLauncherApp ou d'autres fonctions n'utilisent ces globales.
# Typiquement, cela irait au début du bloc if __name__ == "__main__",
# mais si d'autres fonctions au niveau module en ont besoin, alors ici.
# Pour l'instant, mettons-le dans le if __name__ == "__main__" pour être sûr que le logger est prêt.

# ... (Définition de la classe AlmaLauncherApp vient ici) ...
# ... (Elle utilisera les globales ALMA_BASE_DIR, SCRIPTS_CONFIG, etc. qui seront assignées ci-dessous) ...
# --- Fin Initialisation Globale ---

class AlmaLauncherApp(tk.Tk):
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self,
                 alma_base_dir: Path,
                 pid_status_file: Path,
                 scripts_config: Dict[str, Any],
                 launch_patterns: List[Dict[str, Any]],
                 python_venv_executable: Path,
                 logs_dir: Path,
                 launcher_services_logs_dir: Path,
                 launcher_config_path: Path, # Chemin vers launcher_config.yaml
                 launcher_patterns_path: Path,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = _launcher_default_logger

        # Stocker les configurations passées en arguments comme attributs d'instance
        self.ALMA_BASE_DIR = alma_base_dir
        self.PID_STATUS_FILE_PATH_ARG = pid_status_file # Stocker l'argument original
        self.SCRIPTS_CONFIG = scripts_config
        self.LAUNCH_PATTERNS = launch_patterns
        self.PYTHON_VENV_EXECUTABLE = python_venv_executable
        self.LOGS_DIR = logs_dir
        self.LAUNCHER_SERVICES_LOGS_DIR = launcher_services_logs_dir
        self.LAUNCHER_CONFIG_PATH = launcher_config_path # Stocker le chemin du fichier de config
        self.LAUNCHER_PATTERNS_PATH = launcher_patterns_path

        self.logger.info(f"--- Initialisation AlmaLauncherApp V{LAUNCHER_VERSION} ---")
        self.logger.info(f"ALMA_BASE_DIR (instance): {self.ALMA_BASE_DIR}")
        self.logger.info(f"PID_STATUS_FILE (argument): {self.PID_STATUS_FILE_PATH_ARG}")


        if not ALL_UI_COMPONENTS_LOADED: # ALL_UI_COMPONENTS_LOADED est une globale module
            messagebox.showerror("Erreur Critique", "Composants UI non chargés. Arrêt.")
            self.logger.critical("AlmaLauncherApp: ALL_UI_COMPONENTS_LOADED est False. Destruction.")
            self.destroy()
            return

        self.is_running = True
        self.active_processes: Dict[str, Dict[str, Any]] = {}

        # Utiliser self.PID_STATUS_FILE_PATH_ARG qui a été passé et stocké
        if self.PID_STATUS_FILE_PATH_ARG and isinstance(self.PID_STATUS_FILE_PATH_ARG, Path):
            self.pid_status_file_path = self.PID_STATUS_FILE_PATH_ARG
        else:
            self.pid_status_file_path = self.ALMA_BASE_DIR / "logs" / "alma_pids_status.json"
            self.logger.error(f"PID_STATUS_FILE_PATH_ARG reçu invalide ou None, fallback sur: {self.pid_status_file_path}")
        self.logger.info(f"PID_STATUS_FILE utilisé (instance): {self.pid_status_file_path}")


        self.ui_icons: Dict[str, Any] = {}

        self.title(f"ALMA Cognitive Dashboard - V{LAUNCHER_VERSION}")
        self.geometry("1250x850")
        self.minsize(1000, 750)
        self.configure(bg=BG_COLOR_APP_BACKGROUND)

        # --- Initialisation des attributs d'instance pour les constantes de thème ---
        self.BG_COLOR_APP_BACKGROUND = BG_COLOR_APP_BACKGROUND
        self.BG_COLOR_FRAME_MAIN = BG_COLOR_FRAME_MAIN
        self.BG_COLOR_FRAME_MODULES = BG_COLOR_FRAME_MODULES
        self.BG_COLOR_FRAME_INFO = BG_COLOR_FRAME_INFO
        self.TEXT_COLOR_PRIMARY = TEXT_COLOR_PRIMARY
        self.TEXT_COLOR_SECONDARY = TEXT_COLOR_SECONDARY
        self.TEXT_COLOR_HEADER = TEXT_COLOR_HEADER
        self.TEXT_COLOR_ON_ACCENT_PRIMARY = TEXT_COLOR_ON_ACCENT_PRIMARY
        self.TEXT_COLOR_ON_ACCENT_STOP = TEXT_COLOR_ON_ACCENT_STOP
        self.TEXT_COLOR_ON_ACCENT_STOP_ALL = TEXT_COLOR_ON_ACCENT_STOP_ALL
        self.COLOR_ACCENT_PRIMARY = COLOR_ACCENT_PRIMARY
        self.COLOR_BUTTON_DEFAULT_BG = COLOR_BUTTON_DEFAULT_BG
        self.COLOR_BUTTON_STOP_BG = COLOR_BUTTON_STOP_BG
        self.COLOR_BUTTON_STOP_ALL_BG = COLOR_BUTTON_STOP_ALL_BG
        self.COLOR_STATUS_GREEN = COLOR_STATUS_GREEN
        self.COLOR_STATUS_RED = COLOR_STATUS_RED
        self.COLOR_STATUS_GREY = COLOR_STATUS_GREY

        # --- Initialisation des attributs pour le monitoring Wi-Fi ---
        self.WIFI_INTERFACE_NAME: Optional[str] = None
        self.last_net_io: Any = None
        self.last_net_io_time: Optional[float] = None
        self.WIFI_UPDATE_INTERVAL_S: float = 3.0 # Valeur par défaut, peut être surchargée par config

        # Logique pour déterminer WIFI_INTERFACE_NAME
        # Option 1: Charger depuis launcher_config.yaml (si tu l'implémentes)
        # Pour cela, il faudrait une méthode pour charger et parser le YAML ici.
        # Exemple simplifié :
        # if self.LAUNCHER_CONFIG_PATH and self.LAUNCHER_CONFIG_PATH.exists():
        #     try:
        #         import yaml # Nécessite PyYAML
        #         with open(self.LAUNCHER_CONFIG_PATH, 'r', encoding='utf-8') as f_conf:
        #             launcher_cfg_data = yaml.safe_load(f_conf)
        #             if launcher_cfg_data and isinstance(launcher_cfg_data, dict):
        #                 wifi_mon_cfg = launcher_cfg_data.get('wifi_monitoring', {})
        #                 self.WIFI_INTERFACE_NAME = wifi_mon_cfg.get('interface_name')
        #                 self.WIFI_UPDATE_INTERVAL_S = float(wifi_mon_cfg.get('update_interval_s', 3.0))
        #                 self.logger.info(f"Config Wi-Fi chargée depuis YAML: Interface={self.WIFI_INTERFACE_NAME}, Interval={self.WIFI_UPDATE_INTERVAL_S}s")
        #     except ImportError:
        #         self.logger.warning("PyYAML non installé. Impossible de lire launcher_config.yaml pour la config Wi-Fi.")
        #     except Exception as e_yaml:
        #         self.logger.error(f"Erreur lecture launcher_config.yaml pour config Wi-Fi: {e_yaml}")

        # Option 2: Auto-détection si non chargé depuis config (pour Linux)
        if not self.WIFI_INTERFACE_NAME and platform.system() == "Linux": # platform doit être importé globalement
            try:
                result = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], capture_output=True, text=True, check=True, timeout=1)
                match = re.search(r'dev\s+(\S+)', result.stdout)
                if match:
                    self.WIFI_INTERFACE_NAME = match.group(1)
                    self.logger.info(f"Interface réseau par défaut auto-détectée: {self.WIFI_INTERFACE_NAME}")
            except FileNotFoundError:
                self.logger.warning("Commande 'ip' non trouvée, impossible d'auto-détecter l'interface réseau.")
            except subprocess.CalledProcessError:
                self.logger.warning("Impossible d'obtenir la route par défaut (ex: pas de connexion internet pour le test 8.8.8.8).")
            except Exception as e_autodetect:
                self.logger.warning(f"Échec de l'auto-détection de l'interface réseau par défaut: {e_autodetect}")

        if not self.WIFI_INTERFACE_NAME:
            self.logger.warning("Aucune interface Wi-Fi/réseau spécifiée ou auto-détectée. Le monitoring Wi-Fi sera inactif.")
        else:
            self.logger.info(f"Monitoring Wi-Fi configuré pour l'interface: {self.WIFI_INTERFACE_NAME}")
        # --- Fin initialisation Wi-Fi ---

        # --- Initialisation des attributs d'instance pour les polices et style à None ---
        self.font_app_title: Optional[tkfont.Font] = None
        # ... (tous les autres self.font_* ) ...
        self.font_combobox: Optional[tkfont.Font] = None
        self.style: Optional[ttk.Style] = None

        # --- Séquence d'initialisation de l'UI ---
        self._setup_styles_and_fonts()
        self._load_ui_icons()
        self._setup_menubar()
        self._setup_main_layout()

        self.monitoring_thread: Optional[threading.Thread] = None
        self._initialize_monitoring_thread()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.logger.info("AlmaLauncherApp initialisée et prête. Monitoring démarré.")
#DEBUT ACTION MÉTHODE
    def action_lancer_enqueteur(self):
        """
        Lance le script d'enquête ALMA (enquete_alma_complete_v6.sh)
        dans un nouveau terminal (pour Linux).
        """
        self.logger.info("--- action_lancer_enqueteur APPELÉE ---")
        self.logger.info("Action: Lancement du script d'enquête ALMA...")

        if not self.ALMA_BASE_DIR:
            self.logger.error("ALMA_BASE_DIR non défini, impossible de lancer l'enquêteur.")
            messagebox.showerror(
                "Erreur Configuration",
                "Le chemin de base d'ALMA n'est pas configuré.\nImpossible de lancer le script d'enquête.",
                parent=self
            )
            return

        script_name = "enquete_alma_complete_v6.sh" # Nom exact confirmé
        script_path = self.ALMA_BASE_DIR / script_name

        if not script_path.is_file():
            self.logger.error(f"Script d'enquête introuvable: {script_path}")
            messagebox.showerror(
                "Erreur Script",
                f"Le script d'enquête '{script_name}' est introuvable à:\n{script_path}",
                parent=self
            )
            return

        try:
            terminals_linux = [
                # (commande_terminal, option_pour_executer_commande_complexe)
                # Pour gnome-terminal, on va lui passer une chaîne de commande complète à exécuter dans un shell
                ("gnome-terminal", "--"),
                ("konsole", "-e"),
                ("xfce4-terminal", "-x"), # xfce4-terminal -x bash -c "commande; read"
                ("lxterminal", "-e"),
                ("mate-terminal", "-x"),
                ("xterm", "-e")
            ]

            cmd_launched = False
            for term_executable, exec_option in terminals_linux:
                if shutil.which(term_executable):
                    command_to_run_in_terminal = f"bash '{str(script_path)}'; echo -e '\\n--- Script terminé. Appuyez sur Entrée pour fermer. ---'; read"

                    full_command_args = [term_executable]

                    if term_executable in ["gnome-terminal", "konsole", "lxterminal", "mate-terminal"]:
                        # Ces terminaux prennent généralement la commande à exécuter comme argument après leur option -e ou --
                        # gnome-terminal -- bash -c "..."
                        # konsole -e bash -c "..."
                        if exec_option: # -- pour gnome-terminal, -e pour konsole/lxterminal
                             full_command_args.append(exec_option)
                        if term_executable == "gnome-terminal": # gnome-terminal -- bash -c "cmd"
                            full_command_args.extend(["bash", "-c", command_to_run_in_terminal])
                        else: # konsole -e / lxterminal -e / mate-terminal -x (pour mate-terminal -x est comme -e)
                             full_command_args.append(command_to_run_in_terminal) # Passe la chaîne entière

                    elif term_executable == "xfce4-terminal":
                        full_command_args.extend(["-x", "bash", "-c", command_to_run_in_terminal])

                    elif term_executable == "xterm":
                        # xterm -e 'bash /path/to/script; read'
                        # Pour xterm, il est parfois plus simple de passer la commande entière quotée
                        full_command_args.extend([exec_option, f"bash '{str(script_path)}'; echo -e '\\n--- Script terminé ---'; read -p 'Appuyez sur Entrée...'"])
                    else: # Fallback générique, pourrait ne pas garder ouvert
                        full_command_args.append(exec_option)
                        full_command_args.append("bash")
                        full_command_args.append(str(script_path))

                    try:
                        subprocess.Popen(full_command_args, close_fds=True)
                        self.logger.info(f"Tentative de lancement de '{script_name}' avec {term_executable} via: {' '.join(full_command_args)}")
                        cmd_launched = True
                        break
                    except Exception as e_popen:
                        self.logger.warning(f"Échec du lancement avec {term_executable} et la commande {' '.join(full_command_args)}: {e_popen}")
                        cmd_launched = False # Assurer que si Popen échoue, on essaie le suivant

            if not cmd_launched:
                self.logger.warning(
                    "Aucun terminal Linux compatible (gnome-terminal, konsole, xfce4-terminal, etc.) "
                    "n'a été trouvé dans le PATH. Impossible d'ouvrir le script dans un nouveau terminal."
                )
                messagebox.showwarning(
                    "Terminal Manquant",
                    "Impossible de trouver un terminal compatible pour lancer le script d'enquête.\n"
                    "Veuillez en installer un (ex: gnome-terminal, konsole, xfce4-terminal).",
                    parent=self
                )
            # else: # cmd_launched is True
                # TODO: Mettre à jour le statut visuel du bouton Enquêteur (ex: vert)
                # if hasattr(self.header_toolbar_frame, 'update_enqueteur_status'):
                #     self.header_toolbar_frame.update_enqueteur_status("launched")

        except FileNotFoundError: # Si shutil.which renvoie None et qu'on essaie de l'utiliser, ou si bash n'est pas trouvé
            self.logger.error(f"Erreur FileNotFoundError lors de la tentative de lancement du terminal pour '{script_name}'. Vérifiez que le terminal et bash sont installés et dans le PATH.")
            messagebox.showerror("Erreur Terminal", "Impossible de trouver le terminal ou bash pour lancer le script.", parent=self)
            # TODO: Mettre à jour le statut visuel
            # if hasattr(self.header_toolbar_frame, 'update_enqueteur_status'):
            #     self.header_toolbar_frame.update_enqueteur_status("failed")
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du lancement du script d'enquête '{script_name}': {e}", exc_info=True)
            messagebox.showerror(
                "Erreur Inattendue",
                f"Une erreur est survenue lors du lancement du script d'enquête:\n{e}",
                parent=self
            )
            # TODO: Mettre à jour le statut visuel
            # if hasattr(self.header_toolbar_frame, 'update_enqueteur_status'):
            #     self.header_toolbar_frame.update_enqueteur_status("failed")
    def action_lancer_meteo(self):
        """
        Lance le script de l'interface météo ALMA (meteoalma.py).
        """
        self.logger.info("Action: Lancement de l'interface Météo ALMA...")

        # Vérifier que les chemins de base et l'exécutable Python sont définis
        if not self.ALMA_BASE_DIR:
            self.logger.error("ALMA_BASE_DIR non défini, impossible de lancer l'interface Météo.")
            messagebox.showerror("Erreur Configuration",
                                 "Chemin de base d'ALMA non configuré.", parent=self)
            return

        if not self.PYTHON_VENV_EXECUTABLE or not self.PYTHON_VENV_EXECUTABLE.is_file():
            self.logger.error(f"Exécutable Python du venv non valide ou non trouvé: {self.PYTHON_VENV_EXECUTABLE}")
            messagebox.showerror("Erreur Configuration",
                                 "L'exécutable Python de l'environnement virtuel n'est pas correctement configuré.", parent=self)
            return

        script_name = "meteoalma.py"
        script_subdir = "Interfaces" # Sous-dossier où se trouve meteoalma.py
        script_path = self.ALMA_BASE_DIR / script_subdir / script_name

        if not script_path.is_file():
            self.logger.error(f"Script Météo introuvable à l'emplacement attendu: {script_path}")
            messagebox.showerror(
                "Erreur Script",
                f"Le script Météo '{script_name}' est introuvable à:\n{script_path}",
                parent=self
            )
            return

        try:
            # Commande pour lancer le script Python
            # On utilise l'exécutable Python du venv pour s'assurer que les bonnes dépendances sont utilisées.
            # Le script meteoalma.py ouvrira sa propre fenêtre Tkinter.
            command_args = [str(self.PYTHON_VENV_EXECUTABLE), str(script_path)]

            # Utiliser Popen pour lancer le script en tant que processus séparé et non bloquant.
            # Pas besoin d'un nouveau terminal ici car c'est une application GUI.
            process = subprocess.Popen(command_args,
                                       cwd=self.ALMA_BASE_DIR, # Définir le répertoire de travail si besoin
                                       close_fds=(os.name != 'nt')) # close_fds=True sur Unix

            self.logger.info(f"Interface Météo '{script_name}' lancée avec la commande: {' '.join(command_args)}. PID: {process.pid}")

            # Optionnel : Enregistrer le PID si on veut le suivre (pas prioritaire pour une GUI simple)
            # self.active_processes[f"meteo_alma_{process.pid}"] = {
            #     "pid": process.pid,
            #     "command": command_args,
            #     "start_time": datetime.datetime.now().isoformat(),
            #     "type": "gui_tool"
            # }
            # self._write_pid_status_file() # Si on enregistre le PID

            # TODO: Mettre à jour un éventuel indicateur visuel pour le bouton Météo (si implémenté)
            # if hasattr(self.header_toolbar_frame, 'update_meteo_status'):
            #     self.header_toolbar_frame.update_meteo_status("launched", process.pid)

        except FileNotFoundError:
            self.logger.error(f"Erreur FileNotFoundError: L'exécutable Python '{self.PYTHON_VENV_EXECUTABLE}' ou le script '{script_path}' est introuvable.")
            messagebox.showerror("Erreur Lancement",
                                 f"Impossible de trouver l'exécutable Python ou le script Météo.", parent=self)
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du lancement de l'interface Météo '{script_name}': {e}", exc_info=True)
            messagebox.showerror(
                "Erreur Inattendue",
                f"Une erreur est survenue lors du lancement de l'interface Météo:\n{e}",
                parent=self
            )

    def action_lancer_cedille(self):
        """
        Lance le script de l'interface Cédille ALMA (Outils/cedille_interface.py).
        """
        self.logger.info("Action: Lancement de l'interface Cédille ALMA...")

        if not self.ALMA_BASE_DIR:
            self.logger.error("ALMA_BASE_DIR non défini, impossible de lancer l'interface Cédille.")
            messagebox.showerror("Erreur Configuration",
                                 "Chemin de base d'ALMA non configuré.", parent=self)
            return

        if not self.PYTHON_VENV_EXECUTABLE or not self.PYTHON_VENV_EXECUTABLE.is_file():
            self.logger.error(f"Exécutable Python du venv non valide ou non trouvé: {self.PYTHON_VENV_EXECUTABLE}")
            messagebox.showerror("Erreur Configuration",
                                 "L'exécutable Python de l'environnement virtuel n'est pas correctement configuré.", parent=self)
            return

        script_name = "cedille_interface.py"
        script_subdir = "Outils" # Le script est dans ALMA_BASE_DIR/Outils/
        script_path = self.ALMA_BASE_DIR / script_subdir / script_name

        if not script_path.is_file():
            self.logger.error(f"Script Cédille introuvable à l'emplacement attendu: {script_path}")
            messagebox.showerror(
                "Erreur Script",
                f"Le script Cédille '{script_name}' est introuvable à:\n{script_path}",
                parent=self
            )
            return

        try:
            command_args = [str(self.PYTHON_VENV_EXECUTABLE), str(script_path)]
            # Définir le répertoire de travail au dossier où se trouve le script
            # Cela peut aider si le script cedille_interface.py essaie de charger des fichiers relatifs.
            working_directory = self.ALMA_BASE_DIR / script_subdir

            process = subprocess.Popen(command_args,
                                       cwd=working_directory,
                                       close_fds=(os.name != 'nt'))

            self.logger.info(f"Interface Cédille '{script_name}' lancée avec la commande: {' '.join(command_args)}. PID: {process.pid}")

        except FileNotFoundError:
            self.logger.error(f"Erreur FileNotFoundError: L'exécutable Python '{self.PYTHON_VENV_EXECUTABLE}' ou le script '{script_path}' est introuvable.")
            messagebox.showerror("Erreur Lancement",
                                 f"Impossible de trouver l'exécutable Python ou le script Cédille.", parent=self)
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du lancement de l'interface Cédille '{script_name}': {e}", exc_info=True)
            messagebox.showerror(
                "Erreur Inattendue",
                f"Une erreur est survenue lors du lancement de l'interface Cédille:\n{e}",
                parent=self
            )
    # --- FIN DE L'AJOUT POUR CÉDILLE ---
#FIN ACTION MÉTHODE
    def _load_ui_icons(self):
        """Charge les icônes PNG nécessaires pour l'UI (barre d'outils, etc.)."""
        # Accéder aux globales définies au niveau module pour Pillow
        # Ces globales sont OK car elles sont définies une fois à l'import du module.
        global PILLOW_AVAILABLE, PIL_Image, PIL_ImageTk

        if not (PILLOW_AVAILABLE and PIL_Image and PIL_ImageTk):
            self.logger.warning("Pillow non disponible ou import échoué, impossible de charger les icônes PNG.")
            return

        self.logger.debug("Chargement des icônes UI via Pillow...")
        icon_definitions = {
            "wifi_on": "icons_launcher/wifi_on.png",
            "wifi_off": "icons_launcher/wifi_off.png",
            "enqueteur": "icons_launcher/enqueteur_agent.png",
            "meteo": "icons_launcher/meteo_cloud_sun.png",
            "aspirateur": "icons_launcher/aspirateur_maintenance.png",
            "save_disk": "icons_launcher/save_diskette.png",
            "sniffing_dog": "icons_launcher/sniffing_dog.png",
            "cedille": "icons_launcher/cedille.png"
            # TODO: Ajouter les chemins pour les icônes des modules de la grille
        }

        # Utiliser self.ALMA_BASE_DIR (attribut d'instance) au lieu de la globale ALMA_BASE_DIR
        if self.ALMA_BASE_DIR is None:
            self.logger.error("self.ALMA_BASE_DIR (attribut d'instance) non défini, impossible de déterminer le chemin des icônes.")
            return

        # Le chemin de base pour les icônes est maintenant relatif à self.ALMA_BASE_DIR
        # Tu avais "Outils" comme sous-dossier. Vérifie si c'est toujours correct.
        # Si tes icônes sont directement dans ALMA_BASE_DIR/icons_launcher, alors ce serait:
        # icons_base_path = self.ALMA_BASE_DIR
        # Ou si elles sont dans ALMA_BASE_DIR/Outils/icons_launcher:
        icons_base_path = self.ALMA_BASE_DIR / "Outils"

        for key, rel_path_str in icon_definitions.items():
            try:
                # rel_path_str est déjà "icons_launcher/nom_icone.png"
                # donc on le concatène directement à icons_base_path si icons_base_path est "Outils"
                # ou à self.ALMA_BASE_DIR si rel_path_str est juste "nom_icone.png" et icons_base_path est "Outils/icons_launcher"
                # Pour l'instant, je suppose que rel_path_str est le chemin *depuis* icons_base_path
                # Si icons_base_path = self.ALMA_BASE_DIR / "Outils"
                # et rel_path_str = "icons_launcher/wifi_on.png"
                # alors full_path = self.ALMA_BASE_DIR / "Outils" / "icons_launcher" / "wifi_on.png"
                # Cela semble être ce que tu avais.

                full_path = icons_base_path / rel_path_str # Ceci suppose que rel_path_str est relatif à icons_base_path
                                                          # Par exemple, si icons_base_path = self.ALMA_BASE_DIR / "Outils"
                                                          # et rel_path_str = "icons_launcher/wifi_on.png",
                                                          # alors full_path sera ALMA_BASE_DIR/Outils/icons_launcher/wifi_on.png

                if full_path.is_file():
                    img_opened = PIL_Image.open(full_path)
                    # Si tu as besoin de redimensionner TOUTES les icônes à une taille standard :
                    # target_size = (24, 24) # Par exemple, pour des icônes de 24x24
                    # img_opened = img_opened.resize(target_size, PIL_Image.Resampling.LANCZOS)
                    self.ui_icons[key] = PIL_ImageTk.PhotoImage(img_opened)
                    self.logger.debug(f"Icône '{key}' chargée depuis {full_path}")
                else:
                    self.logger.warning(f"Fichier icône introuvable pour '{key}' à {full_path}")
                    self.ui_icons[key] = None # Important pour les vérifications ultérieures
            except Exception as e_icon:
                self.logger.error(f"Erreur chargement icône '{key}' depuis {full_path}: {e_icon}", exc_info=False)
                self.ui_icons[key] = None
                    """TODO: Add docstring."""

    def _setup_styles_and_fonts(self):
        self.logger.debug("Configuration des polices et styles ttk...")
        actual_font_family = FONT_FAMILY_PRIMARY # Constante globale
        try: tkfont.Font(family=FONT_FAMILY_PRIMARY, size=10)
        except tk.TclError: actual_font_family = FONT_FAMILY_FALLBACK; self.logger.warning(f"Police '{FONT_FAMILY_PRIMARY}' non trouvée. Fallback: '{actual_font_family}'.")

        self.font_app_title = tkfont.Font(family=actual_font_family, size=FONT_APP_TITLE_DEF[1], weight=FONT_APP_TITLE_DEF[2])
        self.font_module_button_label = tkfont.Font(family=actual_font_family, size=FONT_MODULE_BUTTON_LABEL_DEF[1], weight=FONT_MODULE_BUTTON_LABEL_DEF[2])
        self.font_module_button_type = tkfont.Font(family=actual_font_family, size=FONT_MODULE_BUTTON_TYPE_DEF[1])
        self.font_action_button = tkfont.Font(family=actual_font_family, size=FONT_ACTION_BUTTON_DEF[1], weight=FONT_ACTION_BUTTON_DEF[2])
        self.font_button_launch = tkfont.Font(family=actual_font_family, size=FONT_BUTTON_LAUNCH_DEF[1], weight=FONT_BUTTON_LAUNCH_DEF[2])
        self.font_button_stop_all = tkfont.Font(family=actual_font_family, size=FONT_BUTTON_STOP_ALL_DEF[1], weight=FONT_BUTTON_STOP_ALL_DEF[2])
        self.font_body_normal = tkfont.Font(family=actual_font_family, size=FONT_BODY_NORMAL_DEF[1], weight=FONT_BODY_NORMAL_DEF[2] if len(FONT_BODY_NORMAL_DEF) > 2 else "normal")
        self.font_info_bar = tkfont.Font(family=actual_font_family, size=FONT_INFO_BAR_DEF[1], weight=FONT_INFO_BAR_DEF[2] if len(FONT_INFO_BAR_DEF) > 2 else "normal")
        self.font_combobox = tkfont.Font(family=actual_font_family, size=FONT_COMBOBOX_DEF[1], weight=FONT_COMBOBOX_DEF[2] if len(FONT_COMBOBOX_DEF) > 2 else "normal")
        self.logger.debug(f"Polices d'instance définies avec: {actual_font_family}")

        self.style = ttk.Style(self)
        try: self.style.theme_use("clam")
        except tk.TclError:
            self.logger.warning("Thème ttk 'clam' non trouvé."); available_themes = self.style.theme_names()
            if available_themes: self.style.theme_use(available_themes[0]); self.logger.info(f"Thème fallback: {available_themes[0]}")
            else: self.logger.error("Aucun thème ttk disponible.")

        self.style.configure(".", font=self.font_body_normal)
        self.style.configure("TFrame", background=BG_COLOR_APP_BACKGROUND) # Constante globale
        self.style.configure("TLabel", background=BG_COLOR_APP_BACKGROUND, foreground=TEXT_COLOR_PRIMARY, font=self.font_body_normal)
        self.style.configure("Header.TLabel", font=self.font_app_title, foreground=TEXT_COLOR_HEADER, padding=10, anchor="center")
        self.style.configure("Info.TLabel", font=self.font_info_bar, foreground=TEXT_COLOR_SECONDARY)
        self.style.configure("TButton", font=self.font_action_button, padding=(8,6))
        self.style.configure("TCombobox", font=self.font_combobox, padding=3)
        self.style.configure("TScale", troughcolor=BG_COLOR_FRAME_INFO, background=COLOR_ACCENT_PRIMARY)
        self.style.configure("StatusBar.TLabel", relief=tk.SUNKEN, anchor=tk.W, padding=3, font=self.font_info_bar, background="#DFE1E5", foreground="#172B4D")
        self.style.configure("TLabelFrame", background=BG_COLOR_FRAME_MODULES, borderwidth=1, relief="solid", padding=5)
        self.style.configure("TLabelFrame.Label", background=BG_COLOR_FRAME_MODULES, foreground=TEXT_COLOR_PRIMARY, font=self.font_action_button)
        self.style.configure("TPanedwindow", background=BG_COLOR_FRAME_MAIN)
        self.style.configure("Vertical.TPanedwindow", background=BG_COLOR_FRAME_MAIN)
        self.style.configure("Horizontal.TPanedwindow", background=BG_COLOR_FRAME_MAIN)
        self.style.configure("Green.Horizontal.TProgressbar", troughcolor=BG_COLOR_FRAME_INFO, background=COLOR_STATUS_GREEN, thickness=15)
        self.style.configure("Blue.Horizontal.TProgressbar", troughcolor=BG_COLOR_FRAME_INFO, background=COLOR_ACCENT_PRIMARY, thickness=15)
        self.style.configure("Module.Launch.TButton", font=FONT_BUTTON_LAUNCH_DEF, padding=(5,5))
        self.style.configure("Module.Stop.TButton", font=FONT_ACTION_BUTTON_DEF, padding=(3,3), background=COLOR_BUTTON_STOP_BG, foreground=TEXT_COLOR_ON_ACCENT_STOP)
        self.style.map("Module.Stop.TButton", background=[("active", self.darken_color(COLOR_BUTTON_STOP_BG, 0.8))])
        self.style.configure("StopAll.TButton", font=FONT_BUTTON_STOP_ALL_DEF, padding=(10, 8), background=COLOR_BUTTON_STOP_ALL_BG, foreground=TEXT_COLOR_ON_ACCENT_STOP_ALL)
        self.style.map("StopAll.TButton", background=[("active", self.darken_color(COLOR_BUTTON_STOP_ALL_BG, 0.8))])
            """TODO: Add docstring."""
        self.logger.debug("Styles ttk configurés.")

    def darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        if not isinstance(hex_color, str) or not hex_color.startswith('#') or len(hex_color) != 7:
            self.logger.warning(f"Format couleur invalide pour darken_color: '{hex_color}'. Retourne noir.")
            return "#000000"
        try:
            r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
                """TODO: Add docstring."""
            return f"#{max(0,min(255,int(r*factor))):02x}{max(0,min(255,int(g*factor))):02x}{max(0,min(255,int(b*factor))):02x}"
        except ValueError: self.logger.warning(f"Err conv couleur darken: '{hex_color}'. Ret noir."); return "#000000"

    def _setup_menubar(self):
        self.logger.debug("Initialisation de MenuBarHandler...")
        # MenuBarHandler est importé au niveau module
            """TODO: Add docstring."""
        self.menu_handler = MenuBarHandler(self, self)
        self.config(menu=self.menu_handler.menubar)
        self.logger.debug("Barre de menu attachée.")

    def _setup_main_layout(self):
        self.logger.debug("Configuration de la disposition principale des panneaux...")

        # S'assurer que les composants UI sont censés être disponibles.
        # La vérification critique est dans __init__, ceci est une double sécurité interne.
        if not ALL_UI_COMPONENTS_LOADED: # ALL_UI_COMPONENTS_LOADED est une globale module
            self.logger.error(
                "_setup_main_layout appelé alors que ALL_UI_COMPONENTS_LOADED est False. "
                "Les panneaux ne seront pas créés."
            )
            # On pourrait afficher un label d'erreur central si cela arrive.
            error_label = ttk.Label(self, text="Erreur critique: Composants UI non chargés.")
            error_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            return

        # Ordre de pack() est important pour que les éléments prennent la bonne place:
        # 1. Header en haut.
        # 2. Status bar tout en bas.
        # 3. Module grid juste au-dessus de la status bar.
        # 4. Le PanedWindow principal remplit l'espace restant au centre.

        # 1. Barre d'outils d'en-tête
        try:
            # Le style "Header.TFrame" (si défini) sera appliqué par la classe HeaderToolbar
            # ou par les styles ttk globaux pour TFrame.
            self.header_toolbar_frame = HeaderToolbar(self, self)
            self.header_toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))
            self.logger.debug("HeaderToolbar instanciée et packée.")
        except Exception as e_header:
            self.logger.error(f"Erreur lors de la création de HeaderToolbar: {e_header}", exc_info=True)
            ttk.Label(self, text="Erreur chargement Barre d'Outils").pack(side=tk.TOP, fill=tk.X)


        # 2. Barre de statut (packée avant la grille des modules pour être tout en bas)
        if not hasattr(self, 'status_bar_text'): # Créer si pas déjà fait dans __init__
             self.status_bar_text = tk.StringVar(value="Prêt.")

        # Recréer ou reconfigurer le widget status_bar pour s'assurer qu'il utilise le style
        # et est packé au bon endroit par rapport aux autres éléments dynamiques.
        if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
            self.status_bar.pack_forget() # Retirer si déjà packé pour contrôler l'ordre

        # Assurez-vous que le style "StatusBar.TLabel" est défini dans _setup_styles_and_fonts
        self.status_bar = ttk.Label(self, textvariable=self.status_bar_text, style="StatusBar.TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.logger.debug("Barre de statut packée en bas.")


        # 3. Grille des modules (packée avant le PanedWindow principal pour être au-dessus de la status bar)
        try:
            # Le style "ModuleGrid.TFrame" sera appliqué par la classe ModuleGridPanel
            self.module_grid_frame = ModuleGridPanel(self, self, SCRIPTS_CONFIG)
            self.module_grid_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 5))
            self.logger.debug("ModuleGridPanel instanciée et packée.")
        except Exception as e_grid:
            self.logger.error(f"Erreur lors de la création de ModuleGridPanel: {e_grid}", exc_info=True)
            ttk.Label(self, text="Erreur chargement Grille Modules").pack(side=tk.BOTTOM, fill=tk.X)


        # 4. PanedWindow principal pour diviser horizontalement (Gauche | Centre-Droite)
        # Il prendra l'espace restant entre le header et la grille des modules.
        # Le style "Main.TPanedwindow" doit être défini dans _setup_styles_and_fonts
        main_h_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL, style="TPanedwindow") # Utiliser style de base ou "Main.TPanedwindow"
        main_h_paned.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.logger.debug("PanedWindow horizontal principal créé et packé.")

        # --- Panneau de Gauche ---
        try:
            # Le style "LeftPanel.TFrame" sera appliqué par la classe LeftMonitorPanel
            self.left_panel_frame = LeftMonitorPanel(main_h_paned, self)
            main_h_paned.add(self.left_panel_frame, weight=25) # Poids pour la répartition initiale (25% de la largeur)
            self.logger.debug("LeftMonitorPanel instancié et ajouté au PanedWindow horizontal.")
        except Exception as e_left:
            self.logger.error(f"Erreur lors de la création de LeftMonitorPanel: {e_left}", exc_info=True)
            error_label_left = ttk.Label(main_h_paned, text="Erreur chargement Panneau Gauche")
            main_h_paned.add(error_label_left, weight=25)

        # --- PanedWindow pour la partie Centre-Droite (division verticale) ---
        # Le style "Sub.TPanedwindow" ou "Vertical.TPanedwindow" doit être défini
        center_right_v_paned = ttk.PanedWindow(main_h_paned, orient=tk.VERTICAL, style="TPanedwindow")
        main_h_paned.add(center_right_v_paned, weight=75) # 75% de la largeur
        self.logger.debug("PanedWindow vertical (centre-droite) créé et ajouté.")

        # --- Panneau Central ---
        try:
            # Le style "CenterPanel.TFrame" sera appliqué par la classe CenterInfoPredictionPanel
            self.center_panel_frame = CenterInfoPredictionPanel(center_right_v_paned, self)
            center_right_v_paned.add(self.center_panel_frame, weight=40) # 40% de la hauteur de cette zone
            self.logger.debug("CenterInfoPredictionPanel instancié et ajouté au PanedWindow vertical.")
        except Exception as e_center:
            self.logger.error(f"Erreur lors de la création de CenterInfoPredictionPanel: {e_center}", exc_info=True)
            error_label_center = ttk.Label(center_right_v_paned, text="Erreur chargement Panneau Central")
            center_right_v_paned.add(error_label_center, weight=40)

        # --- Panneau de Droite ---
        try:
            # Le style "RightPanel.TFrame" sera appliqué par la classe RightGraphPanel
            self.right_graph_panel_frame = RightGraphPanel(center_right_v_paned, self)
            center_right_v_paned.add(self.right_graph_panel_frame, weight=60) # 60% de la hauteur
            self.logger.debug("RightGraphPanel instancié et ajouté au PanedWindow vertical.")
        except Exception as e_right:
            self.logger.error(f"Erreur lors de la création de RightGraphPanel: {e_right}", exc_info=True)
            error_label_right = ttk.Label(center_right_v_paned, text="Erreur chargement Panneau Droit")
            center_right_v_paned.add(error_label_right, weight=60)

        self.logger.info("Disposition principale des panneaux (_setup_main_layout) configurée.")

    def _get_wifi_status_data(self) -> Dict[str, Any]:
        """
        Collecte les informations sur l'état du Wi-Fi, le débit et la qualité du signal.
        Spécifique à Linux pour la qualité du signal (nmcli, iwconfig).
        """
        # Accéder aux globales psutil définies au niveau du module
        global PSUTIL_AVAILABLE, psutil # Nécessaire si psutil n'est pas un attribut de self

        data = {
            'connected_to_ap': False,
            'connected_to_internet': False,
            'upload_kbps': "N/A", # Initialiser en string pour affichage direct si échec
            'download_kbps': "N/A",
            'signal_quality_score': None,
            'interface_name': self.WIFI_INTERFACE_NAME # self.WIFI_INTERFACE_NAME est un attribut d'instance
        }

        if not self.WIFI_INTERFACE_NAME:
            # self.logger.debug("Aucune interface Wi-Fi configurée pour le monitoring.") # Peut être trop verbeux
            return data

        if not PSUTIL_AVAILABLE or not psutil:
            self.logger.warning("psutil non disponible, impossible de récupérer les informations réseau.")
            return data

        try:
            # --- 1. État de connexion à l'AP (Access Point) ---
            if_stats = psutil.net_if_stats().get(self.WIFI_INTERFACE_NAME)
            if if_stats and if_stats.isup:
                # Vérifier si l'interface a une adresse IP (un signe de connexion à un réseau)
                # Cela ne garantit pas que c'est un AP Wi-Fi, mais c'est un bon indicateur.
                # Pour une vérification plus stricte de l'AP, il faudrait des commandes OS spécifiques.
                addrs = psutil.net_if_addrs().get(self.WIFI_INTERFACE_NAME)
                if addrs:
                    for addr in addrs:
                        if addr.family == socket.AF_INET or addr.family == socket.AF_INET6: # type: ignore
                            # socket n'est pas défini ici, il faudrait l'importer ou utiliser psutil. Einige Konstanten sind in psutil. Einige sind in socket.
                            # Pour psutil, les familles sont des entiers. socket.AF_INET est 2.
                            if addr.family == 2: # AF_INET
                                data['connected_to_ap'] = True
                                break

            # --- 2. État de connexion Internet (si connecté à l'AP) ---
            if data['connected_to_ap']:
                try:
                    # Test de résolution DNS rapide. Peut être bloquant brièvement.
                    # Utiliser un host fiable et un timeout court.
                    socket.gethostbyname("one.one.one.one") # Cloudflare DNS, généralement rapide
                    # Ou "www.google.com", "quad9.net"
                    data['connected_to_internet'] = True
                except (socket.error, socket.gaierror): # socket.gaierror pour les erreurs de résolution
                    data['connected_to_internet'] = False
                    # self.logger.debug(f"Pas de connexion Internet (échec résolution DNS) sur {self.WIFI_INTERFACE_NAME}")
            # else:
                # self.logger.debug(f"Non connecté à un AP sur {self.WIFI_INTERFACE_NAME}, donc pas d'Internet.")


            # --- 3. Débit Réseau ---
            current_net_io = psutil.net_io_counters(pernic=True).get(self.WIFI_INTERFACE_NAME)
            current_time_net = time.time() # Utiliser time.time() qui est plus standard que monotonic ici

            if current_net_io and hasattr(self, 'last_net_io') and self.last_net_io and \
               hasattr(self, 'last_net_io_time') and self.last_net_io_time:

                elapsed_time = current_time_net - self.last_net_io_time
                if elapsed_time > 0.1: # Éviter division par zéro ou valeurs aberrantes si trop court
                    bytes_sent_diff = current_net_io.bytes_sent - self.last_net_io.bytes_sent
                    bytes_recv_diff = current_net_io.bytes_recv - self.last_net_io.bytes_recv

                    # Convertir en kbps (kilobits par seconde)
                    data['upload_kbps'] = round((bytes_sent_diff * 8) / elapsed_time / 1000, 1)
                    data['download_kbps'] = round((bytes_recv_diff * 8) / elapsed_time / 1000, 1)

            # Stocker les valeurs actuelles pour le prochain calcul
            self.last_net_io = current_net_io
            self.last_net_io_time = current_time_net

            # --- 4. Qualité du Signal (Linux uniquement pour l'instant) ---
            # Assurer que platform est importé en haut du fichier alma_launcher.py
            if platform.system() == "Linux":
                signal_found = False
                # Tentative 1: nmcli (NetworkManager)
                if shutil.which("nmcli"): # Vérifie si nmcli est dans le PATH
                    try:
                        # -t pour terse, -f pour fields, dev wifi pour lister les devices wifi
                        # On cherche la ligne correspondant à NOTRE interface et où ACTIVE=yes
                        result_nmcli = subprocess.run(
                            ['nmcli', '-t', '-f', 'DEVICE,SIGNAL,ACTIVE', 'dev', 'wifi'],
                            capture_output=True, text=True, check=True, timeout=1.5
                        )
                        for line in result_nmcli.stdout.strip().split('\n'):
                            parts = line.split(':')
                            if len(parts) >= 3 and parts[0] == self.WIFI_INTERFACE_NAME and parts[2].lower() == 'yes':
                                signal_percent = int(parts[1])
                                data['signal_quality_score'] = round(signal_percent / 10) # Convertir 0-100 à 0-10
                                signal_found = True
                                break
                        if signal_found:
                            self.logger.debug(f"Qualité signal (nmcli) pour {self.WIFI_INTERFACE_NAME}: {data['signal_quality_score']}/10")
                    except (subprocess.CalledProcessError, FileNotFoundError, ValueError, subprocess.TimeoutExpired) as e_nmcli:
                        self.logger.debug(f"nmcli non utilisable ou a échoué pour {self.WIFI_INTERFACE_NAME}: {e_nmcli}. Essai avec iwconfig.")
                    except Exception as e_nmcli_generic:
                         self.logger.warning(f"Erreur générique avec nmcli pour {self.WIFI_INTERFACE_NAME}: {e_nmcli_generic}")

                # Tentative 2: iwconfig (Fallback si nmcli échoue ou n'est pas là)
                if not signal_found and shutil.which("iwconfig"):
                    try:
                        result_iwconfig = subprocess.run(
                            ['iwconfig', self.WIFI_INTERFACE_NAME],
                            capture_output=True, text=True, check=True, timeout=1.5
                        )
                        quality_match = re.search(r"Link Quality=(\d+)/(\d+)", result_iwconfig.stdout)
                        # signal_level_match = re.search(r"Signal level=([-\d]+)\s*dBm", result_iwconfig.stdout) # Moins direct à convertir en %

                        if quality_match:
                            current_val = int(quality_match.group(1))
                            total_val = int(quality_match.group(2))
                            if total_val > 0:
                                data['signal_quality_score'] = round((current_val / total_val) * 10)
                                signal_found = True # Marquer comme trouvé même si c'est par iwconfig
                                self.logger.debug(f"Qualité signal (iwconfig) pour {self.WIFI_INTERFACE_NAME}: {data['signal_quality_score']}/10")
                    except (subprocess.CalledProcessError, FileNotFoundError, ValueError, subprocess.TimeoutExpired) as e_iwconfig:
                        self.logger.debug(f"iwconfig non utilisable ou a échoué pour {self.WIFI_INTERFACE_NAME}: {e_iwconfig}")
                    except Exception as e_iwconfig_generic:
                         self.logger.warning(f"Erreur générique avec iwconfig pour {self.WIFI_INTERFACE_NAME}: {e_iwconfig_generic}")

                if not signal_found:
                    self.logger.debug(f"Impossible de déterminer la qualité du signal pour {self.WIFI_INTERFACE_NAME} via nmcli ou iwconfig.")
            else: # Si pas Linux
                self.logger.debug(f"La récupération de la qualité du signal Wi-Fi n'est implémentée que pour Linux (actuellement {platform.system()}).")

        except psutil.NoSuchProcess: # Peut arriver si l'interface disparaît soudainement
            self.logger.warning(f"L'interface {self.WIFI_INTERFACE_NAME} n'existe plus (NoSuchProcess).")
            # Réinitialiser les données à des valeurs par défaut "déconnecté"
            data.update({k: v for k, v in self._get_wifi_status_data().items() if k not in ['interface_name']}) # Appelle récursivement pour reset
        except psutil.Error as e_psutil:
            self.logger.error(f"Erreur psutil lors de la récupération des infos Wi-Fi pour {self.WIFI_INTERFACE_NAME}: {e_psutil}")
                """TODO: Add docstring."""
        except Exception as e_generic:
            self.logger.error(f"Erreur inattendue dans _get_wifi_status_data pour {self.WIFI_INTERFACE_NAME}: {e_generic}", exc_info=True)

        return data

    def _initialize_monitoring_thread(self):
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.logger.info("Le thread de monitoring est déjà actif.")
            return
        self.logger.info("Initialisation et démarrage du thread de monitoring UI...")
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True, name="UIMonitorThread")
        self.monitoring_thread.start()

    def _monitoring_loop(self):
        """
        Boucle principale du thread de monitoring.
        Collecte périodiquement les données et demande des mises à jour de l'UI via self.after().
        """
        thread_name = threading.current_thread().name
        self.logger.info(f"Thread de monitoring UI ({thread_name}) démarré.")

        # Intervalles de rafraîchissement (en secondes)
        # self.WIFI_UPDATE_INTERVAL_S est maintenant un attribut d'instance, initialisé dans __init__
        # Les autres peuvent aussi devenir des attributs d'instance si tu veux les configurer
        INTERVAL_CPU_RAM_ALMA = 1.5
        # INTERVAL_WIFI_STATUS = 3.0 # Remplacé par self.WIFI_UPDATE_INTERVAL_S
        INTERVAL_LOGS_CERVEAU = 60.0
        INTERVAL_ROADMAP_SUMMARY = 30.0
        INTERVAL_MODULE_STATUS_GRID = 2.0
        INTERVAL_GRAPHS_PANEL = 3.0
        # INTERVAL_PREDICTION_PANEL = 10.0

        last_update_time = {
            "cpu_ram_alma": 0.0,
            "wifi_status": 0.0,
            "logs_cerveau": 0.0,
            "roadmap_summary": 0.0,
            "module_status_grid": 0.0,
            "graphs_panel": 0.0,
            # "prediction_panel": 0.0,
        }

        global PSUTIL_AVAILABLE, psutil # Accéder aux globales

        total_system_ram_bytes = 1
        if PSUTIL_AVAILABLE and psutil:
            try:
                total_system_ram_bytes = psutil.virtual_memory().total
                if total_system_ram_bytes == 0:
                    self.logger.warning("psutil.virtual_memory().total a retourné 0, fallback à 1.")
                    total_system_ram_bytes = 1
            except psutil.Error as e_psutil_total_ram:
                 self.logger.error(f"Erreur psutil RAM totale dans {thread_name}: {e_psutil_total_ram}")
                 total_system_ram_bytes = 1
        else:
            self.logger.warning(f"psutil non disponible dans {thread_name}, monitoring CPU/RAM limité.")


        while self.is_running:
            current_time = time.time()

            # --- 1. CPU/RAM ALMA (pour LeftMonitorPanel) ---
            if PSUTIL_AVAILABLE and psutil and \
               (current_time - last_update_time["cpu_ram_alma"] > INTERVAL_CPU_RAM_ALMA):

                # ... (ta logique existante pour CPU/RAM ALMA, qui semble correcte) ...
                current_pids_on_disk: Dict[str, Dict[str, Any]] = {}
                if self.pid_status_file_path and self.pid_status_file_path.exists():
                    try:
                        with open(self.pid_status_file_path, "r", encoding="utf-8") as f_pid:
                            current_pids_on_disk = json.load(f_pid)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Fichier PID {self.pid_status_file_path} corrompu (JSONDecodeError) dans {thread_name}.")
                    except Exception as e_read_pid_loop:
                        self.logger.warning(f"Erreur lecture {self.pid_status_file_path} dans {thread_name}: {e_read_pid_loop}")

                total_alma_cpu_percent = 0.0
                total_alma_ram_rss_bytes = 0
                pids_to_check: List[int] = []
                for proc_data in current_pids_on_disk.values(): # Itérer sur les valeurs directement
                    pid_candidate = proc_data.get("pid")
                    if isinstance(pid_candidate, int) and pid_candidate > 0:
                        pids_to_check.append(pid_candidate)
                    elif isinstance(pid_candidate, (float, str)):
                        try: pid_int = int(pid_candidate); pids_to_check.append(pid_int) if pid_int > 0 else None
                        except ValueError: pass

                for pid_val in pids_to_check:
                    if psutil.pid_exists(pid_val):
                        try:
                            p = psutil.Process(pid_val)
                            with p.oneshot():
                                total_alma_cpu_percent += p.cpu_percent(interval=None)
                                total_alma_ram_rss_bytes += p.memory_info().rss
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
                        except Exception: pass # Log plus détaillé si besoin

                ram_alma_p = (total_alma_ram_rss_bytes / total_system_ram_bytes) * 100 if total_system_ram_bytes > 0 else 0.0
                if total_alma_ram_rss_bytes < 1024: ram_alma_abs_s = f"{total_alma_ram_rss_bytes} B"
                elif total_alma_ram_rss_bytes < 1024**2: ram_alma_abs_s = f"{total_alma_ram_rss_bytes/1024:.1f} KB"
                elif total_alma_ram_rss_bytes < 1024**3: ram_alma_abs_s = f"{total_alma_ram_rss_bytes/1024**2:.1f} MB"
                else: ram_alma_abs_s = f"{total_alma_ram_rss_bytes/1024**3:.1f} GB"

                if hasattr(self, 'left_panel_frame') and self.left_panel_frame and self.winfo_exists():
                     self.after(0, lambda cpu=total_alma_cpu_percent, ram_p=ram_alma_p, ram_abs=ram_alma_abs_s: \
                                     self.left_panel_frame.update_cpu_ram(cpu, ram_p, ram_abs))
                last_update_time["cpu_ram_alma"] = current_time

            # --- 2. Statut Wi-Fi (pour HeaderToolbar) ---
            # Vérifier si header_toolbar_frame existe et si la fenêtre principale existe encore
            if hasattr(self, 'header_toolbar_frame') and self.header_toolbar_frame and self.winfo_exists() and \
               (current_time - last_update_time["wifi_status"] > self.WIFI_UPDATE_INTERVAL_S): # Utiliser self.WIFI_UPDATE_INTERVAL_S

                wifi_data = self._get_wifi_status_data() # Appel à la méthode que nous avons définie

                # Demander la mise à jour de l'UI dans le thread principal de Tkinter
                # Assurer que header_toolbar_frame a bien la méthode update_wifi_status
                if hasattr(self.header_toolbar_frame, 'update_wifi_status'):
                    self.after(0, lambda data=wifi_data: self.header_toolbar_frame.update_wifi_status(data))
                else:
                    self.logger.warning("header_toolbar_frame n'a pas de méthode update_wifi_status.")

                last_update_time["wifi_status"] = current_time

            # --- 3. Logs Cerveau (pour LeftMonitorPanel) ---
            # TODO: (Ta logique existante en TODO)
            # ...

            # --- 4. Résumé Roadmap (pour CenterInfoPredictionPanel) ---
            # TODO: (Ta logique existante en TODO)
            # ...

            # --- 5. Statut des Modules dans la Grille (pour ModuleGridPanel) ---
            # TODO: (Ta logique existante en TODO)
            # ...

            # --- 6. Graphiques du Panneau de Droite (pour RightGraphPanel) ---
            # TODO: (Ta logique existante en TODO)
                """TODO: Add docstring."""
                    """TODO: Add docstring."""
                        """TODO: Add docstring."""
                            """TODO: Add docstring."""
                                """TODO: Add docstring."""
                                    """TODO: Add docstring."""
                                        """TODO: Add docstring."""
                                            """TODO: Add docstring."""
                                                """TODO: Add docstring."""
                                                    """TODO: Add docstring."""
                                                        """TODO: Add docstring."""
                                                            """TODO: Add docstring."""
                                                                """TODO: Add docstring."""
            # ...
                """TODO: Add docstring."""

            time.sleep(0.25) # Sleep court pour la réactivité de la boucle

        self.logger.info(f"Thread de monitoring UI ({thread_name}) terminé.")

    def action_capture_ecran(self): self.logger.info("Action: Capture écran")
    def action_sauvegarder_config_lanceur(self): self.logger.info("Action: Sauvegarder Config Lanceur")
    def action_sauvegarder_disposition_ui(self): self.logger.info("Action: Sauvegarder Disposition UI")
    def action_sauvegarder_kb_backup(self): self.logger.info("Action: Sauvegarder KB Backup")
    def action_quitter_app(self): self.on_closing()
    def action_edition_ouvrir_config(self, config_key: str): self.logger.info(f"Action: Ouvrir config {config_key}")
    def action_edition_copier_logs(self): self.logger.info("Action: Copier logs")
    def action_edition_effacer_logs(self): self.logger.info("Action: Effacer logs")
    def action_edition_explorer_fichiers(self, location_key: str): self.logger.info(f"Action: Explorer {location_key}")
    def action_affichage_changer_theme(self, theme_name: str): self.logger.info(f"Action: Changer thème {theme_name}")
    def action_affichage_changer_police_globale(self, taille_action: str): self.logger.info(f"Action: Changer police {taille_action}")
    def action_aide_consulter_doc(self, doc_key: str): self.logger.info(f"Action: Consulter doc {doc_key}")
    def action_aide_a_propos(self): self.logger.info("Action: À propos"); messagebox.showinfo(f"À Propos", f"{APP_NAME_LAUNCHER} V{LAUNCHER_VERSION}", parent=self)

    def on_closing(self):
        self.logger.info("Demande de fermeture...")
        if messagebox.askokcancel("Quitter", "Quitter ALMA Launcher ?", parent=self):
            self.is_running = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.logger.debug("Attente de la fin du thread de monitoring...")
                self.monitoring_thread.join(timeout=1.0)
            self.logger.info("Lanceur ALMA fermé.")
            self.destroy()
        else:
            self.logger.info("Fermeture annulée.")
# --- BLOC 4: POINT D'ENTRÉE PRINCIPAL ---
if __name__ == "__main__":
    # 1. Configuration initiale du logger (StreamHandler console)
    # On s'assure que _launcher_default_logger est propre avant d'ajouter des handlers ici.
    # Ceci est particulièrement utile si le script est exécuté plusieurs fois dans un interpréteur interactif
    # ou si des imports précédents ont pu ajouter des handlers.
    if _launcher_default_logger.hasHandlers():
        _launcher_default_logger.handlers.clear()
        # _bootstrap_logger.info("Handlers existants pour _launcher_default_logger vidés dans __main__.") # Optionnel

    _launcher_default_logger.setLevel(logging.DEBUG) # Niveau par défaut
    log_formatter_main = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)-7s - [%(threadName)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler_main = logging.StreamHandler(sys.stdout)
    console_handler_main.setFormatter(log_formatter_main)
    _launcher_default_logger.addHandler(console_handler_main)

    _launcher_default_logger.info(f"--- Démarrage {APP_NAME_LAUNCHER} V{LAUNCHER_VERSION} (Bloc __main__) ---") # Changé de "Pré-init" à "Bloc __main__" pour clarté

    # 2. Initialisation des chemins globaux et chargement des configs
    # Déclaration des variables globales qui seront peuplées par la fonction
    # (nécessaire si d'autres parties du module y accèdent globalement, sinon on pourrait
    # juste les passer directement à AlmaLauncherApp)
    # Pour l'instant, on garde la structure avec les globales modules.

    # Initialiser les globales à None pour plus de clarté avant l'appel
    ALMA_BASE_DIR: Optional[Path] = None
    PYTHON_VENV_EXECUTABLE: Optional[Path] = None
    LOGS_DIR: Optional[Path] = None
    LAUNCHER_SERVICES_LOGS_DIR: Optional[Path] = None
    PID_STATUS_FILE: Optional[Path] = None
    LAUNCHER_CONFIG_PATH: Optional[Path] = None
    SCRIPTS_CONFIG: Dict[str, Any] = {}
    LAUNCHER_PATTERNS_PATH: Optional[Path] = None
    LAUNCH_PATTERNS: List[Dict[str, Any]] = [] # Corrigé en List

    try:
        # Appel à la fonction et récupération de toutes les valeurs
        (alma_base_dir_loc, python_venv_loc, logs_dir_loc, launcher_services_logs_dir_loc,
         pid_status_file_loc, launcher_config_path_loc, scripts_config_loc,
         launcher_patterns_path_loc, launch_patterns_loc) = \
            _initialize_global_paths_and_load_configs_v2(_launcher_default_logger) # Passer le logger principal

        # Assignation aux variables globales du module
        ALMA_BASE_DIR = alma_base_dir_loc
        PYTHON_VENV_EXECUTABLE = python_venv_loc
        LOGS_DIR = logs_dir_loc
        LAUNCHER_SERVICES_LOGS_DIR = launcher_services_logs_dir_loc
        PID_STATUS_FILE = pid_status_file_loc
        LAUNCHER_CONFIG_PATH = launcher_config_path_loc
        SCRIPTS_CONFIG = scripts_config_loc
        LAUNCHER_PATTERNS_PATH = launcher_patterns_path_loc
        LAUNCH_PATTERNS = launch_patterns_loc

    except SystemExit:
        _launcher_default_logger.critical("Échec de _initialize_global_paths_and_load_configs_v2 (SystemExit). Le script va s'arrêter.")
        # Pas besoin de sys.exit(1) ici car _initialize_global_paths_and_load_configs_v2 le fait déjà.
        raise # Relancer l'exception pour arrêter proprement
    except Exception as e_init_globals_main:
        _launcher_default_logger.critical(f"Erreur majeure lors de l'initialisation des globales dans __main__: {e_init_globals_main}", exc_info=True)
        sys.exit(1)

    # 3. Ajouter le FileHandler maintenant que LOGS_DIR est connu et est un Path
    if LOGS_DIR: # LOGS_DIR est maintenant une variable globale initialisée
        try:
            _launcher_main_log_file_path = LOGS_DIR / "alma_launcher.log"
            # S'assurer que le répertoire logs existe (déjà fait dans _initialize_global_paths_and_load_configs_v2)
            # LOGS_DIR.mkdir(parents=True, exist_ok=True) # Redondant si déjà fait, mais ne nuit pas

            file_handler_main = RotatingFileHandler(
                _launcher_main_log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
            )
            file_handler_main.setFormatter(log_formatter_main)
            _launcher_default_logger.addHandler(file_handler_main)
            _launcher_default_logger.info(f"FileHandler pour alma_launcher.log ajouté: {_launcher_main_log_file_path}")
        except Exception as e_fh_main:
            _launcher_default_logger.error(f"Erreur ajout FileHandler principal: {e_fh_main}", exc_info=True)
    else:
        _launcher_default_logger.error("LOGS_DIR non défini après initialisation, FileHandler non ajouté.")

    # 4. Import et vérification de PSUTIL
    # Déclaration des globales pour psutil si elles ne sont pas déjà au niveau module
    try:
        import psutil as psutil_imported
        psutil = psutil_imported
        PSUTIL_AVAILABLE = True
        _launcher_default_logger.info(f"psutil (V{psutil.__version__ if hasattr(psutil, '__version__') else 'Inconnue'}) chargé.")
    except ImportError:
        PSUTIL_AVAILABLE = False
        psutil = None # Assurer que psutil est None si l'import échoue
        _launcher_default_logger.warning("psutil non trouvé. Infos système limitées.")

    # 5. Vérification critique des composants UI
    if not ALL_UI_COMPONENTS_LOADED: # ALL_UI_COMPONENTS_LOADED est une globale module
        critical_msg_comp = "ERREUR CRITIQUE: Un ou plusieurs composants UI du lanceur n'ont pas pu être importés (voir logs précédents). L'application va quitter."
        _launcher_default_logger.critical(critical_msg_comp)
        try:
            root_err_comp_main = tk.Tk(); root_err_comp_main.withdraw()
            messagebox.showerror("Erreur Critique Lanceur", critical_msg_comp, parent=root_err_comp_main) # Spécifier parent
            root_err_comp_main.destroy()
        except Exception: pass
        sys.exit(1)

    # 6. Création et lancement de l'application
    try:
        # Passer les configurations nécessaires à AlmaLauncherApp
        app = AlmaLauncherApp(
            alma_base_dir=ALMA_BASE_DIR, # Variable globale module
            pid_status_file=PID_STATUS_FILE, # Variable globale module
            scripts_config=SCRIPTS_CONFIG, # Variable globale module
            launch_patterns=LAUNCH_PATTERNS, # Variable globale module
            python_venv_executable=PYTHON_VENV_EXECUTABLE, # Variable globale module
            logs_dir=LOGS_DIR, # Variable globale module
            launcher_services_logs_dir=LAUNCHER_SERVICES_LOGS_DIR, # Variable globale module
            launcher_config_path=LAUNCHER_CONFIG_PATH, # Variable globale module
            launcher_patterns_path=LAUNCHER_PATTERNS_PATH # Variable globale module
        )
        app.mainloop()
    except Exception as e_runtime:
        _launcher_default_logger.critical(f"Erreur d'exécution non interceptée dans AlmaLauncherApp: {e_runtime}", exc_info=True)
        try:
            root_err_runtime = tk.Tk(); root_err_runtime.withdraw()
            messagebox.showerror("Erreur Fatale Lanceur", f"Une erreur fatale est survenue:\n{e_runtime}", parent=root_err_runtime)
            root_err_runtime.destroy()
        except Exception: pass
        sys.exit(1)

    _launcher_default_logger.info(f"--- {APP_NAME_LAUNCHER} V{LAUNCHER_VERSION} Terminé ---")