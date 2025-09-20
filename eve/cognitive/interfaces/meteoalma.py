# Interfaces/meteoalma.py

# --- Imports système de base ---
import sys # Doit être parmi les premiers pour le contournement sys.path
from pathlib import Path # Doit être parmi les premiers pour le contournement sys.path
from typing import Dict, Any, Optional, Tuple, List
# --- DÉBUT DU CONTOURNEMENT POUR sys.path ---
# Ce bloc tente de s'assurer que le site-packages du venv est prioritaire.
try:
    _project_root_found = False
    _project_root: Optional[Path] = None # Déclarer _project_root pour qu'il soit défini dans tous les cas

    if '__file__' in globals(): # Vérifie si __file__ est défini
        _current_script_path = Path(__file__).resolve()
        # Candidat 1: le script est dans un sous-dossier direct de ALMA (ex: Interfaces/)
        _candidate_parent1 = _current_script_path.parent
        _candidate_root1 = _candidate_parent1.parent # ALMA/
        # Candidat 2: le script est à la racine de ALMA
        _candidate_root2 = _current_script_path.parent # ALMA/

        if (_candidate_root1 / "venv").is_dir():
            _project_root = _candidate_root1
            _project_root_found = True
        elif (_candidate_root2 / "venv").is_dir():
            _project_root = _candidate_root2
            _project_root_found = True

    if not _project_root_found or _project_root is None: # Fallback si la détection ci-dessus échoue ou _project_root reste None
        _project_root = Path("/home/toni/Documents/ALMA") # Chemin codé en dur comme dernier recours
        # Utiliser print ici car le logger n'est pas encore configuré pour ce script autonome
        print(f"INFO (meteoalma.py sys.path): Utilisation du chemin codé pour project_root: {_project_root}")

    _venv_site_packages_path_str = str(_project_root / "venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages")

    if Path(_venv_site_packages_path_str).is_dir():
        if _venv_site_packages_path_str not in sys.path:
            sys.path.insert(0, _venv_site_packages_path_str)
            print(f"INFO (meteoalma.py sys.path): Chemin venv ajouté en priorité: {_venv_site_packages_path_str}")
        # Vérifier si le chemin est présent mais pas en tête (index 0 ou 1, car index 0 est souvent '')
        elif sys.path.index(_venv_site_packages_path_str) > 1:
            sys.path.remove(_venv_site_packages_path_str)
            sys.path.insert(0, _venv_site_packages_path_str)
            print(f"INFO (meteoalma.py sys.path): Chemin venv remonté en priorité: {_venv_site_packages_path_str}")
        # else: # Déjà en bonne position
            # print(f"INFO (meteoalma.py sys.path): Chemin venv déjà en bonne position: {_venv_site_packages_path_str}")
        # print(f"DEBUG (meteoalma.py sys.path): sys.path actuel: {sys.path}") # Décommenter pour debug
    else:
        print(f"AVERTISSEMENT (meteoalma.py sys.path): Dossier site-packages venv NON TROUVÉ à {_venv_site_packages_path_str}")
except Exception as _e_sys_path_mod:
    print(f"AVERTISSEMENT (meteoalma.py sys.path): Erreur lors de la tentative de modification de sys.path: {_e_sys_path_mod}")
# --- FIN DU CONTOURNEMENT POUR sys.path ---


# --- Autres imports ---
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import threading
import requests
import json
# from pathlib import Path # Déjà importé plus haut
import datetime
# import time # Plus utilisé directement ici, mais gardé si tu en as besoin pour autre chose
import traceback
import logging # Pour le logger de la classe MeteoAlmaApp
import locale # Pour les noms de jours/mois en français

# --- Imports Matplotlib (MAINTENANT APRÈS LE CONTOURNEMENT SYS.PATH) ---
import matplotlib
matplotlib.use('TkAgg') # Spécifier le backend TkAgg AVANT d'importer pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Optionnel: from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import matplotlib.dates as mdates # Pour formater les dates sur l'axe X


# Essayer de configurer la locale en français pour les dates
print("INFO (meteoalma.py config): Tentative de configuration de la locale...")
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    current_locale = locale.getlocale(locale.LC_TIME)
    print(f"INFO (meteoalma.py config): Locale LC_TIME configurée avec succès en 'fr_FR.UTF-8'. Actuelle: {current_locale}")
except locale.Error as e1:
    print(f"AVERTISSEMENT (meteoalma.py config): Échec configuration locale 'fr_FR.UTF-8': {e1}. Tentative avec 'french'...")
    try:
        locale.setlocale(locale.LC_TIME, 'french')
        current_locale = locale.getlocale(locale.LC_TIME)
        print(f"INFO (meteoalma.py config): Locale LC_TIME configurée avec succès en 'french'. Actuelle: {current_locale}")
    except locale.Error as e2:
        current_locale = locale.getlocale(locale.LC_TIME)
        print(f"AVERTISSEMENT (meteoalma.py config): Échec configuration locale 'french': {e2}. Locale actuelle: {current_locale}")
        print("Attention: Impossible de configurer la locale en français pour les dates.")

# Configuration
LATITUDE = 44.81985684111081
LONGITUDE = 1.2147718587283332
print(f"INFO (meteoalma.py config): LATITUDE={LATITUDE}, LONGITUDE={LONGITUDE}")

# Détermination de ALMA_BASE_DIR
_alma_base_dir_init_found = False
_alma_base_dir_for_script: Optional[Path] = None # Initialiser à None pour plus de clarté

print("INFO (meteoalma.py config): Début de la détermination de ALMA_BASE_DIR...")
if '__file__' in globals():
    _current_script_path_init = Path(__file__).resolve()
    print(f"INFO (meteoalma.py config): Chemin du script actuel (__file__): {_current_script_path_init}")

    # Candidat 1: le script est dans un sous-dossier direct de ALMA (ex: Interfaces/)
    _candidate_parent1 = _current_script_path_init.parent # ex: ALMA/Interfaces/
    _candidate_root1 = _candidate_parent1.parent       # ex: ALMA/
    print(f"INFO (meteoalma.py config): Candidat Root 1 (parent du parent): {_candidate_root1}")

    # Candidat 2: le script est à la racine de ALMA (moins probable pour meteoalma.py)
    _candidate_root2 = _current_script_path_init.parent # ex: ALMA/
    print(f"INFO (meteoalma.py config): Candidat Root 2 (parent): {_candidate_root2}")

    # Vérification de la présence d'un dossier 'venv' pour valider le répertoire racine du projet
    if (_candidate_root1 / "venv").is_dir():
        _alma_base_dir_for_script = _candidate_root1
        _alma_base_dir_init_found = True
        print(f"INFO (meteoalma.py config): ALMA_BASE_DIR trouvé via Candidat Root 1: {_alma_base_dir_for_script}")
    elif (_candidate_root2 / "venv").is_dir():
        _alma_base_dir_for_script = _candidate_root2
        _alma_base_dir_init_found = True
        print(f"INFO (meteoalma.py config): ALMA_BASE_DIR trouvé via Candidat Root 2: {_alma_base_dir_for_script}")
    else:
        print(f"AVERTISSEMENT (meteoalma.py config): Aucun dossier 'venv' trouvé dans les candidats racines. La détection automatique a échoué.")
else:
    print("AVERTISSEMENT (meteoalma.py config): Variable __file__ non définie. Impossible de déterminer ALMA_BASE_DIR automatiquement.")

if not _alma_base_dir_init_found or _alma_base_dir_for_script is None:
    _alma_base_dir_for_script = Path("/home/toni/Documents/ALMA") # Fallback
    print(f"AVERTISSEMENT (meteoalma.py config): Utilisation du chemin ALMA_BASE_DIR par défaut (fallback): {_alma_base_dir_for_script}")

ALMA_BASE_DIR: Path = _alma_base_dir_for_script.resolve() # S'assurer que c'est un chemin absolu et assigner à la globale
print(f"INFO (meteoalma.py config): ALMA_BASE_DIR final utilisé: {ALMA_BASE_DIR}")

SAVE_DIR = ALMA_BASE_DIR / "Connaissance" / "Environnement" / "Meteo"
print(f"INFO (meteoalma.py config): SAVE_DIR configuré à: {SAVE_DIR}")

HOURLY_VARIABLES = [
    "temperature_2m", "relativehumidity_2m", "apparent_temperature", "precipitation_probability",
    "precipitation", "weathercode", "pressure_msl", "cloudcover", "windspeed_10m",
    "winddirection_10m", "is_day", "uv_index"
]
DAILY_VARIABLES = [
    "weathercode", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset",
    "precipitation_sum", "uv_index_max", "winddirection_10m_dominant", "windgusts_10m_max" # Assurez-vous que windgusts_10m_max est bien demandé si utilisé dans _generate_derived_insights
]
print(f"INFO (meteoalma.py config): HOURLY_VARIABLES: {HOURLY_VARIABLES}")
print(f"INFO (meteoalma.py config): DAILY_VARIABLES: {DAILY_VARIABLES}")


TIMEZONE = "auto"
FORECAST_DAYS = 7
HOURLY_FORECAST_HOURS = 24 # Afficher les prévisions pour les prochaines 24 heures
print(f"INFO (meteoalma.py config): TIMEZONE={TIMEZONE}, FORECAST_DAYS={FORECAST_DAYS}, HOURLY_FORECAST_HOURS={HOURLY_FORECAST_HOURS}")


# Mapping des codes WMO (inchangé)
WMO_CODES: Dict[int, Tuple[str, str]] = {
    0: ("Ciel dégagé", "☀️"), 1: ("Principalement clair", "🌤️"), 2: ("Partiellement nuageux", "🌥️"),
    3: ("Couvert", "☁️"), 45: ("Brouillard", "🌫️"), 48: ("Brouillard givrant", "🌫️❄️"),
    51: ("Bruine légère", "💧"), 53: ("Bruine modérée", "💧"), 55: ("Bruine dense", "💧"),
    56: ("Bruine verglaçante légère", "🧊💧"), 57: ("Bruine verglaçante dense", "🧊💧"),
    61: ("Pluie légère", "🌧️"), 63: ("Pluie modérée", "🌧️"), 65: ("Pluie forte", "🌧️"),
    66: ("Pluie verglaçante légère", "🧊🌧️"), 67: ("Pluie verglaçante forte", "🧊🌧️"),
    71: ("Neige légère", "🌨️"), 73: ("Neige modérée", "🌨️"), 75: ("Neige forte", "🌨️"),
    77: ("Grains de neige", "❄️"), 80: ("Averses légères", "🌦️"), 81: ("Averses modérées", "🌦️"),
    82: ("Averses violentes", "🌦️"), 85: ("Averses de neige légères", "🌨️"), 86: ("Averses de neige fortes", "🌨️"),
    95: ("Orage", "🌩️"), 96: ("Orage avec grêle légère", "🌩️🧊"), 99: ("Orage avec grêle forte", "🌩️🧊"),
}
DEFAULT_WEATHER_ICON = "❓"
DEFAULT_WEATHER_DESCRIPTION = "Inconnu"

