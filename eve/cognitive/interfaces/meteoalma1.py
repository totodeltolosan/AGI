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
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'french')
    except locale.Error:
        print("Attention: Impossible de configurer la locale en français pour les dates.")

# Configuration
LATITUDE = 44.81985684111081
LONGITUDE = 1.2147718587283332

# ALMA_BASE_DIR est maintenant déterminé par le bloc de contournement sys.path
# ou par le fallback s'il est utilisé dans ce script autonome.
# On le redéfinit ici pour clarté, en utilisant la même logique que le contournement.
# S'assurer que ALMA_BASE_DIR est un objet Path.
_alma_base_dir_init_found = False
_alma_base_dir_for_script: Path
if '__file__' in globals():
    _current_script_path_init = Path(__file__).resolve()
    _candidate1_init = _current_script_path_init.parent
    _candidate_root1_init = _candidate_parent1.parent
    _candidate_root2_init = _current_script_path_init.parent
    if (_candidate_root1_init / "venv").is_dir(): # Check venv existence as part of root detection
        _alma_base_dir_for_script = _candidate_root1_init
        _alma_base_dir_init_found = True
    elif (_candidate_root2_init / "venv").is_dir():
        _alma_base_dir_for_script = _candidate_root2_init
        _alma_base_dir_init_found = True
if not _alma_base_dir_init_found:
    _alma_base_dir_for_script = Path("/home/toni/Documents/ALMA") # Fallback
ALMA_BASE_DIR = _alma_base_dir_for_script # Assigner à la globale utilisée plus bas

SAVE_DIR = ALMA_BASE_DIR / "Connaissance" / "Environnement" / "Meteo"

HOURLY_VARIABLES = [
    "temperature_2m", "relativehumidity_2m", "apparent_temperature", "precipitation_probability",
    "precipitation", "weathercode", "pressure_msl", "cloudcover", "windspeed_10m",
    "winddirection_10m", "is_day", "uv_index"
]
DAILY_VARIABLES = [
    "weathercode", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset",
    "precipitation_sum", "uv_index_max"
]
TIMEZONE = "auto"
FORECAST_DAYS = 7
HOURLY_FORECAST_HOURS = 24

# Mapping des codes WMO vers (description française, caractère Unicode)
WMO_CODES: Dict[int, Tuple[str, str]] = {
    0: ("Ciel dégagé", "☀️"),
    1: ("Principalement clair", "🌤️"),
    2: ("Partiellement nuageux", "🌥️"),
    3: ("Couvert", "☁️"),
    45: ("Brouillard", "🌫️"),
    48: ("Brouillard givrant", "🌫️❄️"),
    51: ("Bruine légère", "💧"),
    53: ("Bruine modérée", "💧"),
    55: ("Bruine dense", "💧"),
    56: ("Bruine verglaçante légère", "🧊💧"),
    57: ("Bruine verglaçante dense", "🧊💧"),
    61: ("Pluie légère", "🌧️"),
    63: ("Pluie modérée", "🌧️"),
    65: ("Pluie forte", "🌧️"),
    66: ("Pluie verglaçante légère", "🧊🌧️"),
    67: ("Pluie verglaçante forte", "🧊🌧️"),
    71: ("Neige légère", "🌨️"),
    73: ("Neige modérée", "🌨️"),
    75: ("Neige forte", "🌨️"),
    77: ("Grains de neige", "❄️"),
    80: ("Averses légères", "🌦️"),
    81: ("Averses modérées", "🌦️"),
    82: ("Averses violentes", "🌦️"),
    85: ("Averses de neige légères", "🌨️"),
    86: ("Averses de neige fortes", "🌨️"),
    95: ("Orage", "🌩️"), # Orage: Léger ou modéré
    96: ("Orage avec grêle légère", "🌩️🧊"),
    99: ("Orage avec grêle forte", "🌩️🧊"),
}
DEFAULT_WEATHER_ICON = "❓"
DEFAULT_WEATHER_DESCRIPTION = "Inconnu"