class MeteoAlmaApp:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, root_window):
        self.root = root_window

        # 1. INITIALISATION DU LOGGER EN PREMIER
        # Utiliser logging.getLogger directement, la configuration du handler est bonne.
        self.logger: logging.Logger = logging.getLogger("MeteoAlmaApp") # Annotation de type ajoutée
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.hasHandlers():
            ch = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s (%(funcName)s:%(lineno)d)')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        self.logger.info("Logger pour MeteoAlmaApp configuré et prêt.") # Log après la config du handler

        # 2. Configuration de la fenêtre racine
        self.logger.debug("Configuration du titre et de la géométrie de la fenêtre racine...")
        self.root.title("ALMA Météo")
        self.root.geometry("850x700")
        self.logger.debug("Titre de la fenêtre et géométrie configurés.")

        # 3. Initialisation des attributs pour les graphiques à None
        self.logger.debug("Initialisation des attributs de figures/axes Matplotlib à None...")
        self.temp_figure: Optional[Figure] = None
        self.temp_ax: Optional[Any] = None
        self.temp_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None
        self.humidity_figure: Optional[Figure] = None
        self.humidity_ax: Optional[Any] = None
        self.humidity_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None
        self.precip_figure: Optional[Figure] = None
        self.precip_ax_qty: Optional[Any] = None
        self.precip_ax_prob: Optional[Any] = None
        self.precip_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None
        self.wind_figure: Optional[Figure] = None
        self.wind_ax: Optional[Any] = None
        self.wind_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None
        self.logger.debug("Attributs de graphiques initialisés.")

        self.analysis_labels: List[ttk.Label] = []
        self.logger.debug("self.analysis_labels initialisé (liste vide).")

        # 4. DÉFINITION DES POLICES D'INSTANCE (AVANT L'APPEL À _setup_ui)
        self.logger.info("Initialisation des polices d'instance...")
        try:
            _font_family_primary = "Segoe UI"
            try:
                _ = tkfont.Font(family=_font_family_primary, size=1)
                self.logger.debug(f"  Police primaire '{_font_family_primary}' semble disponible.")
            except tk.TclError:
                self.logger.warning(f"  Police primaire '{_font_family_primary}' non trouvée. Tentative avec TkDefaultFont.")
                _font_family_primary = tkfont.nametofont("TkDefaultFont").actual()["family"]
                self.logger.info(f"  Police primaire de fallback utilisée: '{_font_family_primary}'.")

            self.title_font = tkfont.Font(family=_font_family_primary, size=12, weight="bold")
            self.data_font = tkfont.Font(family=_font_family_primary, size=9)
            self.small_data_font = tkfont.Font(family=_font_family_primary, size=8)

            _icon_font_family = "Segoe UI Symbol"
            try:
                _ = tkfont.Font(family=_icon_font_family, size=1)
                self.logger.debug(f"  Police d'icônes '{_icon_font_family}' semble disponible.")
            except tk.TclError:
                self.logger.warning(f"  Police d'icônes '{_icon_font_family}' non trouvée. Tentative avec 'DejaVu Sans'.")
                _icon_font_family = "DejaVu Sans"
                try:
                    _ = tkfont.Font(family=_icon_font_family, size=1)
                    self.logger.info(f"  Police d'icônes de fallback utilisée: '{_icon_font_family}'.")
                except tk.TclError:
                     self.logger.error(f"  Police d'icônes '{_icon_font_family}' non trouvée non plus. Les icônes pourraient mal s'afficher. Utilisation de TkDefaultFont.")
                     _icon_font_family = tkfont.nametofont("TkDefaultFont").actual()["family"]

            self.icon_font = tkfont.Font(family=_icon_font_family, size=18)
            self.logger.info("Polices d'instance initialisées avec succès.")
        except Exception as e_fonts:
            self.logger.critical(f"Erreur critique lors de l'initialisation des polices: {e_fonts}", exc_info=True)
            self.title_font = tkfont.Font(size=12, weight="bold")
            self.data_font = tkfont.Font(size=9)
            self.small_data_font = tkfont.Font(size=8)
            self.icon_font = tkfont.Font(size=18)
            self.logger.warning("Polices initialisées avec des valeurs par défaut Tkinter suite à une erreur critique.")
        # --- FIN DÉFINITION DES POLICES ---

        # 5. APPEL À _setup_ui pour construire l'interface utilisateur
        self.logger.info("Appel à self._setup_ui() pour construire l'interface utilisateur...")
        try:
            self._setup_ui() # L'APPEL EST ICI
            self.logger.info("self._setup_ui() terminé avec succès.")
        except Exception as e_setup_ui:
            self.logger.critical(f"Erreur critique lors de l'exécution de self._setup_ui(): {e_setup_ui}", exc_info=True)
            messagebox.showerror("Erreur UI Critique", f"Une erreur critique est survenue lors de la construction de l'interface:\n{e_setup_ui}\nL'application pourrait ne pas fonctionner correctement.", parent=self.root)
            # L'application pourrait être dans un état instable ici, envisager de quitter si _setup_ui échoue ?

        # 6. Suite de l'initialisation
        self.logger.debug("Vérification/Création du dossier de sauvegarde...")
        try:
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Dossier de sauvegarde est prêt: {SAVE_DIR}")
        except Exception as e_save_dir:
            self.logger.error(f"Erreur lors de la création du dossier de sauvegarde {SAVE_DIR}: {e_save_dir}", exc_info=True)
            messagebox.showerror("Erreur Création Dossier", f"Impossible de créer le dossier de sauvegarde {SAVE_DIR}:\n{e_save_dir}", parent=self.root)

        self.logger.debug("Mise à jour du statut initial et démarrage de la récupération des données météo...")
        self.update_status("Prêt. Chargement des données initiales...")
        self.start_fetch_weather_data()
        self.logger.info("MeteoAlmaApp __init__ terminé. Application prête.")

    # -------------------------------------------------------------------------
    # MÉTHODES DE CONFIGURATION DE L'INTERFACE UTILISATEUR (UI SETUP METHODS)
    # -------------------------------------------------------------------------
    def _setup_ui(self):
        """
        Configure l'interface utilisateur principale de l'application Météo.
        Crée les frames principaux, le notebook et appelle les méthodes de setup pour chaque onglet.
        """
        self.logger.info("Début _setup_ui...")

        # Appliquer le style global
        self.logger.debug("  Application du style ttk...")
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
            self.logger.debug("    Thème ttk 'clam' appliqué.")
        except tk.TclError:
            self.logger.warning("    Thème ttk 'clam' non trouvé, utilisation du thème par défaut du système.")
        except Exception as e_style:
            self.logger.error(f"    Erreur inattendue lors de l'application du thème ttk: {e_style}", exc_info=True)


        # LES POLICES SONT MAINTENANT DÉFINIES DANS __init__ ET ACCESSIBLES VIA self.title_font, etc.
        # AUCUNE CRÉATION DE tkfont.Font ICI.

        # --- Frame Principal ---
        self.logger.debug("  Création du main_frame...")
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.columnconfigure(0, weight=1)
        self.logger.debug(f"    main_frame créé et packé (ID: {id(main_frame)}).")

        # --- Barre Supérieure (Bouton Actualiser et Label de Statut) ---
        self.logger.debug("  Création du top_bar_frame...")
        top_bar_frame = ttk.Frame(main_frame)
        top_bar_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        top_bar_frame.columnconfigure(1, weight=1)

        # Assigner à self pour y accéder plus tard si besoin (ex: pour changer l'état)
        self.refresh_button = ttk.Button(top_bar_frame, text="Actualiser", command=self.start_fetch_weather_data)
        self.refresh_button.grid(row=0, column=0, padx=(0,10))

        self.status_label = ttk.Label(top_bar_frame, text="Initialisation de l'interface...", anchor="w")
        self.status_label.grid(row=0, column=1, sticky="ew")
        self.logger.debug("    top_bar_frame avec refresh_button et status_label créé et gridé.")

        # --- Notebook pour les différents onglets ---
        self.logger.debug("  Création du data_notebook...")
        self.data_notebook = ttk.Notebook(main_frame)
        self.data_notebook.grid(row=1, column=0, sticky="nsew", pady=5)
        main_frame.rowconfigure(1, weight=1)
        self.logger.debug(f"    data_notebook créé et gridé (ID: {id(self.data_notebook)}).")

        # --- Création et ajout des onglets ---
        # Onglet: Actuellement
        self.logger.info("    Configuration de l'onglet 'Actuellement'...")
        self.current_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.current_tab, text=' Actuellement ')
        self._setup_current_weather_ui(self.current_tab)

        # Onglet: Prévisions Horaires
        self.logger.info("    Configuration de l'onglet 'Prévisions Horaires'...")
        self.hourly_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.hourly_tab, text=' Prévisions Horaires ')
        self.hourly_canvas = tk.Canvas(self.hourly_tab, highlightthickness=0)
        self.hourly_scrollbar = ttk.Scrollbar(self.hourly_tab, orient="vertical", command=self.hourly_canvas.yview)
        self.scrollable_hourly_frame = ttk.Frame(self.hourly_canvas)
        self.scrollable_hourly_frame.bind("<Configure>", lambda e, c=self.hourly_canvas: c.configure(scrollregion=c.bbox("all")))
        self.hourly_canvas_window = self.hourly_canvas.create_window((0, 0), window=self.scrollable_hourly_frame, anchor="nw")
        self.hourly_canvas.configure(yscrollcommand=self.hourly_scrollbar.set)
        self.hourly_canvas.pack(side="left", fill="both", expand=True)
        self.hourly_scrollbar.pack(side="right", fill="y")
        self.bind_mousewheel_to_children(self.scrollable_hourly_frame, self.hourly_canvas)
        self.hourly_canvas.bind('<Enter>', lambda e, c=self.hourly_canvas: self._bind_mousewheel_events(c))
        self.hourly_canvas.bind('<Leave>', lambda e, c=self.hourly_canvas: self._unbind_mousewheel_events(c))
        self.logger.debug("      Structure de l'onglet 'Prévisions Horaires' (scrollable) créée.")

        # Onglet: Prévisions Journalières
        self.logger.info("    Configuration de l'onglet 'Prévisions Journalières'...")
        self.daily_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.daily_tab, text=' Prévisions Journalières ')
        self.daily_canvas = tk.Canvas(self.daily_tab, highlightthickness=0)
        self.daily_scrollbar = ttk.Scrollbar(self.daily_tab, orient="vertical", command=self.daily_canvas.yview)
        self.scrollable_daily_frame = ttk.Frame(self.daily_canvas)
        self.scrollable_daily_frame.bind("<Configure>", lambda e, c=self.daily_canvas: c.configure(scrollregion=c.bbox("all")))
        self.daily_canvas_window = self.daily_canvas.create_window((0, 0), window=self.scrollable_daily_frame, anchor="nw")
        self.daily_canvas.configure(yscrollcommand=self.daily_scrollbar.set)
        self.daily_canvas.pack(side="left", fill="both", expand=True)
        self.daily_scrollbar.pack(side="right", fill="y")
        self._bind_mousewheel_to_children(self.scrollable_daily_frame, self.daily_canvas)
        self.daily_canvas.bind('<Enter>', lambda e, c=self.daily_canvas: self._bind_mousewheel_events(c))
        self.daily_canvas.bind('<Leave>', lambda e, c=self.daily_canvas: self._unbind_mousewheel_events(c))
        self.logger.debug("      Structure de l'onglet 'Prévisions Journalières' (scrollable) créée.")

        # Onglet: Graphiques Météo
        self.logger.info("    Configuration de l'onglet 'Graphiques Météo'...")
        self.graphs_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.graphs_tab, text=' Graphiques Météo ')
        self.graphs_canvas = tk.Canvas(self.graphs_tab, highlightthickness=0)
        self.graphs_scrollbar = ttk.Scrollbar(self.graphs_tab, orient="vertical", command=self.graphs_canvas.yview)
        self.scrollable_graphs_frame = ttk.Frame(self.graphs_canvas)
        self.scrollable_graphs_frame.bind("<Configure>", lambda e, c=self.graphs_canvas: c.configure(scrollregion=c.bbox("all")))
        self.graphs_canvas_window = self.graphs_canvas.create_window((0, 0), window=self.scrollable_graphs_frame, anchor="nw")
        self.graphs_canvas.configure(yscrollcommand=self.graphs_scrollbar.set)
        self.graphs_canvas.pack(side="left", fill="both", expand=True)
        self.graphs_scrollbar.pack(side="right", fill="y")
        self._bind_mousewheel_to_children(self.scrollable_graphs_frame, self.graphs_canvas)
        self.graphs_canvas.bind('<Enter>', lambda e, c=self.graphs_canvas: self._bind_mousewheel_events(c))
        self.graphs_canvas.bind('<Leave>', lambda e, c=self.graphs_canvas: self._unbind_mousewheel_events(c))

        if hasattr(self, 'scrollable_graphs_frame') and self.scrollable_graphs_frame: # Double vérification
            self._setup_graphs_tab_content(self.scrollable_graphs_frame)
        else:
            self.logger.critical("    CRITIQUE: self.scrollable_graphs_frame n'a pas été correctement initialisé avant l'appel à _setup_graphs_tab_content.")
            error_label_graphs = ttk.Label(self.graphs_tab, text="Erreur critique: Init zone graphiques échouée.")
            error_label_graphs.pack(expand=True, fill=tk.BOTH)
        self.logger.debug("      Structure de l'onglet 'Graphiques Météo' (scrollable) créée et contenu initialisé.")

        # Onglet: Analyses & Alertes
        self.logger.info("    Configuration de l'onglet 'Analyses & Alertes'...")
        self.analysis_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.analysis_tab, text=' Analyses & Alertes ')
        self._setup_analysis_tab_content(self.analysis_tab)
        self.logger.debug("      Contenu de l'onglet 'Analyses & Alertes' initialisé.")

        self.logger.info("_setup_ui terminé avec succès.")
            """TODO: Add docstring."""

    def _on_mousewheel(self, event, canvas: tk.Canvas):
        # self.logger.debug(f"_on_mousewheel: event.delta={getattr(event, 'delta', 'N/A')}, event.num={getattr(event, 'num', 'N/A')} sur canvas ID {id(canvas)}") # Peut être trop verbeux
        try:
            if not canvas.winfo_exists(): # Vérifier si le canvas existe encore
                self.logger.warning("_on_mousewheel: Canvas n'existe plus, annulation du scroll.")
                return

            # Sous Linux, event.delta est souvent 120 ou -120.
            # event.num donne le numéro du bouton (4 pour haut, 5 pour bas sur Linux)
            # Sous Windows/macOS, event.delta est utilisé directement.
            if event.num == 5 or (hasattr(event, 'delta') and event.delta < 0): # Molette vers le bas
                canvas.yview_scroll(1, "units")
                # self.logger.debug("  Scrolled down 1 unit")
            elif event.num == 4 or (hasattr(event, 'delta') and event.delta > 0): # Molette vers le haut
                canvas.yview_scroll(-1, "units")
                # self.logger.debug("  Scrolled up 1 unit")
        except tk.TclError as e_scroll:
            self.logger.warning(f"Erreur TclError pendant yview_scroll sur canvas ID {id(canvas)}: {e_scroll}")
        except Exception as e_gen_scroll:
            """TODO: Add docstring."""
            self.logger.error(f"Erreur inattendue dans _on_mousewheel sur canvas ID {id(canvas)}: {e_gen_scroll}", exc_info=True)

    def _bind_mousewheel_to_children(self, widget_or_frame, canvas: tk.Canvas):
        self.logger.debug(f"Début _bind_mousewheel_to_children pour widget '{widget_or_frame.winfo_name() if hasattr(widget_or_frame, 'winfo_name') else id(widget_or_frame)}' sur canvas ID {id(canvas)}")
        if not widget_or_frame.winfo_exists() or not canvas.winfo_exists():
            self.logger.warning("  Widget ou Canvas n'existe plus dans _bind_mousewheel_to_children. Annulation.")
            return
        try:
            # Lier <Enter> et <Leave> au widget actuel pour gérer le focus pour la molette
            widget_or_frame.bind('<Enter>', lambda e, c=canvas: self._bind_mousewheel_events_for_canvas(c), add='+')
            widget_or_frame.bind('<Leave>', lambda e, c=canvas: self._unbind_mousewheel_events_for_canvas(c), add='+')

            for child in widget_or_frame.winfo_children():
                if child.winfo_exists(): # S'assurer que l'enfant existe
                    self._bind_mousewheel_to_children(child, canvas) # Appel récursif
            self.logger.debug(f"  Fin _bind_mousewheel_to_children pour '{widget_or_frame.winfo_name() if hasattr(widget_or_frame, 'winfo_name') else id(widget_or_frame)}'.")
        except Exception as e_bind_children:
            """TODO: Add docstring."""
            self.logger.error(f"  Erreur dans _bind_mousewheel_to_children pour '{widget_or_frame.winfo_name() if hasattr(widget_or_frame, 'winfo_name') else id(widget_or_frame)}': {e_bind_children}", exc_info=True)


    def _bind_mousewheel_events_for_canvas(self, canvas: tk.Canvas):
        # Note: Utiliser bind_all peut avoir des effets de bord si plusieurs canvas sont gérés.
        # Il est souvent préférable de lier directement au canvas si le focus est bien géré.
        # Cependant, pour s'assurer que ça marche même si le focus n'est pas directement sur le canvas
        # mais sur un de ses enfants, bind_all sur <Enter>/<Leave> du widget parent est une approche.
        # Pour cette fonction, on lie au canvas spécifique.
        self.logger.debug(f"Début _bind_mousewheel_events_for_canvas pour canvas ID {id(canvas)}")
        if not canvas.winfo_exists():
            self.logger.warning("  Canvas n'existe plus dans _bind_mousewheel_events_for_canvas. Annulation.")
            return
        try:
            # Lier directement au canvas. Le bind sur <Enter>/<Leave> des enfants devrait aider à diriger le focus.
            canvas.bind("<Button-4>", lambda e, c=canvas: self._on_mousewheel(e, c), add='+')
            canvas.bind("<Button-5>", lambda e, c=canvas: self._on_mousewheel(e, c), add='+')
            canvas.bind("<MouseWheel>", lambda e, c=canvas: self._on_mousewheel(e, c), add='+') # Pour Windows/macOS
            self.logger.debug(f"  Événements de molette (Button-4, Button-5, MouseWheel) liés au canvas ID {id(canvas)}.")
                """TODO: Add docstring."""
        except Exception as e_bind_canvas:
             self.logger.error(f"  Erreur lors de la liaison des événements de molette au canvas ID {id(canvas)}: {e_bind_canvas}", exc_info=True)


    def _unbind_mousewheel_events_for_canvas(self, canvas: tk.Canvas):
        self.logger.debug(f"Début _unbind_mousewheel_events_for_canvas pour canvas ID {id(canvas)}")
        if not canvas.winfo_exists():
            self.logger.warning("  Canvas n'existe plus dans _unbind_mousewheel_events_for_canvas. Annulation.")
            return
        try:
            canvas.unbind("<Button-4>")
            canvas.unbind("<Button-5>")
            canvas.unbind("<MouseWheel>")
            self.logger.debug(f"  Événements de molette (Button-4, Button-5, MouseWheel) déliés du canvas ID {id(canvas)}.")
        except Exception as e_unbind_canvas:
            self.logger.error(f"  Erreur lors du déliement des événements de molette du canvas ID {id(canvas)}: {e_unbind_canvas}", exc_info=True)

    def _setup_graphs_tab_content(self, parent_frame: ttk.Frame):
            """
            Initialise le contenu de l'onglet Graphiques.
            Crée les figures Matplotlib et les canevas TkAgg pour chaque graphique.
            """
            self.logger.info("Début de _setup_graphs_tab_content...")
            if not parent_frame or not parent_frame.winfo_exists():
                self.logger.error("  parent_frame pour les graphiques est invalide ou détruit. Arrêt de _setup_graphs_tab_content.")
                return

            # Le parent_frame est self.scrollable_graphs_frame (qui est dans un canvas scrollable)
            # Chaque graphique aura son propre Frame pour le titre et le canevas Matplotlib
            self.logger.debug(f"  parent_frame type: {type(parent_frame)}, ID: {id(parent_frame)}")

            graph_common_figsize = (7.5, 2.8) # (width, height in inches) - un peu moins haut
            graph_common_dpi = 100
            graph_title_font = self.data_font # Utiliser self.data_font ou self.small_data_font pour les titres
            graph_padding_bottom = 15 # Espace entre les graphiques
            self.logger.debug(f"  Paramètres communs des graphiques: figsize={graph_common_figsize}, dpi={graph_common_dpi}")

            # --- Graphique 1: Températures Horaires ---
            self.logger.debug("  --- Initialisation Graphique Températures ---")
            temp_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
            temp_graph_frame.pack(fill=tk.X, expand=True)
            self.logger.debug(f"    temp_graph_frame créé et packé. Parent: {parent_frame.winfo_id()}")
            ttk.Label(temp_graph_frame, text="Évolution des Températures Horaires", font=graph_title_font).pack(pady=(0,3))
            try:
                self.logger.debug("    Tentative de création de Figure pour températures...")
                self.temp_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
                self.logger.debug(f"      temp_figure créé: ID {id(self.temp_figure)}")
                self.temp_ax = self.temp_figure.add_subplot(111)
                self.logger.debug(f"      temp_ax (subplot) ajouté à temp_figure: ID {id(self.temp_ax)}")

                # Styling de base
                self.temp_ax.set_facecolor(self.root.cget('bg'))
                for spine_name, spine_obj in self.temp_ax.spines.items(): spine_obj.set_edgecolor('gray')
                self.temp_ax.tick_params(colors='gray', labelcolor='gray')
                self.logger.debug("      Styling de base de temp_ax appliqué.")

                self.temp_graph_canvas_widget = FigureCanvasTkAgg(self.temp_figure, master=temp_graph_frame)
                self.logger.debug(f"      temp_graph_canvas_widget (FigureCanvasTkAgg) créé: ID {id(self.temp_graph_canvas_widget)}")
                temp_tk_widget = self.temp_graph_canvas_widget.get_tk_widget()
                temp_tk_widget.pack(side=tk.TOP, fill=tk.X, expand=False)
                self.logger.debug(f"      Widget Tk de temp_graph_canvas_widget packé. ID: {temp_tk_widget.winfo_id()}")
                self.logger.info("  Composants pour graphique Températures initialisés avec succès.")
            except Exception as e_canvas_temp:
                self.logger.error(f"  Erreur majeure lors de la création du graphique Températures: {e_canvas_temp}", exc_info=True)
                self.temp_figure, self.temp_ax, self.temp_graph_canvas_widget = None, None, None
                self.logger.warning("  Attributs temp_figure, temp_ax, temp_graph_canvas_widget remis à None suite à erreur.")


            # --- Graphique 2: Humidité Relative Horaire ---
            self.logger.debug("  --- Initialisation Graphique Humidité ---")
            humidity_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
            humidity_graph_frame.pack(fill=tk.X, expand=True)
            self.logger.debug(f"    humidity_graph_frame créé et packé. Parent: {parent_frame.winfo_id()}")
            ttk.Label(humidity_graph_frame, text="Évolution de l'Humidité Relative Horaire", font=graph_title_font).pack(pady=(0,3))
            try:
                self.logger.debug("    Tentative de création de Figure pour humidité...")
                self.humidity_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
                self.logger.debug(f"      humidity_figure créé: ID {id(self.humidity_figure)}")
                self.humidity_ax = self.humidity_figure.add_subplot(111)
                self.logger.debug(f"      humidity_ax (subplot) ajouté à humidity_figure: ID {id(self.humidity_ax)}")

                self.humidity_ax.set_facecolor(self.root.cget('bg'))
                for spine_name, spine_obj in self.humidity_ax.spines.items(): spine_obj.set_edgecolor('gray')
                self.humidity_ax.tick_params(colors='gray', labelcolor='gray')
                self.logger.debug("      Styling de base de humidity_ax appliqué.")

                self.humidity_graph_canvas_widget = FigureCanvasTkAgg(self.humidity_figure, master=humidity_graph_frame)
                self.logger.debug(f"      humidity_graph_canvas_widget créé: ID {id(self.humidity_graph_canvas_widget)}")
                humidity_tk_widget = self.humidity_graph_canvas_widget.get_tk_widget()
                humidity_tk_widget.pack(side=tk.TOP, fill=tk.X, expand=False)
                self.logger.debug(f"      Widget Tk de humidity_graph_canvas_widget packé. ID: {humidity_tk_widget.winfo_id()}")
                self.logger.info("  Composants pour graphique Humidité initialisés avec succès.")
            except Exception as e_canvas_hum:
                self.logger.error(f"  Erreur majeure lors de la création du graphique Humidité: {e_canvas_hum}", exc_info=True)
                self.humidity_figure, self.humidity_ax, self.humidity_graph_canvas_widget = None, None, None
                self.logger.warning("  Attributs humidity_figure, humidity_ax, humidity_graph_canvas_widget remis à None suite à erreur.")


            # --- Graphique 3: Précipitations Horaires (Quantité et Probabilité) ---
            self.logger.debug("  --- Initialisation Graphique Précipitations ---")
            precip_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
            precip_graph_frame.pack(fill=tk.X, expand=True)
            self.logger.debug(f"    precip_graph_frame créé et packé. Parent: {parent_frame.winfo_id()}")
            ttk.Label(precip_graph_frame, text="Précipitations Horaires (Quantité et Probabilité)", font=graph_title_font).pack(pady=(0,3))
            try:
                self.logger.debug("    Tentative de création de Figure pour précipitations...")
                self.precip_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
                self.logger.debug(f"      precip_figure créé: ID {id(self.precip_figure)}")
                self.precip_ax_qty = self.precip_figure.add_subplot(111) # Axe pour la quantité (mm)
                self.logger.debug(f"      precip_ax_qty (subplot) ajouté à precip_figure: ID {id(self.precip_ax_qty)}")

                self.precip_ax_qty.set_facecolor(self.root.cget('bg'))
                for spine_name, spine_obj in self.precip_ax_qty.spines.items(): spine_obj.set_edgecolor('gray')
                self.precip_ax_qty.tick_params(colors='gray', labelcolor='gray')
                self.logger.debug("      Styling de base de precip_ax_qty appliqué.")

                self.precip_ax_prob = None # Sera créé avec twinx() dans la fonction de dessin
                self.logger.debug("      precip_ax_prob initialisé à None.")

                self.precip_graph_canvas_widget = FigureCanvasTkAgg(self.precip_figure, master=precip_graph_frame)
                self.logger.debug(f"      precip_graph_canvas_widget créé: ID {id(self.precip_graph_canvas_widget)}")
                precip_tk_widget = self.precip_graph_canvas_widget.get_tk_widget()
                precip_tk_widget.pack(side=tk.TOP, fill=tk.X, expand=False)
                self.logger.debug(f"      Widget Tk de precip_graph_canvas_widget packé. ID: {precip_tk_widget.winfo_id()}")
                self.logger.info("  Composants pour graphique Précipitations initialisés avec succès.")
            except Exception as e_canvas_precip:
                self.logger.error(f"  Erreur majeure lors de la création du graphique Précipitations: {e_canvas_precip}", exc_info=True)
                self.precip_figure, self.precip_ax_qty, self.precip_graph_canvas_widget = None, None, None
                self.precip_ax_prob = None
                self.logger.warning("  Attributs precip_figure, precip_ax_qty, precip_graph_canvas_widget, precip_ax_prob remis à None suite à erreur.")


            # --- Graphique 4: Vitesse du Vent Horaire ---
            self.logger.debug("  --- Initialisation Graphique Vent ---")
            wind_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
            wind_graph_frame.pack(fill=tk.X, expand=True)
            self.logger.debug(f"    wind_graph_frame créé et packé. Parent: {parent_frame.winfo_id()}")
            ttk.Label(wind_graph_frame, text="Vitesse du Vent Horaire", font=graph_title_font).pack(pady=(0,3))
            try:
                self.logger.debug("    Tentative de création de Figure pour vent...")
                self.wind_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
                self.logger.debug(f"      wind_figure créé: ID {id(self.wind_figure)}")
                self.wind_ax = self.wind_figure.add_subplot(111)
                self.logger.debug(f"      wind_ax (subplot) ajouté à wind_figure: ID {id(self.wind_ax)}")

                self.wind_ax.set_facecolor(self.root.cget('bg'))
                for spine_name, spine_obj in self.wind_ax.spines.items(): spine_obj.set_edgecolor('gray')
                self.wind_ax.tick_params(colors='gray', labelcolor='gray')
                self.logger.debug("      Styling de base de wind_ax appliqué.")

                self.wind_graph_canvas_widget = FigureCanvasTkAgg(self.wind_figure, master=wind_graph_frame)
                self.logger.debug(f"      wind_graph_canvas_widget créé: ID {id(self.wind_graph_canvas_widget)}")
                wind_tk_widget = self.wind_graph_canvas_widget.get_tk_widget()
                wind_tk_widget.pack(side=tk.TOP, fill=tk.X, expand=False)
                self.logger.debug(f"      Widget Tk de wind_graph_canvas_widget packé. ID: {wind_tk_widget.winfo_id()}")
                self.logger.info("  Composants pour graphique Vent initialisés avec succès.")
            except Exception as e_canvas_wind:
                self.logger.error(f"  Erreur majeure lors de la création du graphique Vent: {e_canvas_wind}", exc_info=True)
                self.wind_figure, self.wind_ax, self.wind_graph_canvas_widget = None, None, None
                self.logger.warning("  Attributs wind_figure, wind_ax, wind_graph_canvas_widget remis à None suite à erreur.")

            self.logger.info("Fin de _setup_graphs_tab_content (initialisation des structures des graphiques).")

    def _update_all_graphs(self, weather_data: dict):
            """
            Appelle les fonctions de mise à jour pour chaque graphique défini.
            """
            self.logger.info("Début de _update_all_graphs...") # Changé en INFO pour marquer une étape clé
            if not isinstance(weather_data, dict):
                self.logger.error("  weather_data n'est pas un dictionnaire. Arrêt de la mise à jour des graphiques.")
                return

            hourly_data = weather_data.get("hourly")
            hourly_units_data = weather_data.get("hourly_units")
            self.logger.debug(f"  Vérification des données: hourly_data est {'PRÉSENT' if hourly_data else 'ABSENT/VIDE'}, hourly_units_data est {'PRÉSENT' if hourly_units_data else 'ABSENT/VIDE'}.")

            # daily_data = weather_data.get("daily") # Pour de futurs graphiques journaliers
            # daily_units_data = weather_data.get("daily_units")

            if hourly_data and isinstance(hourly_data, dict) and \
            hourly_units_data and isinstance(hourly_units_data, dict):
                self.logger.info("  Données horaires et unités trouvées et valides, tentative de mise à jour des graphiques horaires.")

                # Graphique des Températures
                self.logger.debug("    Appel pour graphique Températures...")
                if hasattr(self, '_draw_temperature_hourly_graph') and callable(getattr(self, '_draw_temperature_hourly_graph')) :
                    try:
                        self._draw_temperature_hourly_graph(hourly_data, hourly_units_data)
                        self.logger.debug("      _draw_temperature_hourly_graph appelé.")
                    except Exception as e_draw_temp:
                        self.logger.error(f"      Erreur lors de l'appel à _draw_temperature_hourly_graph: {e_draw_temp}", exc_info=True)
                else:
                    self.logger.warning("    Méthode _draw_temperature_hourly_graph non trouvée ou non appelable.")

                # Graphique de l'Humidité
                self.logger.debug("    Appel pour graphique Humidité...")
                if hasattr(self, '_draw_humidity_hourly_graph') and callable(getattr(self, '_draw_humidity_hourly_graph')):
                    try:
                        self._draw_humidity_hourly_graph(hourly_data, hourly_units_data)
                        self.logger.debug("      _draw_humidity_hourly_graph appelé.")
                    except Exception as e_draw_hum:
                        self.logger.error(f"      Erreur lors de l'appel à _draw_humidity_hourly_graph: {e_draw_hum}", exc_info=True)
                else:
                    self.logger.warning("    Méthode _draw_humidity_hourly_graph non trouvée ou non appelable.")

                # Graphique des Précipitations
                self.logger.debug("    Appel pour graphique Précipitations...")
                if hasattr(self, '_draw_precipitation_hourly_graph') and callable(getattr(self, '_draw_precipitation_hourly_graph')):
                    try:
                        self._draw_precipitation_hourly_graph(hourly_data, hourly_units_data)
                        self.logger.debug("      _draw_precipitation_hourly_graph appelé.")
                    except Exception as e_draw_precip:
                        self.logger.error(f"      Erreur lors de l'appel à _draw_precipitation_hourly_graph: {e_draw_precip}", exc_info=True)
                else:
                    self.logger.warning("    Méthode _draw_precipitation_hourly_graph non trouvée ou non appelable.")

                # Graphique de la Vitesse du Vent
                self.logger.debug("    Appel pour graphique Vent...")
                if hasattr(self, '_draw_windspeed_hourly_graph') and callable(getattr(self, '_draw_windspeed_hourly_graph')):
                    try:
                        self._draw_windspeed_hourly_graph(hourly_data, hourly_units_data)
                        self.logger.debug("      _draw_windspeed_hourly_graph appelé.")
                    except Exception as e_draw_wind:
                        self.logger.error(f"      Erreur lors de l'appel à _draw_windspeed_hourly_graph: {e_draw_wind}", exc_info=True)
                else:
                    self.logger.warning("    Méthode _draw_windspeed_hourly_graph non trouvée ou non appelable.")

            elif hourly_data and isinstance(hourly_data, dict) and (not hourly_units_data or not isinstance(hourly_units_data, dict)):
                self.logger.warning("  Données horaires présentes mais hourly_units_data est absent, vide ou n'est pas un dictionnaire. Les graphiques pourraient manquer d'unités ou échouer.")
                # Tu pourrais décider ici de quand même appeler les fonctions de dessin en passant un dictionnaire vide pour les unités,
                # si tes fonctions de dessin sont conçues pour gérer cela (par exemple, en utilisant des unités par défaut).
                # Exemple:
                # self.logger.debug("    Tentative de dessin des graphiques avec des unités vides...")
                # if hasattr(self, '_draw_temperature_hourly_graph'): self._draw_temperature_hourly_graph(hourly_data, {})
                # ... (idem pour les autres)
                # Pour l'instant, on ne fait rien de plus, le message d'avertissement est la principale action.

            else: # hourly_data est absent, vide, ou n'est pas un dictionnaire
                self.logger.warning("  Données horaires ('hourly') absentes, vides ou invalides dans weather_data. Les graphiques horaires ne seront pas mis à jour et pourraient afficher 'Données non disponibles'.")

                # Logique pour effacer les graphiques existants ou afficher un message "Données non disponibles"
                # Cette partie est importante pour que l'utilisateur voie que quelque chose a été tenté mais a échoué faute de données.
                graphs_to_clear = {
                    "Températures": (getattr(self, 'temp_ax', None), getattr(self, 'temp_graph_canvas_widget', None)),
                    "Humidité": (getattr(self, 'humidity_ax', None), getattr(self, 'humidity_graph_canvas_widget', None)),
                    "Précipitations": (getattr(self, 'precip_ax_qty', None), getattr(self, 'precip_graph_canvas_widget', None)), # precip_ax_prob est lié à precip_ax_qty
                    "Vent": (getattr(self, 'wind_ax', None), getattr(self, 'wind_graph_canvas_widget', None)),
                }

                for name, (ax, canvas_widget) in graphs_to_clear.items():
                    if ax and hasattr(ax, 'clear') and hasattr(ax, 'text') and hasattr(ax, 'transAxes'):
                        self.logger.debug(f"    Nettoyage du graphique '{name}' et affichage 'Données non disponibles' car données horaires sources absentes.")
                        ax.clear()
                        ax.text(0.5, 0.5, "Données sources\nnon disponibles", ha='center', va='center', transform=ax.transAxes, color='gray', fontsize=9)
                        if canvas_widget and hasattr(canvas_widget, 'draw_idle'):
                            canvas_widget.draw_idle()
                    elif ax:
                        self.logger.warning(f"    L'axe pour le graphique '{name}' existe mais manque des méthodes (clear, text, transAxes) pour afficher le message d'erreur.")
                    else:
                        self.logger.debug(f"    L'axe pour le graphique '{name}' n'a pas été initialisé (attribut est None).")

            self.logger.info("Fin de _update_all_graphs.")

    def _draw_temperature_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """
        Dessine ou met à jour le graphique des températures horaires.
        """
        self.logger.info("Début _draw_temperature_hourly_graph...") # Changé en INFO pour étape clé

        # --- Vérification des arguments d'entrée ---
        if not isinstance(hourly_data, dict) or not isinstance(hourly_units, dict):
            self.logger.error(f"  Arguments invalides: hourly_data (type: {type(hourly_data)}) ou hourly_units (type: {type(hourly_units)}) ne sont pas des dictionnaires. Impossible de dessiner.")
            # On pourrait aussi afficher un message d'erreur sur le graphique ici si les axes existent
            if hasattr(self, 'temp_ax') and self.temp_ax and hasattr(self, 'temp_graph_canvas_widget') and self.temp_graph_canvas_widget:
                self.temp_ax.clear()
                self.temp_ax.text(0.5, 0.5, "Erreur: Données\ninternes invalides", ha='center', va='center', transform=self.temp_ax.transAxes, color="red", fontsize=9)
                self.temp_graph_canvas_widget.draw_idle()
            return

        # --- Vérification initiale robuste des composants du graphique ---
        self.logger.debug("  Vérification des composants Matplotlib (figure, axe, canevas)...")
        if not (hasattr(self, 'temp_figure') and self.temp_figure and \
                hasattr(self, 'temp_ax') and self.temp_ax and \
                hasattr(self, 'temp_graph_canvas_widget') and self.temp_graph_canvas_widget):
            self.logger.error("  Composants essentiels du graphique de température (figure, axe ou canevas) non initialisés ou None. Impossible de dessiner.")
            return # Ne rien faire de plus si les objets de base manquent
        self.logger.debug("    Composants Matplotlib vérifiés et présents.")

        # --- Extraction des données ---
        self.logger.debug("  Extraction des données depuis hourly_data et hourly_units...")
        times_str = hourly_data.get("time", [])
        temps_2m = hourly_data.get("temperature_2m", [])
        temps_apparent = hourly_data.get("apparent_temperature", [])
        temp_unit = hourly_units.get("temperature_2m", "°C") # Fallback à °C si non spécifié

        self.logger.debug(f"    Données extraites: times_str (len={len(times_str)}), temps_2m (len={len(temps_2m)}), temps_apparent (len={len(temps_apparent)}), temp_unit='{temp_unit}'")
        if times_str: self.logger.debug(f"      Exemple times_str[0]: {times_str[0] if times_str else 'N/A'}")
        if temps_2m: self.logger.debug(f"      Exemple temps_2m[0]: {temps_2m[0] if temps_2m else 'N/A'}")


        # --- Condition pour "Données non disponibles" ---
        # Vérifier si times_str est vide OU si les deux listes de températures sont vides ou ne contiennent que des None
        no_valid_times = not times_str
        no_valid_temps_2m = not (temps_2m and any(t is not None for t in temps_2m))
        no_valid_temps_apparent = not (temps_apparent and any(t is not None for t in temps_apparent))

        if no_valid_times or (no_valid_temps_2m and no_valid_temps_apparent):
            self.logger.warning("  Données de temps ou de température valides manquantes pour le graphique des températures. Affichage 'Données non disponibles'.")
            self.logger.debug(f"    Détails: no_valid_times={no_valid_times}, no_valid_temps_2m={no_valid_temps_2m}, no_valid_temps_apparent={no_valid_temps_apparent}")
            try:
                self.temp_ax.clear()
                self.temp_ax.text(0.5, 0.5, "Données de température\nnon disponibles",
                                  ha='center', va='center',
                                  transform=self.temp_ax.transAxes, color="gray", fontsize=9)
                self.temp_graph_canvas_widget.draw_idle()
                self.logger.debug("    Message 'Données non disponibles' affiché sur le graphique des températures.")
            except Exception as e_text:
                 self.logger.error(f"    Erreur lors de l'affichage du message 'Données non disponibles' sur temp_ax: {e_text}", exc_info=True)
            return

        # --- Bloc principal de dessin ---
        try:
            self.logger.info("  Début du dessin du graphique des températures...") # Changé en INFO
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            self.logger.debug(f"    Nombre d'heures à tracer (num_hours_to_plot): {num_hours_to_plot}")

            # Conversion des dates/heures
            self.logger.debug("    Conversion des chaînes de temps en objets datetime...")
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            self.logger.debug(f"      Conversion des temps terminée. {len(times_dt)} objets datetime créés.")

            # Préparation des listes de données pour le tracé
            temps_2m_plot = temps_2m[:num_hours_to_plot] if temps_2m else [None] * num_hours_to_plot
            temps_apparent_plot = temps_apparent[:num_hours_to_plot] if temps_apparent else [None] * num_hours_to_plot
            self.logger.debug(f"    Données de tracé prêtes: temps_2m_plot (len={len(temps_2m_plot)}), temps_apparent_plot (len={len(temps_apparent_plot)})")

            self.temp_ax.clear()
            self.logger.debug("    Axe des températures (temp_ax) nettoyé avec clear().")

            self.temp_ax.set_title("Évolution Horaire des Températures", color="gray", fontsize=10)
            self.logger.debug("    Titre du graphique défini.")

            plot_made = False
            # Tracé de la température réelle
            if any(t is not None for t in temps_2m_plot):
                self.logger.debug("    Tracé de la courbe 'Température'...")
                self.temp_ax.plot(times_dt, temps_2m_plot, label=f"Température ({temp_unit})", color="#3498db", marker='o', markersize=4, linestyle='-')
                plot_made = True
                self.logger.debug("      Courbe 'Température' tracée.")
            else:
                self.logger.debug("    Aucune donnée valide pour la courbe 'Température'.")

            # Tracé de la température ressentie
            if any(t is not None for t in temps_apparent_plot):
                self.logger.debug("    Tracé de la courbe 'Ressentie'...")
                self.temp_ax.plot(times_dt, temps_apparent_plot, label=f"Ressentie ({temp_unit})", color="#e74c3c", marker='x', markersize=5, linestyle='--')
                plot_made = True
                self.logger.debug("      Courbe 'Ressentie' tracée.")
            else:
                self.logger.debug("    Aucune donnée valide pour la courbe 'Ressentie'.")

            # Configuration de l'axe X (temps)
            self.logger.debug("    Configuration de l'axe X (formateur et localisateur)...")
            self.temp_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.temp_ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8 if num_hours_to_plot > 0 else 1))) # Eviter division par zero
            if hasattr(self, 'temp_figure') and self.temp_figure: # Vérifier si temp_figure existe
                 self.temp_figure.autofmt_xdate(rotation=30, ha='right')
                 self.logger.debug("      autofmt_xdate appliqué.")
            else:
                 self.logger.warning("      self.temp_figure non trouvé, autofmt_xdate non appliqué.")


            # Configuration de l'axe Y et de la légende
            self.temp_ax.set_ylabel(f"Température ({temp_unit})", color="gray")
            if plot_made:
                 self.temp_ax.legend(loc='best', fontsize='x-small', frameon=False, labelcolor='gray')
                 self.logger.debug("    Légende du graphique ajoutée.")
            else:
                self.logger.debug("    Aucun tracé effectué (plot_made=False), légende non ajoutée.")

            self.temp_ax.grid(True, linestyle=':', linewidth=0.5, color='gray')
            self.logger.debug("    Grille du graphique ajoutée.")

            # Styling final des axes
            self.temp_ax.set_facecolor(self.root.cget('bg')) # Couleur de fond de l'application
            self.temp_ax.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            self.temp_ax.tick_params(axis='y', colors='gray', labelcolor='gray', labelsize='small')
            for spine_name, spine_obj in self.temp_ax.spines.items():
                spine_obj.set_edgecolor('gray')
            self.logger.debug("    Styling final des axes (couleur de fond, graduations, bords) appliqué.")

            self.temp_graph_canvas_widget.draw_idle()
            self.logger.info("Graphique des températures mis à jour et redessiné avec succès.")

        except ValueError as e_val:
            self.logger.error(f"  Erreur de valeur lors du dessin du graphique des températures (probablement conversion de date/heure): {e_val}", exc_info=True)
            if hasattr(self, 'temp_ax') and self.temp_ax:
                self.temp_ax.clear()
                self.temp_ax.text(0.5, 0.5, "Erreur: Format\ndonnées invalide", ha='center', va='center', transform=self.temp_ax.transAxes, color="red", fontsize=9)
            if hasattr(self, 'temp_graph_canvas_widget') and self.temp_graph_canvas_widget: self.temp_graph_canvas_widget.draw_idle()
        except Exception as e_graph:
            self.logger.error(f"  Erreur inattendue lors du dessin du graphique des températures: {e_graph}", exc_info=True)
            if hasattr(self, 'temp_ax') and self.temp_ax:
                self.temp_ax.clear()
                self.temp_ax.text(0.5, 0.5, "Erreur génération\ngraphique", ha='center', va='center', transform=self.temp_ax.transAxes, color="red", fontsize=9)
            if hasattr(self, 'temp_graph_canvas_widget') and self.temp_graph_canvas_widget:
                self.temp_graph_canvas_widget.draw_idle()
            else: # Ce cas ne devrait pas arriver si la vérification initiale est passée
                self.logger.warning("    _draw_temperature_hourly_graph (dans except Exception): temp_graph_canvas_widget non disponible pour draw_idle.")
        self.logger.info("Fin _draw_temperature_hourly_graph.")

    def _draw_humidity_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """Dessine ou met à jour le graphique de l'humidité relative horaire."""
        self.logger.info("Début _draw_humidity_hourly_graph...") # Changé en INFO

        # --- Vérification des arguments d'entrée ---
        if not isinstance(hourly_data, dict) or not isinstance(hourly_units, dict):
            self.logger.error(f"  Arguments invalides: hourly_data (type: {type(hourly_data)}) ou hourly_units (type: {type(hourly_units)}) ne sont pas des dictionnaires. Impossible de dessiner.")
            if hasattr(self, 'humidity_ax') and self.humidity_ax and hasattr(self, 'humidity_graph_canvas_widget') and self.humidity_graph_canvas_widget:
                self.humidity_ax.clear()
                self.humidity_ax.text(0.5, 0.5, "Erreur: Données\ninternes invalides", ha='center', va='center', transform=self.humidity_ax.transAxes, color="red", fontsize=9)
                self.humidity_graph_canvas_widget.draw_idle()
            return

        # --- Vérification initiale robuste des composants du graphique ---
        self.logger.debug("  Vérification des composants Matplotlib (figure, axe, canevas)...")
        if not (hasattr(self, 'humidity_figure') and self.humidity_figure and \
                hasattr(self, 'humidity_ax') and self.humidity_ax and \
                hasattr(self, 'humidity_graph_canvas_widget') and self.humidity_graph_canvas_widget):
            self.logger.error("  Composants essentiels du graphique d'humidité (figure, axe ou canevas) non initialisés ou None. Impossible de dessiner.")
            return
        self.logger.debug("    Composants Matplotlib pour humidité vérifiés et présents.")

        # --- Extraction des données ---
        self.logger.debug("  Extraction des données d'humidité depuis hourly_data et hourly_units...")
        times_str = hourly_data.get("time", [])
        humidity_values = hourly_data.get("relativehumidity_2m", [])
        humidity_unit = hourly_units.get("relativehumidity_2m", "%") # Fallback à %

        self.logger.debug(f"    Données extraites: times_str (len={len(times_str)}), humidity_values (len={len(humidity_values)}), humidity_unit='{humidity_unit}'")
        if times_str: self.logger.debug(f"      Exemple times_str[0]: {times_str[0] if times_str else 'N/A'}")
        if humidity_values: self.logger.debug(f"      Exemple humidity_values[0]: {humidity_values[0] if humidity_values else 'N/A'}")

        # --- Condition pour "Données non disponibles" ---
        no_valid_times_hum = not times_str
        no_valid_humidity_values = not (humidity_values and any(h is not None for h in humidity_values))

        if no_valid_times_hum or no_valid_humidity_values:
            self.logger.warning("  Données de temps ou d'humidité valides manquantes pour le graphique d'humidité. Affichage 'Données non disponibles'.")
            self.logger.debug(f"    Détails: no_valid_times_hum={no_valid_times_hum}, no_valid_humidity_values={no_valid_humidity_values}")
            try:
                self.humidity_ax.clear()
                self.humidity_ax.text(0.5, 0.5, "Données d'humidité\nnon disponibles",
                                      ha='center', va='center', transform=self.humidity_ax.transAxes, color="gray", fontsize=9)
                self.humidity_graph_canvas_widget.draw_idle()
                self.logger.debug("    Message 'Données non disponibles' affiché sur le graphique d'humidité.")
            except Exception as e_text_hum:
                self.logger.error(f"    Erreur lors de l'affichage du message 'Données non disponibles' sur humidity_ax: {e_text_hum}", exc_info=True)
            return

        # --- Bloc principal de dessin ---
        try:
            self.logger.info("  Début du dessin du graphique d'humidité...") # Changé en INFO
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            self.logger.debug(f"    Nombre d'heures à tracer (num_hours_to_plot): {num_hours_to_plot}")

            self.logger.debug("    Conversion des chaînes de temps en objets datetime...")
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            self.logger.debug(f"      Conversion des temps terminée. {len(times_dt)} objets datetime créés.")

            humidity_plot = humidity_values[:num_hours_to_plot] if humidity_values else [None] * num_hours_to_plot
            self.logger.debug(f"    Données de tracé prêtes: humidity_plot (len={len(humidity_plot)})")

            self.humidity_ax.clear()
            self.logger.debug("    Axe d'humidité (humidity_ax) nettoyé avec clear().")
            self.humidity_ax.set_title("Humidité Relative Horaire", color="gray", fontsize=10)
            self.logger.debug("    Titre du graphique d'humidité défini.")

            plot_made_humidity = False
            if any(h is not None for h in humidity_plot): # S'assurer qu'il y a au moins une valeur non-None à tracer
                self.logger.debug("    Tracé de la courbe 'Humidité'...")
                self.humidity_ax.plot(times_dt, humidity_plot, label=f"Humidité ({humidity_unit})", color="#27ae60", marker='.', markersize=5, linestyle='-')
                plot_made_humidity = True
                self.logger.debug("      Courbe 'Humidité' tracée.")
            else:
                self.logger.debug("    Aucune donnée valide pour la courbe 'Humidité'.")

            self.logger.debug("    Configuration de l'axe X (formateur et localisateur)...")
            self.humidity_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.humidity_ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8 if num_hours_to_plot > 0 else 1)))
            if hasattr(self, 'humidity_figure') and self.humidity_figure:
                 self.humidity_figure.autofmt_xdate(rotation=30, ha='right')
                 self.logger.debug("      autofmt_xdate appliqué pour humidité.")
            else:
                 self.logger.warning("      self.humidity_figure non trouvé, autofmt_xdate non appliqué.")

            self.humidity_ax.set_ylabel(f"Humidité ({humidity_unit})", color="gray")
            if plot_made_humidity:
                self.humidity_ax.legend(loc='best', fontsize='x-small', frameon=False, labelcolor='gray')
                self.logger.debug("    Légende du graphique d'humidité ajoutée.")
            else:
                self.logger.debug("    Aucun tracé effectué (plot_made_humidity=False), légende non ajoutée.")

            self.humidity_ax.grid(True, linestyle=':', linewidth=0.5, color='gray')
            self.logger.debug("    Grille du graphique d'humidité ajoutée.")

            self.humidity_ax.set_facecolor(self.root.cget('bg'))
            self.humidity_ax.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            self.humidity_ax.tick_params(axis='y', colors='gray', labelcolor='gray', labelsize='small')
            for spine_name, spine_obj in self.humidity_ax.spines.items():
                spine_obj.set_edgecolor('gray')
            self.logger.debug("    Styling final des axes d'humidité appliqué.")

            self.humidity_graph_canvas_widget.draw_idle()
            self.logger.info("Graphique d'humidité mis à jour et redessiné avec succès.")

        except ValueError as e_val_hum:
            self.logger.error(f"  Erreur de valeur lors du dessin du graphique d'humidité (probablement conversion de date/heure): {e_val_hum}", exc_info=True)
            if hasattr(self, 'humidity_ax') and self.humidity_ax:
                self.humidity_ax.clear()
                self.humidity_ax.text(0.5, 0.5, "Erreur: Format\ndonnées invalide", ha='center', va='center', transform=self.humidity_ax.transAxes, color="red", fontsize=9)
            if hasattr(self, 'humidity_graph_canvas_widget') and self.humidity_graph_canvas_widget: self.humidity_graph_canvas_widget.draw_idle()
        except Exception as e_graph_hum:
            self.logger.error(f"  Erreur inattendue lors du dessin du graphique d'humidité: {e_graph_hum}", exc_info=True)
            if hasattr(self, 'humidity_ax') and self.humidity_ax:
                self.humidity_ax.clear()
                self.humidity_ax.text(0.5, 0.5, "Erreur génération\ngraphique", ha='center', va='center', transform=self.humidity_ax.transAxes, color="red", fontsize=9)
            if hasattr(self, 'humidity_graph_canvas_widget') and self.humidity_graph_canvas_widget:
                self.humidity_graph_canvas_widget.draw_idle()
            else:
                self.logger.warning("    _draw_humidity_hourly_graph (dans except Exception): humidity_graph_canvas_widget non disponible pour draw_idle.")
        self.logger.info("Fin _draw_humidity_hourly_graph.")


    def _draw_precipitation_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """Dessine ou met à jour le graphique des précipitations horaires (quantité et probabilité)."""
        self.logger.info("Début _draw_precipitation_hourly_graph...") # Changé en INFO

        # --- Vérification des arguments d'entrée ---
        if not isinstance(hourly_data, dict) or not isinstance(hourly_units, dict):
            self.logger.error(f"  Arguments invalides: hourly_data (type: {type(hourly_data)}) ou hourly_units (type: {type(hourly_units)}) ne sont pas des dictionnaires. Impossible de dessiner.")
            if hasattr(self, 'precip_ax_qty') and self.precip_ax_qty and hasattr(self, 'precip_graph_canvas_widget') and self.precip_graph_canvas_widget:
                self.precip_ax_qty.clear()
                if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: self.precip_ax_prob.clear()
                self.precip_ax_qty.text(0.5, 0.5, "Erreur: Données\ninternes invalides", ha='center', va='center', transform=self.precip_ax_qty.transAxes, color="red", fontsize=9)
                self.precip_graph_canvas_widget.draw_idle()
            return

        # --- Vérification initiale robuste des composants du graphique ---
        self.logger.debug("  Vérification des composants Matplotlib (figure, axe principal, canevas)...")
        if not (hasattr(self, 'precip_figure') and self.precip_figure and \
                hasattr(self, 'precip_ax_qty') and self.precip_ax_qty and \
                hasattr(self, 'precip_graph_canvas_widget') and self.precip_graph_canvas_widget):
            self.logger.error("  Composants essentiels du graphique de précipitations (figure, axe principal precip_ax_qty ou canevas) non initialisés ou None. Impossible de dessiner.")
            return
        self.logger.debug("    Composants Matplotlib pour précipitations (base) vérifiés et présents.")

        # --- Extraction des données ---
        self.logger.debug("  Extraction des données de précipitation depuis hourly_data et hourly_units...")
        times_str = hourly_data.get("time", [])
        precip_qty_values = hourly_data.get("precipitation", [])
        precip_prob_values = hourly_data.get("precipitation_probability", [])
        qty_unit = hourly_units.get("precipitation", "mm")
        prob_unit = hourly_units.get("precipitation_probability", "%")

        self.logger.debug(f"    Données extraites: times_str (len={len(times_str)}), precip_qty_values (len={len(precip_qty_values)}), precip_prob_values (len={len(precip_prob_values)}), qty_unit='{qty_unit}', prob_unit='{prob_unit}'")
        if times_str: self.logger.debug(f"      Exemple times_str[0]: {times_str[0] if times_str else 'N/A'}")
        if precip_qty_values: self.logger.debug(f"      Exemple precip_qty_values[0]: {precip_qty_values[0] if precip_qty_values else 'N/A'}")
        if precip_prob_values: self.logger.debug(f"      Exemple precip_prob_values[0]: {precip_prob_values[0] if precip_prob_values else 'N/A'}")

        # --- Condition pour "Données non disponibles" ---
        no_valid_times_precip = not times_str
        no_valid_precip_qty = not (precip_qty_values and any(p is not None for p in precip_qty_values))
        no_valid_precip_prob = not (precip_prob_values and any(p is not None for p in precip_prob_values))

        if no_valid_times_precip or (no_valid_precip_qty and no_valid_precip_prob): # Si temps manque OU (quantité ET probabilité manquent)
            self.logger.warning("  Données de temps ou de précipitation (quantité ET probabilité) valides manquantes. Affichage 'Données non disponibles'.")
            self.logger.debug(f"    Détails: no_valid_times_precip={no_valid_times_precip}, no_valid_precip_qty={no_valid_precip_qty}, no_valid_precip_prob={no_valid_precip_prob}")
            try:
                self.precip_ax_qty.clear()
                if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: self.precip_ax_prob.clear()
                self.precip_ax_qty.text(0.5, 0.5, "Données de précipitation\nnon disponibles",
                                        ha='center', va='center', transform=self.precip_ax_qty.transAxes, color="gray", fontsize=9)
                self.precip_graph_canvas_widget.draw_idle()
                self.logger.debug("    Message 'Données non disponibles' affiché sur le graphique des précipitations.")
            except Exception as e_text_precip:
                self.logger.error(f"    Erreur lors de l'affichage du message 'Données non disponibles' sur precip_ax_qty: {e_text_precip}", exc_info=True)
            return

        # --- Bloc principal de dessin ---
        try:
            self.logger.info("  Début du dessin du graphique des précipitations...") # Changé en INFO
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            self.logger.debug(f"    Nombre d'heures à tracer (num_hours_to_plot): {num_hours_to_plot}")

            self.logger.debug("    Conversion des chaînes de temps en objets datetime...")
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            self.logger.debug(f"      Conversion des temps terminée. {len(times_dt)} objets datetime créés.")

            precip_qty_plot = precip_qty_values[:num_hours_to_plot] if precip_qty_values else [None] * num_hours_to_plot
            precip_prob_plot = precip_prob_values[:num_hours_to_plot] if precip_prob_values else [None] * num_hours_to_plot
            self.logger.debug(f"    Données de tracé prêtes: precip_qty_plot (len={len(precip_qty_plot)}), precip_prob_plot (len={len(precip_prob_plot)})")

            self.precip_ax_qty.clear()
            self.logger.debug("    Axe principal precip_ax_qty nettoyé.")

            # Gestion de precip_ax_prob (axe Y secondaire)
            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob:
                self.precip_ax_prob.clear()
                self.logger.debug("    Axe secondaire precip_ax_prob nettoyé.")
            else:
                if hasattr(self, 'precip_ax_qty') and self.precip_ax_qty: # S'assurer que l'axe principal existe
                    self.precip_ax_prob = self.precip_ax_qty.twinx() # Crée un nouvel axe Y partageant le même axe X
                    self.logger.info("    Axe secondaire precip_ax_prob créé avec twinx().")
                else: # Ne devrait pas arriver si la vérification initiale est passée
                    self.logger.error("    Erreur critique: precip_ax_qty est None, impossible de créer precip_ax_prob. Arrêt du dessin pour ce graphique.")
                    return # Important d'arrêter ici pour éviter d'autres erreurs

            self.precip_ax_qty.set_title("Précipitations Horaires", color="gray", fontsize=10)
            self.logger.debug("    Titre du graphique des précipitations défini.")

            # Tracé de la quantité de précipitation (barres)
            color_qty = "#5dade2"; plot_made_qty = False
            if any(p is not None and p > 0 for p in precip_qty_plot): # Ne tracer que s'il y a des valeurs positives
                 self.logger.debug("    Tracé des barres pour 'Quantité Précipitation'...")
                 # Ajustement dynamique de la largeur des barres
                 bar_width_factor = 0.03 # Facteur de base
                 # L'intervalle entre les ticks de l'axe X peut donner une idée de la densité
                 # Ceci est une heuristique et pourrait nécessiter des ajustements
                 num_major_ticks_x = len(self.precip_ax_qty.get_xticks())
                 dynamic_width = bar_width_factor * (num_hours_to_plot / max(1, num_major_ticks_x) / HOURLY_FORECAST_HOURS * 24) if num_major_ticks_x > 0 else bar_width_factor
                 self.precip_ax_qty.bar(times_dt, precip_qty_plot, width=max(0.01, dynamic_width), label=f"Quantité ({qty_unit})", color=color_qty, alpha=0.7)
                 plot_made_qty = True
                 self.logger.debug(f"      Barres 'Quantité Précipitation' tracées avec largeur dynamique approx: {dynamic_width:.3f}")
            else:
                self.logger.debug("    Aucune donnée de quantité de précipitation positive à tracer.")
            self.precip_ax_qty.set_ylabel(f"Quantité ({qty_unit})", color=color_qty)
            self.precip_ax_qty.tick_params(axis='y', labelcolor=color_qty, colors='gray', labelsize='small')
            if hasattr(self.precip_ax_qty, 'spines'): self.precip_ax_qty.spines['left'].set_color(color_qty)


            # Tracé de la probabilité de précipitation (ligne)
            color_prob = "#f1c40f"; plot_made_prob = False
            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: # Vérifier à nouveau avant d'utiliser
                if any(p is not None for p in precip_prob_plot):
                    self.logger.debug("    Tracé de la ligne pour 'Probabilité Précipitation'...")
                    self.precip_ax_prob.plot(times_dt, precip_prob_plot, label=f"Probabilité ({prob_unit})", color=color_prob, marker='.', markersize=4, linestyle='--')
                    plot_made_prob = True
                    self.logger.debug("      Ligne 'Probabilité Précipitation' tracée.")
                else:
                    self.logger.debug("    Aucune donnée valide pour la courbe 'Probabilité Précipitation'.")
                self.precip_ax_prob.set_ylabel(f"Probabilité ({prob_unit})", color=color_prob)
                self.precip_ax_prob.tick_params(axis='y', labelcolor=color_prob, colors='gray', labelsize='small')
                if hasattr(self.precip_ax_prob, 'spines'): self.precip_ax_prob.spines['right'].set_color(color_prob)
                self.precip_ax_prob.set_ylim(0, 105) # Probabilité de 0 à 100%
            else:
                 self.logger.warning("    precip_ax_prob non disponible pour le tracé de probabilité (ne devrait pas arriver si créé ci-dessus).")

            self.logger.debug("    Configuration de l'axe X (formateur et localisateur)...")
            self.precip_ax_qty.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.precip_ax_qty.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8 if num_hours_to_plot > 0 else 1)))
            if hasattr(self, 'precip_figure') and self.precip_figure:
                self.precip_figure.autofmt_xdate(rotation=30, ha='right')
                self.logger.debug("      autofmt_xdate appliqué pour précipitations.")
            else:
                self.logger.warning("      self.precip_figure non trouvé, autofmt_xdate non appliqué.")

            # Gestion de la légende combinée
            lines_qty, labels_qty = self.precip_ax_qty.get_legend_handles_labels()
            lines_prob, labels_prob = [], []
            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob:
                lines_prob, labels_prob = self.precip_ax_prob.get_legend_handles_labels()

            if plot_made_qty or plot_made_prob:
                self.precip_ax_qty.legend(lines_qty + lines_prob, labels_qty + labels_prob, loc='upper left', fontsize='x-small', frameon=False, labelcolor='gray')
                self.logger.debug("    Légende combinée du graphique des précipitations ajoutée.")
            else:
                self.logger.debug("    Aucun tracé effectué (quantité ou probabilité), légende non ajoutée.")

            self.precip_ax_qty.grid(True, linestyle=':', linewidth=0.5, color='gray', axis='x') # Grille seulement sur l'axe X pour l'axe principal
            self.logger.debug("    Grille X du graphique des précipitations ajoutée.")

            # Styling final des axes
            self.precip_ax_qty.set_facecolor(self.root.cget('bg'))
            if hasattr(self.precip_ax_qty, 'patch'): self.precip_ax_qty.patch.set_alpha(0.0) # Rendre le fond de l'axe principal transparent

            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob:
                self.precip_ax_prob.set_facecolor(self.root.cget('bg')) # Même couleur de fond
                if hasattr(self.precip_ax_prob, 'patch'): self.precip_ax_prob.patch.set_alpha(0.0) # Rendre le fond de l'axe secondaire transparent
                # Cacher les spines inutiles de l'axe secondaire
                if hasattr(self.precip_ax_prob, 'spines'):
                    for s_name in ['bottom', 'top', 'left']: self.precip_ax_prob.spines[s_name].set_visible(False)
                    self.precip_ax_prob.spines['right'].set_edgecolor('gray') # S'assurer que la couleur est appliquée

            self.precip_ax_qty.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            # S'assurer que les spines de l'axe principal sont correctement colorés
            if hasattr(self.precip_ax_qty, 'spines'):
                for s_name in ['bottom', 'top', 'right']: self.precip_ax_qty.spines[s_name].set_edgecolor('gray')
                self.precip_ax_qty.spines['left'].set_edgecolor(color_qty) # La couleur de l'axe Y de la quantité

            self.logger.debug("    Styling final des axes de précipitation appliqué.")

            self.precip_graph_canvas_widget.draw_idle()
            self.logger.info("Graphique des précipitations mis à jour et redessiné avec succès.")

        except ValueError as e_val_precip:
            self.logger.error(f"  Erreur de valeur lors du dessin du graphique des précipitations (probablement conversion de date/heure): {e_val_precip}", exc_info=True)
            if hasattr(self, 'precip_ax_qty') and self.precip_ax_qty:
                self.precip_ax_qty.clear();
                if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: self.precip_ax_prob.clear()
                self.precip_ax_qty.text(0.5, 0.5, "Erreur: Format\ndonnées invalide", ha='center', va='center', transform=self.precip_ax_qty.transAxes, color="red", fontsize=9)
            if hasattr(self, 'precip_graph_canvas_widget') and self.precip_graph_canvas_widget: self.precip_graph_canvas_widget.draw_idle()
        except Exception as e_graph_precip:
            self.logger.error(f"  Erreur inattendue lors du dessin du graphique des précipitations: {e_graph_precip}", exc_info=True)
            if hasattr(self, 'precip_ax_qty') and self.precip_ax_qty:
                self.precip_ax_qty.clear();
                if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: self.precip_ax_prob.clear()
                self.precip_ax_qty.text(0.5, 0.5, "Erreur génération\ngraphique", ha='center', va='center', transform=self.precip_ax_qty.transAxes, color="red", fontsize=9)
            if hasattr(self, 'precip_graph_canvas_widget') and self.precip_graph_canvas_widget:
                self.precip_graph_canvas_widget.draw_idle()
            else:
                self.logger.warning("    _draw_precipitation_hourly_graph (dans except Exception): precip_graph_canvas_widget non disponible pour draw_idle.")
        self.logger.info("Fin _draw_precipitation_hourly_graph.")


    def _draw_windspeed_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """Dessine ou met à jour le graphique de la vitesse du vent horaire."""
        self.logger.info("Début _draw_windspeed_hourly_graph...") # Changé en INFO

        # --- Vérification des arguments d'entrée ---
        if not isinstance(hourly_data, dict) or not isinstance(hourly_units, dict):
            self.logger.error(f"  Arguments invalides: hourly_data (type: {type(hourly_data)}) ou hourly_units (type: {type(hourly_units)}) ne sont pas des dictionnaires. Impossible de dessiner.")
            if hasattr(self, 'wind_ax') and self.wind_ax and hasattr(self, 'wind_graph_canvas_widget') and self.wind_graph_canvas_widget:
                self.wind_ax.clear()
                self.wind_ax.text(0.5, 0.5, "Erreur: Données\ninternes invalides", ha='center', va='center', transform=self.wind_ax.transAxes, color="red", fontsize=9)
                self.wind_graph_canvas_widget.draw_idle()
            return

        # --- Vérification initiale robuste des composants du graphique ---
        self.logger.debug("  Vérification des composants Matplotlib (figure, axe, canevas)...")
        if not (hasattr(self, 'wind_figure') and self.wind_figure and \
                hasattr(self, 'wind_ax') and self.wind_ax and \
                hasattr(self, 'wind_graph_canvas_widget') and self.wind_graph_canvas_widget):
            self.logger.error("  Composants essentiels du graphique de vent (figure, axe ou canevas) non initialisés ou None. Impossible de dessiner.")
            return
        self.logger.debug("    Composants Matplotlib pour vent vérifiés et présents.")

        # --- Extraction des données ---
        self.logger.debug("  Extraction des données de vent depuis hourly_data et hourly_units...")
        times_str = hourly_data.get("time", [])
        windspeed_values = hourly_data.get("windspeed_10m", [])
        windgusts_values = hourly_data.get("windgusts_10m", []) # Pour l'affichage optionnel des rafales
        wind_unit = hourly_units.get("windspeed_10m", "km/h") # Unité pour vitesse et rafales

        self.logger.debug(f"    Données extraites: times_str (len={len(times_str)}), windspeed_values (len={len(windspeed_values)}), windgusts_values (len={len(windgusts_values)}), wind_unit='{wind_unit}'")
        if times_str: self.logger.debug(f"      Exemple times_str[0]: {times_str[0] if times_str else 'N/A'}")
        if windspeed_values: self.logger.debug(f"      Exemple windspeed_values[0]: {windspeed_values[0] if windspeed_values else 'N/A'}")


        # --- Condition pour "Données non disponibles" ---
        # On vérifie seulement la vitesse du vent pour cette condition principale. Les rafales sont optionnelles.
        no_valid_times_wind = not times_str
        no_valid_windspeed = not (windspeed_values and any(w is not None for w in windspeed_values))

        if no_valid_times_wind or no_valid_windspeed:
            self.logger.warning("  Données de temps ou de vitesse du vent valides manquantes pour le graphique de vent. Affichage 'Données non disponibles'.")
            self.logger.debug(f"    Détails: no_valid_times_wind={no_valid_times_wind}, no_valid_windspeed={no_valid_windspeed}")
            try:
                self.wind_ax.clear()
                self.wind_ax.text(0.5, 0.5, "Données de vent\nnon disponibles",
                                  ha='center', va='center', transform=self.wind_ax.transAxes, color="gray", fontsize=9)
                self.wind_graph_canvas_widget.draw_idle()
                self.logger.debug("    Message 'Données non disponibles' affiché sur le graphique de vent.")
            except Exception as e_text_wind:
                self.logger.error(f"    Erreur lors de l'affichage du message 'Données non disponibles' sur wind_ax: {e_text_wind}", exc_info=True)
            return

        # --- Bloc principal de dessin ---
        try:
            self.logger.info("  Début du dessin du graphique de la vitesse du vent...") # Changé en INFO
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            self.logger.debug(f"    Nombre d'heures à tracer (num_hours_to_plot): {num_hours_to_plot}")

            self.logger.debug("    Conversion des chaînes de temps en objets datetime...")
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            self.logger.debug(f"      Conversion des temps terminée. {len(times_dt)} objets datetime créés.")

            windspeed_plot = windspeed_values[:num_hours_to_plot] if windspeed_values else [None] * num_hours_to_plot
            windgusts_plot = windgusts_values[:num_hours_to_plot] if windgusts_values else [None] * num_hours_to_plot # Préparer même si non utilisé
            self.logger.debug(f"    Données de tracé prêtes: windspeed_plot (len={len(windspeed_plot)}), windgusts_plot (len={len(windgusts_plot)})")

            self.wind_ax.clear()
            self.logger.debug("    Axe du vent (wind_ax) nettoyé avec clear().")
            self.wind_ax.set_title("Vitesse du Vent Horaire", color="gray", fontsize=10)
            self.logger.debug("    Titre du graphique de vent défini.")

            plot_made_wind = False
            # Tracé de la vitesse du vent
            if any(w is not None for w in windspeed_plot):
                self.logger.debug("    Tracé de la courbe 'Vitesse Vent'...")
                self.wind_ax.plot(times_dt, windspeed_plot, label=f"Vitesse Vent ({wind_unit})", color="#8e44ad", marker='^', markersize=4, linestyle='-')
                plot_made_wind = True
                self.logger.debug("      Courbe 'Vitesse Vent' tracée.")
            else:
                self.logger.debug("    Aucune donnée valide pour la courbe 'Vitesse Vent'.")

            # Optionnel: Afficher les rafales
            if any(g is not None for g in windgusts_plot):
                self.logger.debug("    Tracé de la courbe 'Rafales'...")
                self.wind_ax.plot(times_dt, windgusts_plot, label=f"Rafales ({wind_unit})", color="#c0392b", linestyle=':', alpha=0.7, markersize=3, marker='x')
                plot_made_wind = True # S'assurer que la légende s'affiche si on a les rafales
                self.logger.debug("      Courbe 'Rafales' tracée.")
            else:
                self.logger.debug("    Aucune donnée valide pour la courbe 'Rafales' (ou non demandée).")


            self.logger.debug("    Configuration de l'axe X (formateur et localisateur)...")
            self.wind_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.wind_ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8 if num_hours_to_plot > 0 else 1)))
            if hasattr(self, 'wind_figure') and self.wind_figure:
                 self.wind_figure.autofmt_xdate(rotation=30, ha='right')
                 self.logger.debug("      autofmt_xdate appliqué pour vent.")
            else:
                 self.logger.warning("      self.wind_figure non trouvé, autofmt_xdate non appliqué.")

            self.wind_ax.set_ylabel(f"Vitesse ({wind_unit})", color="gray")
            if plot_made_wind:
                self.wind_ax.legend(loc='best', fontsize='x-small', frameon=False, labelcolor='gray')
                self.logger.debug("    Légende du graphique de vent ajoutée.")
            else:
                self.logger.debug("    Aucun tracé effectué (plot_made_wind=False), légende non ajoutée.")

            self.wind_ax.grid(True, linestyle=':', linewidth=0.5, color='gray')
            self.logger.debug("    Grille du graphique de vent ajoutée.")

            self.wind_ax.set_facecolor(self.root.cget('bg'))
            self.wind_ax.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            self.wind_ax.tick_params(axis='y', colors='gray', labelcolor='gray', labelsize='small')
            for spine_name, spine_obj in self.wind_ax.spines.items():
                spine_obj.set_edgecolor('gray')
            self.logger.debug("    Styling final des axes de vent appliqué.")

            self.wind_graph_canvas_widget.draw_idle()
            self.logger.info("Graphique de la vitesse du vent mis à jour et redessiné avec succès.")

        except ValueError as e_val_wind:
            self.logger.error(f"  Erreur de valeur lors du dessin du graphique de vent (probablement conversion de date/heure): {e_val_wind}", exc_info=True)
            if hasattr(self, 'wind_ax') and self.wind_ax:
                self.wind_ax.clear()
                self.wind_ax.text(0.5, 0.5, "Erreur: Format\ndonnées invalide", ha='center', va='center', transform=self.wind_ax.transAxes, color="red", fontsize=9)
            if hasattr(self, 'wind_graph_canvas_widget') and self.wind_graph_canvas_widget: self.wind_graph_canvas_widget.draw_idle()
        except Exception as e_graph_wind:
            self.logger.error(f"  Erreur inattendue lors du dessin du graphique de vent: {e_graph_wind}", exc_info=True)
            if hasattr(self, 'wind_ax') and self.wind_ax:
                self.wind_ax.clear()
                self.wind_ax.text(0.5, 0.5, "Erreur génération\ngraphique", ha='center', va='center', transform=self.wind_ax.transAxes, color="red", fontsize=9)
            if hasattr(self, 'wind_graph_canvas_widget') and self.wind_graph_canvas_widget:
                """TODO: Add docstring."""
                self.wind_graph_canvas_widget.draw_idle()
            else:
                self.logger.warning("    _draw_windspeed_hourly_graph (dans except Exception): wind_graph_canvas_widget non disponible pour draw_idle.")
        self.logger.info("Fin _draw_windspeed_hourly_graph.")

    def _setup_current_weather_ui(self, parent_frame: ttk.Frame):
        self.logger.info("Début _setup_current_weather_ui...")
        if not parent_frame or not parent_frame.winfo_exists():
            self.logger.error("  parent_frame pour l'onglet 'Actuellement' est invalide ou détruit. Arrêt de la configuration de l'UI actuelle.")
            return
        self.logger.debug(f"  parent_frame type: {type(parent_frame)}, ID: {id(parent_frame)}")

        # Configurer les colonnes pour la disposition
        self.logger.debug("  Configuration des colonnes du parent_frame...")
        try:
            parent_frame.columnconfigure(0, weight=0)
            parent_frame.columnconfigure(1, weight=1) # Permettre aux valeurs de s'étendre
            parent_frame.columnconfigure(2, weight=0, minsize=20) # Petit espace
            parent_frame.columnconfigure(3, weight=0, minsize=50) # Pour l'icône
            self.logger.debug("    Colonnes configurées: 0 (weight=0), 1 (weight=1), 2 (weight=0, minsize=20), 3 (weight=0, minsize=50)")
        except tk.TclError as e_col_config:
            self.logger.error(f"  Erreur TclError lors de la configuration des colonnes de parent_frame: {e_col_config}", exc_info=True)
            # Continuer si possible, mais la disposition pourrait être affectée.

        # Titre et heure des données
        self.logger.debug("  Création du title_frame et de ses labels...")
        title_frame = ttk.Frame(parent_frame)
        title_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0,10))
        self.logger.debug(f"    title_frame créé et gridé. ID: {title_frame.winfo_id()}")

        try:
            ttk.Label(title_frame, text="Météo Actuelle ", font=self.title_font).pack(side=tk.LEFT)
            self.current_data_time_label = ttk.Label(title_frame, text="(pour --:--)", font=self.small_data_font)
            self.current_data_time_label.pack(side=tk.LEFT, padx=(5,0))
            self.logger.debug("    Labels du titre ('Météo Actuelle' et 'current_data_time_label') créés et packés.")
        except Exception as e_title_labels:
            self.logger.error(f"    Erreur lors de la création des labels du titre: {e_title_labels}", exc_info=True)


        row_idx = 1 # Commence à la ligne suivante pour les données
        self.current_weather_labels: Dict[str, ttk.Label] = {}
        self.logger.debug(f"  Initialisation de self.current_weather_labels (dict vide) et row_idx à {row_idx}.")

        fields = {
            "description": "Description :", "temperature": "Température :", "apparent_temp": "Ressentie :",
            "humidity": "Humidité :", "precipitation": "Précipitations :", "cloudcover": "Couv. Nuageuse :",
            "pressure": "Pression :", "wind": "Vent :", "uv_index": "Indice UV :",
            "precipitation_prob": "Prob. Précip. :", "sunrise": "Lever soleil :", "sunset": "Coucher soleil :"
        }
        self.logger.debug(f"  Dictionnaire 'fields' défini avec {len(fields)} éléments: {list(fields.keys())}")

        # Label pour l'icône (caractère Unicode)
        self.logger.debug("  Création du label pour l'icône météo (current_weather_icon_label)...")
        try:
            self.current_weather_icon_label = ttk.Label(parent_frame, text=DEFAULT_WEATHER_ICON, font=self.icon_font, anchor="center")
            # Placer l'icône à droite, s'étendant sur plusieurs lignes de données
            rowspan_val = len(fields) // 2 + 1 # Calcul du rowspan
            self.current_weather_icon_label.grid(row=1, column=3, rowspan=rowspan_val, padx=10, pady=5, sticky="n")
            self.logger.debug(f"    current_weather_icon_label créé et gridé (row=1, column=3, rowspan={rowspan_val}).")
        except Exception as e_icon_label:
            self.logger.error(f"    Erreur lors de la création ou du placement de current_weather_icon_label: {e_icon_label}", exc_info=True)


        self.logger.debug("  Début de la boucle de création des labels de champs (description et valeur)...")
        for key, text in fields.items():
            self.logger.debug(f"    Traitement du champ: clé='{key}', texte='{text}', row_idx={row_idx}")
            try:
                # Label de description (statique)
                desc_label = ttk.Label(parent_frame, text=text, font=self.data_font)
                desc_label.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
                self.logger.debug(f"      Label de description '{text}' créé et gridé (row={row_idx}, col=0).")

                # Label de valeur (dynamique, initialisé à "N/A")
                value_label = ttk.Label(parent_frame, text="N/A", font=self.data_font, anchor="w")
                value_label.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
                self.logger.debug(f"      Label de valeur pour '{key}' (texte initial 'N/A') créé et gridé (row={row_idx}, col=1).")

                self.current_weather_labels[key] = value_label
                self.logger.debug(f"      Label de valeur pour '{key}' stocké dans self.current_weather_labels.")
            except Exception as e_field_label:
                self.logger.error(f"      Erreur lors de la création des labels pour le champ '{key}': {e_field_label}", exc_info=True)
            row_idx +=1

        self.logger.debug(f"  Fin de la boucle de création des labels. {len(self.current_weather_labels)} labels de valeur stockés.")
        self.logger.info("_setup_current_weather_ui terminé avec succès.")

    def _setup_analysis_tab_content(self, parent_frame_for_tab: ttk.Frame):
        """
        Initialise le contenu de l'onglet Analyses & Alertes.
        Prépare un frame scrollable pour afficher les messages d'analyse.
        """
        self.logger.info("Début _setup_analysis_tab_content...") # Changé en INFO
        if not parent_frame_for_tab or not parent_frame_for_tab.winfo_exists():
            self.logger.error("  parent_frame_for_tab pour l'onglet 'Analyses & Alertes' est invalide ou détruit. Arrêt de la configuration.")
            return
        self.logger.debug(f"  parent_frame_for_tab type: {type(parent_frame_for_tab)}, ID: {id(parent_frame_for_tab)}")

        try:
            self.logger.debug("  Configuration de columnconfigure et rowconfigure pour parent_frame_for_tab...")
            parent_frame_for_tab.columnconfigure(0, weight=1) # Permettre au canvas de s'étendre
            parent_frame_for_tab.rowconfigure(0, weight=1)    # Permettre au canvas de s'étendre
            self.logger.debug("    columnconfigure(0, weight=1) et rowconfigure(0, weight=1) appliqués.")
        except tk.TclError as e_config_parent:
            self.logger.error(f"    Erreur TclError lors de la configuration de parent_frame_for_tab: {e_config_parent}", exc_info=True)
            # Continuer si possible, mais la disposition pourrait être affectée.

        self.logger.debug("  Création du Canvas (self.analysis_canvas) et de la Scrollbar (self.analysis_scrollbar)...")
        try:
            self.analysis_canvas = tk.Canvas(parent_frame_for_tab, highlightthickness=0)
            self.logger.debug(f"    self.analysis_canvas créé. ID: {id(self.analysis_canvas)}")
            self.analysis_scrollbar = ttk.Scrollbar(parent_frame_for_tab, orient="vertical", command=self.analysis_canvas.yview)
            self.logger.debug(f"    self.analysis_scrollbar créé. ID: {id(self.analysis_scrollbar)}")
        except Exception as e_canvas_scroll:
            self.logger.error(f"    Erreur lors de la création du canvas ou de la scrollbar: {e_canvas_scroll}", exc_info=True)
            return # Difficile de continuer sans ces éléments

        self.logger.debug("  Création du Frame intérieur scrollable (self.scrollable_analysis_frame)...")
        try:
            self.scrollable_analysis_frame = ttk.Frame(self.analysis_canvas, padding=(5,5))
            self.logger.debug(f"    self.scrollable_analysis_frame créé avec parent self.analysis_canvas. ID: {id(self.scrollable_analysis_frame)}")
            # Configurer la colonne 0 du frame scrollable pour qu'elle s'étende
            self.scrollable_analysis_frame.columnconfigure(0, weight=1)
            self.logger.debug("    columnconfigure(0, weight=1) appliqué à self.scrollable_analysis_frame.")
        except Exception as e_scroll_frame:
            self.logger.error(f"    Erreur lors de la création de self.scrollable_analysis_frame: {e_scroll_frame}", exc_info=True)
            return

        self.logger.debug("  Liaison de l'événement <Configure> à self.scrollable_analysis_frame...")
        try:
            self.scrollable_analysis_frame.bind(
                "<Configure>",
                lambda e, c=self.analysis_canvas: c.configure(scrollregion=c.bbox("all"))
            )
            self.logger.debug("    Événement <Configure> lié pour mettre à jour scrollregion.")
        except Exception as e_bind_conf:
            self.logger.error(f"    Erreur lors de la liaison de <Configure>: {e_bind_conf}", exc_info=True)

        self.logger.debug("  Création de la fenêtre dans le canevas (self.analysis_canvas_window)...")
        try:
            self.analysis_canvas_window = self.analysis_canvas.create_window(
                (0, 0), window=self.scrollable_analysis_frame, anchor="nw"
            )
            self.logger.debug(f"    Fenêtre créée dans self.analysis_canvas avec ID: {self.analysis_canvas_window}")
        except Exception as e_create_win:
            self.logger.error(f"    Erreur lors de create_window: {e_create_win}", exc_info=True)
            return

        self.logger.debug("  Configuration de self.analysis_canvas avec yscrollcommand...")
        try:
            self.analysis_canvas.configure(yscrollcommand=self.analysis_scrollbar.set)
            self.logger.debug("    yscrollcommand configuré pour self.analysis_canvas.")
        except Exception as e_yscroll:
            self.logger.error(f"    Erreur lors de la configuration de yscrollcommand: {e_yscroll}", exc_info=True)

        self.logger.debug("  Placement (grid) de self.analysis_canvas et self.analysis_scrollbar...")
        try:
            self.analysis_canvas.grid(row=0, column=0, sticky="nsew")
            self.analysis_scrollbar.grid(row=0, column=1, sticky="ns")
            self.logger.debug("    self.analysis_canvas et self.analysis_scrollbar placés avec grid.")
        except Exception as e_grid_analysis:
            self.logger.error(f"    Erreur lors du placement (grid) du canvas ou de la scrollbar: {e_grid_analysis}", exc_info=True)

        self.logger.debug("  Liaison des événements de la molette à self.analysis_canvas et ses enfants...")
        try:
            self._bind_mousewheel_to_children(self.scrollable_analysis_frame, self.analysis_canvas)
            self.analysis_canvas.bind('<Enter>', lambda e, c=self.analysis_canvas: self._bind_mousewheel_events(c))
            self.analysis_canvas.bind('<Leave>', lambda e, c=self.analysis_canvas: self._unbind_mousewheel_events(c))
            self.logger.debug("    Événements de la molette liés.")
        except Exception as e_bind_mouse:
            self.logger.error(f"    Erreur lors de la liaison des événements de la molette: {e_bind_mouse}", exc_info=True)

        # self.analysis_labels est déjà initialisé à [] dans __init__
        self.logger.debug(f"  Vérification de self.analysis_labels: initialisé et vide (longueur: {len(self.analysis_labels)}).")

        # Optionnel: Ajouter un label initial si self.analysis_labels est vide
        # if not self.analysis_labels:
        #     try:
        #         initial_analysis_label = ttk.Label(self.scrollable_analysis_frame, text="En attente de données pour analyse...", font=self.data_font, style="Italic.TLabel") # Nécessite de définir "Italic.TLabel"
        #         initial_analysis_label.pack(pady=10, padx=5, anchor="w") # Utiliser pack ici car c'est à l'intérieur du scrollable_frame
        #         self.analysis_labels.append(initial_analysis_label) # Important pour pouvoir l'effacer plus tard
        #         self.logger.debug("    Label initial 'En attente de données...' ajouté à self.scrollable_analysis_frame.")
        #     except Exception as e_initial_label:
        #         self.logger.error(f"    Erreur lors de l'ajout du label initial: {e_initial_label}", exc_info=True)


        self.logger.info("Contenu de l'onglet Analyses & Alertes initialisé avec succès.")

    def _update_analysis_tab_display(self, insights: List[str]):
        """
        Met à jour l'onglet Analyses & Alertes avec la liste des "insights" fournis.
        """
        self.logger.info(f"Début _update_analysis_tab_display avec {len(insights)} insight(s).") # Changé en INFO

        # --- Vérification des arguments d'entrée ---
        if not isinstance(insights, list):
            self.logger.error(f"  Argument 'insights' invalide: type {type(insights)} au lieu de list. Arrêt.")
            # Optionnel: afficher un message d'erreur dans l'onglet si possible
            if hasattr(self, 'scrollable_analysis_frame') and self.scrollable_analysis_frame and self.scrollable_analysis_frame.winfo_exists():
                # Effacer le contenu précédent pour éviter confusion
                for label in self.analysis_labels:
                    if label.winfo_exists(): label.destroy()
                self.analysis_labels.clear()
                error_label = ttk.Label(self.scrollable_analysis_frame, text="Erreur: Données d'analyse invalides.", font=self.data_font, foreground="red")
                error_label.pack(pady=10, padx=5, anchor="w")
                self.analysis_labels.append(error_label) # Pour pouvoir l'effacer au prochain appel
            return

        # S'assurer que le frame existe (devrait être créé par _setup_analysis_tab_content)
        self.logger.debug("  Vérification de self.scrollable_analysis_frame...")
        if not hasattr(self, 'scrollable_analysis_frame') or \
           not self.scrollable_analysis_frame or \
           not self.scrollable_analysis_frame.winfo_exists(): # Vérifier aussi winfo_exists
            self.logger.error("  scrollable_analysis_frame non trouvé, non initialisé ou détruit. Impossible de mettre à jour les analyses.")
            return
        self.logger.debug(f"    self.scrollable_analysis_frame trouvé. ID: {id(self.scrollable_analysis_frame)}")

        self.logger.debug(f"  Effacement des {len(self.analysis_labels)} anciens labels d'analyse...")
        try:
            for i, label in enumerate(self.analysis_labels):
                if label.winfo_exists(): # Vérifier si le widget existe encore avant de le détruire
                    label.destroy()
                    # self.logger.debug(f"    Ancien label {i+1} détruit.") # Peut être trop verbeux
            self.analysis_labels.clear()
            self.logger.debug("    Anciens labels effacés et self.analysis_labels vidé.")
        except Exception as e_clear_labels:
            self.logger.error(f"    Erreur lors de l'effacement des anciens labels: {e_clear_labels}", exc_info=True)
            # Continuer si possible, mais l'affichage pourrait être incorrect.

        if not insights:
            self.logger.info("  Aucun insight fourni. Affichage du message par défaut.")
            try:
                # Définir le style "Italic.TLabel" si ce n'est pas déjà fait (ou utiliser une font italique directement)
                # Pour simplifier, on peut utiliser une font directement ici si le style n'est pas crucial
                italic_font = tkfont.Font(family="Segoe UI", size=9, slant="italic") # Créer une font italique
                no_insights_label = ttk.Label(self.scrollable_analysis_frame,
                                              text="Aucune alerte ou analyse particulière pour le moment.",
                                              font=italic_font) # Utiliser la font directement
                no_insights_label.pack(pady=10, padx=5, anchor="w")
                self.analysis_labels.append(no_insights_label) # Important pour l'effacement futur
                self.logger.debug("    Label 'Aucune alerte...' créé et packé.")
            except Exception as e_no_insight_label:
                self.logger.error(f"    Erreur lors de la création du label 'Aucune alerte...': {e_no_insight_label}", exc_info=True)
            # Mise à jour de la scrollregion même s'il n'y a qu'un seul label
            self.root.update_idletasks()
            if hasattr(self, 'analysis_canvas') and self.analysis_canvas.winfo_exists():
                self.analysis_canvas.configure(scrollregion=self.analysis_canvas.bbox("all"))
            return # Fin de la fonction ici

        self.logger.debug(f"  Début de la boucle pour afficher {len(insights)} insight(s)...")
        for i, insight_text in enumerate(insights):
            self.logger.debug(f"    Traitement de l'insight {i+1}/{len(insights)}: '{insight_text[:70]}...'")
            try:
                # Estimer la largeur disponible
                available_width = 700 # Fallback initial
                if hasattr(self, 'scrollable_analysis_frame') and self.scrollable_analysis_frame.winfo_exists():
                    current_frame_width = self.scrollable_analysis_frame.winfo_width()
                    if current_frame_width > 1:
                        available_width = current_frame_width
                        self.logger.debug(f"      Largeur de scrollable_analysis_frame: {available_width}")
                    elif hasattr(self, 'analysis_canvas') and self.analysis_canvas.winfo_exists():
                        canvas_width = self.analysis_canvas.winfo_width()
                        scrollbar_width = self.analysis_scrollbar.winfo_width() if hasattr(self, 'analysis_scrollbar') and self.analysis_scrollbar.winfo_exists() else 0
                        available_width = canvas_width - scrollbar_width - 20 # Moins padding/scrollbar
                        self.logger.debug(f"      Largeur estimée depuis canvas: {canvas_width} - {scrollbar_width} - 20 = {available_width}")

                if available_width <= 1: # Si toujours pas de largeur valide
                    available_width = 700 # Fallback final
                    self.logger.debug(f"      Utilisation de la largeur fallback: {available_width}")

                # S'assurer que wraplength est positif
                final_wraplength = max(200, available_width - 20)
                self.logger.debug(f"      wraplength final calculé: {final_wraplength}")

                insight_label = ttk.Label(self.scrollable_analysis_frame,
                                          text=f"● {insight_text}", # Ajouter une puce
                                          font=self.data_font,
                                          wraplength=final_wraplength,
                                          justify=tk.LEFT,
                                          anchor="w")
                insight_label.pack(pady=3, padx=5, fill=tk.X, expand=True, anchor="w") # fill=tk.X et expand=True sont importants pour wraplength
                self.analysis_labels.append(insight_label)
                self.logger.debug(f"      Label pour insight {i+1} créé et packé.")
            except Exception as e_insight_label_loop:
                self.logger.error(f"      Erreur lors de la création ou du packing du label pour l'insight '{insight_text[:50]}...': {e_insight_label_loop}", exc_info=True)

        self.logger.debug("  Fin de la boucle d'affichage des insights.")
        self.logger.debug("  Forçage de update_idletasks et reconfiguration de scrollregion pour analysis_canvas...")
        try:
            self.root.update_idletasks() # Important pour que les tailles des widgets soient à jour avant bbox
            if hasattr(self, 'analysis_canvas') and self.analysis_canvas.winfo_exists():
                bbox_val = self.analysis_canvas.bbox("all")
                self.analysis_canvas.configure(scrollregion=bbox_val)
                self.logger.debug(f"    scrollregion de analysis_canvas mise à jour avec bbox: {bbox_val}")
            else:
                self.logger.warning("    self.analysis_canvas non trouvé ou détruit, scrollregion non mise à jour.")
        except Exception as e_scroll_update:
            self.logger.error(f"    Erreur lors de la mise à jour de scrollregion: {e_scroll_update}", exc_info=True)

        self.logger.info("_update_analysis_tab_display terminé.")

    def _generate_derived_insights(self, weather_data: dict) -> List[str]:
        """
        Génère une liste de messages d'analyse et d'alertes basés sur les données météo.
        """
        self.logger.info("Début _generate_derived_insights...") # Changé en INFO
        insights: List[str] = []

        if not isinstance(weather_data, dict):
            self.logger.error("  weather_data n'est pas un dictionnaire. Impossible de générer les analyses.")
            insights.append("Erreur interne: Données météo sources invalides pour l'analyse.")
            return insights

        daily_data = weather_data.get("daily", {})
        hourly_data = weather_data.get("hourly", {})
        current_data = weather_data.get("current", {})
        self.logger.debug(f"  Données disponibles: daily_data {'présent' if daily_data else 'absent/vide'}, hourly_data {'présent' if hourly_data else 'absent/vide'}, current_data {'présent' if current_data else 'absent/vide'}")

        # --- 1. Alerte Gel (basée sur temperature_2m_min des prochains jours) ---
        self.logger.debug("  Analyse 1: Alerte Gel...")
        if daily_data.get("time") and daily_data.get("temperature_2m_min"):
            temps_min_daily = daily_data.get("temperature_2m_min", []) # Utiliser .get avec fallback
            dates_daily = daily_data.get("time", [])
            self.logger.debug(f"    Données pour alerte gel: {len(temps_min_daily)} temp_min, {len(dates_daily)} dates.")

            # Vérifier pour les 3 prochains jours (index 0, 1, 2)
            for i in range(min(3, len(temps_min_daily), len(dates_daily))): # S'assurer qu'on ne dépasse pas la longueur des deux listes
                temp_min = temps_min_daily[i]
                date_iso = dates_daily[i]
                self.logger.debug(f"      Jour {i+1}: temp_min={temp_min}, date_iso='{date_iso}'")
                if temp_min is not None:
                    try:
                        date_str = "Aujourd'hui" if i == 0 else (
                            "Demain" if i == 1 else
                            datetime.datetime.fromisoformat(date_iso).strftime("%A %d %b").capitalize()
                        )
                        if temp_min <= 0:
                            insight_msg = f"❄️ ALERTE GEL: Risque de gelée ({temp_min}°C) prévu pour {date_str}."
                            insights.append(insight_msg)
                            self.logger.info(f"      Insight ajouté: {insight_msg}")
                            break # Une alerte gel suffit peut-être
                        elif temp_min <= 2: # Seuil pour gelée blanche
                            insight_msg = f"❄️ Attention: Risque de gelée blanche ({temp_min}°C) possible pour {date_str}."
                            insights.append(insight_msg)
                            self.logger.info(f"      Insight ajouté: {insight_msg}")
                            # On peut laisser continuer pour voir si un gel plus fort est prévu plus tard
                    except ValueError as e_date_gel:
                        self.logger.warning(f"      Erreur de format de date pour alerte gel (jour {i+1}, date_iso='{date_iso}'): {e_date_gel}")
        else:
            self.logger.debug("    Données 'daily.time' ou 'daily.temperature_2m_min' manquantes pour l'alerte gel.")

        # --- 2. Alerte Vent Fort (basée sur windgusts_10m_max des prochains jours) ---
        self.logger.debug("  Analyse 2: Alerte Vent Fort...")
        if daily_data.get("time") and daily_data.get("windgusts_10m_max"):
            gusts_max_daily = daily_data.get("windgusts_10m_max", [])
            dates_daily_vent = daily_data.get("time", []) # Renommer pour éviter confusion avec dates_daily de l'alerte gel
            self.logger.debug(f"    Données pour alerte vent: {len(gusts_max_daily)} gusts_max, {len(dates_daily_vent)} dates.")

            for i in range(min(3, len(gusts_max_daily), len(dates_daily_vent))):
                gust_max = gusts_max_daily[i]
                date_iso_vent = dates_daily_vent[i]
                self.logger.debug(f"      Jour {i+1}: gust_max={gust_max}, date_iso='{date_iso_vent}'")
                if gust_max is not None and gust_max >= 70: # Seuil de 70 km/h pour vent fort
                    try:
                        date_str_vent = "Aujourd'hui" if i == 0 else (
                            "Demain" if i == 1 else
                            datetime.datetime.fromisoformat(date_iso_vent).strftime("%A %d %b").capitalize()
                        )
                        insight_msg = f"🌬️ ALERTE VENT: Fortes rafales ({gust_max} km/h) attendues {date_str_vent}."
                        insights.append(insight_msg)
                        self.logger.info(f"      Insight ajouté: {insight_msg}")
                        break # Une alerte vent suffit peut-être
                    except ValueError as e_date_vent:
                        self.logger.warning(f"      Erreur de format de date pour alerte vent (jour {i+1}, date_iso='{date_iso_vent}'): {e_date_vent}")
        else:
            self.logger.debug("    Données 'daily.time' ou 'daily.windgusts_10m_max' manquantes pour l'alerte vent.")

        # --- 3. Indication "Beau Temps pour Activité Extérieure" (prochaines 12-24h) ---
        self.logger.debug("  Analyse 3: Indication Beau Temps...")
        hourly_time = hourly_data.get("time")
        hourly_cloudcover = hourly_data.get("cloudcover")
        hourly_precip_prob = hourly_data.get("precipitation_probability")
        hourly_windspeed = hourly_data.get("windspeed_10m")

        if hourly_time and hourly_cloudcover and hourly_precip_prob and hourly_windspeed:
            self.logger.debug(f"    Données pour beau temps: time (len={len(hourly_time)}), cloud (len={len(hourly_cloudcover)}), precip_prob (len={len(hourly_precip_prob)}), wind (len={len(hourly_windspeed)})")
            beau_temps_periodes: List[str] = []
            heures_consecutives_beau_temps = 0
            periode_debut_str = ""

            # S'assurer que toutes les listes ont la même longueur que hourly_time pour éviter IndexError
            max_iter = min(12, len(hourly_time), len(hourly_cloudcover), len(hourly_precip_prob), len(hourly_windspeed))
            self.logger.debug(f"    Analyse des {max_iter} prochaines heures pour beau temps.")

            for i in range(max_iter):
                try:
                    cloud = hourly_cloudcover[i]
                    precip_prob = hourly_precip_prob[i]
                    wind = hourly_windspeed[i]
                    time_dt_str = hourly_time[i]
                    time_dt = datetime.datetime.fromisoformat(time_dt_str.replace("Z","+00:00")).astimezone()
                    self.logger.debug(f"      Heure {i+1} ({time_dt_str}): cloud={cloud}, precip_prob={precip_prob}, wind={wind}")

                    if cloud is not None and precip_prob is not None and wind is not None and \
                       cloud <= 30 and precip_prob <= 15 and wind <= 25: # Seuils à ajuster
                        self.logger.debug("        Conditions de beau temps remplies.")
                        if heures_consecutives_beau_temps == 0:
                            periode_debut_str = time_dt.strftime("%Hh")
                            self.logger.debug(f"          Début d'une période de beau temps à {periode_debut_str}.")
                        heures_consecutives_beau_temps += 1
                    else:
                        self.logger.debug("        Conditions de beau temps NON remplies.")
                        if heures_consecutives_beau_temps >= 3: # Au moins 3h de beau temps consécutives
                            fin_periode_str = time_dt.strftime('%Hh') # L'heure actuelle marque la fin
                            beau_temps_periodes.append(f"de {periode_debut_str} à {fin_periode_str}")
                            self.logger.debug(f"          Période de beau temps enregistrée: de {periode_debut_str} à {fin_periode_str} ({heures_consecutives_beau_temps}h).")
                        heures_consecutives_beau_temps = 0
                except (IndexError, ValueError) as e_beau_temps_loop:
                    self.logger.warning(f"      Erreur lors de l'analyse de l'heure {i+1} pour beau temps: {e_beau_temps_loop}")
                    continue # Passer à l'heure suivante

            # Vérifier la dernière période après la boucle
            if heures_consecutives_beau_temps >= 3:
                try:
                    # Utiliser la dernière heure effectivement analysée si la boucle s'est terminée avant 12 itérations
                    last_analyzed_index = max_iter -1
                    if last_analyzed_index >=0:
                        fin_periode_dt_str = hourly_time[last_analyzed_index]
                        fin_periode_dt = datetime.datetime.fromisoformat(fin_periode_dt_str.replace("Z","+00:00")).astimezone()
                        fin_periode_str_display = (fin_periode_dt + datetime.timedelta(hours=1)).strftime('%Hh') # Fin de l'heure
                        beau_temps_periodes.append(f"de {periode_debut_str} à {fin_periode_str_display}")
                        self.logger.debug(f"          Dernière période de beau temps enregistrée: de {periode_debut_str} à {fin_periode_str_display} ({heures_consecutives_beau_temps}h).")
                except (IndexError, ValueError) as e_last_period:
                     self.logger.warning(f"      Erreur lors de la finalisation de la dernière période de beau temps: {e_last_period}")


            if beau_temps_periodes:
                insight_msg = f"☀️ BEAU TEMPS: Conditions favorables pour activités extérieures prévues aujourd'hui/demain ({', '.join(beau_temps_periodes)})."
                insights.append(insight_msg)
                self.logger.info(f"      Insight ajouté: {insight_msg}")
            else:
                self.logger.debug("    Aucune période de beau temps significative (>= 3h consécutives) détectée.")
        else:
            self.logger.debug("    Données horaires ('time', 'cloudcover', 'precipitation_probability', ou 'windspeed_10m') manquantes pour l'analyse du beau temps.")


        # --- 4. Tendance de la Pression Atmosphérique (sur les prochaines 6h) ---
        self.logger.debug("  Analyse 4: Tendance Pression Atmosphérique...")
        current_pressure = current_data.get("pressure_msl")
        hourly_pressure_list = hourly_data.get("pressure_msl", [])

        if current_pressure is not None and hourly_pressure_list:
            self.logger.debug(f"    Données pour tendance pression: actuelle={current_pressure}, horaire (len={len(hourly_pressure_list)})")
            p_actuelle = current_pressure

            # Pression dans 3h (index 2 si la liste commence à l'heure actuelle + 1h)
            # L'API retourne souvent l'heure actuelle comme premier élément de 'hourly', donc index 2 est H+2 (ou 3ème heure)
            p_3h = hourly_pressure_list[2] if len(hourly_pressure_list) > 2 and hourly_pressure_list[2] is not None else None
            self.logger.debug(f"      Pression à H+3h (index 2): {p_3h}")

            # Pression dans 6h (index 5)
            # p_6h = hourly_pressure_list[5] if len(hourly_pressure_list) > 5 and hourly_pressure_list[5] is not None else None
            # self.logger.debug(f"      Pression à H+6h (index 5): {p_6h}")


            if p_3h is not None:
                diff_3h = p_3h - p_actuelle
                self.logger.debug(f"      Différence de pression sur 3h: {diff_3h:.1f} hPa")
                if diff_3h < -1.5: # Baisse significative > 1.5 hPa en 3h
                    insight_msg = f"📉 TENDANCE PRESSION: Baisse notable ({diff_3h:.1f} hPa/3h), dégradation possible."
                    insights.append(insight_msg)
                    self.logger.info(f"      Insight ajouté: {insight_msg}")
                elif diff_3h > 1.5: # Hausse significative
                    insight_msg = f"📈 TENDANCE PRESSION: Hausse notable ({diff_3h:.1f} hPa/3h), amélioration possible."
                    insights.append(insight_msg)
                    self.logger.info(f"      Insight ajouté: {insight_msg}")
                else:
                    self.logger.debug(f"      Tendance pression stable ou faible variation sur 3h ({diff_3h:.1f} hPa).")
            else:
                self.logger.debug("      Donnée de pression à H+3h non disponible pour calculer la tendance.")
        else:
            self.logger.debug("    Données 'current.pressure_msl' ou 'hourly.pressure_msl' manquantes pour l'analyse de tendance pression.")


        if not insights: # Si aucune alerte ou info majeure
            """TODO: Add docstring."""
            self.logger.info("  Aucune alerte ou tendance majeure détectée, ajout du message par défaut.")
            insights.append("Analyse météo: Pas d'alertes ou de tendances majeures pour le moment.")

        self.logger.info(f"Génération des analyses terminée. {len(insights)} insight(s) produits: {insights}")
        return insights

    def _update_current_weather_display(self, weather_data: dict):
        self.logger.info("Début _update_current_weather_display...") # Changé en INFO
        try:
            if not isinstance(weather_data, dict):
                self.logger.error("  weather_data n'est pas un dictionnaire. Arrêt de la mise à jour de l'affichage actuel.")
                self.update_status("Erreur: Données météo invalides pour l'affichage actuel.")
                return

            current = weather_data.get("current", {})
            hourly = weather_data.get("hourly", {}) # Pour fallback ou données non dispo dans "current"
            daily = weather_data.get("daily", {})
            current_units = weather_data.get("current_units", {})
            hourly_units = weather_data.get("hourly_units", {}) # Pour fallback unités
            daily_units = weather_data.get("daily_units", {}) # Au cas où pour lever/coucher soleil si unités spécifiques

            self.logger.debug(f"  Données sources: current {'présent' if current else 'absent/vide'}, hourly {'présent' if hourly else 'absent/vide'}, daily {'présent' if daily else 'absent/vide'}")
            self.logger.debug(f"  Unités sources: current_units {'présent' if current_units else 'absent/vide'}, hourly_units {'présent' if hourly_units else 'absent/vide'}, daily_units {'présent' if daily_units else 'absent/vide'}")


            # --- Heure des données "actuelles" ---
            current_time_str = current.get("time")
            displayed_time_str = "(--:--)" # Valeur par défaut
            self.logger.debug(f"  Traitement de current.time: '{current_time_str}'")
            if current_time_str and isinstance(current_time_str, str):
                try:
                    current_dt_utc = datetime.datetime.fromisoformat(current_time_str.replace("Z", "+00:00"))
                    current_dt_local = current_dt_utc.astimezone()
                    displayed_time_str = f"(pour {current_dt_local.strftime('%H:%M')})"
                    self.logger.debug(f"    Heure actuelle convertie en: {displayed_time_str}")
                except ValueError:
                    self.logger.warning(f"    Format de date invalide pour current.time: '{current_time_str}'. Utilisation de la valeur par défaut.")
            else:
                self.logger.debug(f"    current.time absent ou invalide. Utilisation de la valeur par défaut '{displayed_time_str}'.")

    """TODO: Add docstring."""
            if hasattr(self, 'current_data_time_label') and self.current_data_time_label:
                 self.current_data_time_label.config(text=displayed_time_str)
            else:
                self.logger.warning("    self.current_data_time_label non trouvé pour mise à jour.")


            # --- Fonction utilitaire interne pour obtenir les valeurs (avec logs) ---
            def get_val(key_name_for_log: str, data_block, units_block_arg, key, fallback_block=None, fallback_units_block_arg=None, unit_alt_key=None, precision=1, default_val="N/A"):
                self.logger.debug(f"    get_val pour '{key_name_for_log}' (clé API: '{key}'):")
                val = data_block.get(key)
                units_to_use = units_block_arg # Renommer pour clarté
                source_log = "current"

                if val is None and fallback_block is not None: # Tenter un fallback si val est None ET fallback_block est fourni
                    self.logger.debug(f"      Valeur pour '{key}' absente dans '{source_log}', tentative de fallback...")
                    val = fallback_block.get(key)
                    source_log = "fallback (hourly/daily)"
                    if val is not None and isinstance(val, list): # Si c'est une liste horaire/journalière, prendre le premier élément
                        if val: # S'assurer que la liste n'est pas vide
                            val = val[0]
                            self.logger.debug(f"        Valeur de fallback (liste, premier élément): {val}")
                        else:
                            val = None # La liste de fallback est vide
                            self.logger.debug(f"        Liste de fallback pour '{key}' est vide.")
                    else:
                        self.logger.debug(f"        Valeur de fallback (directe): {val}")

                    # Utiliser les unités du fallback si les unités primaires étaient celles de 'current' et un fallback d'unités est fourni
                    if units_to_use is current_units and fallback_units_block_arg is not None:
                        units_to_use = fallback_units_block_arg
                        self.logger.debug(f"        Unités mises à jour vers celles du fallback.")
                else:
                    self.logger.debug(f"      Valeur trouvée dans '{source_log}': {val}")

                unit_key_to_use = unit_alt_key if unit_alt_key else key
                unit_str = units_to_use.get(unit_key_to_use, "")
                self.logger.debug(f"      Unité pour '{unit_key_to_use}': '{unit_str}' (depuis le bloc d'unités de '{source_log}')")

                if val is None:
                    self.logger.debug(f"      Valeur finale pour '{key_name_for_log}' est None, retour de default_val: '{default_val}'")
                    return default_val

                formatted_val = ""
                if isinstance(val, (int, float)):
                    formatted_val = f"{val:.{precision}f}{unit_str}" if isinstance(val, float) else f"{val}{unit_str}"
                else: # Pour les strings ou autres types (ex: codes météo si on les passait ici)
                    formatted_val = f"{val}{unit_str}"

                self.logger.debug(f"      Valeur finale formatée pour '{key_name_for_log}': '{formatted_val}'")
                return formatted_val

            # --- Description et Icône ---
            self.logger.debug("  Mise à jour de Description et Icône...")
            # Pour weathercode et is_day, on prend de 'current' en priorité, sinon de la première heure de 'hourly'
            desc_code_current = current.get("weathercode")
            is_day_current = current.get("is_day")

            desc_code_hourly_list = hourly.get("weathercode", [])
            is_day_hourly_list = hourly.get("is_day", [])

            desc_code = desc_code_current if desc_code_current is not None else (desc_code_hourly_list[0] if desc_code_hourly_list else 0)
            is_day = is_day_current if is_day_current is not None else (is_day_hourly_list[0] if is_day_hourly_list else 1)
            self.logger.debug(f"    Valeurs pour _get_weather_display_info: desc_code={desc_code} (current: {desc_code_current}, hourly[0]: {desc_code_hourly_list[0] if desc_code_hourly_list else 'N/A'}), is_day={is_day} (current: {is_day_current}, hourly[0]: {is_day_hourly_list[0] if is_day_hourly_list else 'N/A'})")

            desc, icon_char = self._get_weather_display_info(desc_code, is_day)
            self.logger.debug(f"    Description: '{desc}', Icône: '{icon_char}'")

            if "description" in self.current_weather_labels: self.current_weather_labels["description"].config(text=desc)
            if hasattr(self, 'current_weather_icon_label') and self.current_weather_icon_label: self.current_weather_icon_label.config(text=icon_char)


            # --- Données principales (utilisation de la fonction get_val) ---
            self.logger.debug("  Mise à jour des données principales...")
            if "temperature" in self.current_weather_labels: self.current_weather_labels["temperature"].config(text=get_val("Température", current, current_units, "temperature_2m", hourly, hourly_units))
            if "apparent_temp" in self.current_weather_labels: self.current_weather_labels["apparent_temp"].config(text=get_val("Ressentie", current, current_units, "apparent_temperature", hourly, hourly_units))
            if "humidity" in self.current_weather_labels: self.current_weather_labels["humidity"].config(text=get_val("Humidité", current, current_units, "relativehumidity_2m", hourly, hourly_units))
            if "pressure" in self.current_weather_labels: self.current_weather_labels["pressure"].config(text=get_val("Pression", current, current_units, "pressure_msl", hourly, hourly_units, precision=0))
            if "precipitation" in self.current_weather_labels: self.current_weather_labels["precipitation"].config(text=get_val("Précipitations", current, current_units, "precipitation", hourly, hourly_units, precision=1))
            if "cloudcover" in self.current_weather_labels: self.current_weather_labels["cloudcover"].config(text=get_val("Couv. Nuageuse", current, current_units, "cloudcover", hourly, hourly_units, precision=0))

            # --- Vent ---
            self.logger.debug("  Mise à jour du Vent...")
            wind_s_val_str = get_val("Vent (vitesse)", current, current_units, "windspeed_10m", hourly, hourly_units)

            wind_d_val_current = current.get("winddirection_10m")
            wind_d_hourly_list = hourly.get("winddirection_10m", [])
            wind_d_val = wind_d_val_current if wind_d_val_current is not None else (wind_d_hourly_list[0] if wind_d_hourly_list else None)

            wind_d_unit_current = current_units.get("winddirection_10m", "")
            wind_d_unit_hourly = hourly_units.get("winddirection_10m", "")
            wind_d_unit = wind_d_unit_current if wind_d_val_current is not None else (wind_d_unit_hourly if wind_d_hourly_list else "")

            wind_d_str = f"{wind_d_val}{wind_d_unit}" if wind_d_val is not None else "N/A"
            self.logger.debug(f"    Vent: Vitesse='{wind_s_val_str}', Direction brute='{wind_d_val}', Unité dir='{wind_d_unit}', Direction formatée='{wind_d_str}'")
            if "wind" in self.current_weather_labels: self.current_weather_labels["wind"].config(text=f"{wind_s_val_str} (Dir: {wind_d_str})")

            # --- Indice UV ---
            self.logger.debug("  Mise à jour de l'Indice UV (depuis hourly[0])...")
            uv_val_hourly_list = hourly.get("uv_index", [])
            uv_val_hourly = uv_val_hourly_list[0] if uv_val_hourly_list and uv_val_hourly_list[0] is not None else None
            uv_unit = hourly_units.get("uv_index", "") # Unité depuis hourly_units
            uv_display_str = f"{uv_val_hourly}{uv_unit}" if uv_val_hourly is not None else "N/A"
            self.logger.debug(f"    Indice UV: Valeur horaire[0]={uv_val_hourly}, Unité='{uv_unit}', Affichage='{uv_display_str}'")
            if "uv_index" in self.current_weather_labels: self.current_weather_labels["uv_index"].config(text=uv_display_str)

            # --- Probabilité de Précipitation ---
            self.logger.debug("  Mise à jour de la Probabilité Précipitation (depuis hourly[0])...")
            precip_prob_hourly_list = hourly.get("precipitation_probability", [])
            precip_prob_val_hourly = precip_prob_hourly_list[0] if precip_prob_hourly_list and precip_prob_hourly_list[0] is not None else None
            precip_prob_unit = hourly_units.get("precipitation_probability","%")
            precip_prob_display_str = f"{precip_prob_val_hourly}{precip_prob_unit}" if precip_prob_val_hourly is not None else "N/A"
            self.logger.debug(f"    Prob. Précip.: Valeur horaire[0]={precip_prob_val_hourly}, Unité='{precip_prob_unit}', Affichage='{precip_prob_display_str}'")
            if "precipitation_prob" in self.current_weather_labels: self.current_weather_labels["precipitation_prob"].config(text=precip_prob_display_str)

            # --- Lever et Coucher du Soleil (du bloc journalier, index 0 pour aujourd'hui) ---
            self.logger.debug("  Mise à jour du Lever et Coucher du Soleil (depuis daily[0])...")
            if daily and daily.get("time") and len(daily["time"]) > 0:
                sunrise_iso_list = daily.get("sunrise", [])
                sunset_iso_list = daily.get("sunset", [])

                sunrise_iso = sunrise_iso_list[0] if sunrise_iso_list else "N/A"
                sunset_iso = sunset_iso_list[0] if sunset_iso_list else "N/A"
                self.logger.debug(f"    Données brutes: sunrise_iso='{sunrise_iso}', sunset_iso='{sunset_iso}'")

                sunrise_dt_str = "N/A"; sunset_dt_str = "N/A"
                try:
                    if sunrise_iso != "N/A": sunrise_dt_str = datetime.datetime.fromisoformat(sunrise_iso.replace("Z", "+00:00")).strftime('%H:%M')
                    if sunset_iso != "N/A": sunset_dt_str = datetime.datetime.fromisoformat(sunset_iso.replace("Z", "+00:00")).strftime('%H:%M')
                    self.logger.debug(f"    Heures formatées: Lever='{sunrise_dt_str}', Coucher='{sunset_dt_str}'")
                except ValueError as e_sun_time:
                    self.logger.warning(f"    Erreur de format de date pour lever/coucher soleil: {e_sun_time}. sunrise_iso='{sunrise_iso}', sunset_iso='{sunset_iso}'")

                if "sunrise" in self.current_weather_labels: self.current_weather_labels["sunrise"].config(text=sunrise_dt_str)
                if "sunset" in self.current_weather_labels: self.current_weather_labels["sunset"].config(text=sunset_dt_str)
            else:
                self.logger.debug("    Données journalières (daily.time) absentes ou vides, lever/coucher du soleil non mis à jour.")
                if "sunrise" in self.current_weather_labels: self.current_weather_labels["sunrise"].config(text="N/A")
                if "sunset" in self.current_weather_labels: self.current_weather_labels["sunset"].config(text="N/A")
                    """TODO: Add docstring."""

            self.logger.info("_update_current_weather_display terminé avec succès.")

        except Exception as e:
            self.update_status(f"Erreur màj aff. actuel: {e}") # Met à jour le label de statut de l'app
            self.logger.error(f"Erreur majeure dans _update_current_weather_display: {e}", exc_info=True)

    def _clear_scrollable_frame(self, frame: ttk.Frame):
        self.logger.debug(f"Début _clear_scrollable_frame pour le frame ID: {id(frame) if frame else 'None'}")
        if not frame or not frame.winfo_exists():
            self.logger.warning("  Frame à nettoyer est None ou a été détruit. Aucune action.")
            return

        children = frame.winfo_children()
        num_children = len(children)
        self.logger.debug(f"  Nettoyage de {num_children} widget(s) enfant(s) du frame '{frame.winfo_name()}' (ID: {id(frame)})...")
        try:
            for i, widget in enumerate(children):
                if widget.winfo_exists(): # Vérifier avant de détruire
                    widget_name = widget.winfo_name()
                    widget_id = id(widget)
                    widget.destroy()
                    # self.logger.debug(f"    Enfant {i+1}/{num_children} ('{widget_name}', ID: {widget_id}) détruit.") # Peut être trop verbeux
                # else:
                    # self.logger.debug(f"    Enfant {i+1}/{num_children} déjà détruit ou invalide, ignoré.")
            self.logger.info(f"  {num_children} widget(s) enfant(s) détruit(s) avec succès du frame '{frame.winfo_name()}'.")
        except Exception as e_clear:
            self.logger.error(f"  Erreur lors du nettoyage des enfants du frame '{frame.winfo_name()}': {e_clear}", exc_info=True)
        self.logger.debug("Fin _clear_scrollable_frame.")

    def _degrees_to_cardinal(self, d: Optional[float]) -> str:
        """Convertit une direction en degrés en point cardinal."""
        self.logger.debug(f"Début _degrees_to_cardinal avec d={d} (type: {type(d)})")
        if d is None:
            self.logger.debug("  d est None, retour de 'N/A'.")
            return "N/A"

        if not isinstance(d, (int, float)):
            self.logger.warning(f"  Type d'entrée invalide pour _degrees_to_cardinal: {type(d)}. Attendu float ou int. Retour de 'N/A'.")
            return "N/A"

        dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
        try:
            # S'assurer que d est bien un nombre avant les opérations mathématiques
            d_float = float(d)
                """TODO: Add docstring."""
            ix = round(d_float / (360. / len(dirs)))
            cardinal_point = dirs[int(ix % len(dirs))]
            self.logger.debug(f"  Conversion: {d}° -> ix={ix}, point cardinal='{cardinal_point}'.")
            return cardinal_point
        except (ValueError, TypeError, ZeroDivisionError) as e_conversion: # ZeroDivisionError si len(dirs) est 0, peu probable
            self.logger.error(f"  Erreur de conversion dans _degrees_to_cardinal pour d={d}: {e_conversion}", exc_info=True)
            return "N/A" # Fallback en cas d'erreur

    def _update_hourly_forecast_display(self, weather_data: dict):
        self.logger.info("Début _update_hourly_forecast_display...") # Changé en INFO

        if not isinstance(weather_data, dict):
            self.logger.error("  weather_data n'est pas un dictionnaire. Arrêt de la mise à jour des prévisions horaires.")
            if hasattr(self, 'scrollable_hourly_frame') and self.scrollable_hourly_frame.winfo_exists():
                 self._clear_scrollable_frame(self.scrollable_hourly_frame) # Nettoyer avant d'ajouter le message d'erreur
                 ttk.Label(self.scrollable_hourly_frame, text="Erreur: Données météo sources invalides.", font=self.data_font, foreground="red").pack()
            return

        self.logger.debug(f"  Appel à _clear_scrollable_frame pour self.scrollable_hourly_frame (ID: {id(self.scrollable_hourly_frame) if hasattr(self, 'scrollable_hourly_frame') else 'N/A'})...")
        if hasattr(self, 'scrollable_hourly_frame') and self.scrollable_hourly_frame.winfo_exists():
            self._clear_scrollable_frame(self.scrollable_hourly_frame)
        else:
            self.logger.error("  self.scrollable_hourly_frame non trouvé ou détruit. Impossible de nettoyer ou d'afficher les prévisions horaires.")
            return

        hourly = weather_data.get("hourly", {})
        units_local = weather_data.get("hourly_units", {}) # Renommé de units
        self.logger.debug(f"  Données sources: hourly {'présent' if hourly else 'absent/vide'}, units_local {'présent' if units_local else 'absent/vide'}")

        hourly_times = hourly.get("time", []) # Obtenir la liste des temps une fois
        if not hourly_times: # Vérifier si la liste des temps est vide ou si la clé manque
            self.logger.warning("  Prévisions horaires non disponibles (hourly.time est absent ou vide). Affichage du message par défaut.")
            ttk.Label(self.scrollable_hourly_frame, text="Prévisions horaires non disponibles.", font=self.data_font).pack()
            return
        self.logger.debug(f"  Nombre d'heures disponibles dans hourly.time: {len(hourly_times)}")

        # --- Header pour les prévisions horaires (utilisant grid) ---
        self.logger.debug("  Création du header pour les prévisions horaires...")
        try:
            header_frame_h = ttk.Frame(self.scrollable_hourly_frame)
            header_frame_h.pack(fill="x", pady=(0, 2))
            self.logger.debug(f"    header_frame_h créé et packé. ID: {id(header_frame_h)}")

            col_widths_header = { # Utiliser des clés int pour la cohérence avec l'itération
                0: {"text": "Heure", "min": 70, "weight": 0, "anchor": "w"}, 1: {"text": "Météo", "min": 35, "weight": 0, "anchor": "center"},
                2: {"text": "Temp.", "min": 55, "weight": 0, "anchor": "w"}, 3: {"text": "Description", "min": 140, "weight": 2, "anchor": "w"},
                4: {"text": "Vent", "min": 65, "weight": 0, "anchor": "w"}, 5: {"text": "Précip. (mm)", "min": 70, "weight": 0, "anchor": "w"},
                6: {"text": "Prob. Précip.", "min": 70, "weight": 0, "anchor": "w"}
            }
            for col_idx, conf in col_widths_header.items(): # col_idx sera 0, 1, 2...
                header_frame_h.columnconfigure(col_idx, weight=conf["weight"], minsize=conf["min"])
                ttk.Label(header_frame_h, text=conf["text"], font=self.small_data_font, anchor=conf["anchor"]).grid(
                    row=0, column=col_idx, padx=3, sticky="ew" if conf["anchor"] == "center" else conf["anchor"]
                )
            self.logger.debug("    Labels du header créés et placés.")
            ttk.Separator(self.scrollable_hourly_frame, orient="horizontal").pack(fill="x", pady=(2, 5))
        except Exception as e_header:
            self.logger.error(f"    Erreur lors de la création du header: {e_header}", exc_info=True)
            # Continuer si possible, l'affichage sera juste moins clair sans header

        # --- Données de prévisions horaires ---
        self.logger.debug(f"  Début de la boucle pour afficher les prévisions pour {min(len(hourly_times), HOURLY_FORECAST_HOURS)} heure(s)...")

        # Récupérer toutes les listes de données une fois pour éviter des .get() répétés dans la boucle
        # et pour permettre une vérification de longueur cohérente.
        temps_2m_list = hourly.get("temperature_2m", [])
        precip_prob_list = hourly.get("precipitation_probability", [])
        precip_qty_list = hourly.get("precipitation", [])
        wind_speed_list = hourly.get("windspeed_10m", [])
        wind_dir_list = hourly.get("winddirection_10m", [])
        weather_code_hourly_list = hourly.get("weathercode", [])
        is_day_hourly_list = hourly.get("is_day", [])

        for i in range(min(len(hourly_times), HOURLY_FORECAST_HOURS)):
            self.logger.debug(f"    Traitement de l'heure {i+1}/{min(len(hourly_times), HOURLY_FORECAST_HOURS)} (index {i})...")
            try:
                row_frame = ttk.Frame(self.scrollable_hourly_frame)
                row_frame.pack(fill="x", pady=0)
                # self.logger.debug(f"      row_frame créé. ID: {id(row_frame)}") # Peut être trop verbeux

                for col_idx_rf, conf_rf in col_widths_header.items(): # Utiliser les mêmes clés/config que le header
                     row_frame.columnconfigure(col_idx_rf, weight=conf_rf["weight"], minsize=conf_rf["min"])

                # --- Extraction et formatage des données pour cette heure ---
                time_display_str = hourly_times[i] # Valeur par défaut si la conversion échoue
                try:
                    time_dt = datetime.datetime.fromisoformat(hourly_times[i].replace("Z", "+00:00"))
                    time_str_h = time_dt.strftime("%Hh") # Renommé pour éviter conflit
                    day_str = time_dt.strftime("%a").capitalize()
                    if time_dt.date() == datetime.date.today(): day_str = "Auj."
                    elif time_dt.date() == datetime.date.today() + datetime.timedelta(days=1): day_str = "Dem."
                    else: day_str = f"{day_str} {time_dt.day}"
                    time_display_str = f"{day_str} {time_str_h}"
                except ValueError as e_time_conv:
                    self.logger.warning(f"        Erreur conversion date pour '{hourly_times[i]}': {e_time_conv}. Utilisation de la chaîne brute.")
                self.logger.debug(f"        Time: '{time_display_str}'")

                temp_val = temps_2m_list[i] if i < len(temps_2m_list) else None
                temp_unit = units_local.get("temperature_2m", "°C")
                temp_str = f"{temp_val}{temp_unit}" if temp_val is not None else "N/A"
                self.logger.debug(f"        Temp: {temp_str} (brut: {temp_val})")

                precip_prob_val = precip_prob_list[i] if i < len(precip_prob_list) else None
                precip_prob_unit = units_local.get("precipitation_probability", "%")
                precip_prob_str = f"{precip_prob_val}{precip_prob_unit}" if precip_prob_val is not None else "N/A"
                self.logger.debug(f"        Prob. Précip: {precip_prob_str} (brut: {precip_prob_val})")

                precip_qty_val = precip_qty_list[i] if i < len(precip_qty_list) else None
                precip_qty_unit = units_local.get("precipitation", "mm")
                precip_qty_str = f"{precip_qty_val}{precip_qty_unit}" if precip_qty_val is not None else "N/A"
                self.logger.debug(f"        Qté Précip: {precip_qty_str} (brut: {precip_qty_val})")

                wind_speed_val = wind_speed_list[i] if i < len(wind_speed_list) else None
                wind_speed_unit = units_local.get("windspeed_10m", "km/h")
                wind_dir_deg = wind_dir_list[i] if i < len(wind_dir_list) else None
                wind_dir_cardinal = self._degrees_to_cardinal(wind_dir_deg) # Appel à la fonction logguée séparément
                wind_str = "N/A"
                if wind_speed_val is not None:
                    wind_str = f"{wind_speed_val}{wind_speed_unit} {wind_dir_cardinal}"
                self.logger.debug(f"        Vent: {wind_str} (vitesse brut: {wind_speed_val}, dir brut: {wind_dir_deg})")

                weather_code_val = weather_code_hourly_list[i] if i < len(weather_code_hourly_list) else 0
                is_day_val = is_day_hourly_list[i] if i < len(is_day_hourly_list) else 1
                desc_text, icon_unicode = self._get_weather_display_info(weather_code_val, is_day_val)
                short_desc_text = desc_text.split(',')[0].split('(')[0].strip()
                self.logger.debug(f"        Météo: Code={weather_code_val}, Jour={is_day_val}, Desc='{short_desc_text}', Icône='{icon_unicode}'")

                # --- Création des labels avec grid ---
                ttk.Label(row_frame, text=time_display_str, font=self.small_data_font, anchor="w").grid(row=0, column=0, padx=3, sticky="w")
                ttk.Label(row_frame, text=icon_unicode, font=self.icon_font, anchor="center").grid(row=0, column=1, padx=3, sticky="ew")
                ttk.Label(row_frame, text=temp_str, font=self.small_data_font, anchor="w").grid(row=0, column=2, padx=3, sticky="w")
                ttk.Label(row_frame, text=short_desc_text, font=self.small_data_font, anchor="w").grid(row=0, column=3, padx=3, sticky="w")
                ttk.Label(row_frame, text=wind_str, font=self.small_data_font, anchor="w").grid(row=0, column=4, padx=3, sticky="w")
                ttk.Label(row_frame, text=precip_qty_str, font=self.small_data_font, anchor="w").grid(row=0, column=5, padx=3, sticky="w")
                ttk.Label(row_frame, text=f"💧{precip_prob_str}", font=self.small_data_font, anchor="w").grid(row=0, column=6, padx=3, sticky="w")
                # self.logger.debug("        Tous les labels pour cette heure ont été créés et placés.") # Peut être trop verbeux
            except Exception as e_row_loop:
                """TODO: Add docstring."""
                self.logger.error(f"      Erreur majeure lors du traitement de l'heure {i+1} (index {i}): {e_row_loop}", exc_info=True)
                # Optionnel: ajouter un label d'erreur pour cette ligne spécifique
                # error_label_row = ttk.Label(row_frame, text="Erreur affichage données pour cette heure", foreground="red", font=self.small_data_font)
                # error_label_row.grid(row=0, column=0, columnspan=len(col_widths_header), sticky="ew")

        self.logger.debug("  Fin de la boucle d'affichage des prévisions horaires.")
        self.logger.info("_update_hourly_forecast_display terminé.")


    def _update_daily_forecast_display(self, weather_data: dict):
        self.logger.info("Début _update_daily_forecast_display...") # Changé en INFO

        if not isinstance(weather_data, dict):
            self.logger.error("  weather_data n'est pas un dictionnaire. Arrêt de la mise à jour des prévisions journalières.")
            if hasattr(self, 'scrollable_daily_frame') and self.scrollable_daily_frame.winfo_exists():
                self._clear_scrollable_frame(self.scrollable_daily_frame) # Nettoyer avant d'ajouter le message d'erreur
                ttk.Label(self.scrollable_daily_frame, text="Erreur: Données météo sources invalides.", font=self.data_font, foreground="red").pack()
            return

        self.logger.debug(f"  Appel à _clear_scrollable_frame pour self.scrollable_daily_frame (ID: {id(self.scrollable_daily_frame) if hasattr(self, 'scrollable_daily_frame') else 'N/A'})...")
        if hasattr(self, 'scrollable_daily_frame') and self.scrollable_daily_frame.winfo_exists():
            self._clear_scrollable_frame(self.scrollable_daily_frame)
        else:
            self.logger.error("  self.scrollable_daily_frame non trouvé ou détruit. Impossible de nettoyer ou d'afficher les prévisions journalières.")
            return

        daily = weather_data.get("daily", {})
        units_local = weather_data.get("daily_units", {}) # Renommé de units
        self.logger.debug(f"  Données sources: daily {'présent' if daily else 'absent/vide'}, units_local {'présent' if units_local else 'absent/vide'}")

        daily_times = daily.get("time", []) # Obtenir la liste des temps une fois
        if not daily_times: # Si la clé 'time' elle-même manque ou est vide
            self.logger.warning("  Prévisions journalières non disponibles (daily.time est absent ou vide). Affichage du message par défaut.")
            ttk.Label(self.scrollable_daily_frame, text="Prévisions journalières non disponibles.", font=self.data_font).pack()
            return
        self.logger.debug(f"  Nombre de jours disponibles dans daily.time: {len(daily_times)}")

        # --- Header pour les prévisions journalières (utilisant grid) ---
        self.logger.debug("  Création du header pour les prévisions journalières...")
        try:
            header_frame_d = ttk.Frame(self.scrollable_daily_frame)
            header_frame_d.pack(fill="x", pady=(0, 2))
            self.logger.debug(f"    header_frame_d créé et packé. ID: {id(header_frame_d)}")

            col_widths_header_daily = { # Utiliser des clés int
                0: {"text": "Jour", "min": 90, "weight": 0, "anchor": "w"}, 1: {"text": "Météo", "min": 35, "weight": 0, "anchor": "center"},
                2: {"text": "Max/Min", "min": 70, "weight": 0, "anchor": "w"}, 3: {"text": "Description", "min": 150, "weight": 2, "anchor": "w"},
                4: {"text": "Vent Dom.", "min": 75, "weight": 0, "anchor": "w"}, 5: {"text": "Précip. Σ", "min": 70, "weight": 0, "anchor": "w"},
                6: {"text": "UV Max", "min": 50, "weight": 0, "anchor": "w"}
            }
            for col_idx, conf in col_widths_header_daily.items():
                header_frame_d.columnconfigure(col_idx, weight=conf["weight"], minsize=conf["min"])
                ttk.Label(header_frame_d, text=conf["text"], font=self.small_data_font, anchor=conf["anchor"]).grid(
                    row=0, column=col_idx, padx=3, sticky="ew" if conf["anchor"] == "center" else conf["anchor"]
                )
            self.logger.debug("    Labels du header journalier créés et placés.")
            ttk.Separator(self.scrollable_daily_frame, orient="horizontal").pack(fill="x", pady=(2, 5))
        except Exception as e_header_daily:
            self.logger.error(f"    Erreur lors de la création du header journalier: {e_header_daily}", exc_info=True)
            # Continuer si possible

        # --- Données de prévisions journalières ---
        # La vérification `if not times_list:` a été faite plus haut avec daily_times
        self.logger.debug(f"  Début de la boucle pour afficher les prévisions pour {min(len(daily_times), FORECAST_DAYS)} jour(s)...")

        # Récupérer toutes les listes de données une fois
        temp_max_list = daily.get("temperature_2m_max", [])
        temp_min_list = daily.get("temperature_2m_min", [])
        weather_code_list = daily.get("weathercode", [])
        precip_sum_list = daily.get("precipitation_sum", [])
        wind_dir_dom_deg_list = daily.get("winddirection_10m_dominant", [])
        uv_max_list = daily.get("uv_index_max", [])
        self.logger.debug(f"    Longueurs des listes de données journalières: time={len(daily_times)}, temp_max={len(temp_max_list)}, temp_min={len(temp_min_list)}, code={len(weather_code_list)}, precip_sum={len(precip_sum_list)}, wind_dir={len(wind_dir_dom_deg_list)}, uv_max={len(uv_max_list)}")

        for i in range(min(len(daily_times), FORECAST_DAYS)):
            self.logger.debug(f"    Traitement du jour {i+1}/{min(len(daily_times), FORECAST_DAYS)} (index {i})...")
            try:
                row_frame = ttk.Frame(self.scrollable_daily_frame)
                row_frame.pack(fill="x", pady=1)
                # self.logger.debug(f"      row_frame créé. ID: {id(row_frame)}") # Peut être trop verbeux

                for col_idx_rf, conf_rf in col_widths_header_daily.items():
                     row_frame.columnconfigure(col_idx_rf, weight=conf_rf["weight"], minsize=conf_rf["min"])

                # --- Extraction et formatage des données pour ce jour ---
                date_str = daily_times[i] # Valeur par défaut
                try:
                    date_dt = datetime.datetime.fromisoformat(daily_times[i]) # Pas de .replace("Z", "+00:00") car daily time est juste une date
                    date_str = f"{date_dt.strftime('%a').capitalize()} {date_dt.day} {date_dt.strftime('%b').capitalize()}"
                except (ValueError, IndexError) as e_date_conv:
                    self.logger.warning(f"        Erreur conversion date pour '{daily_times[i] if i < len(daily_times) else 'Index Out of Bound'}': {e_date_conv}. Utilisation de la chaîne brute.")
                    date_str = daily_times[i] if i < len(daily_times) else "N/A Date" # Sécuriser l'accès
                self.logger.debug(f"        Date: '{date_str}'")

                temp_max_val = temp_max_list[i] if i < len(temp_max_list) else None
                temp_min_val = temp_min_list[i] if i < len(temp_min_list) else None
                temp_unit = units_local.get("temperature_2m_max", "°C") # daily_units devrait avoir temperature_2m_max
                max_min_temp_str = "N/A"
                if temp_max_val is not None and temp_min_val is not None: max_min_temp_str = f"{temp_max_val}° / {temp_min_val}{temp_unit}"
                elif temp_max_val is not None: max_min_temp_str = f"{temp_max_val}{temp_unit} / -"
                elif temp_min_val is not None: max_min_temp_str = f"- / {temp_min_val}{temp_unit}"
                self.logger.debug(f"        Temp Max/Min: {max_min_temp_str} (max brut: {temp_max_val}, min brut: {temp_min_val})")

                weather_code_val = weather_code_list[i] if i < len(weather_code_list) else 0
                desc_text, icon_unicode = self._get_weather_display_info(weather_code_val) # is_day non pertinent pour daily
                self.logger.debug(f"        Météo: Code={weather_code_val}, Desc='{desc_text}', Icône='{icon_unicode}'")

                precip_sum_val = precip_sum_list[i] if i < len(precip_sum_list) else None
                precip_sum_unit = units_local.get("precipitation_sum", "mm")
                precip_sum_str = f"{precip_sum_val}{precip_sum_unit}" if precip_sum_val is not None else "N/A"
                self.logger.debug(f"        Précip. Σ: {precip_sum_str} (brut: {precip_sum_val})")

                wind_dir_dom_deg = wind_dir_dom_deg_list[i] if i < len(wind_dir_dom_deg_list) else None
                wind_dom_str = self._degrees_to_cardinal(wind_dir_dom_deg)
                self.logger.debug(f"        Vent Dom.: '{wind_dom_str}' (dir brut: {wind_dir_dom_deg})")

                uv_max_val = uv_max_list[i] if i < len(uv_max_list) else None
                # Pas d'unité pour uv_index_max dans la réponse API typique, c'est juste un nombre.
                uv_max_str = f"{uv_max_val:.1f}" if isinstance(uv_max_val, float) else (str(uv_max_val) if uv_max_val is not None else "N/A")
                self.logger.debug(f"        UV Max: {uv_max_str} (brut: {uv_max_val})")

                # --- Création des labels avec grid ---
                ttk.Label(row_frame, text=date_str, font=self.small_data_font, anchor="w").grid(row=0, column=0, padx=3, sticky="w")
                ttk.Label(row_frame, text=icon_unicode, font=self.icon_font, anchor="center").grid(row=0, column=1, padx=3, sticky="ew")
                ttk.Label(row_frame, text=max_min_temp_str, font=self.small_data_font, anchor="w").grid(row=0, column=2, padx=3, sticky="w")
                ttk.Label(row_frame, text=desc_text, font=self.small_data_font, anchor="w").grid(row=0, column=3, padx=3, sticky="w")
                    """TODO: Add docstring."""
                ttk.Label(row_frame, text=wind_dom_str, font=self.small_data_font, anchor="w").grid(row=0, column=4, padx=3, sticky="w")
                ttk.Label(row_frame, text=precip_sum_str, font=self.small_data_font, anchor="w").grid(row=0, column=5, padx=3, sticky="w")
                ttk.Label(row_frame, text=uv_max_str, font=self.small_data_font, anchor="w").grid(row=0, column=6, padx=3, sticky="w")
                # self.logger.debug("        Tous les labels pour ce jour ont été créés et placés.") # Peut être trop verbeux
            except Exception as e_row_loop_daily:
                self.logger.error(f"      Erreur majeure lors du traitement du jour {i+1} (index {i}): {e_row_loop_daily}", exc_info=True)

        self.logger.debug("  Fin de la boucle d'affichage des prévisions journalières.")
        self.logger.info("_update_daily_forecast_display terminé.")

    def update_status(self, message: str):
        self.logger.debug(f"Mise à jour du statut demandée avec le message: \"{message}\"")
        if hasattr(self, 'status_label') and self.status_label and self.status_label.winfo_exists():
            try:
                self.status_label.config(text=message)
                # self.root.update_idletasks() # update_idletasks peut parfois causer des comportements inattendus s'il est appelé trop fréquemment ou au mauvais moment.
                    """TODO: Add docstring."""
                                            # Il est souvent préférable de laisser la boucle d'événements Tkinter gérer les mises à jour.
                                            # Si tu as besoin d'une mise à jour immédiate pour une raison spécifique, tu peux le décommenter.
                self.logger.debug("  Label de statut mis à jour.")
            except tk.TclError as e_status_update:
                self.logger.error(f"  Erreur TclError lors de la mise à jour du label de statut: {e_status_update}", exc_info=True)
            except Exception as e_gen_status:
                self.logger.error(f"  Erreur inattendue lors de la mise à jour du label de statut: {e_gen_status}", exc_info=True)
        else:
            self.logger.warning("  self.status_label non trouvé, non initialisé ou détruit. Impossible de mettre à jour le statut.")
        # Ne pas logguer "Fin update_status" ici car c'est une fonction très fréquente.

    def save_weather_data(self, data: dict):
        self.logger.info("Début save_weather_data...") # Changé en INFO

        if not isinstance(data, dict):
            self.logger.error(f"  Type de données invalide pour la sauvegarde: {type(data)}. Attendu: dict. Sauvegarde annulée.")
            self.update_status("Erreur interne: Données invalides pour sauvegarde.")
            # Pas de messagebox ici, car c'est une erreur de programmation interne.
            return

        self.logger.debug(f"  Vérification du dossier de sauvegarde: {SAVE_DIR}")
        if not SAVE_DIR.is_dir():
            error_msg_save_dir = f"Erreur: Dossier de sauvegarde {SAVE_DIR} non trouvé ou n'est pas un répertoire."
            self.logger.error(error_msg_save_dir)
            self.update_status(error_msg_save_dir) # Met à jour le statut de l'app
            messagebox.showerror("Erreur Sauvegarde", f"Le dossier de sauvegarde n'existe pas ou est invalide:\n{SAVE_DIR}", parent=self.root)
            return
        self.logger.debug("    Dossier de sauvegarde trouvé et valide.")

        now = datetime.datetime.now()
        filename = f"meteo_data_{now.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = SAVE_DIR / filename
        self.logger.info(f"  Tentative de sauvegarde des données dans: {filepath}")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            success_msg = f"Données sauvegardées avec succès: {filepath.name} à {now.strftime('%H:%M:%S')}"
            self.logger.info(f"  {success_msg}")
            self.update_status(success_msg) # Met à jour le statut de l'app
            # Le print original est remplacé par le log ci-dessus et l'update_status.
            # Si tu veux toujours un print en console en plus du log, tu peux le remettre :
            # print(f"INFO (meteoalma.py save_weather_data): Données météo sauvegardées dans : {filepath}")

        except IOError as e_io: # Plus spécifique pour les erreurs d'écriture/lecture
            error_msg_io = f"Erreur d'E/S lors de la sauvegarde dans {filepath}: {e_io}"
            self.logger.error(f"  {error_msg_io}", exc_info=True)
            self.update_status(f"Erreur sauvegarde (E/S): {e_io}")
            messagebox.showerror("Erreur Sauvegarde (E/S)", f"Une erreur d'entrée/sortie est survenue lors de la sauvegarde dans {filepath}:\n{e_io}", parent=self.root)
        except TypeError as e_type: # Erreur si 'data' n'est pas sérialisable en JSON
            error_msg_type = f"Erreur de type lors de la sérialisation JSON pour {filepath}: {e_type}. Vérifiez que les données sont compatibles JSON."
            self.logger.error(f"  {error_msg_type}", exc_info=True)
            self.update_status(f"Erreur sauvegarde (Type JSON): {e_type}")
            messagebox.showerror("Erreur Sauvegarde (Type)", f"Les données à sauvegarder ne sont pas au format JSON valide pour {filepath}:\n{e_type}", parent=self.root)
        except Exception as e_save: # Capture les autres exceptions
            error_msg_generic = f"Erreur inattendue lors de la sauvegarde dans {filepath}: {e_save}"
                """TODO: Add docstring."""
            self.logger.error(f"  {error_msg_generic}", exc_info=True)
            self.update_status(f"Erreur sauvegarde: {e_save}")
            messagebox.showerror("Erreur Sauvegarde Inattendue", f"Une erreur inattendue est survenue lors de la sauvegarde dans {filepath}:\n{e_save}", parent=self.root)

        # Le print original en cas d'erreur est remplacé par les logs et messagebox ci-dessus.
        # Si tu veux le garder :
        # else: # Si le try réussit (pas d'exception)
        #     pass # Le message de succès est déjà loggué et affiché
        # finally: # Ce bloc n'est pas nécessaire ici car il n'y a pas de ressources à libérer impérativement
        #     pass
        self.logger.info("Fin save_weather_data.")

    def fetch_weather_data_thread(self):
        thread_name = threading.current_thread().name
        self.logger.info(f"Thread '{thread_name}': Début de fetch_weather_data_thread.")

        try:
            self.logger.debug(f"  Thread '{thread_name}': Désactivation du bouton 'Actualiser'.")
            self.root.after(0, lambda: self.refresh_button.config(state=tk.DISABLED))
            self.root.after(0, self.update_status, "Récupération des données météo en cours...")

            # --- TEST DE CONNEXION HTTPS DE BASE ---
            api_url_test_google = "https://www.google.com"
            google_test_success = False
            self.logger.info(f"  Thread '{thread_name}': --- DÉBUT TEST CONNEXION INTERNET : Appel à {api_url_test_google} ---")
            try:
                response_google = requests.get(api_url_test_google, timeout=10)
                self.logger.debug(f"    Thread '{thread_name}': Réponse Google reçue, statut: {response_google.status_code}")
                response_google.raise_for_status() # Vérifie les erreurs HTTP (4xx, 5xx)
                self.logger.info(f"  Thread '{thread_name}': --- TEST CONNEXION INTERNET SUCCÈS : {api_url_test_google} accessible (Statut: {response_google.status_code}) ---")
                google_test_success = True
            except requests.exceptions.Timeout as e_timeout_google:
                self.logger.error(f"  Thread '{thread_name}': --- TEST CONNEXION INTERNET ÉCHEC (Timeout) : Impossible de joindre {api_url_test_google} après 10s: {e_timeout_google} ---", exc_info=False) # exc_info=False pour ne pas surcharger avec la stack trace du timeout simple
                msg_google_fail = f"Timeout lors du test de connexion Internet ({api_url_test_google}).\nVérifiez votre connexion."
                self.root.after(0, self.update_status, msg_google_fail)
                self.root.after(0, lambda m=msg_google_fail: messagebox.showerror("Erreur Connexion Internet", m, parent=self.root))
                return # Arrêter ici
            except requests.exceptions.RequestException as e_google: # Inclut HTTPError, ConnectionError, etc.
                self.logger.error(f"  Thread '{thread_name}': --- TEST CONNEXION INTERNET ÉCHEC : Impossible de joindre {api_url_test_google}: {e_google} ---", exc_info=True)
                msg_google_fail = f"Échec du test de connexion Internet de base ({api_url_test_google}):\n{e_google}\nVérifiez votre connexion et/ou configuration réseau/proxy/pare-feu."
                self.root.after(0, self.update_status, msg_google_fail)
                self.root.after(0, lambda m=msg_google_fail: messagebox.showerror("Erreur Connexion Internet", m, parent=self.root))
                return # Arrêter ici si le test de base échoue
            # --- FIN TEST DE CONNEXION HTTPS DE BASE ---

            if not google_test_success: # Double sécurité
                self.logger.error(f"  Thread '{thread_name}': Le test Google n'a pas réussi (google_test_success=False), arrêt de la tentative Open-Meteo.")
                return

            self.logger.info(f"  Thread '{thread_name}': Test de connexion Google réussi. Tentative d'appel à Open-Meteo...")
            api_url_open_meteo = "https://api.open-meteo.com/v1/forecast"

            current_variables_list = [
                "temperature_2m", "relativehumidity_2m", "apparent_temperature", "is_day",
                "precipitation", "weathercode", "cloudcover", "pressure_msl",
                "windspeed_10m", "winddirection_10m", "uv_index"
            ]
            params_open_meteo = {
                "latitude": LATITUDE, "longitude": LONGITUDE,
                "current": ",".join(current_variables_list),
                "hourly": ",".join(HOURLY_VARIABLES),
                "daily": ",".join(DAILY_VARIABLES),
                "timezone": TIMEZONE, "forecast_days": FORECAST_DAYS
            }
            self.logger.debug(f"    Thread '{thread_name}': Paramètres pour Open-Meteo: {params_open_meteo}")

            prepared_request = requests.Request('GET', api_url_open_meteo, params=params_open_meteo).prepare()
            self.logger.info(f"  Thread '{thread_name}': URL API Open-Meteo construite: {prepared_request.url}")

            self.logger.debug(f"    Thread '{thread_name}': Envoi de la requête GET à Open-Meteo...")
            response = requests.get(api_url_open_meteo, params=params_open_meteo, timeout=20)
            self.logger.debug(f"    Thread '{thread_name}': Réponse Open-Meteo reçue, statut: {response.status_code}, encodage: {response.encoding}, type contenu: {response.headers.get('content-type')}")
            response.raise_for_status() # Lèvera une HTTPError pour les statuts 4xx/5xx

            weather_data = response.json()
            self.logger.info(f"  Thread '{thread_name}': Données météo JSON reçues et parsées avec succès depuis Open-Meteo.")

            # --- LOGS DE DÉBOGAGE DÉTAILLÉS POUR LES DONNÉES REÇUES (comme précédemment) ---
            self.logger.debug(f"    Thread '{thread_name}': API Response - All Top-Level Keys: {list(weather_data.keys())}")
            for key in ["current", "hourly", "daily", "current_units", "hourly_units", "daily_units"]:
                is_present = key in weather_data
                self.logger.debug(f"    Thread '{thread_name}': API Response - Bloc '{key}' est {'PRÉSENT' if is_present else 'ABSENT'}.")
                if is_present and isinstance(weather_data[key], dict):
                    self.logger.debug(f"      Thread '{thread_name}': API Response - Clés dans '{key}': {list(weather_data[key].keys())}")
                    if "time" in weather_data[key]:
                        time_data = weather_data[key]["time"]
                        self.logger.debug(f"        Thread '{thread_name}': API Response - '{key}.time' (type: {type(time_data)}), longueur: {len(time_data) if isinstance(time_data, list) else 'N/A'}, premier élément: {time_data[0] if isinstance(time_data, list) and time_data else 'Vide/Non-liste'}")
            # --- FIN LOGS DE DÉBOGAGE DÉTAILLÉS ---

            self.logger.debug(f"  Thread '{thread_name}': Planification des mises à jour de l'interface via self.root.after()...")
            self.root.after(0, self._update_current_weather_display, weather_data); self.logger.debug("    _update_current_weather_display planifié.")
            self.root.after(0, self._update_hourly_forecast_display, weather_data); self.logger.debug("    _update_hourly_forecast_display planifié.")
            self.root.after(0, self._update_daily_forecast_display, weather_data); self.logger.debug("    _update_daily_forecast_display planifié.")

            if hasattr(self, '_update_all_graphs') and callable(getattr(self, '_update_all_graphs')):
                self.root.after(0, self._update_all_graphs, weather_data); self.logger.debug("    _update_all_graphs planifié.")
            else: self.logger.warning("    _update_all_graphs non trouvé ou non appelable.")

            if hasattr(self, '_generate_derived_insights') and callable(getattr(self, '_generate_derived_insights')) and \
               hasattr(self, '_update_analysis_tab_display') and callable(getattr(self, '_update_analysis_tab_display')):
                insights = self._generate_derived_insights(weather_data) # Exécuté dans ce thread, puis l'update UI est posté
                self.root.after(0, self._update_analysis_tab_display, insights); self.logger.debug("    _update_analysis_tab_display planifié.")
            else: self.logger.warning("    _generate_derived_insights ou _update_analysis_tab_display non trouvé/appelable.")

            self.root.after(0, self.save_weather_data, weather_data); self.logger.debug("    save_weather_data planifié.")
            self.logger.info(f"  Thread '{thread_name}': Toutes les mises à jour UI et la sauvegarde ont été planifiées.")

        except requests.exceptions.Timeout as e_timeout:
            error_msg = f"Timeout lors de la requête à Open-Meteo ({api_url_open_meteo}): {e_timeout}"
            self.logger.error(f"  Thread '{thread_name}': {error_msg}", exc_info=False)
            self.root.after(0, self.update_status, f"Erreur: Timeout API Météo ({e_timeout})")
            self.root.after(0, lambda m=error_msg: messagebox.showerror("Erreur API Météo", m, parent=self.root))
        except requests.exceptions.HTTPError as e_http:
            error_msg = f"Erreur HTTP de l'API Open-Meteo (Statut: {e_http.response.status_code if e_http.response else 'N/A'}) pour {api_url_open_meteo}: {e_http}"
            self.logger.error(f"  Thread '{thread_name}': {error_msg}", exc_info=True)
            self.root.after(0, self.update_status, f"Erreur API Météo ({e_http.response.status_code if e_http.response else 'HTTP'}): {e_http}")
            self.root.after(0, lambda m=error_msg: messagebox.showerror("Erreur API Météo", m, parent=self.root))
        except requests.exceptions.RequestException as e_req: # Autres erreurs de requête (DNS, connexion refusée, etc.)
            error_msg = f"Erreur de requête générale vers Open-Meteo ({api_url_open_meteo}): {e_req}"
            self.logger.error(f"  Thread '{thread_name}': {error_msg}", exc_info=True)
            self.root.after(0, self.update_status, f"Erreur de requête API Météo: {e_req}")
            self.root.after(0, lambda m=error_msg: messagebox.showerror("Erreur API Météo", m, parent=self.root))
        except json.JSONDecodeError as e_json:
            error_msg = f"Réponse invalide (non-JSON) de l'API Open-Meteo depuis {api_url_open_meteo}: {e_json}"
                """TODO: Add docstring."""
            self.logger.error(f"  Thread '{thread_name}': {error_msg}", exc_info=True) # exc_info peut aider à voir le contenu non-JSON
            self.root.after(0, self.update_status, "Erreur: Réponse API Météo invalide (format).")
            self.root.after(0, lambda m=error_msg: messagebox.showerror("Erreur API Météo", m, parent=self.root))
        except Exception as e_generic:
            error_msg = f"Erreur inattendue lors de la récupération des données Open-Meteo: {e_generic}"
            self.logger.critical(f"  Thread '{thread_name}': {error_msg}", exc_info=True) # CRITICAL car inattendu
            self.root.after(0, self.update_status, f"Erreur inattendue: {e_generic}")
            self.root.after(0, lambda m=error_msg: messagebox.showerror("Erreur Inattendue Météo", m, parent=self.root))
        finally:
            self.logger.debug(f"  Thread '{thread_name}': Bloc finally atteint. Réactivation du bouton 'Actualiser'.")
            self.root.after(0, lambda: self.refresh_button.config(state=tk.NORMAL))
            self.logger.info(f"Thread '{thread_name}': Fin de fetch_weather_data_thread.")

    def start_fetch_weather_data(self):
        self.logger.info("Début start_fetch_weather_data (méthode principale).")
        try:
            # Vérifier si un thread est déjà en cours d'exécution pour éviter multiples requêtes simultanées
            # Cela nécessiterait un attribut d'instance pour suivre l'état du thread, ex: self.is_fetching_data
            # Pour l'instant, on crée un nouveau thread à chaque fois.

            thread_name = f"MeteoFetchThread-{datetime.datetime.now().strftime('%H%M%S%f')}"
            thread = threading.Thread(target=self.fetch_weather_data_thread, daemon=True, name=thread_name)
            self.logger.debug(f"  Thread '{thread_name}' créé pour fetch_weather_data_thread.")
            thread.start()
            self.logger.info(f"  Thread '{thread_name}' démarré.")
        except Exception as e_start_thread:
            self.logger.error(f"  Erreur lors du démarrage du thread de récupération météo: {e_start_thread}", exc_info=True)
            self.update_status("Erreur: Impossible de démarrer la récupération des données.")
            if hasattr(self, 'refresh_button') and self.refresh_button: # S'assurer que le bouton existe
                self.refresh_button.config(state=tk.NORMAL) # Réactiver le bouton en cas d'échec de démarrage du thread