class MeteoAlmaApp:
    def __init__(self, root_window):
        self.root = root_window
        self.logger = logging.getLogger("MeteoAlmaApp")
        # Optionnel: Définir un niveau pour ce logger spécifique si besoin
        # self.logger.setLevel(logging.DEBUG)

        self.root.title("ALMA Météo")
        self.root.geometry("850x700")

        # Initialisation des attributs pour les graphiques à None
        # Graphique Températures
        self.temp_figure: Optional[Figure] = None
        self.temp_ax: Optional[Any] = None
        self.temp_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None

        # Graphique Humidité
        self.humidity_figure: Optional[Figure] = None
        self.humidity_ax: Optional[Any] = None
        self.humidity_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None

        # Graphique Précipitations
        self.precip_figure: Optional[Figure] = None
        self.precip_ax_qty: Optional[Any] = None
        self.precip_ax_prob: Optional[Any] = None
        self.precip_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None

        # Graphique Vent
        self.wind_figure: Optional[Figure] = None
        self.wind_ax: Optional[Any] = None
        self.wind_graph_canvas_widget: Optional[FigureCanvasTkAgg] = None

        # Initialisation pour l'onglet Analyses & Alertes
        self.analysis_labels: List[ttk.Label] = [] # <--- AJOUT DE CETTE LIGNE

        # Les autres attributs d'instance (fonts, labels pour les données actuelles, etc.)
        # seront créés dans _setup_ui et _setup_current_weather_ui.
        # Par exemple, self.status_label, self.current_weather_labels, etc.

        self._setup_ui() # Crée l'interface, y compris l'appel à _setup_graphs_tab_content et _setup_analysis_tab_content

        try:
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Dossier de sauvegarde vérifié/créé: {SAVE_DIR}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du dossier de sauvegarde {SAVE_DIR}: {e}", exc_info=True)
            messagebox.showerror("Erreur Création Dossier", f"Impossible de créer le dossier de sauvegarde {SAVE_DIR}:\n{e}", parent=self.root)
            # self.update_status est appelé après _setup_ui, donc si _setup_ui n'est pas encore passé,
            # self.status_label n'existe pas. Le messagebox est le feedback principal ici.

        # self.update_status est appelé après _setup_ui où self.status_label est créé
        self.update_status("Prêt. Chargement des données initiales...")
        self.start_fetch_weather_data()
        self.logger.info("MeteoAlmaApp initialisée.")

    def _on_mousewheel(self, event, canvas: tk.Canvas):
        # Sous Linux, event.delta est souvent 120 ou -120.
        # canvas.yview_scroll prend le nombre d'UNITÉS à scroller, pas de pixels.
        # Unités négatives pour scroller vers le haut, positives vers le bas.
        if event.num == 5 or event.delta < 0: # Molette vers le bas (Linux: button 5)
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0: # Molette vers le haut (Linux: button 4)
            canvas.yview_scroll(-1, "units")

    def _bind_mousewheel_to_children(self, widget_or_frame, canvas: tk.Canvas):
        widget_or_frame.bind('<Enter>', lambda e, c=canvas: self._bind_mousewheel_events(c))
        widget_or_frame.bind('<Leave>', lambda e, c=canvas: self._unbind_mousewheel_events(c))
        for child in widget_or_frame.winfo_children():
            self._bind_mousewheel_to_children(child, canvas) # Récursif

    def _bind_mousewheel_events(self, canvas: tk.Canvas):
        # Linux utilise Button-4 et Button-5 pour la molette
        canvas.bind_all("<Button-4>", lambda e, c=canvas: self._on_mousewheel(e, c))
        canvas.bind_all("<Button-5>", lambda e, c=canvas: self._on_mousewheel(e, c))
        # Windows/macOS utilisent MouseWheel
        canvas.bind_all("<MouseWheel>", lambda e, c=canvas: self._on_mousewheel(e, c))

    def _unbind_mousewheel_events(self, canvas: tk.Canvas):
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        canvas.unbind_all("<MouseWheel>")


    def _get_weather_display_info(self, weather_code: int, is_day: Optional[int] = 1) -> Tuple[str, str]:
        description, unicode_char = WMO_CODES.get(weather_code, (DEFAULT_WEATHER_DESCRIPTION, DEFAULT_WEATHER_ICON))
        if weather_code == 0 and is_day == 0:
            return "Ciel dégagé (nuit)", "🌙"
        return description, unicode_char

    def _setup_ui(self):
        style = ttk.Style(self.root)
        try: style.theme_use("clam")
        except tk.TclError: pass

        self.title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.data_font = tkfont.Font(family="Segoe UI", size=9)
        self.small_data_font = tkfont.Font(family="Segoe UI", size=8)
        self.icon_font = tkfont.Font(family="Segoe UI Symbol", size=18) # Police pour icônes Unicode

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.columnconfigure(0, weight=1) # Permettre au notebook de s'étendre

        top_bar_frame = ttk.Frame(main_frame)
        top_bar_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        top_bar_frame.columnconfigure(1, weight=1) # Permettre au label de statut de s'étendre

        self.refresh_button = ttk.Button(top_bar_frame, text="Actualiser", command=self.start_fetch_weather_data)
        self.refresh_button.grid(row=0, column=0, padx=(0,10))
        self.status_label = ttk.Label(top_bar_frame, text="Prêt.", anchor="w")
        self.status_label.grid(row=0, column=1, sticky="ew")

        # --- Notebook pour les différents affichages ---
        self.data_notebook = ttk.Notebook(main_frame) # Stocker comme attribut d'instance
        self.data_notebook.grid(row=1, column=0, sticky="nsew", pady=5)
        main_frame.rowconfigure(1, weight=1) # Permettre au notebook de s'étendre verticalement

        # --- Onglet: Actuellement ---
        self.current_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.current_tab, text=' Actuellement ')
        self._setup_current_weather_ui(self.current_tab)

        # --- Onglet: Prévisions Horaires ---
        self.hourly_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.hourly_tab, text=' Prévisions Horaires ')
        self.hourly_canvas = tk.Canvas(self.hourly_tab, highlightthickness=0)
        self.hourly_scrollbar = ttk.Scrollbar(self.hourly_tab, orient="vertical", command=self.hourly_canvas.yview)
        self.scrollable_hourly_frame = ttk.Frame(self.hourly_canvas)
        self.scrollable_hourly_frame.bind("<Configure>", lambda e, c=self.hourly_canvas: c.configure(scrollregion=c.bbox("all")))
        self.hourly_canvas_window = self.hourly_canvas.create_window((0, 0), window=self.scrollable_hourly_frame, anchor="nw") # Stocker la référence
        self.hourly_canvas.configure(yscrollcommand=self.hourly_scrollbar.set)
        self.hourly_canvas.pack(side="left", fill="both", expand=True)
        self.hourly_scrollbar.pack(side="right", fill="y")
        self._bind_mousewheel_to_children(self.scrollable_hourly_frame, self.hourly_canvas)
        self.hourly_canvas.bind('<Enter>', lambda e, c=self.hourly_canvas: self._bind_mousewheel_events(c))
        self.hourly_canvas.bind('<Leave>', lambda e, c=self.hourly_canvas: self._unbind_mousewheel_events(c))

        # --- Onglet: Prévisions Journalières ---
        self.daily_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.daily_tab, text=' Prévisions Journalières ')
        self.daily_canvas = tk.Canvas(self.daily_tab, highlightthickness=0)
        self.daily_scrollbar = ttk.Scrollbar(self.daily_tab, orient="vertical", command=self.daily_canvas.yview)
        self.scrollable_daily_frame = ttk.Frame(self.daily_canvas)
        self.scrollable_daily_frame.bind("<Configure>", lambda e, c=self.daily_canvas: c.configure(scrollregion=c.bbox("all")))
        self.daily_canvas_window = self.daily_canvas.create_window((0, 0), window=self.scrollable_daily_frame, anchor="nw") # Stocker la référence
        self.daily_canvas.configure(yscrollcommand=self.daily_scrollbar.set)
        self.daily_canvas.pack(side="left", fill="both", expand=True)
        self.daily_scrollbar.pack(side="right", fill="y")
        self._bind_mousewheel_to_children(self.scrollable_daily_frame, self.daily_canvas)
        self.daily_canvas.bind('<Enter>', lambda e, c=self.daily_canvas: self._bind_mousewheel_events(c))
        self.daily_canvas.bind('<Leave>', lambda e, c=self.daily_canvas: self._unbind_mousewheel_events(c))

        # --- Onglet: Graphiques Météo ---
        self.graphs_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.graphs_tab, text=' Graphiques Météo ')
        self.graphs_canvas = tk.Canvas(self.graphs_tab, highlightthickness=0)
        self.graphs_scrollbar = ttk.Scrollbar(self.graphs_tab, orient="vertical", command=self.graphs_canvas.yview)
        self.scrollable_graphs_frame = ttk.Frame(self.graphs_canvas)
        self.scrollable_graphs_frame.bind("<Configure>", lambda e, c=self.graphs_canvas: c.configure(scrollregion=c.bbox("all")))
        self.graphs_canvas_window = self.graphs_canvas.create_window((0, 0), window=self.scrollable_graphs_frame, anchor="nw") # Stocker la référence
        self.graphs_canvas.configure(yscrollcommand=self.graphs_scrollbar.set)
        self.graphs_canvas.pack(side="left", fill="both", expand=True)
        self.graphs_scrollbar.pack(side="right", fill="y")
        self._bind_mousewheel_to_children(self.scrollable_graphs_frame, self.graphs_canvas)
        self.graphs_canvas.bind('<Enter>', lambda e, c=self.graphs_canvas: self._bind_mousewheel_events(c))
        self.graphs_canvas.bind('<Leave>', lambda e, c=self.graphs_canvas: self._unbind_mousewheel_events(c))
        self.logger.info("--- APPEL IMMINENT de _setup_graphs_tab_content (depuis _setup_ui) ---")
        if hasattr(self, 'scrollable_graphs_frame') and self.scrollable_graphs_frame:
            self.logger.debug(f"   _setup_ui: scrollable_graphs_frame est de type: {type(self.scrollable_graphs_frame)}")
        else:
            self.logger.error("   _setup_ui: ERREUR CRITIQUE: scrollable_graphs_frame non défini avant appel à _setup_graphs_tab_content")
            return
        self._setup_graphs_tab_content(self.scrollable_graphs_frame)
        self.logger.info("--- RETOUR de _setup_graphs_tab_content (depuis _setup_ui) ---")
        # ... (tes logs de vérification pour temp_ax etc. restent ici)

        # --- NOUVEL Onglet: Analyses & Alertes ---
        self.analysis_tab = ttk.Frame(self.data_notebook, padding="10")
        self.data_notebook.add(self.analysis_tab, text=' Analyses & Alertes ')

        # Ce frame contiendra les labels pour chaque "insight" ou "alerte"
        # Il pourrait aussi avoir besoin d'être scrollable si beaucoup de messages.
        # Pour l'instant, un simple Frame.
        self.analysis_content_frame = ttk.Frame(self.analysis_tab)
        self.analysis_content_frame.pack(fill=tk.BOTH, expand=True)

        # Initialiser une liste pour garder une référence aux labels d'analyse (pour les effacer/mettre à jour)
        self.analysis_labels: List[ttk.Label] = []

        # Appel à une méthode pour initialiser le contenu (même si vide au début)
        self._setup_analysis_tab_content(self.analysis_content_frame)
        self.logger.info("Onglet Analyses & Alertes initialisé.")

    def _setup_graphs_tab_content(self, parent_frame: ttk.Frame):
        """
        Initialise le contenu de l'onglet Graphiques.
        Crée les figures Matplotlib et les canevas TkAgg pour chaque graphique.
        """
        self.logger.debug("Début de _setup_graphs_tab_content...")

        # Le parent_frame est self.scrollable_graphs_frame (qui est dans un canvas scrollable)
        # Chaque graphique aura son propre Frame pour le titre et le canevas Matplotlib

        graph_common_figsize = (7.5, 2.8) # (width, height in inches) - un peu moins haut
        graph_common_dpi = 100
        graph_title_font = self.data_font # Utiliser self.data_font ou self.small_data_font pour les titres
        graph_padding_bottom = 15 # Espace entre les graphiques

        # --- Graphique 1: Températures Horaires ---
        temp_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
        temp_graph_frame.pack(fill=tk.X, expand=True)
        ttk.Label(temp_graph_frame, text="Évolution des Températures Horaires", font=graph_title_font).pack(pady=(0,3))
        try:
            self.temp_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
            self.temp_ax = self.temp_figure.add_subplot(111)
            # Styling de base (sera affiné dans la fonction de dessin)
            self.temp_ax.set_facecolor(self.root.cget('bg'))
            for spine in self.temp_ax.spines.values(): spine.set_edgecolor('gray')
            self.temp_ax.tick_params(colors='gray', labelcolor='gray')

            self.temp_graph_canvas_widget = FigureCanvasTkAgg(self.temp_figure, master=temp_graph_frame)
            self.temp_graph_canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=False) # expand=False pour que le pack ne force pas une hauteur
            self.logger.debug("  Composants pour graphique Températures initialisés.")
        except Exception as e_canvas_temp:
            self.logger.error(f"  Erreur création FigureCanvasTkAgg pour temp_graph: {e_canvas_temp}", exc_info=True)
            self.temp_figure, self.temp_ax, self.temp_graph_canvas_widget = None, None, None


        # --- Graphique 2: Humidité Relative Horaire ---
        humidity_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
        humidity_graph_frame.pack(fill=tk.X, expand=True)
        ttk.Label(humidity_graph_frame, text="Évolution de l'Humidité Relative Horaire", font=graph_title_font).pack(pady=(0,3))
        try:
            self.humidity_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
            self.humidity_ax = self.humidity_figure.add_subplot(111)
            self.humidity_ax.set_facecolor(self.root.cget('bg'))
            for spine in self.humidity_ax.spines.values(): spine.set_edgecolor('gray')
            self.humidity_ax.tick_params(colors='gray', labelcolor='gray')

            self.humidity_graph_canvas_widget = FigureCanvasTkAgg(self.humidity_figure, master=humidity_graph_frame)
            self.humidity_graph_canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=False)
            self.logger.debug("  Composants pour graphique Humidité initialisés.")
        except Exception as e_canvas_hum:
            self.logger.error(f"  Erreur création FigureCanvasTkAgg pour humidity_graph: {e_canvas_hum}", exc_info=True)
            self.humidity_figure, self.humidity_ax, self.humidity_graph_canvas_widget = None, None, None


        # --- Graphique 3: Précipitations Horaires (Quantité et Probabilité) ---
        precip_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
        precip_graph_frame.pack(fill=tk.X, expand=True)
        ttk.Label(precip_graph_frame, text="Précipitations Horaires (Quantité et Probabilité)", font=graph_title_font).pack(pady=(0,3))
        try:
            self.precip_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
            self.precip_ax_qty = self.precip_figure.add_subplot(111) # Axe pour la quantité (mm)
            # On créera un deuxième axe Y pour la probabilité dans la fonction de dessin
            self.precip_ax_qty.set_facecolor(self.root.cget('bg'))
            for spine in self.precip_ax_qty.spines.values(): spine.set_edgecolor('gray')
            self.precip_ax_qty.tick_params(colors='gray', labelcolor='gray')
            self.precip_ax_prob = None # Sera créé avec twinx() dans la fonction de dessin

            self.precip_graph_canvas_widget = FigureCanvasTkAgg(self.precip_figure, master=precip_graph_frame)
            self.precip_graph_canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=False)
            self.logger.debug("  Composants pour graphique Précipitations initialisés.")
        except Exception as e_canvas_precip:
            self.logger.error(f"  Erreur création FigureCanvasTkAgg pour precip_graph: {e_canvas_precip}", exc_info=True)
            self.precip_figure, self.precip_ax_qty, self.precip_graph_canvas_widget = None, None, None
            self.precip_ax_prob = None


        # --- Graphique 4: Vitesse du Vent Horaire ---
        wind_graph_frame = ttk.Frame(parent_frame, padding=(0, 0, 0, graph_padding_bottom))
        wind_graph_frame.pack(fill=tk.X, expand=True)
        ttk.Label(wind_graph_frame, text="Vitesse du Vent Horaire", font=graph_title_font).pack(pady=(0,3))
        try:
            self.wind_figure = Figure(figsize=graph_common_figsize, dpi=graph_common_dpi, facecolor=self.root.cget('bg'))
            self.wind_ax = self.wind_figure.add_subplot(111)
            self.wind_ax.set_facecolor(self.root.cget('bg'))
            for spine in self.wind_ax.spines.values(): spine.set_edgecolor('gray')
            self.wind_ax.tick_params(colors='gray', labelcolor='gray')

            self.wind_graph_canvas_widget = FigureCanvasTkAgg(self.wind_figure, master=wind_graph_frame)
            self.wind_graph_canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=False)
            self.logger.debug("  Composants pour graphique Vent initialisés.")
        except Exception as e_canvas_wind:
            self.logger.error(f"  Erreur création FigureCanvasTkAgg pour wind_graph: {e_canvas_wind}", exc_info=True)
            self.wind_figure, self.wind_ax, self.wind_graph_canvas_widget = None, None, None

        self.logger.info("Fin de _setup_graphs_tab_content (initialisation des structures des graphiques).")

    def _update_all_graphs(self, weather_data: dict):
        """
        Appelle les fonctions de mise à jour pour chaque graphique défini.
        """
        self.logger.debug("Début de la mise à jour de tous les graphiques...")

        hourly_data = weather_data.get("hourly") # .get() retourne None si la clé manque
        hourly_units_data = weather_data.get("hourly_units") # .get() retourne None

        # daily_data = weather_data.get("daily") # Pour de futurs graphiques journaliers
        # daily_units_data = weather_data.get("daily_units")

        if hourly_data and hourly_units_data: # S'assurer que les dictionnaires eux-mêmes existent et ne sont pas None
            self.logger.debug("  Données horaires et unités trouvées, mise à jour des graphiques horaires.")

            # Graphique des Températures
            if hasattr(self, '_draw_temperature_hourly_graph'): # Vérifier si la méthode existe
                self._draw_temperature_hourly_graph(hourly_data, hourly_units_data)
            else:
                self.logger.warning("_draw_temperature_hourly_graph non trouvée.")

            # Graphique de l'Humidité
            if hasattr(self, '_draw_humidity_hourly_graph'): # Vérifier si la méthode existe
                self._draw_humidity_hourly_graph(hourly_data, hourly_units_data)
            else:
                self.logger.warning("_draw_humidity_hourly_graph non trouvée.")

            # Graphique des Précipitations
            if hasattr(self, '_draw_precipitation_hourly_graph'): # Vérifier si la méthode existe
                self._draw_precipitation_hourly_graph(hourly_data, hourly_units_data)
            else:
                self.logger.warning("_draw_precipitation_hourly_graph non trouvée.")

            # Graphique de la Vitesse du Vent
            if hasattr(self, '_draw_windspeed_hourly_graph'): # Vérifier si la méthode existe
                self._draw_windspeed_hourly_graph(hourly_data, hourly_units_data)
            else:
                self.logger.warning("_draw_windspeed_hourly_graph non trouvée.")

        elif hourly_data and not hourly_units_data:
            self.logger.warning("Données horaires présentes mais unités horaires absentes. Certains graphiques pourraient ne pas avoir d'unités.")
            # On pourrait quand même essayer de dessiner les graphiques, ils afficheront "N/A" pour les unités
            # ou utiliser des unités par défaut si les fonctions de dessin le gèrent.
            # Pour l'instant, on ne les dessine pas pour éviter des erreurs potentielles.
            # Si tu veux quand même essayer, décommente les appels ci-dessous et assure-toi
            # que les fonctions de dessin gèrent bien hourly_units_data étant None ou {}.
            # self._draw_temperature_hourly_graph(hourly_data, {})
            # self._draw_humidity_hourly_graph(hourly_data, {})
            # ...
        else:
            self.logger.warning("Données horaires ('hourly' ou 'hourly_units') absentes ou invalides dans weather_data. Graphiques horaires non mis à jour.")
            # On pourrait effacer les graphiques existants ou afficher un message "Données non disponibles"
            # sur chaque axe si les attributs _ax existent.
            if hasattr(self, 'temp_ax') and self.temp_ax:
                self.temp_ax.clear()
                self.temp_ax.text(0.5, 0.5, "Données non disponibles", ha='center', va='center', transform=self.temp_ax.transAxes, color='gray')
                if hasattr(self, 'temp_graph_canvas_widget') and self.temp_graph_canvas_widget: self.temp_graph_canvas_widget.draw_idle()
            # Faire de même pour humidity_ax, precip_ax_qty, wind_ax...

        self.logger.debug("Fin de la mise à jour de tous les graphiques.")

    def _draw_temperature_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """
        Dessine ou met à jour le graphique des températures horaires.
        """
        self.logger.debug("Entrée _draw_temperature_hourly_graph.")

        # --- Vérification initiale robuste des composants du graphique ---
        if not (hasattr(self, 'temp_figure') and self.temp_figure and \
                hasattr(self, 'temp_ax') and self.temp_ax and \
                hasattr(self, 'temp_graph_canvas_widget') and self.temp_graph_canvas_widget):
            self.logger.warning("Composants essentiels du graphique de température (figure, axe ou canevas) non initialisés ou None. Impossible de dessiner.")
            return
        # À partir d'ici, on sait que self.temp_figure, self.temp_ax, et self.temp_graph_canvas_widget ne sont pas None.

        times_str = hourly_data.get("time", [])
        temps_2m = hourly_data.get("temperature_2m", [])
        temps_apparent = hourly_data.get("apparent_temperature", [])
        temp_unit = hourly_units.get("temperature_2m", "°C")

        if not times_str or (not (temps_2m and any(t is not None for t in temps_2m)) and not (temps_apparent and any(t is not None for t in temps_apparent))):
            self.logger.info("Données de temps ou de température valides manquantes pour le graphique des températures.")
            self.temp_ax.clear()
            self.temp_ax.text(0.5, 0.5, "Données de température non disponibles",
                              ha='center', va='center', # Utiliser ha et va pour Matplotlib
                              transform=self.temp_ax.transAxes, color="gray")
            self.temp_graph_canvas_widget.draw_idle()
            return

        try:
            self.logger.debug("  _draw_temp_graph: Début du bloc try pour le dessin des températures.")
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            temps_2m_plot = temps_2m[:num_hours_to_plot] if temps_2m else [None] * num_hours_to_plot
            temps_apparent_plot = temps_apparent[:num_hours_to_plot] if temps_apparent else [None] * num_hours_to_plot

            self.temp_ax.clear()
            self.logger.debug("  _draw_temp_graph: Axe des températures nettoyé (clear).")

            self.temp_ax.set_title("Évolution Horaire des Températures", color="gray", fontsize=10)

            plot_made = False
            if any(t is not None for t in temps_2m_plot):
                self.temp_ax.plot(times_dt, temps_2m_plot, label=f"Température ({temp_unit})", color="#3498db", marker='o', markersize=4, linestyle='-')
                plot_made = True
            if any(t is not None for t in temps_apparent_plot):
                self.temp_ax.plot(times_dt, temps_apparent_plot, label=f"Ressentie ({temp_unit})", color="#e74c3c", marker='x', markersize=5, linestyle='--')
                plot_made = True

            self.temp_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.temp_ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8)))

            # self.temp_figure doit exister si self.temp_ax existe (car temp_ax est créé à partir de temp_figure)
            self.temp_figure.autofmt_xdate(rotation=30, ha='right')

            self.temp_ax.set_ylabel(f"Température ({temp_unit})", color="gray")
            if plot_made:
                 self.temp_ax.legend(loc='best', fontsize='x-small', frameon=False, labelcolor='gray')
            self.temp_ax.grid(True, linestyle=':', linewidth=0.5, color='gray')

            self.temp_ax.set_facecolor(self.root.cget('bg'))
            self.temp_ax.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            self.temp_ax.tick_params(axis='y', colors='gray', labelcolor='gray', labelsize='small')
            for spine in self.temp_ax.spines.values():
                spine.set_edgecolor('gray')
            self.logger.debug("  _draw_temp_graph: Axes et style des températures configurés.")

            self.temp_graph_canvas_widget.draw_idle()
            self.logger.info("Graphique des températures mis à jour avec succès.")

        except Exception as e_graph:
            self.logger.error(f"Erreur lors du dessin du graphique des températures: {e_graph}", exc_info=True)
            # Les vérifications ci-dessous sont redondantes si la vérification initiale en haut est passée,
            # mais ne font pas de mal pour une robustesse extrême dans le bloc d'erreur.
            if hasattr(self, 'temp_ax') and self.temp_ax:
                self.temp_ax.clear()
                self.temp_ax.text(0.5, 0.5, "Erreur génération graphique",
                                  ha='center', va='center',
                                  transform=self.temp_ax.transAxes, color="red")

            if hasattr(self, 'temp_graph_canvas_widget') and self.temp_graph_canvas_widget:
                self.temp_graph_canvas_widget.draw_idle()
            else:
                self.logger.warning("  _draw_temp_graph (dans except): temp_graph_canvas_widget non disponible pour draw_idle.")

    def _draw_humidity_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """Dessine ou met à jour le graphique de l'humidité relative horaire."""
        self.logger.debug("  Début _draw_humidity_hourly_graph.")

        # --- Vérification initiale robuste des composants du graphique ---
        if not (hasattr(self, 'humidity_figure') and self.humidity_figure and \
                hasattr(self, 'humidity_ax') and self.humidity_ax and \
                hasattr(self, 'humidity_graph_canvas_widget') and self.humidity_graph_canvas_widget):
            self.logger.warning("  Composants essentiels du graphique d'humidité (figure, axe ou canevas) non initialisés ou None.")
            return
        # À partir d'ici, on sait que self.humidity_figure, self.humidity_ax, et self.humidity_graph_canvas_widget ne sont pas None.

        times_str = hourly_data.get("time", [])
        humidity_values = hourly_data.get("relativehumidity_2m", [])
        humidity_unit = hourly_units.get("relativehumidity_2m", "%")

        if not times_str or not (humidity_values and any(h is not None for h in humidity_values)):
            self.logger.info("  Données de temps ou d'humidité valides manquantes pour le graphique d'humidité.")
            # Vérifier avant d'utiliser dans ce bloc de données manquantes
            if hasattr(self, 'humidity_ax') and self.humidity_ax:
                self.humidity_ax.clear()
                self.humidity_ax.text(0.5, 0.5, "Données d'humidité non disponibles",
                                      ha='center', va='center', transform=self.humidity_ax.transAxes, color="gray")
            if hasattr(self, 'humidity_graph_canvas_widget') and self.humidity_graph_canvas_widget:
                self.humidity_graph_canvas_widget.draw_idle()
            return

        try:
            self.logger.debug("    _draw_humidity_graph: Début du bloc try pour le dessin.")
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            humidity_plot = humidity_values[:num_hours_to_plot] if humidity_values else [None] * num_hours_to_plot

            self.humidity_ax.clear()
            self.logger.debug("    _draw_humidity_graph: Axe d'humidité nettoyé.")
            self.humidity_ax.set_title("Humidité Relative Horaire", color="gray", fontsize=10)

            plot_made_humidity = False
            if any(h is not None for h in humidity_plot):
                self.humidity_ax.plot(times_dt, humidity_plot, label=f"Humidité ({humidity_unit})", color="#27ae60", marker='.', markersize=5, linestyle='-')
                plot_made_humidity = True
                self.logger.debug("    _draw_humidity_graph: Ligne Humidité dessinée.")


            self.humidity_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.humidity_ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8)))
            # self.humidity_figure doit exister si self.humidity_ax existe
            self.humidity_figure.autofmt_xdate(rotation=30, ha='right')

            self.humidity_ax.set_ylabel(f"Humidité ({humidity_unit})", color="gray")
            if plot_made_humidity:
                self.humidity_ax.legend(loc='best', fontsize='x-small', frameon=False, labelcolor='gray')
            self.humidity_ax.grid(True, linestyle=':', linewidth=0.5, color='gray')

            # Styling
            self.humidity_ax.set_facecolor(self.root.cget('bg'))
            self.humidity_ax.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            self.humidity_ax.tick_params(axis='y', colors='gray', labelcolor='gray', labelsize='small')
            for spine in self.humidity_ax.spines.values(): spine.set_edgecolor('gray')
            self.logger.debug("    _draw_humidity_graph: Axes et style d'humidité configurés.")

            self.humidity_graph_canvas_widget.draw_idle()
            self.logger.info("  Graphique d'humidité mis à jour avec succès.")
        except Exception as e_graph:
            self.logger.error(f"  Erreur dessin graphique humidité: {e_graph}", exc_info=True)
            # Vérifier à nouveau avant d'utiliser dans le bloc except
            if hasattr(self, 'humidity_ax') and self.humidity_ax:
                self.humidity_ax.clear()
                self.humidity_ax.text(0.5, 0.5, "Erreur graphique humidité",
                                      ha='center', va='center',
                                      transform=self.humidity_ax.transAxes, color="red")

            if hasattr(self, 'humidity_graph_canvas_widget') and self.humidity_graph_canvas_widget:
                self.humidity_graph_canvas_widget.draw_idle()
            else:
                self.logger.warning("    _draw_humidity_graph (dans except): humidity_graph_canvas_widget non disponible pour draw_idle.")


    def _draw_precipitation_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """Dessine ou met à jour le graphique des précipitations horaires (quantité et probabilité)."""
        self.logger.debug("  Début _draw_precipitation_hourly_graph.")

        # --- Vérification initiale robuste des composants du graphique ---
        if not (hasattr(self, 'precip_figure') and self.precip_figure and \
                hasattr(self, 'precip_ax_qty') and self.precip_ax_qty and \
                hasattr(self, 'precip_graph_canvas_widget') and self.precip_graph_canvas_widget):
            # Note: self.precip_ax_prob est créé dynamiquement avec twinx(), donc on ne le vérifie pas ici.
            self.logger.warning("  Composants essentiels du graphique de précipitations (figure, axe principal ou canevas) non initialisés ou None.")
            return
        # À partir d'ici, on sait que precip_figure, precip_ax_qty, et precip_graph_canvas_widget sont valides.

        times_str = hourly_data.get("time", [])
        precip_qty_values = hourly_data.get("precipitation", [])
        precip_prob_values = hourly_data.get("precipitation_probability", [])

        qty_unit = hourly_units.get("precipitation", "mm")
        prob_unit = hourly_units.get("precipitation_probability", "%")

        if not times_str or \
           (not (precip_qty_values and any(p is not None for p in precip_qty_values)) and \
            not (precip_prob_values and any(p is not None for p in precip_prob_values))):
            self.logger.info("  Données de temps ou de précipitation valides manquantes pour le graphique des précipitations.")
            # Vérifier avant d'utiliser dans ce bloc
            if hasattr(self, 'precip_ax_qty') and self.precip_ax_qty:
                self.precip_ax_qty.clear()
                if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: self.precip_ax_prob.clear()
                self.precip_ax_qty.text(0.5, 0.5, "Données de précipitation non disponibles",
                                        ha='center', va='center', transform=self.precip_ax_qty.transAxes, color="gray")
            if hasattr(self, 'precip_graph_canvas_widget') and self.precip_graph_canvas_widget:
                self.precip_graph_canvas_widget.draw_idle()
            return

        try:
            self.logger.debug("    _draw_precip_graph: Début du bloc try pour le dessin.")
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            precip_qty_plot = precip_qty_values[:num_hours_to_plot] if precip_qty_values else [None] * num_hours_to_plot
            precip_prob_plot = precip_prob_values[:num_hours_to_plot] if precip_prob_values else [None] * num_hours_to_plot

            self.precip_ax_qty.clear()
            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob:
                self.precip_ax_prob.clear()
            else: # Créer le deuxième axe Y pour la probabilité s'il n'a pas été créé avant ou a été remis à None
                if hasattr(self, 'precip_ax_qty') and self.precip_ax_qty: # S'assurer que l'axe principal existe
                    self.precip_ax_prob = self.precip_ax_qty.twinx()
                else: # Ne devrait pas arriver si la vérification initiale est passée
                    self.logger.error("    _draw_precip_graph: precip_ax_qty est None, impossible de créer precip_ax_prob.")
                    return
            self.logger.debug("    _draw_precip_graph: Axes nettoyés (ou precip_ax_prob créé).")

            self.precip_ax_qty.set_title("Précipitations Horaires", color="gray", fontsize=10)

            color_qty = "#5dade2"
            plot_made_qty = False
            if any(p is not None and p > 0 for p in precip_qty_plot):
                 self.precip_ax_qty.bar(times_dt, precip_qty_plot, width=0.03 * (num_hours_to_plot/max(1,num_hours_to_plot//8)/HOURLY_FORECAST_HOURS*24), label=f"Quantité ({qty_unit})", color=color_qty, alpha=0.7) # Ajustement width barre
                 plot_made_qty = True
            self.precip_ax_qty.set_ylabel(f"Quantité ({qty_unit})", color=color_qty)
            self.precip_ax_qty.tick_params(axis='y', labelcolor=color_qty, colors='gray', labelsize='small')
            self.precip_ax_qty.spines['left'].set_color(color_qty)

            color_prob = "#f1c40f"
            plot_made_prob = False
            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: # Vérifier avant d'utiliser
                if any(p is not None for p in precip_prob_plot):
                    self.precip_ax_prob.plot(times_dt, precip_prob_plot, label=f"Probabilité ({prob_unit})", color=color_prob, marker='.', markersize=4, linestyle='--')
                    plot_made_prob = True
                self.precip_ax_prob.set_ylabel(f"Probabilité ({prob_unit})", color=color_prob)
                self.precip_ax_prob.tick_params(axis='y', labelcolor=color_prob, colors='gray', labelsize='small')
                self.precip_ax_prob.spines['right'].set_color(color_prob)
                self.precip_ax_prob.set_ylim(0, 105)
            else:
                 self.logger.warning("    _draw_precip_graph: precip_ax_prob non disponible pour le tracé de probabilité.")


            self.precip_ax_qty.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.precip_ax_qty.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8)))
            self.precip_figure.autofmt_xdate(rotation=30, ha='right')

            lines_qty, labels_qty = self.precip_ax_qty.get_legend_handles_labels()
            lines_prob, labels_prob = [], []
            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob:
                lines_prob, labels_prob = self.precip_ax_prob.get_legend_handles_labels()

            if plot_made_qty or plot_made_prob:
                self.precip_ax_qty.legend(lines_qty + lines_prob, labels_qty + labels_prob, loc='upper left', fontsize='x-small', frameon=False, labelcolor='gray')

            self.precip_ax_qty.grid(True, linestyle=':', linewidth=0.5, color='gray', axis='x')

            self.precip_ax_qty.set_facecolor(self.root.cget('bg'))
            if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob:
                self.precip_ax_prob.set_facecolor(self.root.cget('bg'))
                self.precip_ax_prob.patch.set_alpha(0.0)
                for s_name in ['bottom', 'top', 'left']: self.precip_ax_prob.spines[s_name].set_visible(False)
                self.precip_ax_prob.spines['right'].set_edgecolor('gray') # S'assurer que la couleur est appliquée

            self.precip_ax_qty.patch.set_alpha(0.0)
            self.precip_ax_qty.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            for s_name in ['bottom', 'top', 'left']: self.precip_ax_qty.spines[s_name].set_edgecolor('gray')
            self.logger.debug("    _draw_precip_graph: Axes et style des précipitations configurés.")

            self.precip_graph_canvas_widget.draw_idle()
            self.logger.info("  Graphique des précipitations mis à jour avec succès.")
        except Exception as e_graph:
            self.logger.error(f"  Erreur dessin graphique précipitations: {e_graph}", exc_info=True)
            if hasattr(self, 'precip_ax_qty') and self.precip_ax_qty:
                self.precip_ax_qty.clear()
                if hasattr(self, 'precip_ax_prob') and self.precip_ax_prob: self.precip_ax_prob.clear()
                self.precip_ax_qty.text(0.5, 0.5, "Erreur graphique précipitations",
                                        ha='center', va='center',
                                        transform=self.precip_ax_qty.transAxes, color="red")

            if hasattr(self, 'precip_graph_canvas_widget') and self.precip_graph_canvas_widget:
                self.precip_graph_canvas_widget.draw_idle()
            else:
                self.logger.warning("    _draw_precip_graph (dans except): precip_graph_canvas_widget non disponible pour draw_idle.")


    def _draw_windspeed_hourly_graph(self, hourly_data: dict, hourly_units: dict):
        """Dessine ou met à jour le graphique de la vitesse du vent horaire."""
        self.logger.debug("  Début _draw_windspeed_hourly_graph.")

        # --- Vérification initiale robuste des composants du graphique ---
        if not (hasattr(self, 'wind_figure') and self.wind_figure and \
                hasattr(self, 'wind_ax') and self.wind_ax and \
                hasattr(self, 'wind_graph_canvas_widget') and self.wind_graph_canvas_widget):
            self.logger.warning("  Composants essentiels du graphique de vent (figure, axe ou canevas) non initialisés ou None.")
            return
        # À partir d'ici, on sait que wind_figure, wind_ax, et wind_graph_canvas_widget sont valides.

        times_str = hourly_data.get("time", [])
        windspeed_values = hourly_data.get("windspeed_10m", [])
        # windgusts_values = hourly_data.get("windgusts_10m", []) # Optionnel: rafales
        wind_unit = hourly_units.get("windspeed_10m", "km/h")

        if not times_str or not (windspeed_values and any(w is not None for w in windspeed_values)):
            self.logger.info("  Données de temps ou de vitesse du vent valides manquantes pour le graphique de vent.")
            # Vérifier avant d'utiliser dans ce bloc
            if hasattr(self, 'wind_ax') and self.wind_ax:
                self.wind_ax.clear()
                self.wind_ax.text(0.5, 0.5, "Données de vent non disponibles",
                                  ha='center', va='center', transform=self.wind_ax.transAxes, color="gray")
            if hasattr(self, 'wind_graph_canvas_widget') and self.wind_graph_canvas_widget:
                self.wind_graph_canvas_widget.draw_idle()
            return

        try:
            self.logger.debug("    _draw_windspeed_graph: Début du bloc try pour le dessin.")
            num_hours_to_plot = min(len(times_str), HOURLY_FORECAST_HOURS)
            times_dt = [datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times_str[:num_hours_to_plot]]
            windspeed_plot = windspeed_values[:num_hours_to_plot] if windspeed_values else [None] * num_hours_to_plot
            # windgusts_plot = windgusts_values[:num_hours_to_plot] if windgusts_values else [None] * num_hours_to_plot

            self.wind_ax.clear()
            self.logger.debug("    _draw_windspeed_graph: Axe du vent nettoyé.")
            self.wind_ax.set_title("Vitesse du Vent Horaire", color="gray", fontsize=10)

            plot_made_wind = False
            if any(w is not None for w in windspeed_plot):
                self.wind_ax.plot(times_dt, windspeed_plot, label=f"Vitesse Vent ({wind_unit})", color="#8e44ad", marker='^', markersize=4, linestyle='-')
                plot_made_wind = True
                self.logger.debug("    _draw_windspeed_graph: Ligne Vitesse Vent dessinée.")

            # Optionnel: Afficher les rafales
            # windgusts_values_full = hourly_data.get("windgusts_10m", [])
            # windgusts_plot = windgusts_values_full[:num_hours_to_plot] if windgusts_values_full else [None] * num_hours_to_plot
            # if any(g is not None for g in windgusts_plot):
            #     self.wind_ax.plot(times_dt, windgusts_plot, label=f"Rafales ({wind_unit})", color="#c0392b", linestyle=':', alpha=0.7, markersize=3)
            #     plot_made_wind = True # S'assurer que la légende s'affiche si on a les rafales

            self.wind_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.wind_ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, num_hours_to_plot // 8)))
            # self.wind_figure doit exister si self.wind_ax existe
            self.wind_figure.autofmt_xdate(rotation=30, ha='right')

            self.wind_ax.set_ylabel(f"Vitesse ({wind_unit})", color="gray")
            if plot_made_wind:
                self.wind_ax.legend(loc='best', fontsize='x-small', frameon=False, labelcolor='gray')
            self.wind_ax.grid(True, linestyle=':', linewidth=0.5, color='gray')

            # Styling
            self.wind_ax.set_facecolor(self.root.cget('bg'))
            self.wind_ax.tick_params(axis='x', colors='gray', labelcolor='gray', labelsize='small')
            self.wind_ax.tick_params(axis='y', colors='gray', labelcolor='gray', labelsize='small')
            for spine in self.wind_ax.spines.values(): spine.set_edgecolor('gray')
            self.logger.debug("    _draw_windspeed_graph: Axes et style du vent configurés.")

            self.wind_graph_canvas_widget.draw_idle()
            self.logger.info("  Graphique de la vitesse du vent mis à jour avec succès.")
        except Exception as e_graph:
            self.logger.error(f"  Erreur dessin graphique vent: {e_graph}", exc_info=True)
            # Vérifier à nouveau avant d'utiliser dans le bloc except
            if hasattr(self, 'wind_ax') and self.wind_ax:
                self.wind_ax.clear()
                self.wind_ax.text(0.5, 0.5, "Erreur graphique vent",
                                  ha='center', va='center',
                                  transform=self.wind_ax.transAxes, color="red")

            if hasattr(self, 'wind_graph_canvas_widget') and self.wind_graph_canvas_widget:
                self.wind_graph_canvas_widget.draw_idle()
            else:
                self.logger.warning("    _draw_windspeed_graph (dans except): wind_graph_canvas_widget non disponible pour draw_idle.")

    def _setup_current_weather_ui(self, parent_frame: ttk.Frame):
        # Configurer les colonnes pour la disposition
        # Colonne 0: Labels de description
        # Colonne 1: Valeurs des données
        # Colonne 2: Espace (ou autre)
        # Colonne 3: Icône météo principale
        parent_frame.columnconfigure(0, weight=0)
        parent_frame.columnconfigure(1, weight=1) # Permettre aux valeurs de s'étendre
        parent_frame.columnconfigure(2, weight=0, minsize=20) # Petit espace
        parent_frame.columnconfigure(3, weight=0, minsize=50) # Pour l'icône

        # Titre et heure des données
        title_frame = ttk.Frame(parent_frame)
        title_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0,10))
        ttk.Label(title_frame, text="Météo Actuelle ", font=self.title_font).pack(side=tk.LEFT)
        self.current_data_time_label = ttk.Label(title_frame, text="(pour --:--)", font=self.small_data_font)
        self.current_data_time_label.pack(side=tk.LEFT, padx=(5,0))

        row_idx = 1 # Commence à la ligne suivante pour les données
        self.current_weather_labels: Dict[str, ttk.Label] = {}

        # Champs à afficher, groupés pour une éventuelle disposition en 2 colonnes de données
        # (Pour l'instant, une seule colonne de données à gauche de l'icône)
        fields = {
            "description": "Description :",
            "temperature": "Température :",
            "apparent_temp": "Ressentie :",
            "humidity": "Humidité :",
            "precipitation": "Précipitations :", # Nouveau
            "cloudcover": "Couv. Nuageuse :", # Nouveau
            "pressure": "Pression :",
            "wind": "Vent :",
            "uv_index": "Indice UV :",
            "precipitation_prob": "Prob. Précip. :", # Peut-être redondant si on a déjà les précip.
            "sunrise": "Lever soleil :",
            "sunset": "Coucher soleil :"
        }

        # Label pour l'icône (caractère Unicode)
        self.current_weather_icon_label = ttk.Label(parent_frame, text=DEFAULT_WEATHER_ICON, font=self.icon_font, anchor="center")
        # Placer l'icône à droite, s'étendant sur plusieurs lignes de données
        self.current_weather_icon_label.grid(row=1, column=3, rowspan=len(fields)//2 +1 , padx=10, pady=5, sticky="n")


        for key, text in fields.items():
            ttk.Label(parent_frame, text=text, font=self.data_font).grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
            value_label = ttk.Label(parent_frame, text="N/A", font=self.data_font, anchor="w")
            value_label.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
            self.current_weather_labels[key] = value_label
            row_idx +=1

    def _setup_analysis_tab_content(self, parent_frame_for_tab: ttk.Frame):
        """
        Initialise le contenu de l'onglet Analyses & Alertes.
        Prépare un frame scrollable pour afficher les messages d'analyse.
        """
        self.logger.debug("Début de _setup_analysis_tab_content...")
        parent_frame_for_tab.columnconfigure(0, weight=1) # Permettre au canvas de s'étendre
        parent_frame_for_tab.rowconfigure(0, weight=1)    # Permettre au canvas de s'étendre

        # Créer un canvas scrollable pour les analyses
        self.analysis_canvas = tk.Canvas(parent_frame_for_tab, highlightthickness=0)
        self.analysis_scrollbar = ttk.Scrollbar(parent_frame_for_tab, orient="vertical", command=self.analysis_canvas.yview)

        # Frame intérieur qui contiendra réellement les labels d'analyse
        self.scrollable_analysis_frame = ttk.Frame(self.analysis_canvas, padding=(5,5))
        # Configurer la colonne 0 du frame scrollable pour qu'elle s'étende
        self.scrollable_analysis_frame.columnconfigure(0, weight=1)

        self.scrollable_analysis_frame.bind(
            "<Configure>",
            lambda e, c=self.analysis_canvas: c.configure(scrollregion=c.bbox("all"))
        )
        self.analysis_canvas_window = self.analysis_canvas.create_window(
            (0, 0), window=self.scrollable_analysis_frame, anchor="nw"
        )
        self.analysis_canvas.configure(yscrollcommand=self.analysis_scrollbar.set)

        # Utiliser grid pour le canvas et la scrollbar dans parent_frame_for_tab
        self.analysis_canvas.grid(row=0, column=0, sticky="nsew")
        self.analysis_scrollbar.grid(row=0, column=1, sticky="ns")

        # Lier la molette au canvas des analyses et à ses enfants
        self._bind_mousewheel_to_children(self.scrollable_analysis_frame, self.analysis_canvas)
        self.analysis_canvas.bind('<Enter>', lambda e, c=self.analysis_canvas: self._bind_mousewheel_events(c))
        self.analysis_canvas.bind('<Leave>', lambda e, c=self.analysis_canvas: self._unbind_mousewheel_events(c))

        # self.analysis_labels est déjà initialisé à [] dans __init__
        # On pourrait ajouter un label initial "Aucune analyse pour le moment."
        # qui sera effacé lors de la première mise à jour.
        # initial_analysis_label = ttk.Label(self.scrollable_analysis_frame, text="En attente de données pour analyse...", font=self.data_font)
        # initial_analysis_label.pack(pady=10)
        # self.analysis_labels.append(initial_analysis_label)

        self.logger.info("Contenu de l'onglet Analyses & Alertes initialisé.")

    def _update_analysis_tab_display(self, insights: List[str]):
        """
        Met à jour l'onglet Analyses & Alertes avec la liste des "insights" fournis.
        """
        self.logger.debug(f"Mise à jour de l'affichage des analyses avec {len(insights)} insight(s).")

        # S'assurer que le frame existe (devrait être créé par _setup_analysis_tab_content)
        if not hasattr(self, 'scrollable_analysis_frame') or not self.scrollable_analysis_frame:
            self.logger.error("scrollable_analysis_frame non trouvé. Impossible de mettre à jour les analyses.")
            return

        # Effacer les anciens labels d'analyse
        for label in self.analysis_labels:
            if label.winfo_exists(): # Vérifier si le widget existe encore
                label.destroy()
        self.analysis_labels.clear()

        if not insights:
            no_insights_label = ttk.Label(self.scrollable_analysis_frame,
                                          text="Aucune alerte ou analyse particulière pour le moment.",
                                          font=self.data_font,
                                          style="Italic.TLabel") # Style optionnel pour italique
            no_insights_label.pack(pady=10, padx=5, anchor="w")
            self.analysis_labels.append(no_insights_label)
            return

        for insight_text in insights:
            # On pourrait utiliser des couleurs différentes ou des icônes Unicode pour les alertes vs infos
            # Pour l'instant, un simple label.
            # Utiliser wraplength pour que les longs messages passent à la ligne.
            # La largeur du scrollable_analysis_frame est déterminée par le canvas,
            # donc on peut estimer une largeur pour le wraplength.

            # Estimer la largeur disponible (un peu moins que la largeur du canvas)
            # Ceci est une estimation, pourrait nécessiter un ajustement ou une méthode plus dynamique
            # si la taille de la fenêtre change beaucoup.
            try:
                # Tenter d'obtenir la largeur du frame parent (scrollable_analysis_frame)
                # Cela ne fonctionne bien que si le layout a déjà eu lieu.
                # Au premier appel, la largeur peut être 1.
                available_width = self.scrollable_analysis_frame.winfo_width()
                if available_width <= 1: # Si la largeur n'est pas encore déterminée
                    available_width = self.analysis_canvas.winfo_width() - self.analysis_scrollbar.winfo_width() - 20 # Moins padding/scrollbar
                if available_width <= 1:
                    available_width = 700 # Fallback si toujours pas de largeur
            except tk.TclError: # Si le widget n'existe pas encore pleinement
                available_width = 700

            insight_label = ttk.Label(self.scrollable_analysis_frame,
                                      text=f"● {insight_text}", # Ajouter une puce
                                      font=self.data_font,
                                      wraplength=max(200, available_width - 20), # wraplength basé sur la largeur estimée
                                      justify=tk.LEFT,
                                      anchor="w")
            insight_label.pack(pady=3, padx=5, fill=tk.X, expand=True, anchor="w")
            self.analysis_labels.append(insight_label)

        # Forcer la mise à jour du canvas pour recalculer la scrollregion
        # Cela peut être nécessaire si le contenu change dynamiquement
        self.root.update_idletasks()
        if hasattr(self, 'analysis_canvas') and self.analysis_canvas.winfo_exists():
            self.analysis_canvas.configure(scrollregion=self.analysis_canvas.bbox("all"))

    def _generate_derived_insights(self, weather_data: dict) -> List[str]:
        """
        Génère une liste de messages d'analyse et d'alertes basés sur les données météo.
        """
        self.logger.debug("Génération des analyses et alertes météo...")
        insights: List[str] = []

        daily_data = weather_data.get("daily", {})
        hourly_data = weather_data.get("hourly", {})
        current_data = weather_data.get("current", {}) # On a maintenant current

        # --- 1. Alerte Gel (basée sur temperature_2m_min des prochains jours) ---
        if daily_data.get("time") and daily_data.get("temperature_2m_min"):
            temps_min_daily = daily_data["temperature_2m_min"]
            dates_daily = daily_data["time"]
            # Vérifier pour les 3 prochains jours (index 0, 1, 2)
            for i in range(min(3, len(temps_min_daily))):
                temp_min = temps_min_daily[i]
                if temp_min is not None:
                    date_str = "Aujourd'hui" if i == 0 else (
                        "Demain" if i == 1 else
                        datetime.datetime.fromisoformat(dates_daily[i]).strftime("%A %d %b").capitalize()
                    )
                    if temp_min <= 0:
                        insights.append(f"❄️ ALERTE GEL: Risque de gelée ({temp_min}°C) prévu pour {date_str}.")
                        break # Une alerte gel suffit peut-être pour ne pas surcharger
                    elif temp_min <= 2: # Seuil pour gelée blanche
                        insights.append(f"❄️ Attention: Risque de gelée blanche ({temp_min}°C) possible pour {date_str}.")
                        # On peut laisser continuer pour voir si un gel plus fort est prévu plus tard

        # --- 2. Alerte Vent Fort (basée sur windgusts_10m_max des prochains jours) ---
        # Ou sur hourly.windgusts_10m si on veut une alerte plus imminente
        if daily_data.get("time") and daily_data.get("windgusts_10m_max"):
            gusts_max_daily = daily_data["windgusts_10m_max"]
            dates_daily = daily_data["time"]
            # Vérifier pour les 3 prochains jours
            for i in range(min(3, len(gusts_max_daily))):
                gust_max = gusts_max_daily[i]
                if gust_max is not None and gust_max >= 70: # Seuil de 70 km/h pour vent fort
                    date_str = "Aujourd'hui" if i == 0 else (
                        "Demain" if i == 1 else
                        datetime.datetime.fromisoformat(dates_daily[i]).strftime("%A %d %b").capitalize()
                    )
                    insights.append(f"🌬️ ALERTE VENT: Fortes rafales ({gust_max} km/h) attendues {date_str}.")
                    break # Une alerte vent suffit peut-être

        # --- 3. Indication "Beau Temps pour Activité Extérieure" (prochaines 12-24h) ---
        # Critères: peu de nuages, faible prob. précip., vent modéré
        if hourly_data.get("time") and hourly_data.get("cloudcover") and \
           hourly_data.get("precipitation_probability") and hourly_data.get("windspeed_10m"):

            beau_temps_periodes: List[str] = []
            heures_consecutives_beau_temps = 0
            periode_debut_str = ""

            # Analyser les prochaines 12 heures par exemple
            for i in range(min(12, len(hourly_data["time"]))):
                cloud = hourly_data["cloudcover"][i]
                precip_prob = hourly_data["precipitation_probability"][i]
                wind = hourly_data["windspeed_10m"][i]
                time_dt = datetime.datetime.fromisoformat(hourly_data["time"][i].replace("Z","+00:00")).astimezone()

                if cloud is not None and precip_prob is not None and wind is not None and \
                   cloud <= 30 and precip_prob <= 15 and wind <= 25: # Seuils à ajuster
                    if heures_consecutives_beau_temps == 0:
                        periode_debut_str = time_dt.strftime("%Hh")
                    heures_consecutives_beau_temps += 1
                else:
                    if heures_consecutives_beau_temps >= 3: # Au moins 3h de beau temps consécutives
                        beau_temps_periodes.append(f"de {periode_debut_str} à {time_dt.strftime('%Hh')}")
                    heures_consecutives_beau_temps = 0

            # Vérifier la dernière période
            if heures_consecutives_beau_temps >= 3:
                fin_periode_dt = datetime.datetime.fromisoformat(hourly_data["time"][min(11, len(hourly_data["time"])-1)].replace("Z","+00:00")).astimezone()
                beau_temps_periodes.append(f"de {periode_debut_str} à {fin_periode_dt.strftime('%Hh')}")

            if beau_temps_periodes:
                insights.append(f"☀️ BEAU TEMPS: Conditions favorables pour activités extérieures prévues aujourd'hui/demain "
                                f"({', '.join(beau_temps_periodes)}).")
            # else:
            #     insights.append("ℹ️ Météo variable pour activités extérieures prochainement.")


        # --- 4. Tendance de la Pression Atmosphérique (sur les prochaines 6h) ---
        if current_data.get("pressure_msl") is not None and hourly_data.get("pressure_msl"):
            p_actuelle = current_data["pressure_msl"]
            # Pression dans 3h et 6h (si disponibles)
            p_3h = hourly_data["pressure_msl"][min(2, len(hourly_data["pressure_msl"])-1)] if len(hourly_data["pressure_msl"]) > 2 else None # index 2 = 3ème heure
            p_6h = hourly_data["pressure_msl"][min(5, len(hourly_data["pressure_msl"])-1)] if len(hourly_data["pressure_msl"]) > 5 else None # index 5 = 6ème heure

            if p_3h is not None:
                diff_3h = p_3h - p_actuelle
                if diff_3h < -1.5: # Baisse significative > 1.5 hPa en 3h
                    insights.append(f"📉 TENDANCE PRESSION: Baisse notable ({diff_3h:.1f} hPa/3h), dégradation possible.")
                elif diff_3h > 1.5: # Hausse significative
                    insights.append(f"📈 TENDANCE PRESSION: Hausse notable ({diff_3h:.1f} hPa/3h), amélioration possible.")
                # else:
                #     insights.append(f"ℹ️ TENDANCE PRESSION: Stable ou faible variation ({diff_3h:.1f} hPa/3h).")

            # On pourrait aussi ajouter une tendance sur 6h si p_6h est disponible.

        if not insights: # Si aucune alerte ou info majeure
            insights.append("Analyse météo: Pas d'alertes ou de tendances majeures pour le moment.")

        self.logger.info(f"Analyses générées: {len(insights)} insight(s).")
        return insights

    def _update_current_weather_display(self, weather_data: dict):
        try:
            current = weather_data.get("current", {})
            hourly = weather_data.get("hourly", {}) # Pour fallback ou données non dispo dans "current"
            daily = weather_data.get("daily", {})

            current_units = weather_data.get("current_units", {})
            hourly_units = weather_data.get("hourly_units", {}) # Pour fallback unités

            # --- Heure des données "actuelles" ---
            current_time_str = current.get("time")
            displayed_time_str = "(--:--)"
            if current_time_str:
                try:
                    # Convertir l'heure ISO en HH:MM locale
                    current_dt_utc = datetime.datetime.fromisoformat(current_time_str.replace("Z", "+00:00"))
                    current_dt_local = current_dt_utc.astimezone() # Convertir au fuseau horaire local du système
                    displayed_time_str = f"(pour {current_dt_local.strftime('%H:%M')})"
                except ValueError:
                    self.logger.warning(f"Format de date invalide pour current.time: {current_time_str}")
            self.current_data_time_label.config(text=displayed_time_str)

            # --- Fonction utilitaire interne pour obtenir les valeurs ---
            def get_val(data_block, units_block, key, fallback_block=None, fallback_units_block=None, unit_alt_key=None, precision=1, default_val="N/A"):
                val = data_block.get(key)
                units = units_block

                if val is None and fallback_block: # Tenter un fallback
                    val = fallback_block.get(key)
                    if val is not None and isinstance(val, list) and val: # Si c'est une liste horaire, prendre le premier élément
                        val = val[0]
                    if units is current_units and fallback_units_block: # Utiliser les unités du fallback si besoin
                        units = fallback_units_block

                unit_str = units.get(unit_alt_key if unit_alt_key else key, "")

                if val is None: return default_val
                if isinstance(val, (int, float)): # Vérifier si c'est un nombre avant de formater
                    return f"{val:.{precision}f}{unit_str}" if isinstance(val, float) else f"{val}{unit_str}"
                return f"{val}{unit_str}" # Pour les strings ou autres types

            # --- Description et Icône ---
            desc_code = current.get("weathercode", hourly.get("weathercode", [0])[0])
            is_day = current.get("is_day", hourly.get("is_day", [1])[0])
            desc, icon_char = self._get_weather_display_info(desc_code, is_day)

            self.current_weather_labels["description"].config(text=desc)
            self.current_weather_icon_label.config(text=icon_char)

            # --- Données principales ---
            self.current_weather_labels["temperature"].config(text=get_val(current, current_units, "temperature_2m", hourly, hourly_units))
            self.current_weather_labels["apparent_temp"].config(text=get_val(current, current_units, "apparent_temperature", hourly, hourly_units))
            self.current_weather_labels["humidity"].config(text=get_val(current, current_units, "relativehumidity_2m", hourly, hourly_units))
            self.current_weather_labels["pressure"].config(text=get_val(current, current_units, "pressure_msl", hourly, hourly_units, precision=0))

            # --- Précipitations (quantité) ---
            # "precipitation" est souvent dans "current" et "hourly"
            precip_val = get_val(current, current_units, "precipitation", hourly, hourly_units, precision=1)
            self.current_weather_labels["precipitation"].config(text=precip_val)

            # --- Couverture Nuageuse ---
            cloudcover_val = get_val(current, current_units, "cloudcover", hourly, hourly_units, precision=0)
            self.current_weather_labels["cloudcover"].config(text=cloudcover_val)

            # --- Vent ---
            wind_s = get_val(current, current_units, "windspeed_10m", hourly, hourly_units)
            wind_d_val = current.get("winddirection_10m", hourly.get("winddirection_10m", [None])[0])
            wind_d_unit = current_units.get("winddirection_10m", hourly_units.get("winddirection_10m", ""))
            wind_d_str = f"{wind_d_val}{wind_d_unit}" if wind_d_val is not None else "N/A"
            self.current_weather_labels["wind"].config(text=f"{wind_s} (Dir: {wind_d_str})")

            # --- Indice UV ---
            # UV n'est généralement pas dans "current", on le prend de "hourly" (première heure)
            uv_val_hourly = hourly.get("uv_index", [None])[0] if hourly.get("uv_index") else None
            uv_unit = hourly_units.get("uv_index", "")
            self.current_weather_labels["uv_index"].config(text=f"{uv_val_hourly}{uv_unit}" if uv_val_hourly is not None else "N/A")

            # --- Probabilité de Précipitation ---
            # Non dispo dans "current", prendre de "hourly"
            precip_prob_val_hourly = hourly.get("precipitation_probability", [None])[0] if hourly.get("precipitation_probability") else None
            precip_prob_unit = hourly_units.get("precipitation_probability","%")
            self.current_weather_labels["precipitation_prob"].config(text=f"{precip_prob_val_hourly}{precip_prob_unit}" if precip_prob_val_hourly is not None else "N/A")

            # --- Lever et Coucher du Soleil (du bloc journalier, index 0 pour aujourd'hui) ---
            if daily and daily.get("time") and len(daily["time"]) > 0:
                sunrise_iso = daily.get("sunrise", ["N/A"])[0]
                sunset_iso = daily.get("sunset", ["N/A"])[0]
                try:
                    sunrise_dt_str = datetime.datetime.fromisoformat(sunrise_iso.replace("Z", "+00:00")).strftime('%H:%M') if sunrise_iso != "N/A" else "N/A"
                    sunset_dt_str = datetime.datetime.fromisoformat(sunset_iso.replace("Z", "+00:00")).strftime('%H:%M') if sunset_iso != "N/A" else "N/A"
                    self.current_weather_labels["sunrise"].config(text=sunrise_dt_str)
                    self.current_weather_labels["sunset"].config(text=sunset_dt_str)
                except ValueError:
                    self.current_weather_labels["sunrise"].config(text="N/A")
                    self.current_weather_labels["sunset"].config(text="N/A")
        except Exception as e:
            self.update_status(f"Erreur màj aff. actuel: {e}")
            self.logger.error(f"Erreur _update_current_weather_display: {e}", exc_info=True) # Ajouté logger
            # traceback.print_exc() # Déjà loggué par exc_info=True

    def _clear_scrollable_frame(self, frame: ttk.Frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _degrees_to_cardinal(self, d: Optional[float]) -> str:
        """Convertit une direction en degrés en point cardinal."""
        if d is None:
            return "N/A"
        dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
        ix = round(d / (360. / len(dirs)))
        return dirs[int(ix % len(dirs))]

    def _update_hourly_forecast_display(self, weather_data: dict):
        self._clear_scrollable_frame(self.scrollable_hourly_frame)
        hourly = weather_data.get("hourly", {})
        units = weather_data.get("hourly_units", {})

        if not hourly.get("time"):
            ttk.Label(self.scrollable_hourly_frame, text="Prévisions horaires non disponibles.", font=self.data_font).pack()
            return

        # --- Header pour les prévisions horaires (utilisant grid) ---
        header_frame_h = ttk.Frame(self.scrollable_hourly_frame)
        header_frame_h.pack(fill="x", pady=(0, 2))

        # Configurer les colonnes du header
        # Heure | Météo | Temp. | Description | Vent (dir) | Précip. (mm) | Prob. Précip.
        col_widths_header = {
            0: {"text": "Heure", "min": 70, "weight": 0, "anchor": "w"},
            1: {"text": "Météo", "min": 35, "weight": 0, "anchor": "center"}, # Icône
            2: {"text": "Temp.", "min": 55, "weight": 0, "anchor": "w"},
            3: {"text": "Description", "min": 140, "weight": 2, "anchor": "w"}, # Plus de poids
            4: {"text": "Vent", "min": 65, "weight": 0, "anchor": "w"}, # Vitesse et Direction
            5: {"text": "Précip. (mm)", "min": 70, "weight": 0, "anchor": "w"}, # Quantité
            6: {"text": "Prob. Précip.", "min": 70, "weight": 0, "anchor": "w"}  # Probabilité
        }

        for col, conf in col_widths_header.items():
            header_frame_h.columnconfigure(col, weight=conf["weight"], minsize=conf["min"])
            ttk.Label(header_frame_h, text=conf["text"], font=self.small_data_font, anchor=conf["anchor"]).grid(
                row=0, column=col, padx=3, sticky="ew" if conf["anchor"] == "center" else conf["anchor"]
            )

        ttk.Separator(self.scrollable_hourly_frame, orient="horizontal").pack(fill="x", pady=(2, 5))

        # --- Données de prévisions horaires ---
        times = hourly.get("time", [])
        for i in range(min(len(times), HOURLY_FORECAST_HOURS)):
            row_frame = ttk.Frame(self.scrollable_hourly_frame)
            row_frame.pack(fill="x", pady=0) # Moins de padding vertical pour les lignes

            # Configurer les colonnes pour cette ligne de données
            for col, conf in col_widths_header.items():
                 row_frame.columnconfigure(col, weight=conf["weight"], minsize=conf["min"])

            # --- Extraction et formatage des données pour cette heure ---
            try:
                time_dt = datetime.datetime.fromisoformat(times[i].replace("Z", "+00:00"))
                time_str = time_dt.strftime("%Hh")
                day_str = time_dt.strftime("%a").capitalize()
                if time_dt.date() == datetime.date.today(): day_str = "Auj."
                elif time_dt.date() == datetime.date.today() + datetime.timedelta(days=1): day_str = "Dem."
                else: day_str = f"{day_str} {time_dt.day}"
                time_display_str = f"{day_str} {time_str}"
            except ValueError:
                time_display_str = times[i]

            temp_val = hourly.get("temperature_2m", [None])[i]
            temp_unit = units.get("temperature_2m", "°C")
            temp_str = f"{temp_val}{temp_unit}" if temp_val is not None else "N/A"

            precip_prob_val = hourly.get("precipitation_probability", [None])[i]
            precip_prob_unit = units.get("precipitation_probability", "%")
            precip_prob_str = f"{precip_prob_val}{precip_prob_unit}" if precip_prob_val is not None else "N/A"

            # Nouvelle donnée: Quantité de précipitation
            precip_qty_val = hourly.get("precipitation", [None])[i] # 'precipitation' est la somme de pluie, neige, etc.
            precip_qty_unit = units.get("precipitation", "mm")
            precip_qty_str = f"{precip_qty_val}{precip_qty_unit}" if precip_qty_val is not None else "N/A"

            # Nouvelle donnée: Vent (vitesse et direction textuelle)
            wind_speed_val = hourly.get("windspeed_10m", [None])[i]
            wind_speed_unit = units.get("windspeed_10m", "km/h")
            wind_dir_deg = hourly.get("winddirection_10m", [None])[i]
            wind_dir_cardinal = self._degrees_to_cardinal(wind_dir_deg)
            wind_str = "N/A"
            if wind_speed_val is not None:
                wind_str = f"{wind_speed_val}{wind_speed_unit} {wind_dir_cardinal}"

            weather_code_val = hourly.get("weathercode", [0])[i]
            is_day_val = hourly.get("is_day", [1])[i]
            desc_text, icon_unicode = self._get_weather_display_info(weather_code_val, is_day_val)
            short_desc_text = desc_text.split(',')[0].split('(')[0].strip()

            # --- Création des labels avec grid ---
            # Heure
            ttk.Label(row_frame, text=time_display_str, font=self.small_data_font, anchor="w").grid(row=0, column=0, padx=3, sticky="w")
            # Météo (Icône)
            ttk.Label(row_frame, text=icon_unicode, font=self.icon_font, anchor="center").grid(row=0, column=1, padx=3, sticky="ew")
            # Température
            ttk.Label(row_frame, text=temp_str, font=self.small_data_font, anchor="w").grid(row=0, column=2, padx=3, sticky="w")
            # Description
            ttk.Label(row_frame, text=short_desc_text, font=self.small_data_font, anchor="w").grid(row=0, column=3, padx=3, sticky="w")
            # Vent (Vitesse + Direction)
            ttk.Label(row_frame, text=wind_str, font=self.small_data_font, anchor="w").grid(row=0, column=4, padx=3, sticky="w")
            # Précipitation (Quantité mm)
            ttk.Label(row_frame, text=precip_qty_str, font=self.small_data_font, anchor="w").grid(row=0, column=5, padx=3, sticky="w")
            # Probabilité Précipitation
            ttk.Label(row_frame, text=f"💧{precip_prob_str}", font=self.small_data_font, anchor="w").grid(row=0, column=6, padx=3, sticky="w")


    def _update_daily_forecast_display(self, weather_data: dict):
        self._clear_scrollable_frame(self.scrollable_daily_frame)
        daily = weather_data.get("daily", {})
        units = weather_data.get("daily_units", {})

        if not daily.get("time"): # Si la clé 'time' elle-même manque ou est vide
            ttk.Label(self.scrollable_daily_frame, text="Prévisions journalières non disponibles.", font=self.data_font).pack()
            return

        header_frame_d = ttk.Frame(self.scrollable_daily_frame)
        header_frame_d.pack(fill="x", pady=(0, 2))
        col_widths_header_daily = {
            0: {"text": "Jour", "min": 90, "weight": 0, "anchor": "w"}, 1: {"text": "Météo", "min": 35, "weight": 0, "anchor": "center"},
            2: {"text": "Max/Min", "min": 70, "weight": 0, "anchor": "w"}, 3: {"text": "Description", "min": 150, "weight": 2, "anchor": "w"},
            4: {"text": "Vent Dom.", "min": 75, "weight": 0, "anchor": "w"}, 5: {"text": "Précip. Σ", "min": 70, "weight": 0, "anchor": "w"},
            6: {"text": "UV Max", "min": 50, "weight": 0, "anchor": "w"}
        }
        for col, conf in col_widths_header_daily.items():
            header_frame_d.columnconfigure(col, weight=conf["weight"], minsize=conf["min"])
            ttk.Label(header_frame_d, text=conf["text"], font=self.small_data_font, anchor=conf["anchor"]).grid(
                row=0, column=col, padx=3, sticky="ew" if conf["anchor"] == "center" else conf["anchor"]
            )
        ttk.Separator(self.scrollable_daily_frame, orient="horizontal").pack(fill="x", pady=(2, 5))

        times_list = daily.get("time", []) # Récupérer la liste des dates
        if not times_list: # Vérifier si la liste de dates est vide
            ttk.Label(self.scrollable_daily_frame, text="Données de temps journalières non disponibles.", font=self.data_font).pack()
            return

        # Récupérer toutes les listes de données une fois
        temp_max_list = daily.get("temperature_2m_max", [])
        temp_min_list = daily.get("temperature_2m_min", [])
        weather_code_list = daily.get("weathercode", [])
        precip_sum_list = daily.get("precipitation_sum", [])
        wind_dir_dom_deg_list = daily.get("winddirection_10m_dominant", [])
        uv_max_list = daily.get("uv_index_max", [])

        for i in range(min(len(times_list), FORECAST_DAYS)):
            row_frame = ttk.Frame(self.scrollable_daily_frame)
            row_frame.pack(fill="x", pady=1)
            for col, conf in col_widths_header_daily.items():
                 row_frame.columnconfigure(col, weight=conf["weight"], minsize=conf["min"])

            try:
                date_dt = datetime.datetime.fromisoformat(times_list[i])
                date_str = f"{date_dt.strftime('%a').capitalize()} {date_dt.day} {date_dt.strftime('%b').capitalize()}"
            except (ValueError, IndexError): # Index error si times_list est plus courte que prévu
                date_str = times_list[i] if i < len(times_list) else "N/A Date"

            temp_max_val = temp_max_list[i] if i < len(temp_max_list) else None
            temp_min_val = temp_min_list[i] if i < len(temp_min_list) else None
            temp_unit = units.get("temperature_2m_max", "°C")

            weather_code_val = weather_code_list[i] if i < len(weather_code_list) else 0 # Fallback à 0 (ciel clair) si code manquant
            desc_text, icon_unicode = self._get_weather_display_info(weather_code_val)

            max_min_temp_str = "N/A"
            if temp_max_val is not None and temp_min_val is not None:
                max_min_temp_str = f"{temp_max_val}° / {temp_min_val}{temp_unit}"
            elif temp_max_val is not None:
                max_min_temp_str = f"{temp_max_val}{temp_unit} / -"
            elif temp_min_val is not None:
                max_min_temp_str = f"- / {temp_min_val}{temp_unit}"

            precip_sum_val = precip_sum_list[i] if i < len(precip_sum_list) else None
            precip_sum_unit = units.get("precipitation_sum", "mm")
            precip_sum_str = f"{precip_sum_val}{precip_sum_unit}" if precip_sum_val is not None else "N/A"

            wind_dir_dom_deg = wind_dir_dom_deg_list[i] if i < len(wind_dir_dom_deg_list) else None
            wind_dom_str = self._degrees_to_cardinal(wind_dir_dom_deg)

            uv_max_val = uv_max_list[i] if i < len(uv_max_list) else None
            uv_max_str = f"{uv_max_val:.1f}" if isinstance(uv_max_val, float) else (str(uv_max_val) if uv_max_val is not None else "N/A")

            ttk.Label(row_frame, text=date_str, font=self.small_data_font, anchor="w").grid(row=0, column=0, padx=3, sticky="w")
            ttk.Label(row_frame, text=icon_unicode, font=self.icon_font, anchor="center").grid(row=0, column=1, padx=3, sticky="ew")
            ttk.Label(row_frame, text=max_min_temp_str, font=self.small_data_font, anchor="w").grid(row=0, column=2, padx=3, sticky="w")
            ttk.Label(row_frame, text=desc_text, font=self.small_data_font, anchor="w").grid(row=0, column=3, padx=3, sticky="w")
            ttk.Label(row_frame, text=wind_dom_str, font=self.small_data_font, anchor="w").grid(row=0, column=4, padx=3, sticky="w")
            ttk.Label(row_frame, text=precip_sum_str, font=self.small_data_font, anchor="w").grid(row=0, column=5, padx=3, sticky="w")
            ttk.Label(row_frame, text=uv_max_str, font=self.small_data_font, anchor="w").grid(row=0, column=6, padx=3, sticky="w")

    def update_status(self, message: str):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def save_weather_data(self, data: dict):
        if not SAVE_DIR.is_dir():
            self.update_status(f"Erreur: Dossier de sauvegarde {SAVE_DIR} non trouvé.")
            messagebox.showerror("Erreur Sauvegarde", f"Le dossier de sauvegarde n'existe pas:\n{SAVE_DIR}", parent=self.root)
            return
        now = datetime.datetime.now()
        filename = f"meteo_data_{now.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = SAVE_DIR / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.update_status(f"Données sauvegardées: {filepath.name} à {now.strftime('%H:%M:%S')}")
            print(f"Données météo sauvegardées dans : {filepath}")
        except Exception as e:
            self.update_status(f"Erreur sauvegarde: {e}")
            messagebox.showerror("Erreur Sauvegarde", f"Impossible de sauvegarder dans {filepath}:\n{e}", parent=self.root)
            print(f"Erreur sauvegarde données: {e}")

    def fetch_weather_data_thread(self):
        self.refresh_button.config(state=tk.DISABLED)
        self.update_status("Récupération des données météo en cours...")

        # --- TEST DE CONNEXION HTTPS DE BASE ---
        api_url_test_google = "https://www.google.com"
        google_test_success = False
        self.logger.info(f"--- DÉBUT TEST CONNEXION : Appel à {api_url_test_google} ---")
        try:
            response_google = requests.get(api_url_test_google, timeout=10)
            response_google.raise_for_status() # Vérifie les erreurs HTTP (4xx, 5xx)
            self.logger.info(f"--- TEST CONNEXION SUCCÈS : Réponse de {api_url_test_google} - Statut: {response_google.status_code} ---")
            # self.logger.debug(f"Contenu Google (début): {response_google.text[:200]}") # Optionnel
            google_test_success = True
        except requests.exceptions.RequestException as e_google:
            self.logger.error(f"--- TEST CONNEXION ÉCHEC : Impossible de joindre {api_url_test_google}: {e_google} ---", exc_info=True)
            msg_google_fail = f"Échec du test de connexion Internet de base ({api_url_test_google}):\n{e_google}\nVérifiez votre connexion et/ou configuration réseau/proxy/pare-feu."
            self.root.after(0, self.update_status, msg_google_fail)
            self.root.after(0, lambda m=msg_google_fail: messagebox.showerror("Erreur Connexion Internet", m, parent=self.root))
            self.root.after(0, lambda: self.refresh_button.config(state=tk.NORMAL)) # Réactiver le bouton
            return # Arrêter ici si le test de base échoue
        # --- FIN TEST DE CONNEXION HTTPS DE BASE ---

        # Si le test Google a réussi, on continue avec Open-Meteo
        if not google_test_success: # Double sécurité, ne devrait pas être atteint si return est fait
            self.logger.error("Le test Google n'a pas réussi, arrêt de la tentative Open-Meteo.")
            return

        self.logger.info("Test de connexion Google réussi. Tentative d'appel à Open-Meteo...")
        api_url_open_meteo = "https://api.open-meteo.com/v1/forecast" # AJOUT DE API.
        # Utiliser les paramètres simplifiés pour le test Open-Meteo
        current_variables_list = [
            "temperature_2m", "relativehumidity_2m", "apparent_temperature", "is_day",
            "precipitation", "weathercode", "cloudcover", "pressure_msl",
            "windspeed_10m", "winddirection_10m", "uv_index" # Ajout de uv_index pour l'affichage actuel
        ]

        params_open_meteo = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": ",".join(current_variables_list), # Joindre la liste en une chaîne
            "hourly": ",".join(HOURLY_VARIABLES),     # HOURLY_VARIABLES est déjà une liste de strings
            "daily": ",".join(DAILY_VARIABLES),       # DAILY_VARIABLES est déjà une liste de strings
            "timezone": TIMEZONE,
            "forecast_days": FORECAST_DAYS            # Utiliser ta constante FORECAST_DAYS
        }

        # Log de l'URL construite pour Open-Meteo
        # Pour construire l'URL à des fins de logging sans faire la requête:
        prepared_request = requests.Request('GET', api_url_open_meteo, params=params_open_meteo).prepare()
        self.logger.info(f"URL API Open-Meteo construite: {prepared_request.url}")

        try:
            response = requests.get(api_url_open_meteo, params=params_open_meteo, timeout=20)
            response.raise_for_status()
            weather_data = response.json()
            self.logger.debug("Données météo JSON reçues de l'API Open-Meteo.")

            # Remettre ici la logique complète si tu veux tester l'affichage avec les données simplifiées
            self.root.after(0, self._update_current_weather_display, weather_data)
            # Pour un test plus ciblé de l'API, tu peux commenter les lignes suivantes temporairement :
            # self.root.after(0, self._update_hourly_forecast_display, weather_data) # Aura besoin de 'hourly' dans params
            # self.root.after(0, self._update_daily_forecast_display, weather_data)   # Aura besoin de 'daily' dans params
            # if hasattr(self, '_update_all_graphs'):
            #     self.root.after(0, self._update_all_graphs, weather_data)
            # if hasattr(self, '_generate_derived_insights') and hasattr(self, '_update_analysis_tab_display'):
            #     insights = self._generate_derived_insights(weather_data)
            #     self.root.after(0, self._update_analysis_tab_display, insights)
            self.root.after(0, self.save_weather_data, weather_data) # Garder la sauvegarde pour voir le JSON reçu

        except requests.exceptions.Timeout:
            msg = "Erreur: Timeout API Open-Meteo."
            self.root.after(0, self.update_status, msg)
            self.root.after(0, lambda m=msg: messagebox.showerror("Erreur API Météo", m, parent=self.root))
            self.logger.error(msg)
        except requests.exceptions.RequestException as e: # Inclut HTTPError pour 404, etc.
            msg = f"Erreur de requête API Open-Meteo: {e}"
            self.root.after(0, self.update_status, msg)
            self.root.after(0, lambda m=msg, e_arg=e: messagebox.showerror("Erreur API Météo", m, parent=self.root))
            self.logger.error(msg, exc_info=True)
        except json.JSONDecodeError:
            msg = "Erreur: Réponse invalide de l'API Open-Meteo (pas JSON)."
            self.root.after(0, self.update_status, msg)
            self.root.after(0, lambda m=msg: messagebox.showerror("Erreur API Météo", m, parent=self.root))
            self.logger.error(msg)
        except Exception as e_generic:
            msg = f"Erreur inattendue lors de la récupération des données Open-Meteo: {e_generic}"
            self.root.after(0, self.update_status, msg)
            self.root.after(0, lambda m=msg, e_arg=e_generic: messagebox.showerror("Erreur Inattendue Météo", m, parent=self.root))
            self.logger.error(f"Erreur inattendue dans fetch_weather_data_thread (Open-Meteo): {e_generic}", exc_info=True)
        finally:
            self.root.after(0, lambda: self.refresh_button.config(state=tk.NORMAL))

    def start_fetch_weather_data(self):
        thread = threading.Thread(target=self.fetch_weather_data_thread, daemon=True)
        thread.start()

if __name__ == '__main__':
    root = tk.Tk()
    s = ttk.Style()
    try: s.theme_use('clam')
    except tk.TclError: pass
    app = MeteoAlmaApp(root)
    root.mainloop()