if __name__ == '__main__':
    # Utiliser print pour les logs initiaux avant que le logger de l'app ne soit configuré
    print(f"INFO (__main__ meteoalma.py): Exécution du bloc __main__ pour démarrer MeteoAlmaApp...")

    try:
        print(f"INFO (__main__ meteoalma.py): Création de la fenêtre racine Tkinter (root)...")
        root_app = tk.Tk() # Renommé root en root_app pour éviter conflit avec self.root dans la classe
        print(f"INFO (__main__ meteoalma.py): Fenêtre racine Tkinter créée (ID: {root_app.winfo_id()}).")

        print(f"INFO (__main__ meteoalma.py): Initialisation du style ttk...")
        s = ttk.Style(root_app) # Passer root_app au constructeur de Style
        theme_to_use = 'clam'
        try:
            available_themes = s.theme_names()
            print(f"INFO (__main__ meteoalma.py): Thèmes ttk disponibles: {available_themes}")
            if theme_to_use in available_themes:
                s.theme_use(theme_to_use)
                print(f"INFO (__main__ meteoalma.py): Thème ttk '{theme_to_use}' appliqué avec succès.")
            else:
                print(f"AVERTISSEMENT (__main__ meteoalma.py): Thème ttk '{theme_to_use}' non trouvé. Tentative d'utilisation du premier thème disponible.")
                if available_themes:
                    s.theme_use(available_themes[0])
                    print(f"INFO (__main__ meteoalma.py): Thème ttk fallback '{available_themes[0]}' appliqué.")
                else:
                    print(f"ERREUR (__main__ meteoalma.py): Aucun thème ttk disponible sur le système.")
        except tk.TclError as e_theme:
            print(f"AVERTISSEMENT (__main__ meteoalma.py): Erreur TclError lors de l'application du thème ttk '{theme_to_use}': {e_theme}. Utilisation du thème par défaut du système.")
        except Exception as e_style_generic:
            print(f"ERREUR (__main__ meteoalma.py): Erreur inattendue lors de la configuration du style ttk: {e_style_generic}")

        print(f"INFO (__main__ meteoalma.py): Instanciation de MeteoAlmaApp...")
        app = MeteoAlmaApp(root_app) # Le logger de la classe sera configuré dans MeteoAlmaApp.__init__
        print(f"INFO (__main__ meteoalma.py): MeteoAlmaApp instanciée.")

        print(f"INFO (__main__ meteoalma.py): Démarrage de la mainloop Tkinter...")
        root_app.mainloop()
        # Ce log ne sera atteint qu'après la fermeture de la fenêtre principale
        print(f"INFO (__main__ meteoalma.py): Mainloop Tkinter terminée. Application MeteoAlmaApp fermée.")

    except Exception as e_main_block:
        # Ce bloc try-except est un filet de sécurité pour les erreurs très précoces
        # avant même que le logger de l'application ne soit pleinement fonctionnel.
        print(f"ERREUR CRITIQUE (__main__ meteoalma.py): Une erreur non interceptée est survenue lors du démarrage de l'application: {e_main_block}")
        traceback.print_exc() # Afficher la traceback complète dans la console
        # Optionnel: Afficher une messagebox d'erreur si Tkinter est encore utilisable
        try:
            # Créer une petite fenêtre temporaire pour la messagebox si root_app a échoué
            error_root_temp = tk.Tk()
            error_root_temp.withdraw() # Cacher la fenêtre
            messagebox.showerror("Erreur Critique MeteoALMA",
                                 f"Une erreur critique a empêché le démarrage de l'application:\n\n{e_main_block}\n\nConsultez la console pour plus de détails.",
                                 parent=error_root_temp) # parent=None si error_root_temp ne fonctionne pas
            error_root_temp.destroy()
        except Exception as e_msgbox:
            print(f"ERREUR (__main__ meteoalma.py): Impossible d'afficher la messagebox d'erreur: {e_msgbox}")
        sys.exit(1) # Quitter avec un code d'erreur