# cerveau.py
"""
---
name: cerveau.py
version: 20.5.1-alpha # Version incrémentée pour refléter les corrections et l'intégration psutil/embeddings
author: Toni
description: "Module central d'analyse et d'amélioration continue de la base de connaissances d'ALMA (V20 Intégration Core)."
role: Analyse et amélioration continue de la base de connaissances
type_execution: service
état: actif
last_update: 2025-05-25 # Mise à jour pour intégration filtres NER
dossier: Cerveau
tags: [V20, connaissance, analyse, amélioration, service, NLP, AI, config, modular, robust, sqlite, spacy, core_integration, psutil, embeddings, ner_filtering]
dependencies: [watchdog, PyYAML, spacy, filelock, psutil (optionnel mais recommandé)]
optional_nlp_dependencies: [nltk, rake_nltk, yake, scikit-learn]
---
"""

import os
import sys
print(f"DEBUG SCRIPT (début): Exécutable Python: {sys.executable}")
print(f"DEBUG SCRIPT (début): sys.path: {sys.path}")

# --- TEST DE CHARGEMENT SPACY MINIMALISTE AU DÉBUT ---
print("DEBUG SCRIPT (début): Tentative de chargement spaCy et modèle fr_core_news_lg PAR CHEMIN ABSOLU...")
CHEMIN_MODELE_SPACY_LG = "/home/toni/Documents/ALMA/venv/lib/python3.12/site-packages/fr_core_news_lg/fr_core_news_lg-3.8.0"
try:
    import spacy # Import local pour le test
    print("DEBUG SCRIPT (début): 'import spacy' (pour test) RÉUSSI.")
    nlp_test_instance = spacy.load(CHEMIN_MODELE_SPACY_LG)
    print(f"DEBUG SCRIPT (début): MODÈLE '{CHEMIN_MODELE_SPACY_LG}' CHARGÉ AVEC SUCCÈS (test).")
    print(f"DEBUG SCRIPT (début): Pipeline du modèle testé: {nlp_test_instance.pipe_names}")
    if hasattr(nlp_test_instance, 'vocab') and hasattr(nlp_test_instance.vocab, 'vectors_length') and nlp_test_instance.vocab.vectors_length > 0:
        print(f"DEBUG SCRIPT (début): Vecteurs présents (test), dimension: {nlp_test_instance.vocab.vectors_length}")
    else:
        print("DEBUG SCRIPT (début): AVERTISSEMENT (test) - Vecteurs NON présents ou non détectables facilement dans le modèle chargé.")
except ImportError as e_imp_test_spacy:
    print(f"ERREUR DEBUG SCRIPT (début test): Échec de 'import spacy': {e_imp_test_spacy}")
except Exception as e_spacy_load_test:
    print(f"ERREUR DEBUG SCRIPT (début test): Échec lors de spacy.load('{CHEMIN_MODELE_SPACY_LG}'): {type(e_spacy_load_test).__name__}: {e_spacy_load_test}")
print("--- FIN DU TEST DE CHARGEMENT SPACY MINIMALISTE AU DÉBUT ---")

import time
import datetime
import logging
from logging.handlers import RotatingFileHandler
import threading
import signal
import json
import hashlib
import re
import tempfile
import sqlite3
from pathlib import Path
from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError
from typing import Any, Dict, List, Optional, Tuple, Deque, Type, Union
import platform

# --- IMPORT CONDITIONNEL WATCHDOG (DÉPLACÉ ICI) ---
WATCHDOG_AVAILABLE = False
Observer_alias: Optional[Type] = None # Pour typer Observer
FileSystemEventHandler_alias: Optional[Type] = None # Pour typer FileSystemEventHandler
try:
    from watchdog.observers import Observer as ImportedObserver
    from watchdog.events import FileSystemEventHandler as ImportedFileSystemEventHandler
    Observer_alias = ImportedObserver
    FileSystemEventHandler_alias = ImportedFileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    print("DEBUG SCRIPT: 'watchdog.observers.Observer' et 'watchdog.events.FileSystemEventHandler' importés avec succès.")
except ImportError:
    print("DEBUG SCRIPT: 'watchdog' non trouvé ou impossible à importer. La surveillance événementielle sera désactivée.")
Observer = Observer_alias # Rendre accessible globalement (ou None)
FileSystemEventHandler = FileSystemEventHandler_alias # Rendre accessible globalement (ou None)

# --- IMPORT CONDITIONNEL YAML ---
YAML_AVAILABLE = False
yaml_module_alias = None
try:
    import yaml as yaml_imported_module
    yaml_module_alias = yaml_imported_module
    YAML_AVAILABLE = True
    print("DEBUG SCRIPT: PyYAML importé avec succès.")
except ImportError:
    print("DEBUG SCRIPT: PyYAML non trouvé ou impossible à importer.")
# --- FIN IMPORT YAML ---

# --- IMPORT CONDITIONNEL PSUTIL ---
PSUTIL_AVAILABLE = False
psutil_module_alias = None
try:
    import psutil as psutil_imported_module
    psutil_module_alias = psutil_imported_module
    PSUTIL_AVAILABLE = True
    print("DEBUG SCRIPT: psutil importé avec succès.")
except ImportError:
    print("DEBUG SCRIPT: psutil non trouvé ou impossible à importer.")
psutil = psutil_module_alias
# --- FIN IMPORT PSUTIL ---

# --- LIGNES DE DEBUG (peuvent être retirées en production) ---
# print(f"DEBUG SCRIPT: Exécutable Python utilisé par cerveau.py: {sys.executable}")
# print(f"DEBUG SCRIPT: sys.path utilisé par cerveau.py: {sys.path}")
# --- FIN LIGNES DE DEBUG ---

# --- V20 CORE INTEGRATION ---
alma_core = None                # Variable globale pour le module importé
ALMA_CORE_AVAILABLE = False     # DÉCLARER ET INITIALISER LA GLOBALE ICI

try:
    from .Core import core as alma_core_imported_module # Import relatif
    alma_core = alma_core_imported_module
    ALMA_CORE_AVAILABLE = True # Mettre à jour la globale si l'import réussit
    print("DEBUG SCRIPT: Import de '.Core.core as alma_core' RÉUSSI.")
except ImportError as e_core_imp:
    # alma_core reste None, ALMA_CORE_AVAILABLE reste False (valeur initiale)
    print(f"ERREUR DEBUG SCRIPT: Échec de 'from .Core import core as alma_core': {e_core_imp}")
except Exception as e_core_general:
    # alma_core reste None, ALMA_CORE_AVAILABLE reste False (valeur initiale)
    print(f"ERREUR DEBUG SCRIPT: Erreur générale import Core: {type(e_core_general).__name__}: {e_core_general}")
# --- FIN CORE INTEGRATION ---

# --- Imports Conditionnels pour spaCy et ses composants ---
spacy_module: Optional[Any] = None
SpacyDoc_class: Optional[Type] = None
SPACY_STOP_WORDS_SET: set = set()
ModelsNotFound_exception: Optional[Type[Exception]] = None
try:
    import spacy as spacy_global_import
    spacy_module = spacy_global_import
    print("DEBUG SCRIPT: Import global de 'spacy' RÉUSSI.")
    # ... (imports Doc, STOP_WORDS, ModelsNotFound comme dans votre code)
    try:
        from spacy.tokens import Doc as SpacyDoc_imported_class_local
        SpacyDoc_class = SpacyDoc_imported_class_local
        print("DEBUG SCRIPT: 'spacy.tokens.Doc' importé.")
    except ImportError: print("DEBUG SCRIPT: Échec import 'spacy.tokens.Doc'.")
    try:
        from spacy.lang.fr.stop_words import STOP_WORDS as fr_stopwords
        SPACY_STOP_WORDS_SET.update(fr_stopwords)
        print(f"DEBUG SCRIPT: Stopwords français spaCy chargés ({len(fr_stopwords)}).")
    except ImportError:
        print("DEBUG SCRIPT: Stopwords français spaCy non trouvés. Tentative avec anglais.")
        try:
            from spacy.lang.en.stop_words import STOP_WORDS as en_stopwords
            SPACY_STOP_WORDS_SET.update(en_stopwords)
            print(f"DEBUG SCRIPT: Stopwords anglais spaCy chargés ({len(en_stopwords)}).")
        except ImportError: print("DEBUG SCRIPT: Stopwords anglais spaCy non trouvés non plus.")
    if hasattr(spacy_module, 'errors') and hasattr(spacy_module.errors, 'ModelsNotFound'):
        ModelsNotFound_exception = spacy_module.errors.ModelsNotFound
        print("DEBUG SCRIPT: Exception 'spacy.errors.ModelsNotFound' récupérée.")
    else: print("DEBUG SCRIPT: Impossible de récupérer 'spacy.errors.ModelsNotFound'.")
except ImportError: print("DEBUG SCRIPT: Échec de l'import global de 'spacy'.")
except Exception as e_spacy_global_setup: print(f"DEBUG SCRIPT: Erreur config globale de spaCy: {e_spacy_global_setup}")
spacy = spacy_module
SpacyDoc = SpacyDoc_class
SPACY_STOP_WORDS = SPACY_STOP_WORDS_SET
ModelsNotFound = ModelsNotFound_exception
# --- FIN Imports spaCy ---

# --- Imports Conditionnels pour FileLock et fcntl ---
# ... (comme dans votre code)
ExternalFileLock: Optional[Type] = None
FileLockTimeout: Optional[Type[Exception]] = None
try:
    from filelock import FileLock as ImportedFileLock, Timeout as ImportedFileLockTimeout
    ExternalFileLock = ImportedFileLock
    FileLockTimeout = ImportedFileLockTimeout
    print("DEBUG SCRIPT: 'filelock' importé.")
except ImportError: print("DEBUG SCRIPT: 'filelock' non trouvé.")
fcntl_module_alias: Optional[Any] = None
if platform.system() != "Windows":
    try:
        import fcntl as fcntl_imported_module
        fcntl_module_alias = fcntl_imported_module
        print("DEBUG SCRIPT: 'fcntl' importé.")
    except ImportError: print("DEBUG SCRIPT: 'fcntl' non trouvé.")
else: print("DEBUG SCRIPT: 'fcntl' non applicable sur Windows.")
fcntl = fcntl_module_alias
# --- FIN Imports FileLock et fcntl --- #

# --- Initialisation des variables globales pour les bibliothèques NLP optionnelles --- #
nltk: Optional[Any] = None
#rake_nltk: Optional[Any] = None
Rake_class_alias = None # Nouvelle variable pour la classe
yake: Optional[Any] = None
sklearn_tfidf: Optional[Any] = None
try:
    import nltk as nltk_global_import
    nltk = nltk_global_import
    print("DEBUG SCRIPT: NLTK pré-importé globalement.")
except ImportError: print("DEBUG SCRIPT: NLTK non trouvé globalement.")
# --- FIN NLP Optionnelles ---

# --- Constantes de Chemin et Configuration ---
BASE_ALMA_DIR_ENV_VAR: str = "ALMA_BASE_DIR"
DEFAULT_BASE_ALMA_DIR_STR: str = "/home/toni/Documents/ALMA" # Garder en str pour os.getenv
DEFAULT_BASE_ALMA_DIR: Path = Path(DEFAULT_BASE_ALMA_DIR_STR)
CONFIG_FILE_NAME: str = "cerveau_config.yaml"

_base_alma_dir_env = os.getenv(BASE_ALMA_DIR_ENV_VAR)
BASE_ALMA_DIR: Path = Path(_base_alma_dir_env).resolve() if _base_alma_dir_env else DEFAULT_BASE_ALMA_DIR.resolve()
print(f"DEBUG SCRIPT: ALMA_BASE_DIR final utilisé: {BASE_ALMA_DIR}")

CONFIG_FILE_PATH: Path = BASE_ALMA_DIR / "Cerveau" / CONFIG_FILE_NAME
# --- FIN Constantes de Chemin ---

DEFAULT_CONFIG: Dict[str, Any] = {
    # ... (votre DEFAULT_CONFIG complet ici, avec la section logging.rotation et service_params.excluded_dir_parts) #
    "paths": {"connaissance_dir_suffix": "Connaissance", "cerveau_dir_suffix": "Cerveau", "log_dir_suffix": "logs", "improvements_subdir": "ameliorations_proposees", "active_improvements_dir_suffix": "Connaissance/Amelioree"},
    "logging": {"log_file_name": "cerveau.log", "emergency_log_file_name": "cerveau_emergency.log", "module_registry_file_name": "module_registry.json", "module_registry_lock_file_name": "module_registry.lock", "rotation": {"max_bytes": 20971520, "backup_count": 5}},
    "service_params": {"watchdog_enabled": True, "file_scan_interval_seconds": 60, "allowed_file_extensions": [".txt", ".md", ".json", ".xml", ".py", ".sh"], "max_workers": os.cpu_count() or 4, "file_queue_max_size": 1000, "self_report_interval_seconds": 3600, "task_timeout_seconds": 300, "backpressure_active_task_multiplier": 3, "health_check_interval_seconds": 900, "excluded_dir_parts": ['.venv', 'venv', 'env', '__pycache__', 'node_modules', '.git', '.hg', '.svn'], "excluded_dir_prefixes": ['.']},
    "circuit_breaker": {"threshold": 3, "timeout_seconds": 3600},
    "nlp": {"use_spacy_if_available": True, "spacy_model_names": ["fr_core_news_lg", "fr_core_news_sm", "en_core_web_sm"], "spacy_max_text_length": 1000000, "sentiment_positive_words": ["bon", "excellent", "super", "amélioration", "positif", "correct", "valide", "réussi"], "sentiment_negative_words": ["mauvais", "erreur", "problème", "négatif", "pire", "invalide", "échec", "cassé"], "significant_pos_tags": ["NOUN", "PROPN", "VERB", "ADJ"], "use_nltk_if_available": True, "use_rake_if_available": True, "use_yake_if_available": True, "use_sklearn_tfidf_if_available": True, "default_language": "fr"},
    "knowledge_base": {"use_sqlite_db": True, "db_name": "cerveau_knowledge.sqlite", "schema_file": "cerveau_kb_schema.sql", "db_timeout_seconds": 10},
    "pipeline_steps": {"ComprehensionStep": {"enabled": True, "priority": 10}, "AnalysisStep": {"enabled": True, "priority": 20, "sentiment_threshold": 0.1}, "StudyStep": {"enabled": True, "priority": 30}, "ImprovementProposalStep": {"enabled": True, "priority": 40}, "ActiveImprovementStep": {"enabled": True, "priority": 50, "auto_apply_summary": False, "auto_apply_grammar": False}},
    "core_algorithms_config": {"text_improver": {"default_language": "fr", "summary_ratio": 0.15, "grammar_api_config": None}, "knowledge_linker": {"min_similarity_for_link": 0.7, "num_semantic_links_to_propose": 5}} # Ajout num_semantic_links_to_propose
}
APP_CONFIG: Dict[str, Any] = {}

# --- DÉCLARATION ET INITIALISATION DES VARIABLES GLOBALES DE CHEMIN (Basées sur DEFAULT_CONFIG) ---
_base_alma_dir_resolved_for_globals = Path(os.getenv(BASE_ALMA_DIR_ENV_VAR, DEFAULT_BASE_ALMA_DIR_STR)).resolve() # Utiliser la str pour getenv

CONNAISSANCE_DIR: Path = _base_alma_dir_resolved_for_globals / DEFAULT_CONFIG["paths"]["connaissance_dir_suffix"]
CERVEAU_DIR: Path = _base_alma_dir_resolved_for_globals / DEFAULT_CONFIG["paths"]["cerveau_dir_suffix"]
LOG_DIR: Path = _base_alma_dir_resolved_for_globals / DEFAULT_CONFIG["paths"]["log_dir_suffix"]
LOG_FILE: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["log_file_name"]
EMERGENCY_LOG_FILE: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["emergency_log_file_name"]
MODULE_REGISTRY_PATH: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["module_registry_file_name"]
MODULE_REGISTRY_LOCK_PATH: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["module_registry_lock_file_name"]
IMPROVEMENTS_DIR: Path = CERVEAU_DIR / DEFAULT_CONFIG["paths"]["improvements_subdir"]
ACTIVE_IMPROVEMENTS_DIR: Path = _base_alma_dir_resolved_for_globals / DEFAULT_CONFIG["paths"]["active_improvements_dir_suffix"]
KB_DB_PATH: Optional[Path] = None
if DEFAULT_CONFIG["knowledge_base"]["use_sqlite_db"]:
    KB_DB_PATH = CERVEAU_DIR / DEFAULT_CONFIG["knowledge_base"]["db_name"]
# --- FIN DÉCLARATION GLOBALES DE CHEMIN ---

SCRIPT_NAME: str = Path(__file__).name if '__file__' in globals() else "cerveau.py" # Plus robuste si __file__ n'est pas défini
MODULE_VERSION: str = "20.5.1-alpha" # Version mise à jour
MODULE_NAME: str = "Cerveau"

log_lock: threading.Lock = threading.Lock()
logger: logging.Logger = logging.getLogger(MODULE_NAME)
AUDIT_LEVEL_NUM: int = 25
# --- FIN VARIABLES GLOBALES DE BASE ---


# >>> EMPLACEMENT POUR LES CONSTANTES DE FILTRAGE NER <<<
# --- Constantes pour le Filtrage NER ---
ENTITY_TEXT_BLACKLIST = {
    "http", "https", "www", "com", "org", "net", "html", "css", "js", "div", "span", "class",
    "id", "px", "em", "rem", "pt", "rgb", "rgba", "true", "false", "null", "none", "td", "tr", "th",
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche",
    "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre",
    "ko", "mo", "go", "to", "=", ";", ":", "{", "}", "(", ")", "[", "]", "<", ">",
    "script", "style", "font", "color", "background", "width", "height", "margin", "padding",
    "border", "display", "position", "index", "content", "data", "value", "type", "name",
    "nbsp", "amp", "lt", "gt", "quot", "apos", "error", "warning", "info", "debug",
    "traceback", "exception", "path", "file", "line", "pid", "tid",
    "var", "let", "const", "function", "return", "if", "else", "for", "while",
    "src", "href", "alt", "title", "target", "pointer", "cursor", "flex", "grid",
    "absolute", "relative", "static", "arial", "helvetica", "times new roman", "verdana",
    "tahoma", "segoe ui", "note", "important", "tip", "example",
    "config", "settings", "params", "status", "report", "summary", "details", # Termes génériques de log/config
    "texte", "document", "fichier", "analyse", "module", "version", "auteur", # Mots français courants
    "github", "gitlab", "commit", "branch", "merge", "pull", "push", # Termes Git
    "api", "url", "uri", "json", "xml", "yaml", # Termes techniques
    # Termes vus dans vos logs d'explorateur qui sont du bruit :
    "pointer;=", "cu=", "flex-grow", "max-width:100", ".9489", "adius", "rgb(170",
    "scale(1.05", "translate(-5=", "9px", "a9", "background-co=\n", "content:=", "ellipsis",
    "heig=", "height:=", "middle", ".25544", ".53033", ".8104", ".9017", ".91903",
    ".icon[data-v-8ad1b7ca", ".news_link[data", "2cc", "<span class=3d\"hljs-attr\">href</span>=3d<span",
    "c3", "fe2f", "h11.25c11.4489", "direction:=", "pre-wrap", "r\">0</span", "us",
    ".conversa=", ".input-focused", ".input-icon", "e2=94=9c", "e2=94=9c=", "in=", "items:=",
    "justify-conten=\nt", "margi=", "nt-size", "te=", "uppercase", "v-3bface01",
    "xmln=\ns=3d\"http://www.w3.org/2000", "14p=\nx", "1s ease-in-out", "3ff",
    "kb</div></div></div></div></div></div></div><div", "bac=\nkground-color", "ce=\nnter",
    "data-v-e47f9881", "pre { background: none", "style:=", "svg path { stroke", "ter",
    "var(--tw-bg-opacity,1", "widt=", "--tw-bg-opacity", ".-md-ext-promptlink",
    ".n-carousel__slide", ".n-checkbox-box__border { border"
}

ENTITY_REGEX_BLACKLIST_PATTERNS = [
    r"^[.-]*$", r"^\d+$", r"^\d{1,2}:\d{1,2}(:\d{1,2})?$", r"^[a-fA-F0-9]{4,}$", # Hex un peu plus long
    r"^U\+[0-9A-Fa-f]{2,6}(\-[0-9A-Fa-f]{2,6})?$", r"^(rgb|rgba)\(.*\)$",
    r"^\.[a-zA-Z0-9_-]+", r"^#[a-zA-Z0-9_-]+", r"^[a-z0-9-]+[:=]", # Attributs CSS/HTML (font-size:=)
    r"^[A-Z_]{2,}$", # Constantes (au moins 2 lettres)
    r".*==?$", r".*%>?$", r".*<\/?\w+.*>$", # Balises HTML/XML plus spécifiques
    r".*\b(function|var|let|const|if|else|for|while|return|class|import|export|def|try|except|finally|self|this|document|window|console|log)\b",
    r"^[ \t\n\r]*$", r"^(?:[a-zA-Z]\.){2,}$", r"^\d{1,3}(\.\d{1,3}){3}$",
    r".*\[data-v-[0-9a-f]{8,}\]",
    r"^(?:[a-zA-Z0-9+/]{4})*(?:|(?:[a-zA-Z0-9+/]{3}=)|(?:[a-zA-Z0-9+/]{2}==))$", # Base64
    r"^[\W_]+$", # Que des non-alphanumériques et underscores
    r".*\.(?:py|js|css|html|json|xml|yaml|sh|bat|md|txt|log|ini|cfg|conf)$", # Terminaisons de fichiers
    r".*Error.*", r".*Exception.*", r".*Warning.*", # Messages d'erreur
    r"^\s*$", # Lignes vides ou composées uniquement d'espaces
    r"^(True|False|None|NaN|Infinity)$", # Mots-clés Python/JS pour valeurs spéciales
    r"\S+@\S+\.\S+", # Adresses email simples
    r"([a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12})", # UUIDs
]
ENTITY_REGEX_BLACKLIST = [re.compile(p, re.IGNORECASE) for p in ENTITY_REGEX_BLACKLIST_PATTERNS]

MIN_ENTITY_LENGTH = 3
MIN_ENTITY_LENGTH_ACRONYM = 2
# --- FIN Constantes NER ---

# --- Constantes de Chemin et Configuration ---
BASE_ALMA_DIR_ENV_VAR: str = "ALMA_BASE_DIR"
DEFAULT_BASE_ALMA_DIR: Path = Path("/home/toni/Documents/ALMA") # Chemin par défaut
CONFIG_FILE_NAME: str = "cerveau_config.yaml"

# Résolution de BASE_ALMA_DIR une bonne fois pour toutes
# os.getenv peut retourner None si la variable n'est pas définie
_base_alma_dir_str = os.getenv(BASE_ALMA_DIR_ENV_VAR)
if _base_alma_dir_str:
    BASE_ALMA_DIR = Path(_base_alma_dir_str).resolve()
    print(f"DEBUG SCRIPT: ALMA_BASE_DIR utilisé depuis variable d'environnement: {BASE_ALMA_DIR}")
else:
    BASE_ALMA_DIR = DEFAULT_BASE_ALMA_DIR.resolve()
    print(f"DEBUG SCRIPT: ALMA_BASE_DIR non défini, utilisation du défaut: {BASE_ALMA_DIR}")

CONFIG_FILE_PATH: Path = BASE_ALMA_DIR / "Cerveau" / CONFIG_FILE_NAME
# --- FIN Constantes ---

DEFAULT_CONFIG: Dict[str, Any] = {
    "paths": {
        "connaissance_dir_suffix": "Connaissance",
        "cerveau_dir_suffix": "Cerveau",
        "log_dir_suffix": "logs",
        "improvements_subdir": "ameliorations_proposees",
        "active_improvements_dir_suffix": "Connaissance/Amelioree"
    },
    "logging": {
        "log_file_name": "cerveau.log",
        "emergency_log_file_name": "cerveau_emergency.log",
        "module_registry_file_name": "module_registry.json",
        "module_registry_lock_file_name": "module_registry.lock",
        "rotation": { # AJOUTÉ: Configuration pour la rotation des logs
            "max_bytes": 20971520,  # MODIFIÉ : Valeur numérique pour 20M
            "backup_count": 5
        }
    },
    "service_params": {
        "watchdog_enabled": True,
        "file_scan_interval_seconds": 60,
        "allowed_file_extensions": [".txt", ".md", ".json", ".xml", ".py", ".sh"],
        "max_workers": os.cpu_count() or 4,
        "file_queue_max_size": 1000,
        "self_report_interval_seconds": 3600,
        "task_timeout_seconds": 300,
        "backpressure_active_task_multiplier": 3,
        "health_check_interval_seconds": 900,
        # AJOUTÉ: Configuration pour l'exclusion de répertoires
        "excluded_dir_parts": ['.venv', 'venv', 'env', '__pycache__', 'node_modules', '.git', '.hg', '.svn'],
        "excluded_dir_prefixes": ['.'] # Pour tous les dossiers cachés commençant par un point
    },
    "circuit_breaker": {
        "threshold": 3,
        "timeout_seconds": 3600
    },
    "nlp": {
        "use_spacy_if_available": True,
        "spacy_model_names": ["fr_core_news_lg", "fr_core_news_sm", "en_core_web_sm"],
        "spacy_max_text_length": 1_000_000,
        "sentiment_positive_words": ["bon", "excellent", "super", "amélioration", "positif", "correct", "valide", "réussi"],
        "sentiment_negative_words": ["mauvais", "erreur", "problème", "négatif", "pire", "invalide", "échec", "cassé"],
        "significant_pos_tags": ["NOUN", "PROPN", "VERB", "ADJ"],
        "use_nltk_if_available": True,
        "use_rake_if_available": True,
        "use_yake_if_available": True,
        "use_sklearn_tfidf_if_available": True,
        "default_language": "fr"
    },
    "knowledge_base": {
        "use_sqlite_db": True,
        "db_name": "cerveau_knowledge.sqlite",
        "schema_file": "cerveau_kb_schema.sql",
        "db_timeout_seconds": 10
    },
    "pipeline_steps": {
        "ComprehensionStep": {"enabled": True, "priority": 10},
        "AnalysisStep": {"enabled": True, "priority": 20, "sentiment_threshold": 0.1},
        "StudyStep": {"enabled": True, "priority": 30},
        "ImprovementProposalStep": {"enabled": True, "priority": 40},
        "ActiveImprovementStep": {"enabled": True, "priority": 50, "auto_apply_summary": False, "auto_apply_grammar": False}
    },
    "core_algorithms_config": {
        "text_improver": {"default_language": "fr", "summary_ratio": 0.15, "grammar_api_config": None},
        "knowledge_linker": {"min_similarity_for_link": 0.7}
    }
}
APP_CONFIG: Dict[str, Any] = {} # Sera rempli par load_configuration

# --- NOUVEAU BLOC DE DÉCLARATION ET INITIALISATION DES VARIABLES GLOBALES ---
# Ces variables sont maintenant initialisées avec les VALEURS PAR DÉFAUT de DEFAULT_CONFIG.
# Elles seront mises à jour plus tard par initialize_paths_and_logging avec les valeurs du fichier cerveau_config.yaml.

# D'abord, résolvez la variable d'environnement BASE_ALMA_DIR pour l'utiliser partout.
_base_alma_dir_resolved = Path(os.getenv(BASE_ALMA_DIR_ENV_VAR, DEFAULT_BASE_ALMA_DIR)).resolve()

CONNAISSANCE_DIR: Path = _base_alma_dir_resolved / DEFAULT_CONFIG["paths"]["connaissance_dir_suffix"]
CERVEAU_DIR: Path = _base_alma_dir_resolved / DEFAULT_CONFIG["paths"]["cerveau_dir_suffix"]
LOG_DIR: Path = _base_alma_dir_resolved / DEFAULT_CONFIG["paths"]["log_dir_suffix"]

LOG_FILE: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["log_file_name"]
EMERGENCY_LOG_FILE: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["emergency_log_file_name"]
MODULE_REGISTRY_PATH: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["module_registry_file_name"]
MODULE_REGISTRY_LOCK_PATH: Path = LOG_DIR / DEFAULT_CONFIG["logging"]["module_registry_lock_file_name"]

IMPROVEMENTS_DIR: Path = CERVEAU_DIR / DEFAULT_CONFIG["paths"]["improvements_subdir"]
# Correction IMPORTANTE pour ACTIVE_IMPROVEMENTS_DIR : elle dépend de BASE_ALMA_DIR et non CERVEAU_DIR par défaut.
ACTIVE_IMPROVEMENTS_DIR: Path = _base_alma_dir_resolved / DEFAULT_CONFIG["paths"]["active_improvements_dir_suffix"]

# Initialisation conditionnelle de KB_DB_PATH (même logique que l'ancienne mais avec les nouvelles globales)
KB_DB_PATH: Optional[Path] = None
if DEFAULT_CONFIG["knowledge_base"]["use_sqlite_db"]:
    KB_DB_PATH = CERVEAU_DIR / DEFAULT_CONFIG["knowledge_base"]["db_name"]
# --- FIN DU NOUVEAU BLOC DE DÉCLARATION ET INITIALISATION ---

SCRIPT_NAME: str = Path(__file__).name if __file__ else "cerveau.py"
MODULE_VERSION: str = "20.5.0-alpha" # Incrémenter la version pour refléter tous ces changements
MODULE_NAME: str = "Cerveau"

log_lock: threading.Lock = threading.Lock()
logger: logging.Logger = logging.getLogger(MODULE_NAME) # Logger global du module

AUDIT_LEVEL_NUM: int = 25
if logging.getLevelName(AUDIT_LEVEL_NUM) == f"Level {AUDIT_LEVEL_NUM}":
    logging.addLevelName(AUDIT_LEVEL_NUM, "AUDIT")

def audit(self: logging.Logger, message: str, *args: Any, **kws: Any) -> None:
    """TODO: Add docstring."""
    if self.isEnabledFor(AUDIT_LEVEL_NUM):
        # pylint: disable=protected-access
        self._log(AUDIT_LEVEL_NUM, message, args, **kws)
logging.Logger.audit = audit # type: ignore

# La fonction log_message est correcte telle que vous l'avez fournie précédemment.
# Elle utilise les variables globales LOG_FILE et EMERGENCY_LOG_FILE qui seront
# définies par initialize_paths_and_logging.
    """TODO: Add docstring."""
def log_message(level: str, message: str, exc_info: bool = False, logger_instance: Optional[logging.Logger] = None) -> None:
    # ... (votre code correct pour log_message) ...
    effective_logger = logger_instance if logger_instance else logger
    try:
        with log_lock:
            # La réinitialisation ici est une sécurité, mais initialize_paths_and_logging est appelé avant.
            if not effective_logger.handlers and 'LOG_FILE' in globals() and LOG_FILE:
                 initialize_paths_and_logging(APP_CONFIG if APP_CONFIG else DEFAULT_CONFIG)

            upper_level = level.upper()
            log_func_map = {
                "DEBUG": effective_logger.debug, "INFO": effective_logger.info,
                "WARNING": effective_logger.warning, "ERROR": effective_logger.error,
                "CRITICAL": effective_logger.critical, "AUDIT": getattr(effective_logger, 'audit', effective_logger.info)
            }
            log_func = log_func_map.get(upper_level, effective_logger.info)
            log_func(message, exc_info=exc_info)
    except Exception as log_err:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        emergency_msg = f"{timestamp} [LOGGING_ERROR] {level.upper()}: {message}\nOriginal log error: {log_err}\n"
        print(emergency_msg, file=sys.stderr)
        try:
            _log_file_to_use = EMERGENCY_LOG_FILE if 'EMERGENCY_LOG_FILE' in globals() and EMERGENCY_LOG_FILE is not None else BASE_ALMA_DIR / "logs" / "cerveau_emergency_fallback.log"
            _log_file_to_use.parent.mkdir(parents=True, exist_ok=True)
            with open(_log_file_to_use, "a", encoding="utf-8") as f_emerg: f_emerg.write(emergency_msg)
        except Exception as emerg_log_err: print(f"{timestamp} [EMERGENCY_LOG_FAILURE] Could not write to emergency log: {emerg_log_err}", file=sys.stderr)
            """TODO: Add docstring."""

def deep_update(source: Dict[Any, Any], overrides: Dict[Any, Any]) -> Dict[Any, Any]:
    for key, value in overrides.items():
        if isinstance(value, dict) and key in source and isinstance(source[key], dict): source[key] = deep_update(source[key], value)
        else: source[key] = value
            """TODO: Add docstring."""
    return source

def load_configuration(config_path: Path, default_config: Dict[str, Any]) -> Dict[str, Any]:
    config = default_config.copy() # Commencer avec une copie des défauts

    # Déterminer le chemin réel du fichier de configuration à utiliser (YAML ou JSON)
    actual_config_path_to_try = config_path
    can_try_yaml = config_path.suffix.lower() in [".yaml", ".yml"]

    if can_try_yaml and not YAML_AVAILABLE: # Si c'est un .yaml mais que PyYAML n'est pas dispo
        log_message("WARNING", f"PyYAML non disponible. Tentative de lecture de {config_path} comme YAML impossible.")
        # Tenter de trouver un équivalent .json
        json_equivalent_path = config_path.with_suffix(".json")
        if json_equivalent_path.exists():
            log_message("INFO", f"Utilisation du fichier JSON de fallback: {json_equivalent_path}")
            actual_config_path_to_try = json_equivalent_path
        else:
            log_message("INFO", f"Fichier de configuration YAML ({config_path}) non lisible (PyYAML manquant) et fichier JSON équivalent ({json_equivalent_path}) non trouvé. Utilisation des valeurs par défaut.")
            return config # Retourner les défauts si aucune option de fichier de config n'est viable

    # À ce stade, actual_config_path_to_try pointe soit vers le .yaml original (si YAML_AVAILABLE),
    # soit vers un .json (si YAML non dispo et .json existe), soit toujours vers le .yaml (si YAML dispo).

    if actual_config_path_to_try.exists() and actual_config_path_to_try.is_file():
        try:
            with open(actual_config_path_to_try, 'r', encoding='utf-8') as f:
                loaded_config: Optional[Dict[Any, Any]] = None # Initialiser
                file_suffix_lower = actual_config_path_to_try.suffix.lower()

                if file_suffix_lower in [".yaml", ".yml"]:
                    if YAML_AVAILABLE and yaml_module_alias: # Vérifier explicitement les deux
                        log_message("INFO", f"Lecture du fichier de configuration YAML: {actual_config_path_to_try}")
                        loaded_config = yaml_module_alias.safe_load(f)
                    else:
                        # Ce cas ne devrait pas être atteint si la logique précédente est correcte,
                        # car on aurait switché vers .json ou retourné les défauts.
                        # Mais par sécurité :
                        log_message("ERROR", f"Tentative de lecture de {actual_config_path_to_try} comme YAML alors que PyYAML n'est pas disponible. Utilisation des valeurs par défaut.")
                        return config

                elif file_suffix_lower == ".json":
                    log_message("INFO", f"Lecture du fichier de configuration JSON: {actual_config_path_to_try}")
                    # Assurer que json est bien le module json standard
                    import json as json_standard_lib
                    loaded_config = json_standard_lib.load(f)

                else:
                    log_message("WARNING", f"Format de fichier de configuration non supporté: {actual_config_path_to_try.suffix} pour {actual_config_path_to_try}. Utilisation des valeurs par défaut.")
                    return config # Retourner les défauts si format non supporté

                # Vérifier le contenu chargé
                if loaded_config and isinstance(loaded_config, dict):
                    config = deep_update(config, loaded_config) # Fusionner avec les défauts
                    log_message("INFO", f"Configuration chargée et fusionnée avec succès depuis: {actual_config_path_to_try}")
                elif loaded_config is None and file_suffix_lower in [".yaml", ".yml"] and YAML_AVAILABLE:
                     log_message("WARNING", f"Fichier de configuration YAML {actual_config_path_to_try} est vide ou contient seulement 'null'. Utilisation des valeurs par défaut ou précédemment chargées.")
                elif loaded_config is None and file_suffix_lower == ".json":
                     log_message("WARNING", f"Fichier de configuration JSON {actual_config_path_to_try} est vide ou contient seulement 'null'. Utilisation des valeurs par défaut ou précédemment chargées.")
                else: # loaded_config n'est pas un dictionnaire
                    log_message("WARNING", f"Fichier de configuration {actual_config_path_to_try} ne contient pas un dictionnaire valide. Utilisation des valeurs par défaut ou précédemment chargées.")

        except json.JSONDecodeError as e_json_decode:
            log_message("ERROR", f"Erreur de décodage JSON pour le fichier de configuration {actual_config_path_to_try}: {e_json_decode}. Vérifiez la syntaxe du fichier.", exc_info=False) # exc_info=False pour JSONDecodeError
        except yaml_module_alias.YAMLError as e_yaml_decode: # type: ignore # Si yaml_module_alias est None, cette exception ne sera pas attrapée
             log_message("ERROR", f"Erreur de décodage YAML pour le fichier de configuration {actual_config_path_to_try}: {e_yaml_decode}. Vérifiez la syntaxe du fichier.", exc_info=False)
        except Exception as e_load:
            log_message("ERROR", f"Erreur inattendue lors du chargement du fichier de configuration {actual_config_path_to_try}: {e_load}.", exc_info=True)
            # En cas d'erreur de chargement, on retourne la config actuelle (qui pourrait être juste default_config)
            # ou on pourrait choisir de retourner default_config explicitement pour plus de sécurité.
    else:
        # Si le chemin initial était un .yaml et qu'on n'a pas trouvé de .json, on logue ici.
        # Si le chemin initial était déjà un .json et qu'il n'existe pas, on logue aussi.
        log_message("INFO", f"Fichier de configuration {actual_config_path_to_try} non trouvé. Utilisation des valeurs par défaut.")
        # config est déjà default_config.copy() à ce stade si le fichier n'est pas trouvé.
            """TODO: Add docstring."""

    return config

def initialize_paths_and_logging(config: Dict[str, Any]) -> None:
    global CONNAISSANCE_DIR, CERVEAU_DIR, LOG_DIR, LOG_FILE, EMERGENCY_LOG_FILE, MODULE_REGISTRY_PATH, MODULE_REGISTRY_LOCK_PATH, IMPROVEMENTS_DIR, ACTIVE_IMPROVEMENTS_DIR, KB_DB_PATH, logger

    # Utiliser .get() avec un fallback sur DEFAULT_CONFIG pour chaque section,
    # puis .get() à nouveau pour chaque clé spécifique avec une valeur par défaut finale.
    # Cela rend l'accès à la configuration plus robuste si des sections ou des clés manquent.
    default_paths_config = DEFAULT_CONFIG.get("paths", {})
    paths_config = config.get("paths", default_paths_config)

    default_logging_config = DEFAULT_CONFIG.get("logging", {})
    logging_config_section = config.get("logging", default_logging_config)

    default_kb_config = DEFAULT_CONFIG.get("knowledge_base", {})
    kb_config = config.get("knowledge_base", default_kb_config)

    CONNAISSANCE_DIR = BASE_ALMA_DIR / paths_config.get("connaissance_dir_suffix", "Connaissance")
    CERVEAU_DIR = BASE_ALMA_DIR / paths_config.get("cerveau_dir_suffix", "Cerveau")
    LOG_DIR = BASE_ALMA_DIR / paths_config.get("log_dir_suffix", "logs")

    LOG_FILE = LOG_DIR / logging_config_section.get("log_file_name", "cerveau.log")
    EMERGENCY_LOG_FILE = LOG_DIR / logging_config_section.get("emergency_log_file_name", "cerveau_emergency.log")
    MODULE_REGISTRY_PATH = LOG_DIR / logging_config_section.get("module_registry_file_name", "module_registry.json")
    MODULE_REGISTRY_LOCK_PATH = LOG_DIR / logging_config_section.get("module_registry_lock_file_name", "module_registry.lock")

    IMPROVEMENTS_DIR = CERVEAU_DIR / paths_config.get("improvements_subdir", "ameliorations_proposees")
    ACTIVE_IMPROVEMENTS_DIR = BASE_ALMA_DIR / paths_config.get("active_improvements_dir_suffix", "Connaissance/Amelioree")

    if kb_config.get("use_sqlite_db", False): # Le False est le défaut si use_sqlite_db manque
        KB_DB_PATH = CERVEAU_DIR / kb_config.get("db_name", "cerveau_knowledge.sqlite")
    else:
        KB_DB_PATH = None

    # Nettoyer les anciens handlers du logger global pour éviter les duplications
    # ou les handlers pointant vers d'anciens fichiers si la config change.
    current_handlers = logger.handlers[:]
    for handler in current_handlers:
        try:
            handler.flush()
            logger.removeHandler(handler)
            handler.close()
        except Exception as e_handler_close:
            # Utiliser print ici car le logger est en cours de reconfiguration.
            print(f"WARNING: Erreur lors de la fermeture/suppression d'un ancien handler de log: {e_handler_close}", file=sys.stderr)

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True) # S'assurer que le répertoire de log existe

        _log_formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)-8s] [%(threadName)s (%(thread)d) - PID:%(process)d] %(name)s.%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
        )

        # Configuration pour la rotation des logs
        # Utiliser la section "rotation" de logging_config_section, avec fallback sur DEFAULT_CONFIG, puis sur des valeurs codées en dur.
        default_rotation_settings_from_default_config = DEFAULT_CONFIG.get("logging", {}).get("rotation", {})
        log_rotation_config = logging_config_section.get("rotation", default_rotation_settings_from_default_config)

        # Valeurs par défaut finales si rien n'est trouvé dans les configs
        max_bytes = int(log_rotation_config.get("max_bytes", 20 * 1024 * 1024))  # 20MB
        backup_count = int(log_rotation_config.get("backup_count", 5))

        # Utiliser RotatingFileHandler
        main_file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
            # mode='a' est le comportement par défaut pour RotatingFileHandler
        )
        main_file_handler.setFormatter(_log_formatter)
        logger.addHandler(main_file_handler)

        # Définir le niveau de log global pour le logger (affecte tous ses handlers)
        # Ce niveau peut être surchargé par des niveaux spécifiques aux handlers si nécessaire.
        # Pour l'instant, on met DEBUG pour le fichier, la console peut avoir un niveau différent.
        logger.setLevel(logging.DEBUG)

        # Log de confirmation (utilisera le handler fraîchement configuré)
        # On ne peut pas utiliser log_message() ici car log_message() appelle elle-même
        # initialize_paths_and_logging() si les handlers sont absents, créant une récursion.
        # On utilise donc directement le logger.
        logger.info(f"Logger principal (fichier) réinitialisé avec RotatingFileHandler. MaxBytes: {max_bytes}, BackupCount: {backup_count}. Niveau effectif: {logging.getLevelName(logger.getEffectiveLevel())}")

    except Exception as e_log_init:
        # Si l'initialisation du logger de fichier échoue, on logue sur stderr et dans le log d'urgence.
        print(f"CRITICAL: Échec de la réinitialisation du handler de log principal pour {LOG_FILE}: {e_log_init}", file=sys.stderr)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        emergency_msg = f"{timestamp} [LOGGING_INIT_ERROR] CRITICAL: Échec de la réinitialisation du handler de log principal pour {LOG_FILE}: {e_log_init}\n"
        try:
            _emergency_log_file_path = EMERGENCY_LOG_FILE if 'EMERGENCY_LOG_FILE' in globals() and EMERGENCY_LOG_FILE is not None else BASE_ALMA_DIR / "logs" / "cerveau_emergency_fallback.log"
            _emergency_log_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(_emergency_log_file_path, "a", encoding="utf-8") as f_emerg: f_emerg.write(emergency_msg)
        except Exception as emerg_log_err:
            print(f"{timestamp} [EMERGENCY_LOG_INIT_FAILURE] Could not write to emergency log during logger init: {emerg_log_err}", file=sys.stderr)
                """TODO: Add docstring."""

# L'appel à initialize_paths_and_logging(APP_CONFIG) se fait au niveau global du script
# après que APP_CONFIG ait été chargé.

def enregistrer_module(status: str = "actif", message: str = "") -> None:
    # ... (code inchangé, il est déjà assez robuste) ...
    registry_data: Dict[str, Any] = {}
    lock_path_str = str(MODULE_REGISTRY_LOCK_PATH) # filelock prend une chaîne
    lock_timeout = 10
    lock_instance: Optional[ExternalFileLock] = None # Type explicite

    if ExternalFileLock:
        lock_instance = ExternalFileLock(lock_path_str, timeout=lock_timeout)
    elif platform.system() != "Windows" and fcntl:
        pass # fcntl sera géré ci-dessous
    else:
        log_message("WARNING", "Aucun mécanisme de locking robuste disponible pour module_registry.json.")

    fd_fcntl: Optional[int] = None # Pour fcntl
    acquired_by_ext_lock = False

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True) # S'assurer que LOG_DIR existe

        if lock_instance:
            try:
                lock_instance.acquire()
                acquired_by_ext_lock = True
            except FileLockTimeout: # type: ignore # FileLockTimeout peut être None
                log_message("ERROR", f"Timeout lors de l'acquisition du verrou pour {MODULE_REGISTRY_LOCK_PATH}.")
                return
            except Exception as e_lock_acq:
                log_message("ERROR", f"Erreur lors de l'acquisition du verrou (filelock) pour {MODULE_REGISTRY_LOCK_PATH}: {e_lock_acq}")
                return
        elif platform.system() != "Windows" and fcntl:
            try:
                fd_fcntl = os.open(str(MODULE_REGISTRY_LOCK_PATH), os.O_CREAT | os.O_RDWR)
                fcntl.flock(fd_fcntl, fcntl.LOCK_EX)
            except Exception as e_fcntl_lock:
                log_message("ERROR", f"Erreur lors de l'acquisition du verrou (fcntl) pour {MODULE_REGISTRY_LOCK_PATH}: {e_fcntl_lock}")
                if fd_fcntl is not None: os.close(fd_fcntl)
                return

        if MODULE_REGISTRY_PATH.exists() and MODULE_REGISTRY_PATH.stat().st_size > 0:
            try:
                with open(MODULE_REGISTRY_PATH, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
            except json.JSONDecodeError:
                log_message("WARNING", f"Fichier {MODULE_REGISTRY_PATH} corrompu ou vide. Il sera écrasé.")
            except Exception as e_read_reg:
                log_message("ERROR", f"Erreur lors de la lecture de {MODULE_REGISTRY_PATH}: {e_read_reg}", exc_info=True)

        module_info = {
            "name": MODULE_NAME, "script_name": SCRIPT_NAME, "version": MODULE_VERSION,
            "status": status, "type_execution": "service",
            "role": "Analyse et amélioration continue de la base de connaissances",
            "last_heartbeat": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "pid": os.getpid(), "message": message, "log_file": str(LOG_FILE.resolve())
        }
        registry_data[MODULE_NAME] = module_info

        temp_registry_path_obj: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile('w', dir=LOG_DIR, delete=False, encoding='utf-8', suffix='.json_tmp') as tmp_f:
                json.dump(registry_data, tmp_f, indent=4, ensure_ascii=False)
                temp_registry_path_obj = Path(tmp_f.name)

            if temp_registry_path_obj:
                os.replace(temp_registry_path_obj, MODULE_REGISTRY_PATH)
                # log_message("INFO", f"Module {MODULE_NAME} enregistré/mis à jour. Statut: {status}.") # Peut être un peu trop verbeux
            else:
                log_message("ERROR", "Le fichier temporaire pour module_registry n'a pas pu être créé.")
        except Exception as e_write_reg:
            log_message("ERROR", f"Erreur lors de l'écriture atomique de module_registry: {e_write_reg}", exc_info=True)
            if temp_registry_path_obj and temp_registry_path_obj.exists():
                try: temp_registry_path_obj.unlink()
                except OSError: pass
    except Exception as e_main_reg:
        log_message("ERROR", f"Échec global de l'enregistrement du module: {e_main_reg}", exc_info=True)
    finally:
        if acquired_by_ext_lock and lock_instance:
            try: lock_instance.release()
            except Exception: pass
        if fd_fcntl is not None and platform.system() != "Windows" and fcntl:
            """TODO: Add docstring."""
            try:
                fcntl.flock(fd_fcntl, fcntl.LOCK_UN)
                os.close(fd_fcntl)
            except Exception: pass

def calculate_checksum(filepath: Path, chunk_size: int = 8192) -> Optional[str]:
    # ... (code inchangé) ...
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except IOError as e:
        """TODO: Add docstring."""
        log_message("ERROR", f"Erreur de lecture du fichier {filepath} pour calcul du checksum: {e}", exc_info=True)
        return None
    except Exception as e:
        log_message("ERROR", f"Erreur inattendue lors du calcul du checksum pour {filepath}: {e}", exc_info=True)
        return None

def robust_file_read(filepath: Path) -> Tuple[Optional[str], Optional[str]]:
    # ... (code inchangé) ...
    common_encodings = ['utf-8', 'latin-1', 'cp1252', sys.getfilesystemencoding()]
    for encoding in common_encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read(), encoding
        except UnicodeDecodeError:
            continue
        except IOError as e:
            log_message("ERROR", f"Erreur I/O lors de la lecture de {filepath} avec l'encodage {encoding}: {e}", exc_info=True)
            return None, None
                """TODO: Add docstring."""
                    """TODO: Add docstring."""
        except Exception as e:
            log_message("ERROR", f"Erreur inattendue lors de la lecture de {filepath} avec l'encodage {encoding}: {e}", exc_info=True)
            return None, None
    log_message("WARNING", f"Impossible de décoder le fichier {filepath} avec les encodages testés: {common_encodings}.")
    return None, None


class KnowledgeBase:
    def __init__(self, nlp_config: Dict[str, Any]):
        self.nlp_config: Dict[str, Any] = nlp_config
        self.nlp_instance: Optional[Any] = None # Sera l'instance spaCy si chargée
            """TODO: Add docstring."""
        self.is_spacy_ready: bool = False
        self.logger = logging.getLogger(f"{MODULE_NAME}.KnowledgeBase")

        # L'initialisation des ressources NLP (chargement du modèle spaCy, etc.)
        self._initialize_nlp_resources()
        # L'initialisation du schéma de la DB est maintenant faite par CerveauService
        # en appelant la méthode statique initialize_schema_if_needed.

    @staticmethod
    def initialize_schema_if_needed(db_path: Path, schema_file_path: Optional[Path], db_timeout_seconds: int) -> None:
        logger_static = logging.getLogger(f"{MODULE_NAME}.KnowledgeBase.StaticSchemaInit") # Logger spécifique

        # Créer seulement si la DB n'existe pas ou est vide
        if not db_path.exists() or db_path.stat().st_size == 0:
            logger_static.info(f"Base de données {db_path.name} non trouvée ou vide. Tentative d'initialisation du schéma.")
            try:
                db_path.parent.mkdir(parents=True, exist_ok=True) # S'assurer que le répertoire parent existe

                # Utiliser une connexion temporaire pour initialiser le schéma
                with sqlite3.connect(str(db_path), timeout=db_timeout_seconds) as temp_conn: # str(db_path) pour compatibilité
                    temp_conn.row_factory = sqlite3.Row # Utile si on lit des choses pendant l'init
                    temp_conn.execute("PRAGMA foreign_keys = ON;")
                    temp_conn.execute("PRAGMA journal_mode=WAL;") # Activer WAL pour la nouvelle DB

                    schema_sql = ""
                    if schema_file_path and schema_file_path.exists() and schema_file_path.is_file():
                        logger_static.info(f"Lecture du schéma depuis le fichier: {schema_file_path}")
                        with open(schema_file_path, 'r', encoding='utf-8') as f_schema:
                            schema_sql = f_schema.read()
                    else:
                        if schema_file_path: # Si un chemin était fourni mais non trouvé/valide
                            logger_static.warning(f"Fichier de schéma spécifié ({schema_file_path}) non trouvé ou invalide. Utilisation du schéma par défaut interne.")
                        else:
                            logger_static.info("Aucun fichier de schéma spécifié. Utilisation du schéma par défaut interne.")

                        # --- Schéma par défaut interne (incluant la colonne 'embedding') ---
                        schema_sql = """
                        CREATE TABLE IF NOT EXISTS files (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            filepath TEXT UNIQUE NOT NULL,
                            checksum TEXT NOT NULL,
                            last_processed_utc TEXT NOT NULL,
                            size_bytes INTEGER,
                            encoding TEXT,
                            embedding BLOB -- Colonne pour les embeddings de documents
                        );
                        CREATE INDEX IF NOT EXISTS idx_files_filepath ON files (filepath);

                        CREATE TABLE IF NOT EXISTS linguistic_tokens (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            file_id INTEGER NOT NULL,
                            token_text TEXT,
                            lemma TEXT,
                            pos TEXT,
                            is_stop BOOLEAN,
                            is_punct BOOLEAN,
                            is_alpha BOOLEAN,
                            is_significant BOOLEAN,
                            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
                        );
                        CREATE INDEX IF NOT EXISTS idx_linguistic_tokens_file_id ON linguistic_tokens (file_id);
                        CREATE INDEX IF NOT EXISTS idx_linguistic_tokens_lemma ON linguistic_tokens (lemma);

                        CREATE TABLE IF NOT EXISTS named_entities (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            file_id INTEGER NOT NULL,
                            entity_text TEXT,
                            entity_type TEXT,
                            start_char INTEGER,
                            end_char INTEGER,
                            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
                        );
                        CREATE INDEX IF NOT EXISTS idx_named_entities_file_id ON named_entities (file_id);
                        CREATE INDEX IF NOT EXISTS idx_named_entities_text_type ON named_entities (entity_text, entity_type);

                        CREATE TABLE IF NOT EXISTS metadata (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            file_id INTEGER NOT NULL,
                            meta_key TEXT NOT NULL,
                            meta_value TEXT,
                            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
                        );
                        CREATE INDEX IF NOT EXISTS idx_metadata_file_id ON metadata (file_id);
                        CREATE INDEX IF NOT EXISTS idx_metadata_key_value ON metadata (meta_key, meta_value);

                        CREATE TABLE IF NOT EXISTS entity_relations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            file_id INTEGER NOT NULL,
                            source_entity_id INTEGER,
                            target_entity_id INTEGER,
                            relation_type TEXT,
                            context_snippet TEXT,
                            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE,
                            FOREIGN KEY (source_entity_id) REFERENCES named_entities (id) ON DELETE SET NULL,
                            FOREIGN KEY (target_entity_id) REFERENCES named_entities (id) ON DELETE SET NULL
                        );
                        CREATE INDEX IF NOT EXISTS idx_entity_relations_file_id ON entity_relations (file_id);
                        """

                    if schema_sql:
                        temp_conn.executescript(schema_sql)
                        temp_conn.commit()
                        logger_static.info(f"Schéma de la base de données initialisé avec succès à {db_path}.")
                    else:
                        logger_static.error("Aucun SQL de schéma n'a pu être déterminé. La base de données ne sera pas initialisée.")
                            """TODO: Add docstring."""

            except sqlite3.Error as e_sqlite_init:
                logger_static.critical(f"Erreur SQLite majeure lors de l'initialisation du schéma de la KB {db_path}: {e_sqlite_init}", exc_info=True)
                raise # Re-lever l'exception pour que le service Cerveau ne démarre pas sans une DB fonctionnelle.
            except Exception as e_gen_init:
                logger_static.critical(f"Erreur générale majeure lors de l'initialisation du schéma de la KB: {e_gen_init}", exc_info=True)
                raise
        else:
            logger_static.debug(f"Base de données {db_path.name} existe déjà et n'est pas vide. Aucune initialisation de schéma effectuée.")

    def get_file_checksum(self, db_conn: sqlite3.Connection, filepath_str: str) -> Optional[str]:
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT checksum FROM files WHERE filepath = ?", (filepath_str,))
            result = cursor.fetchone() # sqlite3.Row ou None
            if result:
                checksum_val: Optional[str] = result['checksum']
                self.logger.debug(f"Checksum trouvé dans la KB pour '{filepath_str}': {checksum_val}")
                    """TODO: Add docstring."""
                return checksum_val
            else:
                self.logger.debug(f"Fichier '{filepath_str}' non trouvé dans la KB (ou pas de checksum).")
                return None
        except sqlite3.Error as e_sqlite:
            self.logger.error(f"Erreur SQLite lors de la récupération du checksum pour {filepath_str}: {e_sqlite}", exc_info=True)
            return None
        except Exception as e_general: # Attraper d'autres erreurs potentielles
             self.logger.error(f"Erreur générale lors de la récupération du checksum pour {filepath_str}: {e_general}", exc_info=True)
             return None

    def _initialize_nlp_resources(self) -> None:
        # Déclarer les variables globales du module cerveau.py que cette méthode
        # pourrait tenter de réassigner si leur import initial a échoué.
        # Ces variables sont déjà initialisées à None ou à leur module/classe
        # au niveau global du script cerveau.py.
        global nltk, rake_nltk, yake, sklearn_tfidf
        # Les globales spacy, ModelsNotFound, SPACY_STOP_WORDS sont gérées lors de leur import initial
        # et ne sont pas réassignées ici. On utilise la variable globale 'spacy' directement.

        self.logger.info("Initialisation des ressources NLP pour KnowledgeBase...")

        # --- 1. Initialisation de spaCy (si activé et disponible globalement) ---
        if spacy and self.nlp_config.get("use_spacy_if_available", True):
            # model_names_config est déjà adapté par _apply_adaptive_settings en fonction de la RAM
            # donc l'ordre ici reflète déjà la décision prise (ex: _lg en premier si RAM OK)
            model_names_config = self.nlp_config.get("spacy_model_names", [])
            if not isinstance(model_names_config, list) or not model_names_config:
                self.logger.warning("Config 'nlp.spacy_model_names' invalide ou vide. Utilisation de la liste par défaut ['fr_core_news_lg', 'fr_core_news_sm'].")
                model_names_config = ["fr_core_news_lg", "fr_core_news_sm"]

            self.logger.debug(f"Ordre de tentative de chargement des modèles spaCy (après adaptation ressources): {model_names_config}")

            # Chemins absolus connus pour les modèles (au cas où le nom ne suffirait pas)
            # Assurez-vous que ces chemins correspondent EXACTEMENT à votre installation venv
            known_model_paths = {
                "fr_core_news_lg": "/home/toni/Documents/ALMA/venv/lib/python3.12/site-packages/fr_core_news_lg/fr_core_news_lg-3.8.0",
                "fr_core_news_sm": "/home/toni/Documents/ALMA/venv/lib/python3.12/site-packages/fr_core_news_sm/fr_core_news_sm-3.8.0",
                "en_core_web_sm": "/home/toni/Documents/ALMA/venv/lib/python3.12/site-packages/en_core_web_sm/en_core_web_sm-3.8.0"
                # Ajoutez d'autres modèles si nécessaire
            }

            _ModelsNotFound_local_kb = ModelsNotFound # Utiliser la variable globale déjà initialisée

            for model_name_to_try in model_names_config:
                model_loaded_successfully = False
                disable_pipes_list = [] # Par défaut, ne rien désactiver pour _lg

                # Configuration des pipes à désactiver
                # Pour _lg, on veut garder 'parser' si possible pour raisonneur.py plus tard,
                # mais pour cerveau.py actuel, il n'est pas utilisé directement.
                # Pour l'instant, on le désactive pour _lg pour alléger, mais c'est un point à revoir.
                if model_name_to_try.endswith("_sm"):
                    disable_pipes_list.extend(["parser", "ner"]) # NER de _sm est souvent peu utile
                    self.logger.info(f"Modèle '{model_name_to_try}' est SMALL, désactivation de 'parser' et 'ner'.")
                elif model_name_to_try.endswith("_md") or model_name_to_try.endswith("_lg"):
                    # Pour les modèles plus grands, on pourrait vouloir garder NER.
                    # Le parser est coûteux et pas utilisé par cerveau.py directement pour l'instant.
                    disable_pipes_list.append("parser")
                    self.logger.info(f"Modèle '{model_name_to_try}' est MD/LG, désactivation de 'parser'.")


                # Tentative 1: Charger par nom
                try:
                    self.logger.info(f"Chargement spaCy modèle '{model_name_to_try}' par NOM (désactivés: {disable_pipes_list or 'aucun'})...")
                    self.nlp_instance = spacy.load(model_name_to_try, disable=disable_pipes_list) # Utilise la globale 'spacy'
                    self.logger.info(f"OK: Modèle spaCy '{self.nlp_instance.meta['name']}' v{self.nlp_instance.meta['version']} chargé (NOM).")
                    model_loaded_successfully = True
                except OSError as e_os_load_name:
                    self.logger.warning(f"Échec OS chargement '{model_name_to_try}' par NOM: {e_os_load_name}")
                    if "[E050]" in str(e_os_load_name): # Code d'erreur spaCy pour modèle non trouvé
                        self.logger.info(f"Modèle '{model_name_to_try}' non trouvé par NOM. Tentative par CHEMIN ABSOLU.")
                        absolute_path_to_try = known_model_paths.get(model_name_to_try)
                        if absolute_path_to_try and Path(absolute_path_to_try).exists():
                            try:
                                self.logger.info(f"Chargement spaCy modèle '{model_name_to_try}' via CHEMIN '{absolute_path_to_try}' (désactivés: {disable_pipes_list or 'aucun'})...")
                                self.nlp_instance = spacy.load(absolute_path_to_try, disable=disable_pipes_list)
                                self.logger.info(f"OK: Modèle spaCy '{model_name_to_try}' (via {absolute_path_to_try}) chargé (CHEMIN).")
                                model_loaded_successfully = True
                            except Exception as e_spacy_path_load:
                                self.logger.error(f"ÉCHEC chargement via CHEMIN '{absolute_path_to_try}': {e_spacy_path_load}", exc_info=False) # exc_info=False pour ne pas surcharger
                        else:
                            self.logger.warning(f"Aucun chemin absolu connu ou valide pour '{model_name_to_try}'. Impossible de charger par chemin. Essayez 'python -m spacy download {model_name_to_try}'.")
                    else: # Autre OSError
                         self.logger.error(f"Erreur OSError inattendue lors du chargement de '{model_name_to_try}' par NOM.", exc_info=False)
                except Exception as e_spacy_load_name: # Autres exceptions (ex: ModelsNotFound si bien importé)
                    if _ModelsNotFound_local_kb and isinstance(e_spacy_load_name, _ModelsNotFound_local_kb):
                        self.logger.warning(f"Modèle spaCy '{model_name_to_try}' non trouvé (via ModelsNotFound). Essayez 'python -m spacy download {model_name_to_try}'. Erreur: {e_spacy_load_name}")
                    else:
                        self.logger.error(f"Erreur inattendue lors du chargement du modèle spaCy '{model_name_to_try}' par NOM: {e_spacy_load_name}", exc_info=False)

                if model_loaded_successfully and self.nlp_instance:
                    self.is_spacy_ready = True
                    self.logger.info(f"Pipeline spaCy ACTIF pour {self.nlp_instance.meta['name']}: {self.nlp_instance.pipe_names}")
                    if hasattr(self.nlp_instance.vocab, 'vectors_length') and self.nlp_instance.vocab.vectors_length > 0:
                        self.logger.info(f"  Vecteurs du modèle: présents (dimension: {self.nlp_instance.vocab.vectors_length}).")
                    else:
                        self.logger.warning(f"  Vecteurs du modèle: NON présents ou dimension nulle pour '{self.nlp_instance.meta['name']}'. La similarité sémantique spaCy sera limitée.")

                    spacy_max_len_config = self.nlp_config.get("spacy_max_text_length", 1_000_000) # Valeur par défaut si non configuré
                    if hasattr(self.nlp_instance, 'max_length') and isinstance(spacy_max_len_config, int) and spacy_max_len_config > self.nlp_instance.max_length:
                        try:
                            self.nlp_instance.max_length = spacy_max_len_config
                            self.logger.info(f"  nlp.max_length pour '{self.nlp_instance.meta['name']}' ajusté à {spacy_max_len_config}.")
                        except Exception as e_max_len:
                            self.logger.error(f"  Impossible d'ajuster nlp.max_length pour '{self.nlp_instance.meta['name']}': {e_max_len}")
                    break # Succès, sortir de la boucle des modèles à essayer

            if not self.is_spacy_ready:
                self.logger.error("ÉCHEC FINAL: Aucun modèle spaCy configuré n'a pu être chargé. NLP avancé avec spaCy sera désactivé.")

        elif not spacy:
            self.logger.warning("Module spaCy non disponible globalement. NLP avancé avec spaCy désactivé.")
        else: # spacy est disponible mais use_spacy_if_available est False
            self.logger.info("Utilisation de spaCy désactivée dans la configuration (nlp.use_spacy_if_available).")

        # --- 2. Vérification/Réassignation des bibliothèques NLP optionnelles (fallbacks) ---
        # Les variables globales nltk, Rake_class_alias, yake, sklearn_tfidf ont été
        # initialisées à None au début de cerveau.py.
        # Cette section s'assure qu'elles sont correctement (ré)assignées si leur import
        # initial a échoué mais que la configuration demande leur utilisation.

        # Utiliser self.logger qui est l'instance logger de KnowledgeBase
        current_logger_nlp_res = self.logger

        # NLTK (module principal)
        if self.nlp_config.get("use_nltk_if_available", True): # Vérifier la config
            global nltk # Nécessaire pour modifier la globale
            if not nltk: # Si la globale nltk est toujours None (échec de l'import initial)
                current_logger_nlp_res.info("NLTK non pré-importé globalement, tentative d'import maintenant...")
                try:
                    import nltk as nltk_lib_local
                    nltk = nltk_lib_local # Assignation à la globale
                    current_logger_nlp_res.info("NLTK (module) ré-assigné globalement avec succès.")
                except ImportError:
                    current_logger_nlp_res.warning("NLTK activé dans config mais échec de l'import (même en fallback). NLTK restera non disponible.")
                except Exception as e_nltk_load_kb: # Autres erreurs d'import
                    current_logger_nlp_res.warning(f"Erreur inattendue lors de l'import de NLTK: {e_nltk_load_kb}. NLTK non disponible.")

            # Log final sur la disponibilité de NLTK
            if nltk:
                 current_logger_nlp_res.info("NLTK est DISPONIBLE pour utilisation.")
            else:
                 current_logger_nlp_res.warning("NLTK activé dans config mais NON DISPONIBLE globalement.")
        else:
            current_logger_nlp_res.info("Utilisation de NLTK désactivée dans la configuration nlp.")

        # Rake-NLTK (pour la classe Rake)
        if self.nlp_config.get("use_rake_if_available", True): # Vérifier la config
            global Rake_class_alias # Nécessaire pour modifier la globale
            if not Rake_class_alias: # Si la globale pour la classe Rake est toujours None
                current_logger_nlp_res.info("Classe Rake de Rake-NLTK non pré-importée, tentative d'import maintenant...")
                try:
                    from rake_nltk import Rake as Rake_imported_class_local # Importer la CLASSE
                    Rake_class_alias = Rake_imported_class_local # ASSIGNER LA CLASSE à la globale
                    current_logger_nlp_res.info("Rake-NLTK (CLASSE Rake) disponible et assignée globalement.")
                except ImportError:
                    current_logger_nlp_res.warning("Bibliothèque Rake-NLTK non installée. Fallback Rake désactivé.")
                except Exception as e_rake_class_load:
                    current_logger_nlp_res.warning(f"Erreur lors de l'import de la classe Rake de Rake-NLTK: {e_rake_class_load}. Fallback Rake désactivé.")

            # Log final sur la disponibilité de la classe Rake
            if Rake_class_alias:
                current_logger_nlp_res.info("Rake-NLTK (CLASSE Rake) est DISPONIBLE pour utilisation.")
            else:
                current_logger_nlp_res.warning("Rake-NLTK (CLASSE Rake) activé dans config mais NON DISPONIBLE globalement.")
        else:
            current_logger_nlp_res.info("Utilisation de Rake-NLTK désactivée dans la configuration nlp.")

        # YAKE! (module)
        if self.nlp_config.get("use_yake_if_available", True): # Vérifier la config
            global yake # Nécessaire pour modifier la globale
            if not yake: # Si la globale yake est toujours None
                current_logger_nlp_res.info("YAKE! non pré-importé globalement, tentative d'import maintenant...")
                try:
                    import yake as yake_lib_local
                    yake = yake_lib_local # Assignation du module à la globale
                    current_logger_nlp_res.info("YAKE! (module) ré-assigné globalement avec succès.")
                except ImportError:
                    current_logger_nlp_res.warning("YAKE! activé dans config mais échec de l'import. YAKE! non disponible.")
                except Exception as e_yake_load_kb:
                    current_logger_nlp_res.warning(f"Erreur inattendue lors de l'import de YAKE!: {e_yake_load_kb}. YAKE! non disponible.")

            # Log final sur la disponibilité de YAKE!
            if yake:
                current_logger_nlp_res.info("YAKE! (module) est DISPONIBLE pour utilisation.")
            else:
                current_logger_nlp_res.warning("YAKE! activé dans config mais NON DISPONIBLE globalement.")
        else:
            current_logger_nlp_res.info("Utilisation de YAKE! désactivée dans la configuration nlp.")

        # Scikit-learn TfidfVectorizer (classe)
        if self.nlp_config.get("use_sklearn_tfidf_if_available", True): # Vérifier la config
            global sklearn_tfidf # Nécessaire pour modifier la globale
            if not sklearn_tfidf: # Si la globale sklearn_tfidf est toujours None
                current_logger_nlp_res.info("Scikit-learn TfidfVectorizer non pré-importé, tentative d'import maintenant...")
                try:
                    from sklearn.feature_extraction.text import TfidfVectorizer as TfidfVectorizer_imported_class_local
                    sklearn_tfidf = TfidfVectorizer_imported_class_local # Assignation de la classe à la globale
                    current_logger_nlp_res.info("Scikit-learn TfidfVectorizer (classe) ré-assigné globalement avec succès.")
                except ImportError:
                    current_logger_nlp_res.warning("Scikit-learn non installé. TF-IDF via sklearn désactivé.")
                except Exception as e_sklearn_load_kb:
                     current_logger_nlp_res.warning(f"Erreur inattendue lors de l'import de TfidfVectorizer: {e_sklearn_load_kb}. TF-IDF non disponible.")
                         """TODO: Add docstring."""

            # Log final sur la disponibilité de TfidfVectorizer
            if sklearn_tfidf:
                current_logger_nlp_res.info("Scikit-learn TfidfVectorizer (classe) est DISPONIBLE pour utilisation.")
            else:
                current_logger_nlp_res.warning("Scikit-learn TF-IDF activé dans config mais NON DISPONIBLE globalement.")
        else:
            current_logger_nlp_res.info("Utilisation de Scikit-learn TF-IDF désactivée dans la configuration nlp.")

    # --- FIN DE LA MÉTHODE _initialize_nlp_resources ---

    # --- MÉTHODE MODIFIÉE --- #
    def record_file_analysis(self, db_conn: sqlite3.Connection, filepath_str: str, checksum: str, analysis_data: Dict[str, Any]) -> Optional[int]:
        file_id_to_log: Optional[int] = None # Utiliser une variable distincte pour le logging dans les blocs except
        cursor = db_conn.cursor()
        try:
            # La transaction est gérée par _file_processing_worker.
            # Aucun BEGIN, COMMIT, ou ROLLBACK ici.

            embedding_blob_to_store = analysis_data.get('document_embedding_blob')

            cursor.execute("""
                INSERT INTO files (filepath, checksum, last_processed_utc, size_bytes, encoding, embedding)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(filepath) DO UPDATE SET
                    checksum=excluded.checksum,
                    last_processed_utc=excluded.last_processed_utc,
                    size_bytes=excluded.size_bytes,
                    encoding=excluded.encoding,
                    embedding=excluded.embedding
                RETURNING id;
            """, (
                filepath_str,
                checksum,
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                analysis_data.get('file_size'),
                analysis_data.get('encoding'),
                embedding_blob_to_store
            ))
            file_id_row = cursor.fetchone()

            if not file_id_row or file_id_row['id'] is None:
                self.logger.error(f"N'a pas pu obtenir un file_id valide pour '{filepath_str}' après INSERT/UPDATE. "
                                  "L'opération DB a pu échouer ou RETURNING id n'est pas supporté/activé.")
                return None

            file_id = file_id_row['id']
            file_id_to_log = file_id # Assigner pour le logging en cas d'erreur plus tard
            self.logger.debug(f"Obtenu file_id: {file_id} pour le fichier: '{filepath_str}'.")

            # Suppression explicite des anciennes données associées avant réinsertion
            tables_to_clear = ["linguistic_tokens", "named_entities", "metadata", "entity_relations"]
            for table in tables_to_clear:
                self.logger.debug(f"Nettoyage de la table '{table}' pour file_id {file_id} avant réinsertion...")
                cursor.execute(f"DELETE FROM {table} WHERE file_id = ?", (file_id,))
                # Log facultatif du nombre de lignes supprimées si utile pour le débogage
                # self.logger.debug(f"{cursor.rowcount} lignes supprimées de '{table}' pour file_id {file_id}.")

            # Insertion des tokens linguistiques
            tokens_data = analysis_data.get('linguistic_features', {}).get('tokens', [])
            if tokens_data:
                tokens_to_insert = [
                    (file_id,
                     str(t_info.get('text',''))[:500],
                     str(t_info.get('lemma',''))[:255],
                     str(t_info.get('pos',''))[:50],
                     1 if t_info.get('is_stop') else 0,
                     1 if t_info.get('is_punct') else 0,
                     1 if t_info.get('is_alpha') else 0,
                     1 if t_info.get('is_significant') else 0)
                    for t_info in tokens_data
                ]
                if tokens_to_insert:
                    cursor.executemany("INSERT INTO linguistic_tokens (file_id, token_text, lemma, pos, is_stop, is_punct, is_alpha, is_significant) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tokens_to_insert)
                    self.logger.debug(f"{len(tokens_to_insert)} tokens linguistiques insérés pour file_id {file_id}.")

            # Insertion des entités nommées
            entities_data = analysis_data.get('linguistic_features', {}).get('entities', [])
            if entities_data:
                entities_to_insert = [
                    (file_id,
                     str(e_info.get('text',''))[:500],
                     str(e_info.get('label',''))[:100],
                     e_info.get('start_char'),
                     e_info.get('end_char'))
                    for e_info in entities_data
                ]
                if entities_to_insert:
                    cursor.executemany("INSERT INTO named_entities (file_id, entity_text, entity_type, start_char, end_char) VALUES (?, ?, ?, ?, ?)", entities_to_insert)
                    self.logger.debug(f"{len(entities_to_insert)} entités nommées insérées pour file_id {file_id}.")

            # Insertion des métadonnées
            metadata_items = analysis_data.get('extracted_metadata', {}).items()
            if metadata_items:
                metadata_to_insert = [
                    (file_id,
                     str(k)[:255],
                     str(v)[:1000] if v is not None else None)
                    for k, v in metadata_items
                ]
                if metadata_to_insert:
                    cursor.executemany("INSERT INTO metadata (file_id, meta_key, meta_value) VALUES (?, ?, ?)", metadata_to_insert)
                    self.logger.debug(f"{len(metadata_to_insert)} paires de métadonnées insérées pour file_id {file_id}.")

            self.logger.info(
                f"Données pour '{filepath_str}' (ID: {file_id}) préparées avec succès pour commit dans la KB. "
                f"Embedding: {'Présent' if embedding_blob_to_store else 'Absent'} "
                f"(taille blob: {len(embedding_blob_to_store) if embedding_blob_to_store else 'N/A'} octets)."
            )
            return file_id

        except sqlite3.IntegrityError as e_integrity:
            self.logger.error(f"Erreur d'intégrité SQLite DANS record_file_analysis pour '{filepath_str}' (file_id utilisé/tenté: {file_id_to_log}): {e_integrity}", exc_info=True)
            return None
        except sqlite3.Error as e_sqlite: # Attrape les autres erreurs SQLite spécifiques
            self.logger.error(f"Erreur SQLite générique DANS record_file_analysis pour '{filepath_str}' (file_id utilisé/tenté: {file_id_to_log}): {e_sqlite}", exc_info=True)
            return None
        except Exception as e_general: # Attrape toute autre exception non prévue
            self.logger.error(f"Erreur générale inattendue DANS record_file_analysis pour '{filepath_str}' (file_id utilisé/tenté: {file_id_to_log}): {e_general}", exc_info=True)
            return None

    # --- NOUVELLE MÉTHODE ---
    def get_all_document_embeddings(self, db_conn: sqlite3.Connection) -> List[Tuple[int, Optional[bytes]]]:
        """Récupère tous les file_id et leurs embeddings (blob) de la base de données."""
        self.logger.debug("Récupération de tous les embeddings de documents depuis la KB...")
        embeddings_list: List[Tuple[int, Optional[bytes]]] = []
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT id, embedding FROM files WHERE embedding IS NOT NULL")
            results = cursor.fetchall() # Liste de sqlite3.Row

            for row_data in results:
                file_id: int = row_data['id']
                # L'embedding peut être None même si la colonne n'est pas NULL si une insertion précédente
                # a mis None explicitement, bien que "WHERE embedding IS NOT NULL" devrait l'empêcher.
                embedding_val: Optional[bytes] = row_data['embedding']
                embeddings_list.append((file_id, embedding_val))

            self.logger.info(f"Récupéré {len(embeddings_list)} embeddings de documents depuis la KB pour le peuplement FAISS.")
            return embeddings_list
        except sqlite3.Error as e_sqlite:
            self.logger.error(f"Erreur SQLite lors de la récupération de tous les embeddings: {e_sqlite}", exc_info=True)
            return [] # Retourner une liste vide en cas d'erreur
        except Exception as e_general:
            self.logger.error(f"Erreur générale inattendue lors de la récupération de tous les embeddings: {e_general}", exc_info=True)
            return [] # Retourner une liste vide en cas d'erreur

    def get_filepath_by_id(self, db_conn: sqlite3.Connection, file_id: int) -> Optional[str]:
        """Récupère le chemin de fichier (filepath) pour un file_id donné."""
        self.logger.debug(f"Récupération du chemin pour file_id {file_id} depuis la KB...")
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT filepath FROM files WHERE id = ?", (file_id,))
            result_row = cursor.fetchone() # sqlite3.Row ou None

            if result_row:
                # La colonne filepath est NOT NULL dans le schéma, donc elle ne devrait pas être None ici
                # si result_row n'est pas None.
                filepath_val: Any = result_row['filepath']
                if filepath_val is not None: # Double vérification par sécurité
                    return str(filepath_val)
                else:
                    """TODO: Add docstring."""
                    # Ce cas ne devrait pas arriver si la contrainte NOT NULL est respectée
                    self.logger.warning(f"Filepath est None dans la DB pour file_id {file_id} bien que l'enregistrement existe (incohérence de schéma?).")
                    return None
            else:
                self.logger.debug(f"Aucun fichier trouvé avec l'ID {file_id} dans la KB.")
                return None
        except sqlite3.Error as e_sqlite:
            self.logger.error(f"Erreur SQLite lors de la récupération du chemin pour file_id {file_id}: {e_sqlite}", exc_info=True)
            return None
        except Exception as e_general:
            self.logger.error(f"Erreur générale inattendue lors de la récupération du chemin pour file_id {file_id}: {e_general}", exc_info=True)
            return None

    def get_related_files_by_entity(self, db_conn: sqlite3.Connection, entity_text: str, entity_type: Optional[str] = None, current_file_id: Optional[int] = None, limit: int = 10) -> List[Dict[str, Any]]:
        self.logger.debug(f"Recherche de fichiers liés à l'entité '{entity_text}' (type: {entity_type or 'Any'}, limit: {limit}).")
        results: List[Dict[str, Any]] = []
        try:
            cursor = db_conn.cursor()
            query = """
                SELECT DISTINCT f.id as file_id, f.filepath, f.checksum, ne.entity_text as matched_entity_text, ne.entity_type as matched_entity_type, ne.start_char, ne.end_char
                FROM files f
                JOIN named_entities ne ON f.id = ne.file_id
                WHERE LOWER(ne.entity_text) = LOWER(?)
            """ # Ajout de file_id et des noms d'entités matchées pour plus de clarté
            params: List[Any] = [entity_text.lower()] # Assurer que le paramètre est aussi en minuscules

            if entity_type:
                query += " AND LOWER(ne.entity_type) = LOWER(?)"
                params.append(entity_type.lower())
            if current_file_id is not None:
                query += " AND f.id != ?"
                params.append(current_file_id)

    """TODO: Add docstring."""
            query += " ORDER BY f.last_processed_utc DESC LIMIT ?;"
            params.append(limit)

            cursor.execute(query, tuple(params))
            results = [dict(row) for row in cursor.fetchall()]
            self.logger.debug(f"{len(results)} fichiers liés trouvés pour l'entité '{entity_text}'.")
            return results
        except sqlite3.Error as e_sqlite:
            self.logger.error(f"Erreur SQLite lors de la recherche de fichiers liés à l'entité '{entity_text}': {e_sqlite}", exc_info=True)
            return [] # Retourner une liste vide en cas d'erreur
        except Exception as e_general:
            self.logger.error(f"Erreur générale lors de la recherche de fichiers liés à l'entité '{entity_text}': {e_general}", exc_info=True)
            return []

    def get_entity_definitions(self, db_conn: sqlite3.Connection, entity_text: str) -> List[Dict[str, Any]]:
        self.logger.debug(f"Récupération des définitions/métadonnées pour l'entité '{entity_text}'.")
        # Étendu les meta_key pour inclure des synonymes courants
        meta_keys_to_search = ('titre', 'title', 'description', 'version', 'statut', 'status', 'auteur', 'author', 'sujet', 'subject')

        # Créer les placeholders pour la clause IN
        placeholders = ', '.join('?' for _ in meta_keys_to_search)
        query = f"""
            SELECT f.filepath, m.meta_key, m.meta_value
            FROM files f
            JOIN named_entities ne ON f.id = ne.file_id
            JOIN metadata m ON f.id = m.file_id
            WHERE LOWER(ne.entity_text) = LOWER(?)
              AND LOWER(m.meta_key) IN ({placeholders})
            ORDER BY f.filepath, m.meta_key;
        """
            """TODO: Add docstring."""
        params = [entity_text.lower()] + list(meta_keys_to_search)

        try:
            cursor = db_conn.cursor()
            cursor.execute(query, tuple(params))
            results = [dict(row) for row in cursor.fetchall()]
            self.logger.debug(f"{len(results)} définitions/métadonnées trouvées pour l'entité '{entity_text}'.")
            return results
        except sqlite3.Error as e_sqlite:
            self.logger.error(f"Erreur SQLite lors de la récupération des définitions pour l'entité '{entity_text}': {e_sqlite}", exc_info=True)
            return []
        except Exception as e_general:
            self.logger.error(f"Erreur générale lors de la récupération des définitions pour l'entité '{entity_text}': {e_general}", exc_info=True)
            return []

    def get_all_files_summary(self, db_conn: sqlite3.Connection, limit: int = 50, exclude_id: Optional[int] = None) -> List[Dict[str, Any]]:
        self.logger.debug(f"Récupération du résumé de tous les fichiers (limit: {limit}, exclude_id: {exclude_id}).")
        # Ajout de plus de colonnes utiles pour un "résumé"
        query = "SELECT id, filepath, checksum, last_processed_utc, size_bytes, encoding, (embedding IS NOT NULL) as embedding_present FROM files"
        params: List[Any] = []
        conditions: List[str] = []

        if exclude_id is not None:
            conditions.append("id != ?")
            params.append(exclude_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

    """TODO: Add docstring."""
        query += " ORDER BY last_processed_utc DESC LIMIT ?;"
        params.append(limit)

        try:
            cursor = db_conn.cursor()
            cursor.execute(query, tuple(params))
            results = [dict(row) for row in cursor.fetchall()]
            self.logger.debug(f"{len(results)} fichiers récupérés pour le résumé.")
            return results
        except sqlite3.Error as e_sqlite:
            self.logger.error(f"Erreur SQLite lors de la récupération du résumé des fichiers: {e_sqlite}", exc_info=True)
            return []
        except Exception as e_general:
            self.logger.error(f"Erreur générale lors de la récupération du résumé des fichiers: {e_general}", exc_info=True)
            return []

    def remove_file_record(self, db_conn: sqlite3.Connection, filepath_str: str) -> None:
        # La transaction (commit/rollback) est gérée par l'appelant (ex: CerveauService._handle_deleted_file)
        self.logger.debug(f"Tentative de suppression de l'enregistrement pour '{filepath_str}' de la KB.")
        try:
            cursor = db_conn.cursor()
                """TODO: Add docstring."""
            # La suppression des données associées est gérée par ON DELETE CASCADE dans le schéma SQL
            cursor.execute("DELETE FROM files WHERE filepath = ?", (filepath_str,))

            if cursor.rowcount > 0:
                self.logger.info(f"Enregistrement pour '{filepath_str}' marqué pour suppression de la KB (commit sera fait par l'appelant).")
            else:
                """TODO: Add docstring."""
                self.logger.info(f"Aucun enregistrement trouvé pour '{filepath_str}' à supprimer de la KB (ou déjà supprimé).")
        except sqlite3.Error as e_sqlite:
            self.logger.error(f"Erreur SQLite lors de la tentative de suppression de '{filepath_str}' de la KB: {e_sqlite}", exc_info=True)
            # L'appelant gérera le rollback si nécessaire.
        except Exception as e_general:
            self.logger.error(f"Erreur générale inattendue lors de la tentative de suppression de '{filepath_str}': {e_general}", exc_info=True)


class PipelineStepInterface:
    # MODIFICATION: Le constructeur prend maintenant une référence à l'instance de KnowledgeBase
    # mais les méthodes `process` devront recevoir la connexion DB du worker si elles en ont besoin.
    def __init__(self,
                 step_config: Dict[str, Any],
                 global_config: Dict[str, Any],
                 kb_instance: Optional[KnowledgeBase],
                 # --- CES DEUX ARGUMENTS SONT LES NOUVEAUX ET IMPORTANTS ---
                 text_improver_shared: Optional[alma_core.TextImprover],      # NOUVEL ARGUMENT
                 knowledge_linker_shared: Optional[alma_core.KnowledgeLinker] # NOUVEL ARGUMENT
                ):
        self.step_config = step_config
        self.global_config = global_config
        self.kb_instance = kb_instance # Stocker l'instance de KB (pour NLP, etc.)
        self.logger = logging.getLogger(f"{MODULE_NAME}.{self.__class__.__name__}")

        # --- CORRECTION : UTILISER LES INSTANCES PARTAGÉES PASSÉES EN ARGUMENT ---
        self.text_improver = text_improver_shared
        self.knowledge_linker = knowledge_linker_shared

    """TODO: Add docstring."""
        if alma_core:
            core_cfg = self.global_config.get("core_algorithms_config", {})
            ti_cfg = core_cfg.get("text_improver")
                """TODO: Add docstring."""
            kl_cfg = core_cfg.get("knowledge_linker")

            # L'instance NLP est maintenant dans kb_instance
            nlp_inst_for_core = self.kb_instance.nlp_instance if self.kb_instance and self.kb_instance.is_spacy_ready else None

            # Passer kb_instance aux constructeurs de Core
            if ti_cfg:
                try: self.text_improver = alma_core.TextImprover(ti_cfg, self.kb_instance, nlp_inst_for_core, self.logger)
                except Exception as e: self.logger.error(f"Erreur init TextImprover: {e}", exc_info=True)
            if kl_cfg:
                """TODO: Add docstring."""
                try: self.knowledge_linker = alma_core.KnowledgeLinker(kl_cfg, self.kb_instance, nlp_inst_for_core, self.logger)
                except Exception as e: self.logger.error(f"Erreur init KnowledgeLinker: {e}", exc_info=True)
        else:
            self.logger.warning("Module alma_core non disponible.")

    # MODIFICATION: La méthode process prend maintenant une connexion DB en argument
    def process(self, processor: 'FileProcessor', db_conn_worker: sqlite3.Connection) -> bool:
        raise NotImplementedError

class ComprehensionStep(PipelineStepInterface):
    def __init__(self,
                 step_config: Dict[str, Any],
                 global_config: Dict[str, Any],
                 kb_instance: Optional[KnowledgeBase],
                 text_improver_shared: Optional[alma_core.TextImprover],
                 knowledge_linker_shared: Optional[alma_core.KnowledgeLinker]
                ):
        super().__init__(step_config, global_config, kb_instance,
                         text_improver_shared, knowledge_linker_shared)

        # Utiliser self.logger qui est initialisé dans PipelineStepInterface.__init__
        # self.logger.debug("Initialisation de ComprehensionStep...") # Log de debug optionnel

        # Récupérer la configuration NLP globale de manière sûre
        # nlp_config est utilisé plusieurs fois, donc le stocker localement est bien.
        nlp_config = self.global_config.get("nlp", {}) # Récupère la section 'nlp' de APP_CONFIG
        if not nlp_config: # Au cas où la section 'nlp' serait absente de la config
            self.logger.warning("Section 'nlp' manquante dans la configuration globale. Utilisation des valeurs par défaut pour ComprehensionStep.")
            nlp_config = DEFAULT_CONFIG.get("nlp", {}) # Fallback sur DEFAULT_CONFIG['nlp']

        self.significant_pos_tags = set(nlp_config.get("significant_pos_tags", ["NOUN", "PROPN", "VERB", "ADJ"]))

        self.rake_instance: Optional[Any] = None
        self.yake_extractor: Optional[Any] = None

        # Initialisation de Rake-NLTK (utilise la globale Rake_class_alias)
        if nlp_config.get("use_rake_if_available", True): # Vérifier la config
            if Rake_class_alias: # Rake_class_alias est la variable globale qui contient la classe Rake
                try:
                    # Déterminer la langue pour Rake
                    lang_for_rake_str = nlp_config.get("default_language", "fr")
                    rake_language_map = {"fr": "french", "en": "english", "es": "spanish", "pt": "portuguese", "it": "italian", "nl": "dutch", "de": "german", "ru": "russian"} # Étendre si besoin
                    rake_lang_param = rake_language_map.get(lang_for_rake_str.lower()[:2], "english") # Prend les 2 premières lettres, fallback sur english

                    self.rake_instance = Rake_class_alias(language=rake_lang_param) # Instancier la CLASSE
                    self.logger.debug(f"Instance Rake-NLTK créée avec succès (langue: {rake_lang_param}).")
                except Exception as e_rake_init_comprehension:
                    self.logger.warning(f"Impossible d'initialiser Rake-NLTK dans ComprehensionStep: {e_rake_init_comprehension}", exc_info=True)
            else:
                self.logger.info("Rake-NLTK activé dans config mais la classe Rake (Rake_class_alias) n'est pas disponible globalement (échec import initial).")
        else:
            self.logger.info("Utilisation de Rake-NLTK désactivée dans la configuration nlp pour ComprehensionStep.")

        # Initialisation de YAKE! (utilise la globale yake qui est le module)
        if nlp_config.get("use_yake_if_available", True): # Vérifier la config
            if yake: # yake est la variable globale qui contient le module yake
                try:
                    lang_yake_str = nlp_config.get("default_language", "fr")[:2].lower() # ex: "fr", "en"
                    # Paramètres YAKE! (peuvent être mis en config plus tard si besoin)
                    n_yake = int(nlp_config.get("yake_ngram_size", 3))
                    dedupLim_yake = float(nlp_config.get("yake_dedup_limit", 0.9))
                    top_yake = int(nlp_config.get("yake_top_n_keywords", 10))

                    self.yake_extractor = yake.KeywordExtractor(lan=lang_yake_str, n=n_yake, dedupLim=dedupLim_yake, top=top_yake, features=None)
                    self.logger.debug(f"Instance YAKE! créée (lang: {lang_yake_str}, n: {n_yake}, dedupLim: {dedupLim_yake}, top: {top_yake}).")
                except Exception as e_yake_init_comprehension:
                    self.logger.warning(f"Impossible d'initialiser YAKE! dans ComprehensionStep: {e_yake_init_comprehension}", exc_info=True)
            else:
                self.logger.info("YAKE! activé dans config mais le module yake n'est pas disponible globalement (échec import initial).")
        else:
            self.logger.info("Utilisation de YAKE! désactivée dans la configuration nlp pour ComprehensionStep.")

        # self.logger.debug("ComprehensionStep initialisé.") # Log de fin d'init optionnel

    def _is_valid_entity(self, entity_text: str, entity_label: str) -> bool:
        """
        Applique des filtres pour déterminer si une entité extraite par spaCy est valide
        et pertinente pour ALMA, afin de réduire le bruit.
        """
        text_lower = entity_text.lower().strip()
        if not text_lower: # Ignorer les entités vides après strip
            return False

        # 1. Filtre par liste noire de textes exacts (insensible à la casse)
        if text_lower in ENTITY_TEXT_BLACKLIST:
            self.logger.debug(f"NER Filter: Entité '{entity_text}' rejetée (blacklist texte).")
            return False

        # 2. Filtre par expressions régulières
        for regex_pattern in ENTITY_REGEX_BLACKLIST:
            if regex_pattern.fullmatch(entity_text): # Utiliser fullmatch pour correspondre à toute la chaîne
                self.logger.debug(f"NER Filter: Entité '{entity_text}' rejetée (regex: {regex_pattern.pattern}).")
                return False

        # 3. Filtre par longueur
        if entity_text.isupper() and len(entity_text) < MIN_ENTITY_LENGTH_ACRONYM: # Acronymes (ex: IA)
            self.logger.debug(f"NER Filter: Acronyme potentiel '{entity_text}' trop court (<{MIN_ENTITY_LENGTH_ACRONYM}).")
            return False
        if not entity_text.isupper() and len(entity_text) < MIN_ENTITY_LENGTH:
            """TODO: Add docstring."""
            self.logger.debug(f"NER Filter: Entité '{entity_text}' trop courte (<{MIN_ENTITY_LENGTH}).")
            return False

        # 4. Filtre basé sur la casse et les caractères pour certains types
        if entity_label in ["PER", "ORG", "LOC"]:
            # Doit contenir au moins une lettre (pour éviter les chiffres purs tagués comme PER/ORG/LOC)
            if not any(char.isalpha() for char in entity_text):
                self.logger.debug(f"NER Filter: Entité '{entity_text}' ({entity_label}) sans lettres rejetée.")
                return False
            # Pour PER et ORG, on s'attend souvent à une majuscule (sauf si c'est un acronyme déjà géré)
            # Cette règle peut être trop stricte pour certaines langues ou cas.
            # if entity_label in ["PER", "ORG"] and not entity_text.isupper() and not any(char.isupper() for char in entity_text if char.isalpha()):
            #     self.logger.debug(f"NER Filter: Entité '{entity_text}' ({entity_label}) sans majuscule rejetée.")
            #     return False

        # 5. Filtre pour les entités contenant des sauts de ligne (souvent du code ou du texte mal formaté)
        if "\n" in entity_text or "\r" in entity_text:
            self.logger.debug(f"NER Filter: Entité '{entity_text.replace(chr(10), '/n').replace(chr(13), '/r')}' contenant des sauts de ligne rejetée.")
            return False

        return True # Si tous les filtres sont passés

    def _extract_with_spacy(self, text_content: str, processor_data: Dict[str, Any]) -> None:
        if not self.kb_instance or not self.kb_instance.is_spacy_ready or not self.kb_instance.nlp_instance:
            self.logger.debug("_extract_with_spacy: Instance spaCy non prête.")
            return

        doc: Optional[SpacyDoc] = None
        try:
            nlp_config = self.global_config.get("nlp", {})
            max_len = nlp_config.get("spacy_max_text_length", 1_000_000)
            text_to_process = text_content
            if len(text_content) > self.kb_instance.nlp_instance.max_length:
                self.logger.warning(f"Texte ({len(text_content)} chars) dépasse spaCy max_length ({self.kb_instance.nlp_instance.max_length}). Troncature.")
                text_to_process = text_content[:self.kb_instance.nlp_instance.max_length]
            doc = self.kb_instance.nlp_instance(text_to_process)
        except Exception as e_spacy_proc:
            self.logger.error(f"Erreur lors du traitement spaCy: {e_spacy_proc}", exc_info=True)
            return
        if not doc:
            self.logger.warning("Traitement spaCy n'a pas retourné de document.")
            return

        features: Dict[str, List[Dict[str, Any]]] = {"tokens": [], "entities": []}
        for token in doc:
            is_significant_token = (token.pos_ in self.significant_pos_tags and
                                    not token.is_stop and not token.is_punct and token.is_alpha)
            features["tokens"].append({
                "text": token.text, "lemma": token.lemma_.lower(), "pos": token.pos_,
                    """TODO: Add docstring."""
                "is_stop": token.is_stop, "is_punct": token.is_punct,
                "is_alpha": token.is_alpha, "is_significant": is_significant_token
            })

        # --- MODIFICATION : Application du Filtre NER ---
        raw_entities_count = len(doc.ents)
        filtered_entities_count = 0
        for ent in doc.ents:
            if self._is_valid_entity(ent.text, ent.label_): # Appel au filtre
                features["entities"].append({
                    "text": ent.text, "label": ent.label_,
                    "start_char": ent.start_char, "end_char": ent.end_char
                })
                filtered_entities_count += 1
            # else: l'entité est filtrée, déjà loguée par _is_valid_entity

        if features["tokens"] or features["entities"]:
            processor_data['linguistic_features'] = features
            self.logger.debug(f"spaCy: {len(features['tokens'])} tokens. Entités brutes: {raw_entities_count}, Entités filtrées: {filtered_entities_count}.")
        else:
            self.logger.debug("spaCy: Aucun token ou entité notable après filtrage.")
        # --- FIN MODIFICATION ---

    def _extract_with_nltk(self, text_content: str, processor_data: Dict[str, Any]) -> None:
        # ... (code inchangé) ...
        if not nltk:
            self.logger.debug("_extract_with_nltk: NLTK non disponible.")
            return
        try:
            try: tokens = nltk.word_tokenize(text_content, language='french')
            except Exception: tokens = nltk.word_tokenize(text_content)
            try: pos_tags = nltk.pos_tag(tokens)
            except Exception: pos_tags = [(token, "UNK") for token in tokens]
            lemmatizer = nltk.WordNetLemmatizer() if hasattr(nltk, 'WordNetLemmatizer') else None
            nlp_config = self.global_config.get("nlp", {})
            lang_nltk = nlp_config.get("default_language", "english")
            lang_stopwords_nltk = "french" if lang_nltk == "fr" else "english"
            stopwords_set = set()
            try: stopwords_set = set(nltk.corpus.stopwords.words(lang_stopwords_nltk))
                """TODO: Add docstring."""
            except OSError: self.logger.warning(f"Ressources stopwords NLTK pour '{lang_stopwords_nltk}' non trouvées.")
            except Exception as e_sw: self.logger.warning(f"Erreur stopwords NLTK '{lang_stopwords_nltk}': {e_sw}")
            nltk_features: Dict[str, List[Dict[str, Any]]] = {"tokens": []}
            for token, tag in pos_tags:
                token_lower = token.lower(); lemma = token_lower
                if lemmatizer:
                    try:
                        wn_pos = tag[0].lower() if tag[0].lower() in ['a', 'r', 'n', 'v'] else 'n'
                        lemma = lemmatizer.lemmatize(token_lower, pos=wn_pos)
                    except Exception: lemma = token_lower
                is_alpha_nltk = token.isalpha()
                is_punct_nltk = not is_alpha_nltk and len(token) == 1 and not token.isdigit()
                is_stop_nltk = token_lower in stopwords_set
                is_significant_nltk = (tag.startswith(('NN', 'VB', 'JJ')) and not is_stop_nltk and not is_punct_nltk and is_alpha_nltk)
                nltk_features["tokens"].append({"text": token, "lemma": lemma, "pos": tag, "is_stop": is_stop_nltk, "is_punct": is_punct_nltk, "is_alpha": is_alpha_nltk, "is_significant": is_significant_nltk})
            if nltk_features["tokens"]:
                if 'linguistic_features' in processor_data and 'tokens' in processor_data['linguistic_features']:
                    processor_data['linguistic_features']['tokens_nltk'] = nltk_features["tokens"]
                else:
                    processor_data.setdefault('linguistic_features', {})['tokens'] = nltk_features["tokens"]
                self.logger.debug(f"NLTK a extrait {len(nltk_features['tokens'])} tokens.")
        except Exception as e_nltk_main: self.logger.warning(f"Erreur NLTK: {e_nltk_main}", exc_info=True)
            """TODO: Add docstring."""


    def _extract_keywords_fallback(self, text_content: str, processor_data: Dict[str, Any]) -> None:
        # ... (code inchangé) ...
        keywords: List[Tuple[str, float]] = []
        if self.rake_instance:
            try:
                self.rake_instance.extract_keywords_from_text(text_content)
                ranked_phrases = self.rake_instance.get_ranked_phrases_with_scores()
                keywords.extend([(str(phrase), float(score)) for score, phrase in ranked_phrases[:10]])
                if keywords: self.logger.debug(f"Rake-NLTK: {len(keywords)} mots-clés.")
            except Exception as e_rake_extract: self.logger.warning(f"Erreur Rake: {e_rake_extract}", exc_info=True)
        if not keywords and self.yake_extractor:
            try:
                yake_keywords_extracted = self.yake_extractor.extract_keywords(text_content)
                keywords.extend([(str(kw), float(score)) for kw, score in yake_keywords_extracted])
                if keywords: self.logger.debug(f"YAKE!: {len(keywords)} mots-clés.")
            except Exception as e_yake_extract: self.logger.warning(f"Erreur YAKE!: {e_yake_extract}", exc_info=True)
        if keywords:
            if not self.rake_instance and self.yake_extractor: keywords_sorted = sorted(keywords, key=lambda x: x[1])
            else: keywords_sorted = sorted(keywords, key=lambda x: x[1], reverse=True)
            processor_data['keywords_fallback'] = keywords_sorted
            self.logger.debug(f"Mots-clés fallback stockés.")


    def process(self, processor: 'FileProcessor', db_conn_worker: sqlite3.Connection) -> bool:
        # ... (code inchangé, il appelle déjà les méthodes _extract_... ci-dessus) ...
        self.logger.debug(f"Début Compréhension pour: {processor.filepath}")
        processor.processed_data['document_embedding_blob'] = None
        try:
            processor.file_content, processor.encoding = robust_file_read(processor.filepath)
            if processor.file_content is None:
                self.logger.warning(f"Contenu non lisible pour {processor.filepath}. Compréhension échouée.")
                return False
            processor.processed_data['encoding'] = processor.encoding
            try: processor.processed_data['file_size'] = processor.filepath.stat().st_size
            except FileNotFoundError:
                self.logger.error(f"Fichier {processor.filepath} non trouvé lors de stat() dans ComprehensionStep.")
                return False

            parsed_structure_preview: Any = {"type": "text", "content_preview": processor.file_content[:200]}
            if processor.filepath.suffix.lower() == ".json":
                try:
                    loaded_json_content = json.loads(processor.file_content)
                    parsed_structure_preview = loaded_json_content
                    self.logger.debug(f"Fichier {processor.filepath} parsé comme JSON.")
                    processor.processed_data['parsed_structure_type'] = "json_object_root" if isinstance(loaded_json_content, dict) else "json_array_root"
                except json.JSONDecodeError as e_json:
                    self.logger.warning(f"Échec parsing JSON pour {processor.filepath}: {e_json}. Traité comme texte.")
                    processor.processed_data['parsed_structure_type'] = "text"
            else:
                processor.processed_data['parsed_structure_type'] = "text"

            if processor.processed_data['parsed_structure_type'] != "text":
                 processor.processed_data['parsed_data_preview'] = {"type": processor.processed_data['parsed_structure_type'], "preview": str(parsed_structure_preview)[:500] + ("..." if len(str(parsed_structure_preview)) > 500 else "")}
            else:
                 processor.processed_data['parsed_data_preview'] = parsed_structure_preview

            if self.kb_instance and self.kb_instance.is_spacy_ready:
                self._extract_with_spacy(processor.file_content, processor.processed_data)
            else:
                nlp_global_config = self.global_config.get("nlp", {})
                if nltk and nlp_global_config.get("use_nltk_if_available", False):
                    self._extract_with_nltk(processor.file_content, processor.processed_data)
                self._extract_keywords_fallback(processor.file_content, processor.processed_data)

            sbert_model_to_use = None
            if alma_core and hasattr(self, 'knowledge_linker') and self.knowledge_linker and \
               isinstance(self.knowledge_linker, alma_core.KnowledgeLinker) and \
               self.knowledge_linker.sbert_model:
                sbert_model_to_use = self.knowledge_linker.sbert_model

            if sbert_model_to_use and processor.file_content:
                _numpy_module_local = None
                try:
                    import numpy
                        """TODO: Add docstring."""
                    _numpy_module_local = numpy
                except ImportError: self.logger.warning("Numpy non trouvé. SBERT embedding désactivé.")
                if _numpy_module_local:
                    try:
                        self.logger.info(f"Génération SBERT embedding pour {processor.filepath}...")
                        embedding_np = sbert_model_to_use.encode(processor.file_content, convert_to_numpy=True, show_progress_bar=False)
                        norm = _numpy_module_local.linalg.norm(embedding_np)
                        normalized_embedding_np = embedding_np / norm if norm > 0 else embedding_np
                        if norm == 0: self.logger.warning(f"Vecteur SBERT nul pour {processor.filepath}.")
                        processor.processed_data['document_embedding_blob'] = normalized_embedding_np.astype(_numpy_module_local.float32).tobytes()
                        self.logger.info(f"SBERT embedding généré (blob: {len(processor.processed_data['document_embedding_blob'])} octets) pour {processor.filepath}.")
                    except Exception as e_sbert_embed: self.logger.error(f"Erreur génération SBERT embedding pour {processor.filepath}: {e_sbert_embed}", exc_info=True)
            else:
                if not sbert_model_to_use: self.logger.debug(f"Modèle SBERT non dispo. Pas d'embedding SBERT pour {processor.filepath}.")
                if not processor.file_content: self.logger.debug(f"Contenu fichier vide. Pas d'embedding SBERT pour {processor.filepath}.")
                    """TODO: Add docstring."""

            self.logger.audit(f"Compréhension OK pour: {processor.filepath}")
            return True
                """TODO: Add docstring."""
        except FileNotFoundError:
            self.logger.error(f"ERREUR CRITIQUE: Fichier {processor.filepath} NON TROUVÉ pendant ComprehensionStep.process.")
            return False
        except Exception as e:
            self.logger.error(f"Erreur inattendue dans ComprehensionStep.process pour {processor.filepath}: {e}", exc_info=True)
            return False

class AnalysisStep(PipelineStepInterface):
    def _analyze_sentiment_basic(self, text_content: str) -> Dict[str, Any]:
        # Utilise self.global_config pour les listes de mots
        pos_words = set(self.global_config.get("nlp",{}).get("sentiment_positive_words",[]))
        neg_words = set(self.global_config.get("nlp",{}).get("sentiment_negative_words",[]))
        score = 0
        # Utiliser une regex plus simple pour les mots, ou celle que vous aviez si elle est préférée
        words = set(re.findall(r'\b[a-zA-Z\u00C0-\u00FF]{3,}\b', text_content.lower())) # Mots d'au moins 3 lettres alpha

        for w in words:
            if w in pos_words: score +=1
            if w in neg_words: score -=1

        lbl="neutre"
        # Utilise self.step_config pour le seuil spécifique à cette étape
        thr=self.step_config.get("sentiment_threshold",0.1) # Assurez-vous que 0.1 est un float

        if score > thr: lbl="plutôt positif"
        elif score < -thr: lbl="plutôt négatif"
        return {"score":score, "label":lbl, "method":"basic_keyword"}

    def _detect_topics_tfidf(self, processor_data: Dict[str, Any]) -> Optional[List[str]]:
        if not sklearn_tfidf:
            self.logger.debug("sklearn_tfidf non disponible pour TF-IDF.")
            return None

        tokens = processor_data.get('linguistic_features',{}).get('tokens',[]) or \
                 processor_data.get('linguistic_features',{}).get('tokens_nltk',[])
        if not tokens:
            self.logger.debug("Aucun token disponible pour TF-IDF.")
            return None

        terms = [t['lemma'] for t in tokens if t.get('is_significant')]
        if not terms:
            self.logger.debug("Aucun terme significatif pour TF-IDF.")
            return None

        try:
            # CORRECTION PRINCIPALE : Utiliser self.global_config pour la config NLP globale
            nlp_global_config = self.global_config.get("nlp", {})
            sw: Union[str, List[str], None] = None # Type pour les stopwords de sklearn
            lang_cfg = nlp_global_config.get("default_language", "fr")

            # Stratégie pour les stopwords :
            # 1. Essayer les stopwords de spaCy (globaux) s'ils sont chargés
            # 2. Sinon, utiliser les noms de langue pour sklearn ('french', 'english')
            # 3. Sinon, pas de stopwords (None)
            if SPACY_STOP_WORDS: # Variable globale SPACY_STOP_WORDS_SET
                sw = list(SPACY_STOP_WORDS)
                self.logger.debug(f"Utilisation des stopwords spaCy (taille: {len(sw)}) pour TF-IDF (langue de config: {lang_cfg})")
            elif lang_cfg == "fr":
                sw = "french"
                self.logger.debug("Utilisation des stopwords 'french' de scikit-learn pour TF-IDF.")
            elif lang_cfg == "en":
                sw = "english"
                self.logger.debug("Utilisation des stopwords 'english' de scikit-learn pour TF-IDF.")
            else:
                self.logger.warning(f"Langue non supportée ('{lang_cfg}') pour les stopwords TF-IDF sklearn, ou stopwords spaCy non chargés. TF-IDF sans stopwords spécifiques.")
                sw = None # Explicitement None si aucune condition n'est remplie

            # TfidfVectorizer peut prendre None, 'english', ou une liste de mots pour stop_words
            vectorizer = sklearn_tfidf(max_features=10, stop_words=sw) # type: ignore

            if not terms: # Double vérification après la constitution de la liste terms
                self.logger.debug("La liste 'terms' est vide après filtrage, impossible de faire TF-IDF.")
                return None

            document_to_vectorize = " ".join(terms)
            if not document_to_vectorize.strip(): # S'assurer qu'il y a du contenu non vide
                self.logger.debug("Document à vectoriser est vide ou ne contient que des espaces après join. TF-IDF annulé.")
                return None

            matrix = vectorizer.fit_transform([document_to_vectorize])
            names = vectorizer.get_feature_names_out()
                """TODO: Add docstring."""

            if matrix.shape[0] == 0 or matrix.shape[1] == 0: # Vérifier si la matrice est vide
                self.logger.debug("Matrice TF-IDF vide après vectorisation. Aucun thème détecté.")
                return None

            vec = matrix[0]
            # Obtenir les indices des N plus grands scores (ici 5, mais max_features est 10)
            num_top_topics = min(5, len(names)) # S'assurer de ne pas demander plus de thèmes qu'il n'y a de features
            if num_top_topics == 0:
                self.logger.debug("Aucun feature name après vectorisation. Aucun thème détecté.")
                return None

            top_indices = vec.toarray()[0].argsort()[-num_top_topics:][::-1]

            detected_topics = [names[i] for i in top_indices if vec[0,i] > 0.01] # Seuil de 0.01 pour la pertinence

            if detected_topics:
                self.logger.debug(f"Thèmes TF-IDF détectés: {detected_topics}")
                return detected_topics
            else:
                self.logger.debug("Aucun thème TF-IDF détecté avec un score suffisant.")
                return None
        except ValueError as ve: # Peut arriver si le vocabulaire est vide après stop words
            self.logger.warning(f"Erreur ValueError dans TF-IDF (souvent vocabulaire vide): {ve}", exc_info=False) # exc_info=False pour ne pas polluer avec la stacktrace complète pour cette erreur attendue
            return None
        except Exception as e:
            self.logger.warning(f"Erreur TF-IDF inattendue: {e}", exc_info=True)
            return None

    def process(self, processor: 'FileProcessor', db_conn_worker: sqlite3.Connection) -> bool: # db_conn_worker non utilisé ici directement
        self.logger.debug(f"Début: {processor.filepath}")
        if not processor.file_content:
            self.logger.warning(f"Contenu de fichier vide pour {processor.filepath}, AnalysisStep sautée.")
            return False # Ou True si on considère que ce n'est pas une erreur bloquante pour le pipeline

        try:
            processor.processed_data['sentiment_analysis'] = self._analyze_sentiment_basic(processor.file_content)

            meta = {}
            # Limiter le nombre de lignes à parser pour les métadonnées pour éviter de lire des fichiers entiers inutilement
            for line in processor.file_content.splitlines()[:20]: # Augmenté à 20 lignes pour plus de flexibilité
                if ":" in line:
                    """TODO: Add docstring."""
                    key, val = line.split(":",1)
                    key=key.strip().lower()
                    val=val.strip()
                    # Liste de clés de métadonnées plus restrictive et normalisée
                    if key in ["auteur", "author", "date", "version", "titre", "title", "description", "statut", "status", "sujet", "subject", "tags", "keywords"]:
                        # Normaliser les clés (ex: 'auteur' -> 'author')
                        normalized_key = key.replace("auteur","author").replace("titre","title").replace("sujet","subject").replace("statut","status")
                        meta[normalized_key] = val
            if meta:
                processor.processed_data['extracted_metadata'] = meta
                self.logger.debug(f"Métadonnées extraites pour {processor.filepath}: {meta}")

            topics = self._detect_topics_tfidf(processor.processed_data)
            if topics:
                processor.processed_data['detected_topics_tfidf'] = topics
            elif 'keywords_fallback' in processor.processed_data and processor.processed_data['keywords_fallback']:
                # S'assurer que keywords_fallback est une liste de tuples (keyword, score)
                    """TODO: Add docstring."""
                kw_data = processor.processed_data['keywords_fallback']
                    """TODO: Add docstring."""
                if isinstance(kw_data, list) and all(isinstance(item, tuple) and len(item) == 2 for item in kw_data):
                    processor.processed_data['detected_topics_keywords'] = [kw_score[0] for kw_score in kw_data[:5]]
                else:
                    self.logger.warning(f"Format inattendu pour 'keywords_fallback' pour {processor.filepath}")

            self.logger.audit(f"Analyse OK: {processor.filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur dans AnalysisStep.process pour {processor.filepath}: {e}", exc_info=True)
            return False

class StudyStep(PipelineStepInterface):
    def process(self, processor: 'FileProcessor', db_conn_worker: sqlite3.Connection) -> bool:
        self.logger.debug(f"Début: {processor.filepath}")
        try:
            if self.kb_instance and processor.checksum:
                """TODO: Add docstring."""
                # MODIFICATION: Passer db_conn_worker à record_file_analysis
                file_id = self.kb_instance.record_file_analysis(db_conn_worker, str(processor.filepath), processor.checksum, processor.processed_data)
                if file_id:
                    processor.processed_data['kb_file_id'] = file_id
                    # La logique de cross-référencement utiliserait aussi db_conn_worker si elle accède à la KB
                    # entities = processor.processed_data.get('linguistic_features',{}).get('entities',[])[:3]
                    # for ent in entities:
                    #     related = self.kb_instance.get_related_files_by_entity(db_conn_worker, ent['text'], ent['label'], file_id)
                    #     if related: processor.processed_data.setdefault('cross_references_kb',{}).setdefault(f"{ent['label']}::{ent['text']}",[]).extend(related)
            self.logger.audit(f"Étude OK: {processor.filepath}"); return True
        except Exception as e: self.logger.error(f"Erreur: {e}", exc_info=True); return False

class ImprovementProposalStep(PipelineStepInterface):
    # Dans la classe ImprovementProposalStep, méthode process
    def process(self, processor: 'FileProcessor', db_conn_worker: sqlite3.Connection) -> bool:
        self.logger.debug(f"Début: {processor.filepath}")
        proposals: List[Dict[str, Any]] = []
        try: # Englober toute la logique de l'étape
            if not processor.processed_data.get('extracted_metadata'):
                proposals.append({"type":"metadata", "suggestion":"Ajouter métadonnées standard.", "priority":"medium"})

            if self.knowledge_linker and self.kb_instance and self.kb_instance.is_spacy_ready and \
            processor.file_content and processor.processed_data.get("kb_file_id"):
                current_file_data = {
                    "filepath_str": str(processor.filepath),
                    "kb_file_id": processor.processed_data["kb_file_id"],
                    "file_content": processor.file_content,
                    "analysis_data": processor.processed_data
                }
                try:
                    proposals.extend(self.knowledge_linker.find_and_propose_semantic_links(current_file_data, db_conn_worker))
                except Exception as e_kl_links:
                    self.logger.error(f"Erreur dans KL.find_and_propose_semantic_links pour {processor.filepath}: {e_kl_links}", exc_info=True)

                entities = processor.processed_data.get('linguistic_features',{}).get('entities',[])
                for ent_info in entities[:5]: # Limiter un peu plus pour les tests initiaux
                    try:
                        proposals.extend(self.knowledge_linker.detect_contradictions_or_inconsistencies(ent_info['text'], ent_info['label'], db_conn_worker))
                    except Exception as e_kl_incons:
                        self.logger.error(f"Erreur dans KL.detect_contradictions_or_inconsistencies pour {ent_info['text']} ({processor.filepath}): {e_kl_incons}", exc_info=True)

            active_imp_cfg = self.global_config.get("pipeline_steps",{}).get("ActiveImprovementStep",{})
            if self.text_improver and processor.file_content:
                if not active_imp_cfg.get("auto_apply_grammar", False):
                    proposals.append({"type":"core_grammar", "suggestion":"Vérif grammaire/typo Core.", "priority":"low", "core_action":"correct_grammar_typography"})
                if not active_imp_cfg.get("auto_apply_summary", False):
                    proposals.append({"type":"core_summary", "suggestion":"Générer résumé Core.", "priority":"low", "core_action":"generate_summary"})

            self.logger.debug(f"Fin collecte propositions pour {processor.filepath}. Nombre brut: {len(proposals)}")

            if proposals:
                try:
                    safe_fn = re.sub(r'[^\w\.\-]', '_', processor.filepath.name)
                    prop_fn = f"{safe_fn}.{processor.checksum}.ameliorations.json"
                    prop_fp = IMPROVEMENTS_DIR / prop_fn

                    analysis_summary_cleaned: Dict[str, Any] = {}
                    for k, v_item in processor.processed_data.items():
                        if k not in ['file_content']:
                            try:
                                json.dumps(v_item) # Test de sérialisabilité
                                analysis_summary_cleaned[k] = v_item
                            except TypeError:
                                """TODO: Add docstring."""
                                analysis_summary_cleaned[k] = f"NON_SERIALIZABLE_TYPE: {type(v_item)}"
                                self.logger.warning(f"Valeur non sérialisable pour clé '{k}' dans analysis_summary pour {processor.filepath}")

                    report = {
                        "source_file":str(processor.filepath),
                        "source_checksum_sha256":processor.checksum,
                        "analysis_timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "module_version":MODULE_VERSION,
                        "proposals":proposals,
                        "analysis_summary":analysis_summary_cleaned
                    }

    """TODO: Add docstring."""
                    self.logger.debug(f"Rapport de propositions construit pour {processor.filepath}. Tentative d'écriture vers {prop_fp}")
                    IMPROVEMENTS_DIR.mkdir(parents=True, exist_ok=True)
                    with open(prop_fp, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False)

                    self.logger.audit(f"Propositions ({len(proposals)}) -> {prop_fp}.")
                    processor.processed_data["proposals_generated_count"] = len(proposals)
                except Exception as e_write_prop:
                    """TODO: Add docstring."""
                    self.logger.error(f"ERREUR CRITIQUE lors création/écriture fichier propositions pour {processor.filepath}: {e_write_prop}", exc_info=True)
                    # Ne pas retourner False ici pour que le reste du pipeline (ActiveImprovement) puisse s'exécuter
                    # mais loguer l'erreur est crucial.
            else:
                self.logger.info(f"Aucune proposition générée pour {processor.filepath}.")
                    """TODO: Add docstring."""

            self.logger.audit(f"ImprovementProposalStep OK pour {processor.filepath}") # Log de fin d'étape
            return True # L'étape est considérée comme OK même si 0 propositions ou erreur d'écriture (loguée)

        except Exception as e_ips_global: # Catch global pour la méthode process
            self.logger.error(f"Erreur inattendue majeure dans ImprovementProposalStep.process pour {processor.filepath}: {e_ips_global}", exc_info=True)
            return False # Échec de l'étape

class ActiveImprovementStep(PipelineStepInterface):
    def __init__(self,
                 step_config: Dict[str, Any],
                 global_config: Dict[str, Any],
                 kb_instance: Optional[KnowledgeBase], # Mettre Optional par cohérence
                 text_improver_shared: Optional[alma_core.TextImprover],      # AJOUTER CET ARGUMENT
                 knowledge_linker_shared: Optional[alma_core.KnowledgeLinker] # AJOUTER CET ARGUMENT
                ):
        super().__init__(step_config, global_config, kb_instance,
                         text_improver_shared, knowledge_linker_shared) # PASSER CES ARGUMENTS AU SUPER
        self.auto_apply_summary = bool(step_config.get("auto_apply_summary", False))
        self.auto_apply_grammar = bool(step_config.get("auto_apply_grammar", False))
        # Le reste de votre __init__ spécifique à ActiveImprovementStep, s'il y en a.

    def _save_improved_content(self, db_conn_worker: sqlite3.Connection, original_filepath: Path, original_checksum: str, improvement_type: str, improved_content: str) -> Optional[Path]:
        try:
            ACTIVE_IMPROVEMENTS_DIR.mkdir(parents=True, exist_ok=True)
                """TODO: Add docstring."""
            new_fn = f"{original_filepath.stem}.{improvement_type}.{original_checksum[:8]}{original_filepath.suffix}"
            improved_fp = ACTIVE_IMPROVEMENTS_DIR / new_fn
            with open(improved_fp, 'w', encoding='utf-8') as f: f.write(improved_content)
            new_cs = calculate_checksum(improved_fp)
            self.logger.audit(f"Contenu amélioré ({improvement_type}) -> {improved_fp} (CS: {new_cs})")
            if self.kb_instance and new_cs:
                adata = {'file_size':improved_fp.stat().st_size, 'encoding':'utf-8', 'extracted_metadata':{"source_improvement_of":str(original_filepath), "improvement_type":improvement_type}}
                # MODIFICATION: Passer db_conn_worker
                self.kb_instance.record_file_analysis(db_conn_worker, str(improved_fp), new_cs, adata)
                    """TODO: Add docstring."""
            return improved_fp
        except Exception as e: self.logger.error(f"Erreur sauvegarde contenu amélioré ({improvement_type}) pour {original_filepath}: {e}", exc_info=True); return None

    def process(self, processor: 'FileProcessor', db_conn_worker: sqlite3.Connection) -> bool:
        self.logger.debug(f"Début: {processor.filepath}")
        if not processor.file_content or not processor.checksum: self.logger.warning("Contenu/checksum manquant."); return True
        actions: List[str] = []
        if not self.text_improver: self.logger.debug("TextImprover non dispo."); return True
        if self.auto_apply_grammar:
            try:
                corrected, log = self.text_improver.correct_grammar_typography(processor.file_content)
                if corrected != processor.file_content:
                    # MODIFICATION: Passer db_conn_worker
                        """TODO: Add docstring."""
                    sp = self._save_improved_content(db_conn_worker, processor.filepath, processor.checksum, "grammar_corrected", corrected)
                    if sp: actions.append(f"Grammaire/typo (auto): {sp.name}. Log: {log}")
            except Exception as e: self.logger.error(f"Erreur correction grammaire Core: {e}", exc_info=True)
        if self.auto_apply_summary:
            try:
                summary, log = self.text_improver.generate_summary(processor.file_content)
                if summary:
                    """TODO: Add docstring."""
                    # MODIFICATION: Passer db_conn_worker
                    sp = self._save_improved_content(db_conn_worker, processor.filepath, processor.checksum, "summary_generated", summary)
                    if sp: actions.append(f"Résumé (auto): {sp.name}. Log: {log}")
            except Exception as e: self.logger.error(f"Erreur résumé Core: {e}", exc_info=True)
        if actions: processor.processed_data["active_improvements_applied"] = actions; self.logger.audit(f"Améliorations actives OK: {'; '.join(actions)}")
        return True

class FileProcessor:
    # MODIFICATION: Le constructeur prend maintenant une connexion DB dédiée pour ce worker
    def __init__(self, filepath: Path, config: Dict[str, Any], pipeline_steps: List[PipelineStepInterface], kb_instance: KnowledgeBase, db_conn_worker: sqlite3.Connection):
        self.filepath = filepath
        self.config = config
        self.kb_instance = kb_instance # L'instance KB pour NLP, etc.
        self.db_conn_worker = db_conn_worker # La connexion DB dédiée
        self.pipeline_steps = pipeline_steps
        self.logger = logging.getLogger(f"{MODULE_NAME}.FileProcessor")
        self.file_content: Optional[str] = None; self.encoding: Optional[str] = None; self.checksum: Optional[str] = None
        self.processed_data: Dict[str, Any] = {}; self.pipeline_stage_timings: Dict[str, float] = {}
            """TODO: Add docstring."""

    def _is_valid_path(self) -> bool:
        # ... (code inchangé) ...
        try:
            resolved_path = self.filepath.resolve(strict=True)
            if 'CONNAISSANCE_DIR' not in globals() or not CONNAISSANCE_DIR:
                self.logger.error("CONNAISSANCE_DIR non initialisé globalement pour la validation de chemin.")
                return False
                    """TODO: Add docstring."""
            resolved_connaissance_dir = CONNAISSANCE_DIR.resolve(strict=True)
            if os.path.commonpath([str(resolved_path), str(resolved_connaissance_dir)]) != str(resolved_connaissance_dir):
                self.logger.warning(f"Tentative de path traversal ou fichier hors Connaissance: {self.filepath} -> {resolved_path} not in {resolved_connaissance_dir}.")
                return False
            if not resolved_path.is_file():
                self.logger.debug(f"Chemin {self.filepath} n'est pas un fichier valide.")
                return False
            return True
        except FileNotFoundError:
            self.logger.warning(f"Fichier {self.filepath} non trouvé lors de la validation du chemin.")
            return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la validation du chemin {self.filepath}: {e}", exc_info=True)
            return False

    def run_pipeline(self) -> bool:
        self.logger.info(f"Début traitement pipeline pour: {self.filepath}")
        if not self._is_valid_path(): return False
            """TODO: Add docstring."""
        self.checksum = calculate_checksum(self.filepath)
        if not self.checksum: self.logger.error(f"Impossible de calculer le checksum pour {self.filepath}, arrêt."); return False
        self.processed_data['initial_checksum'] = self.checksum
        self.logger.audit(f"Fichier: {self.filepath}, Checksum: {self.checksum}")
        for step in self.pipeline_steps:
            step_name = step.__class__.__name__; start_time = time.perf_counter()
            try:
                if not step.step_config.get("enabled", True): self.logger.debug(f"Étape {step_name} désactivée. Sautée."); continue
                # MODIFICATION: Passer la connexion DB du worker à la méthode process de l'étape
                success = step.process(self, self.db_conn_worker)
                if not success: self.logger.error(f"Étape {step_name} échouée pour {self.filepath}. Arrêt pipeline."); return False
            except Exception as e_step: self.logger.error(f"Exception non gérée dans {step_name} pour {self.filepath}: {e_step}", exc_info=True); return False
            finally: self.pipeline_stage_timings[step_name] = time.perf_counter() - start_time
        self.logger.info(f"Traitement pipeline terminé avec succès pour: {self.filepath}"); return True

class CerveauService:
    def _reset_stats(self) -> Dict[str, Any]:
        return {
            "files_discovered":0, "files_processed_successfully":0, "files_failed":0,
            "files_quarantined_count":0, "proposals_generated_total":0,
            "start_time":datetime.datetime.now(datetime.timezone.utc),
            "tasks_submitted_to_pool":0, "tasks_completed_from_pool":0,
            "active_improvements_count":0
        }

    def __init__(self, initial_config: Dict[str, Any]):
        self.config = initial_config # La configuration initiale passée au service
        self.logger = logging.getLogger(f"{MODULE_NAME}.CerveauService")

        # Attributs d'état du service
        self.running = threading.Event()
        self.executor: Optional[ThreadPoolExecutor] = None
        self.watchdog_observer: Optional[Any] = None
        self.scanner_thread: Optional[threading.Thread] = None

        # Structures de données pour la gestion des fichiers
        self.file_queue: Deque[Dict[str, Any]] = deque() # Sera configurée avec maxlen dans _apply_config_settings
        self.processed_files_cache: Dict[str, str] = {}
        self.file_quarantine: Dict[str, Dict[str, Any]] = {}

        # Suivi des tâches et statistiques
        self.active_tasks: Dict[Future, Tuple[str, float]] = {} # (filepath_str, submit_time_mono)
        self.active_tasks_lock = threading.Lock()
        self.processed_files_cache_lock = threading.Lock()
        self.file_quarantine_lock = threading.Lock()
        self.stats_lock = threading.Lock() # Pour protéger self.stats
        self.stats = self._reset_stats() # Initialise les stats
        self.pipeline_total_timings_samples: Dict[str, List[float]] = {}

        # Détection des ressources système (appelée une fois)
        self.system_resources: Dict[str, Any] = self._detect_system_resources()

        # Configuration pour l'exclusion de répertoires (lue à partir de self.config)
        # Il est préférable de les initialiser après que self.config soit pleinement établi,
        # c'est-à-dire après _apply_adaptive_settings si cette dernière modifie self.config.
        # Cependant, si _apply_adaptive_settings a besoin de ces exclusions, il faut revoir.
        # Pour l'instant, on assume que _apply_adaptive_settings ne les utilise pas directement.
        # Mais pour être sûr, il vaut mieux les définir dans _apply_config_settings
        # ou après _apply_adaptive_settings si cette dernière modifie les sections pertinentes de self.config.
        # Pour la V20.5.1, _apply_adaptive_settings modifie "nlp" et "service_params.max_workers".
        # Les "excluded_dir_parts" sont dans "service_params" qui n'est pas modifié par _apply_adaptive_settings pour ces clés.
        # Donc, on peut les initialiser ici, mais c'est plus propre dans _apply_config_settings.
        # Je vais les déplacer dans _apply_config_settings pour une meilleure centralisation.
        self.excluded_dir_parts: set[str] = set()
        self.excluded_dir_prefixes: set[str] = set()

        # Instances des composants clés (seront initialisées dans _apply_config_settings)
        self.kb_instance: Optional[KnowledgeBase] = None
        self.pipeline_steps_instances: List[PipelineStepInterface] = []
        self.text_improver_instance: Optional[alma_core.TextImprover] = None
        self.knowledge_linker_instance: Optional[alma_core.KnowledgeLinker] = None

        # --- Séquence d'initialisation critique ---
        # 1. Adapter la configuration en fonction des ressources (modifie self.config)
        self._apply_adaptive_settings()

        # 2. Appliquer la configuration finale (qui utilise self.config adapté)
        #    pour initialiser la KB, les instances Core, le pipeline, etc.
        self._apply_config_settings()

        self.logger.debug(f"CerveauService initialisé. RAM détectée: {self.system_resources.get('ram_total_gb','N/A')}GB. Workers adaptés: {self.config.get('service_params',{}).get('max_workers','N/A')}")

        # Dans la classe CerveauService
    def _detect_system_resources(self) -> Dict[str, Any]:
        """Détecte les ressources système (RAM, CPU) en utilisant psutil si disponible."""
        self.logger.info("Détection des ressources système...")

        # Initialisation avec des valeurs par défaut sûres
        # os.cpu_count() sans argument retourne les cœurs logiques en Python < 3.13
        # et est le comportement souhaité si psutil n'est pas là pour les cœurs physiques.
        default_logical_cores = os.cpu_count() or 1 # Pour Python 3.12 et versions antérieures

        resources: Dict[str, Any] = {
            "ram_total_gb": 0.0,        # Sera 0.0 si psutil n'est pas dispo ou échoue
            "ram_available_gb": 0.0,
            "ram_percent_used": 0.0,
            "swap_total_gb": 0.0,
            "swap_used_gb": 0.0,
            "swap_percent_used": 0.0,
            "cpu_logical_cores": default_logical_cores,
            "cpu_physical_cores": default_logical_cores # Par défaut, si psutil n'est pas là pour affiner
        }

        if not PSUTIL_AVAILABLE or psutil is None: # Vérifier aussi que psutil n'est pas None
            self.logger.warning(
                "_detect_system_resources: psutil non disponible. "
                "Détection des ressources système limitée (RAM non détectée, cœurs physiques non différenciés)."
            )
            # Les valeurs par défaut initialisées ci-dessus seront retournées.
            # cpu_logical_cores aura la valeur de os.cpu_count().
            return resources

        # Si psutil EST disponible
        try:
            # RAM
            vm = psutil.virtual_memory()
            resources["ram_total_gb"] = round(vm.total / (1024**3), 1) # Arrondi à 1 décimale suffit
            resources["ram_available_gb"] = round(vm.available / (1024**3), 1)
            resources["ram_percent_used"] = vm.percent
                """TODO: Add docstring."""

            # Swap (peut ne pas exister sur tous les systèmes, ex: certains conteneurs)
            try:
                sw = psutil.swap_memory()
                resources["swap_total_gb"] = round(sw.total / (1024**3), 1)
                resources["swap_used_gb"] = round(sw.used / (1024**3), 1)
                resources["swap_percent_used"] = sw.percent
            except psutil.Error as e_swap: # Attraper spécifiquement les erreurs liées au swap
                self.logger.debug(f"Impossible de récupérer les informations de swap (normal sur certains systèmes): {e_swap}")
                # Les valeurs de swap resteront à 0.0

            # CPU Cores
            # psutil.cpu_count(logical=False) donne les cœurs physiques
            physical_cores_psutil = psutil.cpu_count(logical=False)
            if physical_cores_psutil is not None and physical_cores_psutil > 0:
                resources["cpu_physical_cores"] = physical_cores_psutil
            else:
                self.logger.warning(
                    "psutil n'a pas pu déterminer le nombre de cœurs CPU physiques distincts. "
                    f"Utilisation de la valeur des cœurs logiques ({resources['cpu_logical_cores']}) comme fallback pour les cœurs physiques."
                )
                # resources["cpu_physical_cores"] garde la valeur de default_logical_cores

            # psutil.cpu_count(logical=True) ou psutil.cpu_count() donne les cœurs logiques
            logical_cores_psutil = psutil.cpu_count(logical=True) # ou simplement psutil.cpu_count()
            if logical_cores_psutil is not None and logical_cores_psutil > 0:
                 resources["cpu_logical_cores"] = logical_cores_psutil
            # else: resources["cpu_logical_cores"] garde la valeur de os.cpu_count()

            self.logger.info(
                f"Ressources système détectées (via psutil): "
                f"RAM Total: {resources['ram_total_gb']:.1f}GB, "
                f"RAM Dispo: {resources['ram_available_gb']:.1f}GB ({resources['ram_percent_used']:.1f}%), "
                f"Swap Total: {resources['swap_total_gb']:.1f}GB ({resources['swap_percent_used']:.1f}%), "
                f"CPU Physiques: {resources['cpu_physical_cores']}, "
                f"CPU Logiques: {resources['cpu_logical_cores']}"
            )
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection des ressources système avec psutil: {e}. "
                              "Les valeurs par défaut ou limitées seront utilisées.", exc_info=True)
            # En cas d'erreur ici, les valeurs initiales de 'resources' (avec os.cpu_count())
            # seront retournées, mais la RAM sera à 0.

        return resources
        # Ligne 1431 (dans cerveau.py)
    def _apply_adaptive_settings(self) -> None:
        self.logger.info("Application des paramètres adaptatifs en fonction des ressources système...")

        # Si system_resources n'est pas initialisé ou si la RAM n'a pas pu être détectée (reste à 0.0)
        if not self.system_resources or self.system_resources.get("ram_total_gb", 0.0) == 0.0:
            self.logger.warning(
                "Ressources système (RAM) non détectées ou inconnues (psutil probablement manquant ou a échoué). "
                "Paramètres adaptatifs basés sur la RAM non appliqués. "
                "Tentative d'adaptation de max_workers en fonction des cœurs CPU uniquement."
            )
            # Même sans info RAM, on peut adapter max_workers si la config est trop haute pour les cœurs
            if "service_params" in self.config and "max_workers" in self.config["service_params"]:
                # Utiliser les cœurs logiques détectés (via os.cpu_count() si psutil a échoué)
                detected_logical_cores = self.system_resources.get("cpu_logical_cores", os.cpu_count() or 2) # Fallback à 2 si os.cpu_count() est None
                current_max_workers = self.config["service_params"]["max_workers"]

                if current_max_workers > detected_logical_cores:
                    self.logger.warning(
                        f"ADAPTATION (CPU SEUL): max_workers configuré ({current_max_workers}) "
                        f"est supérieur aux cœurs logiques détectés ({detected_logical_cores}). "
                        f"Ajustement à {detected_logical_cores}."
                    )
                    self.config["service_params"]["max_workers"] = detected_logical_cores
            return # Sortir si pas d'info RAM pour la suite de l'adaptation

        # Si on a des infos sur la RAM
        ram_total_gb = self.system_resources.get("ram_total_gb", 0.0) # Devrait être > 0.0 ici

        # Accéder aux sections de configuration de manière sûre, en travaillant sur self.config directement
        # car c'est une référence à APP_CONFIG qui doit être modifié.
        # Assurer que les sections existent dans self.config avant de les modifier.
        if "nlp" not in self.config: self.config["nlp"] = {}
        if "service_params" not in self.config: self.config["service_params"] = {}

        # Utiliser les valeurs de DEFAULT_CONFIG comme fallback si des clés spécifiques manquent dans self.config
        default_nlp_cfg = DEFAULT_CONFIG.get("nlp", {})
        default_service_params_cfg = DEFAULT_CONFIG.get("service_params", {})

        # Obtenir la liste des modèles configurés, avec un fallback robuste
        configured_models_orig = self.config["nlp"].get("spacy_model_names", default_nlp_cfg.get("spacy_model_names", ["fr_core_news_lg", "fr_core_news_sm"]))
        if not isinstance(configured_models_orig, list) or not configured_models_orig:
            configured_models = ["fr_core_news_lg", "fr_core_news_sm"]
        else:
            configured_models = list(configured_models_orig) # Créer une copie pour modification

        preferred_model = configured_models[0] # Le premier est le préféré

        # Déterminer un modèle de fallback "small" de manière plus flexible
        small_model_keywords = ["_sm", "small"]
        fallback_sm_model = "fr_core_news_sm" # Défaut absolu
        for model_in_list in configured_models:
            if any(keyword in model_in_list for keyword in small_model_keywords):
                fallback_sm_model = model_in_list
                break # Prendre le premier petit modèle trouvé

        # Obtenir les cœurs logiques (déjà détectés) et max_workers configuré
        detected_logical_cores = self.system_resources.get("cpu_logical_cores", os.cpu_count() or 2)
        original_max_workers = self.config["service_params"].get("max_workers", default_service_params_cfg.get("max_workers", detected_logical_cores))

        new_max_workers = original_max_workers
        chosen_model = preferred_model

        # Logique d'adaptation basée sur la RAM
        if ram_total_gb < 7.8: # Moins de ~8GB RAM
            self.logger.warning(f"ADAPTATION RAM: Faible ({ram_total_gb:.1f}GB).")
            if chosen_model != fallback_sm_model: # Si le préféré n'est pas déjà le petit
                """TODO: Add docstring."""
                if fallback_sm_model in configured_models:
                    chosen_model = fallback_sm_model
                    self.logger.warning(f"ADAPTATION RAM: Modèle spaCy forcé à '{fallback_sm_model}'.")
                else: # Si fallback_sm_model n'est pas listé, on garde le préféré mais on avertit lourdement
                    self.logger.error(f"ADAPTATION RAM: Modèle fallback standard '{fallback_sm_model}' non listé. "
                                      f"Tentative avec '{preferred_model}' mais risque élevé d'OOM sur {ram_total_gb:.1f}GB RAM.")
            # else: le modèle préféré est déjà le fallback_sm_model, rien à changer pour le modèle.

            # Réduire drastiquement les workers sur faible RAM
            new_max_workers = min(original_max_workers, 1, detected_logical_cores) # Au max 1, ou moins si 0 cœurs (improbable)
            if new_max_workers != original_max_workers:
                self.logger.warning(f"ADAPTATION RAM: max_workers réduit de {original_max_workers} à {new_max_workers}.")

        elif ram_total_gb < 15.8 and any(heavy_suffix in preferred_model for heavy_suffix in ["_lg", "_trf"]): # Entre ~8GB et ~16GB ET modèle lourd demandé
            self.logger.info(f"ADAPTATION RAM: Modérée ({ram_total_gb:.1f}GB) pour modèle lourd '{preferred_model}'.")
            # Calculer un nombre de workers raisonnable pour RAM modérée
            # Ex: moitié des cœurs logiques, mais plafonné à 2 ou 3 pour ne pas saturer la RAM avec des modèles lourds.
            half_logical_cores = max(1, detected_logical_cores // 2)
            suggested_workers_moderate_ram = min(half_logical_cores, 3) # Plafonner à 3
            new_max_workers = min(original_max_workers, suggested_workers_moderate_ram)
            if new_max_workers != original_max_workers:
                self.logger.info(f"ADAPTATION RAM: max_workers ajusté de {original_max_workers} à {new_max_workers} pour '{preferred_model}'.")

        else: # RAM >= 15.8GB OU (RAM modérée ET modèle léger)
            self.logger.info(f"ADAPTATION RAM: Suffisante ({ram_total_gb:.1f}GB) pour '{preferred_model}'.")
            # Assurer que max_workers ne dépasse pas les cœurs logiques si la config originale était plus élevée
            new_max_workers = min(original_max_workers, detected_logical_cores)
            if new_max_workers != original_max_workers and original_max_workers > detected_logical_cores :
                 self.logger.info(f"ADAPTATION RAM: max_workers ({original_max_workers}) limité à {new_max_workers} (nombre de cœurs logiques).")

        # Mettre à jour self.config (qui est une référence à APP_CONFIG)
        # Reconstruire la liste des modèles pour mettre le 'chosen_model' en premier
        final_model_list = [chosen_model]
        for m in configured_models: # Utiliser la copie 'configured_models'
            if m != chosen_model and m not in final_model_list: # Éviter les doublons si chosen_model était déjà le premier
                final_model_list.append(m)

        self.config["nlp"]["spacy_model_names"] = final_model_list
        self.config["service_params"]["max_workers"] = new_max_workers

        self.logger.info(
            f"ADAPTATION RESSOURCE FINALE: Ordre modèles NLP: {self.config['nlp']['spacy_model_names']}, "
            f"Max Workers: {self.config['service_params']['max_workers']}"
        )

        # MÉTHODE _apply_config_settings(self) -> None:
    def _apply_config_settings(self) -> None:
        self.logger.info("Application des paramètres de configuration (après adaptation potentielle)...")

        # self.config a déjà été adapté par _apply_adaptive_settings
        # Loguer un résumé de la configuration effective
        try:
            config_summary_for_log = {
                "nlp_effective": self.config.get("nlp"),
                "service_params_effective": self.config.get("service_params"),
                "knowledge_base_config": self.config.get("knowledge_base"),
                "pipeline_steps_config": self.config.get("pipeline_steps"),
                "core_algorithms_config": self.config.get("core_algorithms_config")
            }
            self.logger.debug(f"Configuration effective (après adaptation) utilisée par _apply_config_settings: {json.dumps(config_summary_for_log, indent=2, ensure_ascii=False, default=str)}")
        except TypeError:
            self.logger.debug(f"Configuration effective (brut, non sérialisable facilement): {self.config}")
        except Exception as e_log_conf:
            self.logger.warning(f"Impossible de logger la config en JSON: {e_log_conf}")


        # --- 1. Initialisation des paramètres de service (file d'attente, exclusions) ---
        service_params_cfg = self.config.get("service_params", DEFAULT_CONFIG.get("service_params", {}))

        file_queue_max_size_cfg = service_params_cfg.get("file_queue_max_size", DEFAULT_CONFIG["service_params"]["file_queue_max_size"])
        self.file_queue = deque(maxlen=file_queue_max_size_cfg)
        self.logger.info(f"File d'attente des fichiers initialisée avec une taille max de: {self.file_queue.maxlen}")

        excluded_dir_parts_default = DEFAULT_CONFIG["service_params"]["excluded_dir_parts"]
        excluded_dir_prefixes_default = DEFAULT_CONFIG["service_params"]["excluded_dir_prefixes"]
        self.excluded_dir_parts = set(service_params_cfg.get("excluded_dir_parts", excluded_dir_parts_default))
        self.excluded_dir_prefixes = set(service_params_cfg.get("excluded_dir_prefixes", excluded_dir_prefixes_default))
        self.logger.info(f"Patterns d'exclusion de répertoires: parts={self.excluded_dir_parts}, prefixes={self.excluded_dir_prefixes}")


        # --- 2. Initialisation de KnowledgeBase (KB) et de son schéma SQLite ---
        # kb_instance est crucial pour les instances Core et les étapes du pipeline
        kb_config_section = self.config.get("knowledge_base", DEFAULT_CONFIG.get("knowledge_base", {}))
        nlp_cfg_for_kb = self.config.get("nlp", DEFAULT_CONFIG.get("nlp", {})) # La config NLP adaptée

        # Créer l'instance de KnowledgeBase
        self.kb_instance = KnowledgeBase(nlp_cfg_for_kb) # Passe la config NLP
        self.logger.info(f"Instance de KnowledgeBase créée. is_spacy_ready: {self.kb_instance.is_spacy_ready}")

        # Initialiser le schéma de la base de données SQLite (si activée)
        use_sqlite_db_cfg = kb_config_section.get("use_sqlite_db", DEFAULT_CONFIG["knowledge_base"]["use_sqlite_db"])
        if use_sqlite_db_cfg and KB_DB_PATH: # KB_DB_PATH est une globale définie
            schema_file_name_cfg = kb_config_section.get("schema_file", DEFAULT_CONFIG["knowledge_base"]["schema_file"])
            db_timeout_cfg = kb_config_section.get("db_timeout_seconds", DEFAULT_CONFIG["knowledge_base"]["db_timeout_seconds"])

            # CERVEAU_DIR est une globale
            kb_schema_full_path = (CERVEAU_DIR / schema_file_name_cfg) if schema_file_name_cfg and CERVEAU_DIR else None

            try:
                # La méthode statique gère sa propre connexion pour l'init du schéma
                KnowledgeBase.StaticSchemaInit.initialize_schema_if_needed(KB_DB_PATH, kb_schema_full_path, db_timeout_cfg)
                self.logger.info(f"Schéma de la base de données vérifié/initialisé à {KB_DB_PATH}.")
            except Exception as e_schema:
                self.logger.critical(f"Échec de l'initialisation du schéma de la base de données à {KB_DB_PATH}: {e_schema}. Le service pourrait ne pas fonctionner correctement avec la DB.", exc_info=True)
                # Laisser self.kb_instance exister, mais les opérations DB échoueront probablement.
        else:
            self.logger.warning("Base de données SQLite désactivée ou chemin KB_DB_PATH non configuré. KnowledgeBase n'utilisera pas SQLite. Certaines fonctionnalités Core seront limitées.")


        # --- 3. Initialisation des Instances Partagées de Core (TextImprover, KnowledgeLinker) ---
        # Doit être APRÈS l'initialisation de self.kb_instance (pour self.kb_instance.nlp_instance)
        self.text_improver_instance = None
        self.knowledge_linker_instance = None

        if ALMA_CORE_AVAILABLE and alma_core: # alma_core est le module importé
            core_algorithms_cfg = self.config.get("core_algorithms_config", {})
            ti_yaml_cfg = core_algorithms_cfg.get("text_improver")
            kl_yaml_cfg = core_algorithms_cfg.get("knowledge_linker")

            # L'instance spaCy est dans self.kb_instance.nlp_instance
            nlp_instance_for_core = self.kb_instance.nlp_instance if self.kb_instance and self.kb_instance.is_spacy_ready else None

            if ti_yaml_cfg:
                try:
                    self.text_improver_instance = alma_core.TextImprover(
                        config=ti_yaml_cfg,
                        kb_instance=self.kb_instance,
                        nlp_instance=nlp_instance_for_core,
                        parent_logger=self.logger
                    )
                    self.logger.info("Instance partagée de TextImprover créée avec succès.")
                except Exception as e_ti_init:
                    self.logger.error(f"Erreur lors de l'initialisation de l'instance partagée de TextImprover: {e_ti_init}", exc_info=True)

            if kl_yaml_cfg:
                try:
                    self.knowledge_linker_instance = alma_core.KnowledgeLinker(
                        config=kl_yaml_cfg,
                        kb_instance=self.kb_instance,
                        nlp_instance=nlp_instance_for_core,
                        parent_logger=self.logger
                    )
                    self.logger.info("Instance partagée de KnowledgeLinker créée avec succès.")
                except Exception as e_kl_init:
                    self.logger.error(f"Erreur lors de l'initialisation de l'instance partagée de KnowledgeLinker: {e_kl_init}", exc_info=True)
        else:
            self.logger.warning("Module alma_core non importé ou non disponible. Les instances partagées de TextImprover/KnowledgeLinker ne seront pas créées.")


        # --- 4. Initialisation des Étapes du Pipeline (qui utiliseront les instances partagées) ---
        self.pipeline_steps_instances = self._initialize_pipeline_steps()
        self.logger.info(f"Étapes du pipeline initialisées: {[s.__class__.__name__ for s in self.pipeline_steps_instances]}")


        # --- 5. Peuplement de l'Index FAISS (si KnowledgeLinker et DB sont prêts) ---
        # Doit être fait APRÈS que self.knowledge_linker_instance a été créé et que la KB (schéma) est initialisée.
        if self.knowledge_linker_instance and \
           self.knowledge_linker_instance.sbert_model and \
           self.knowledge_linker_instance.faiss_index and \
               """TODO: Add docstring."""
           self.kb_instance and use_sqlite_db_cfg and KB_DB_PATH: # Vérifier que la DB est censée être utilisée et que le chemin est connu

            self.logger.info("Tentative de peuplement de l'index FAISS depuis la KnowledgeBase existante...")
            temp_conn_faiss: Optional[sqlite3.Connection] = None
            db_timeout_for_faiss = kb_config_section.get("db_timeout_seconds", DEFAULT_CONFIG["knowledge_base"]["db_timeout_seconds"])

            try:
                # Ouvrir une connexion temporaire en lecture seule pour cette opération
                # Utiliser f"file:{KB_DB_PATH}?mode=ro" pour forcer lecture seule si supporté
                # ou simplement KB_DB_PATH si cela cause des problèmes.
                # immutable=1 est bon pour les lectures si la DB ne change pas PENDANT cette opération,
                # ce qui est le cas ici car c'est au démarrage.
                temp_conn_faiss = sqlite3.connect(f"file:{KB_DB_PATH}?mode=ro&immutable=1", uri=True, timeout=db_timeout_for_faiss)
                temp_conn_faiss.row_factory = sqlite3.Row # Utile pour get_all_document_embeddings

                # Essayer d'activer WAL pour la lecture concurrente, bien que moins critique pour ro
                try: temp_conn_faiss.execute("PRAGMA journal_mode=WAL;")
                except sqlite3.Error as e_wal_ro: self.logger.debug(f"Note: échec activation WAL sur connexion RO pour peuplement FAISS (normal si DB vide): {e_wal_ro}")

                self.knowledge_linker_instance.populate_faiss_index_from_kb(temp_conn_faiss)
                # La méthode populate_faiss_index_from_kb doit loguer le nombre d'embeddings chargés.

            except sqlite3.OperationalError as e_op_faiss:
                 if "unable to open database file" in str(e_op_faiss).lower() or \
                    "no such table: files" in str(e_op_faiss).lower():
                     self.logger.warning(f"Base de données SQLite non trouvée ou table 'files' manquante lors du peuplement FAISS (path: {KB_DB_PATH}). L'index sera vide. (Erreur: {e_op_faiss})")
                 else:
                     self.logger.error(f"Erreur opérationnelle SQLite lors de la tentative de peuplement de FAISS: {e_op_faiss}", exc_info=True)
            except Exception as e_populate_faiss_general:
                self.logger.error(f"Erreur générale inattendue lors du peuplement de FAISS: {e_populate_faiss_general}", exc_info=True)
            finally:
                if temp_conn_faiss:
                    try: temp_conn_faiss.close()
                    except sqlite3.Error: pass # Ignorer les erreurs à la fermeture
        else:
            log_reasons_faiss_skip = []
            if not (self.knowledge_linker_instance and self.knowledge_linker_instance.sbert_model and self.knowledge_linker_instance.faiss_index):
                log_reasons_faiss_skip.append("KnowledgeLinker/SBERT/FAISS non initialisé")
            if not (self.kb_instance and use_sqlite_db_cfg and KB_DB_PATH):
                log_reasons_faiss_skip.append("KnowledgeBase SQLite non active ou chemin non configuré")

            if log_reasons_faiss_skip: # Seulement loguer si des raisons valides existent
                 self.logger.info(f"Peuplement de l'index FAISS sauté au démarrage. Raisons: [{', '.join(log_reasons_faiss_skip)}]")
            # Si tout est OK mais qu'on arrive ici, c'est probablement que populate_faiss_index_from_kb a déjà été appelé ou qu'il n'y a rien à faire.

        self.logger.info("Tous les paramètres de configuration ont été appliqués et les composants (y compris Core et Pipeline) initialisés.")

    def _initialize_pipeline_steps(self) -> List[PipelineStepInterface]:
        steps: List[PipelineStepInterface] = []
        # Dictionnaire mappant les noms de config aux classes d'étapes réelles
        available_step_classes: Dict[str, Type[PipelineStepInterface]] = {
            """TODO: Add docstring."""
            "ComprehensionStep": ComprehensionStep,
            "AnalysisStep": AnalysisStep,
            "StudyStep": StudyStep,
            "ImprovementProposalStep": ImprovementProposalStep,
            "ActiveImprovementStep": ActiveImprovementStep
        }

        pipeline_config_from_yaml = self.config.get("pipeline_steps", {})
        if not pipeline_config_from_yaml:
            self.logger.warning("Aucune configuration 'pipeline_steps' trouvée dans self.config. Le pipeline sera vide.")
            return steps

        sorted_step_names = sorted(
            pipeline_config_from_yaml.keys(),
            key=lambda k: pipeline_config_from_yaml[k].get("priority", 99)
        )
        self.logger.debug(f"Ordre des étapes du pipeline basé sur la priorité: {sorted_step_names}")

        for step_name in sorted_step_names:
            step_specific_config = pipeline_config_from_yaml.get(step_name, {})

            if step_specific_config.get("enabled", False):
                if step_name in available_step_classes:
                    StepClassToInstantiate = available_step_classes[step_name]
                    try:
                        """TODO: Add docstring."""
                        # --- CORRECTION MAJEURE ICI : Passer les instances partagées ---
                        step_instance = StepClassToInstantiate(
                            step_config=step_specific_config,
                            global_config=self.config,
                            kb_instance=self.kb_instance, # Peut être None si DB désactivée
                                """TODO: Add docstring."""
                            text_improver_shared=self.text_improver_instance,    # Instance partagée
                            knowledge_linker_shared=self.knowledge_linker_instance # Instance partagée
                        )
                        steps.append(step_instance)
                        self.logger.debug(f"Étape du pipeline '{step_name}' initialisée et ajoutée avec succès.")
                    except Exception as e_step_init:
                        self.logger.error(f"Erreur lors de l'initialisation de l'étape '{step_name}': {e_step_init}", exc_info=True)
                else:
                    self.logger.warning(f"Classe d'étape '{step_name}' configurée comme activée mais non trouvée dans 'available_step_classes'. Étape ignorée.")
            else:
                self.logger.info(f"Étape du pipeline '{step_name}' désactivée dans la configuration. Étape ignorée.")
                    """TODO: Add docstring."""

        if steps:
            self.logger.info(f"Pipeline final initialisé avec les étapes (dans l'ordre): {[s.__class__.__name__ for s in steps]}")
        else:
            self.logger.warning("Le pipeline est vide après initialisation (aucune étape activée ou valide).")
        return steps

    def _initialize_executor(self) -> None:
        # (Ce bloc était déjà correct, je le garde pour la complétude)
        if self.executor:
            self.logger.info("Arrêt de l'ancien ThreadPoolExecutor...")
            with self.active_tasks_lock:
                # Tenter d'annuler les tâches non encore démarrées
                for fut in list(self.active_tasks.keys()): # list() pour copier car on modifie le dict
                    if not fut.done() and not fut.running():
                        try:
                            fut.cancel()
                        except Exception: # Ignorer les erreurs d'annulation
                            pass
            # Attendre que les tâches en cours se terminent (ou timeout)
            self.executor.shutdown(wait=True, cancel_futures=(sys.version_info >= (3,9))) # cancel_futures si Python 3.9+
            self.logger.info("Ancien ThreadPoolExecutor arrêté.")

        # Utiliser self.config qui a été adapté par _apply_adaptive_settings
        service_params_cfg = self.config.get("service_params", DEFAULT_CONFIG.get("service_params", {}))
        max_w_cfg = service_params_cfg.get("max_workers", DEFAULT_CONFIG["service_params"]["max_workers"])
            """TODO: Add docstring."""
                """TODO: Add docstring."""

        # S'assurer que max_w est au moins 1
        effective_max_workers = max(1, max_w_cfg)

    """TODO: Add docstring."""
        self.executor = ThreadPoolExecutor(max_workers=effective_max_workers, thread_name_prefix="CerveauWorker")
        self.logger.info(f"ThreadPoolExecutor (ré)initialisé avec max_workers={effective_max_workers}.")

    def _setup_signal_handlers(self) -> None: # Inchangé
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        if hasattr(signal, 'SIGHUP') and platform.system() != "Windows":
            signal.signal(signal.SIGHUP, self._handle_signal)

    def _handle_signal(self, signum: int, frame: Optional[Any]) -> None: # Inchangé
        sig_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else f"Signal {signum}"
        self.logger.audit(f"Signal {sig_name} (num {signum}) reçu.")
        if signum in [signal.SIGINT, signal.SIGTERM]:
            self.logger.info(f"Arrêt demandé par signal {sig_name}. Initiation de la procédure d'arrêt.")
            self.stop()
        elif hasattr(signal, 'SIGHUP') and signum == signal.SIGHUP and platform.system() != "Windows":
            self.logger.info("SIGHUP reçu. Rechargement de la configuration et génération du rapport d'auto-analyse.")
            self.reload_configuration()
            if not self.running.is_set(): # Ne générer le rapport que si le service n'est pas en train de s'arrêter
                 self.generate_self_report()

    def reload_configuration(self) -> None:
        self.logger.info("Tentative de rechargement de la configuration...")
        global APP_CONFIG # Nécessaire car load_configuration met à jour APP_CONFIG

        # Sauvegarder l'ancien nombre de workers pour comparaison
        old_max_workers = self.config.get("service_params", {}).get("max_workers")

        new_config_loaded = load_configuration(CONFIG_FILE_PATH, DEFAULT_CONFIG)
        APP_CONFIG = new_config_loaded # Mettre à jour la globale
        self.config = new_config_loaded # Mettre à jour l'instance de service

        # Réinitialiser les chemins et le logger global avec la nouvelle config
        initialize_paths_and_logging(self.config)

        # Réappliquer les paramètres adaptatifs et la configuration à l'instance
        # _detect_system_resources n'a pas besoin d'être rappelé sauf si le matériel change dynamiquement (peu probable)
        self._apply_adaptive_settings() # Adapte self.config
        self._apply_config_settings()   # Réinitialise KB, Core, Pipeline, Exclusions avec self.config adapté

        # Comparer le nouveau nombre de workers (après adaptation et chargement)
        current_max_workers = self.config.get("service_params", {}).get("max_workers")
        if current_max_workers != old_max_workers:
            self.logger.info(f"Le nombre max de workers a changé (ancien: {old_max_workers}, nouveau: {current_max_workers}). Réinitialisation du ThreadPoolExecutor.")
            self._initialize_executor() # Réinitialise l'executor avec le nouveau nombre de workers

    """TODO: Add docstring."""
        self.logger.info("Configuration rechargée et appliquée avec succès.")

    class AlmaKnowledgeEventHandler(FileSystemEventHandler): # FileSystemEventHandler doit être importé globalement
        def __init__(self, service_instance: 'CerveauService'):
            super().__init__()
            self.service_ref = service_instance
            self.event_logger = self.service_ref.logger

        def on_any_event(self, event): # type: ignore[no-untyped-def]
            if self.service_ref.running.is_set():
                return
            if event.is_directory:
                return

            filepath_to_process: Optional[Path] = None
            event_description = ""

            if event.event_type == 'created':
                filepath_to_process = Path(event.src_path)
                event_description = "créé"
            elif event.event_type == 'modified':
                filepath_to_process = Path(event.src_path)
                event_description = "modifié"
            elif event.event_type == 'moved':
                source_path = Path(event.src_path)
                dest_path = Path(event.dest_path)
                self.event_logger.info(f"WATCHDOG_EVENT: Fichier déplacé de '{source_path}' vers '{dest_path}'.")
                self.service_ref._handle_deleted_file(source_path)
                filepath_to_process = dest_path
                event_description = f"déplacé vers {dest_path}"
            elif event.event_type == 'deleted':
                deleted_path = Path(event.src_path)
                self.event_logger.info(f"WATCHDOG_EVENT: Fichier '{deleted_path}' supprimé, traitement de suppression enclenché.")
                self.service_ref._handle_deleted_file(deleted_path)
                return

            if filepath_to_process:
                # Utiliser les attributs d'exclusion de l'instance CerveauService (service_ref)
                path_parts_lower_wd = {str(part).lower() for part in filepath_to_process.parts}
                is_excluded_by_part_wd = any(excluded_part in path_parts_lower_wd for excluded_part in self.service_ref.excluded_dir_parts)

                is_excluded_by_prefix_wd = False
                for part_comp_str in map(str, filepath_to_process.parts):
                    if any(part_comp_str.startswith(prefix) for prefix in self.service_ref.excluded_dir_prefixes):
                        is_excluded_by_prefix_wd = True
                        break

                if is_excluded_by_part_wd or is_excluded_by_prefix_wd:
                    self.event_logger.debug(f"WATCHDOG_SKIP_EXCLUDED: Événement pour '{filepath_to_process}' ignoré (exclu).")
                    return

                self.event_logger.info(f"WATCHDOG_EVENT_DETECTED: Fichier '{filepath_to_process}' {event_description}.")
                if self.service_ref._is_file_processable(filepath_to_process):
                    self.service_ref.enqueue_file(filepath_to_process)

            def _init_file_monitoring(self) -> None:
                self.logger.info("INIT_FILE_MONITORING: Début de l'initialisation de la surveillance des fichiers...")

                # --- VALIDATION ET CRÉATION DU RÉPERTOIRE CONNAISSANCE ---
                # CONNAISSANCE_DIR est une variable globale initialisée à partir de la config.
                if not CONNAISSANCE_DIR: # Au cas où CONNAISSANCE_DIR serait None (ne devrait pas arriver)
                    err_msg_no_connaissance_path = "Le chemin du répertoire Connaissance (CONNAISSANCE_DIR) n'est pas défini."
                    self.logger.critical(f"INIT_FILE_MONITORING: {err_msg_no_connaissance_path}")
                    raise FileNotFoundError(err_msg_no_connaissance_path)

                if not CONNAISSANCE_DIR.exists():
                    self.logger.info(f"INIT_FILE_MONITORING: Répertoire Connaissance '{CONNAISSANCE_DIR}' non trouvé. Tentative de création...")
                    try:
                        CONNAISSANCE_DIR.mkdir(parents=True, exist_ok=True)
                        self.logger.info(f"INIT_FILE_MONITORING: Répertoire Connaissance créé avec succès : {CONNAISSANCE_DIR}")
                    except OSError as e_mkdir_connaissance:
                        self.logger.critical(f"INIT_FILE_MONITORING: Impossible de créer le répertoire Connaissance '{CONNAISSANCE_DIR}': {e_mkdir_connaissance}. Le service ne peut pas surveiller les fichiers.", exc_info=True)
                        raise FileNotFoundError(f"Répertoire Connaissance '{CONNAISSANCE_DIR}' non trouvé et impossible à créer.") from e_mkdir_connaissance
                elif not CONNAISSANCE_DIR.is_dir():
                    err_msg_not_dir = f"Le chemin spécifié pour Connaissance '{CONNAISSANCE_DIR}' existe mais n'est pas un répertoire."
                    self.logger.critical(f"INIT_FILE_MONITORING: {err_msg_not_dir}")
                    raise NotADirectoryError(err_msg_not_dir)
                else:
                    self.logger.debug(f"INIT_FILE_MONITORING: Répertoire Connaissance '{CONNAISSANCE_DIR}' validé.")


                # --- 1. SCAN INITIAL DU RÉPERTOIRE CONNAISSANCE ---
                self.logger.info("INIT_FILE_MONITORING: Lancement du scan initial du répertoire Connaissance...")
                initial_scan_added_count = 0
                try:
                    for filepath_obj in CONNAISSANCE_DIR.rglob('*'): # rglob pour récursif
                        if self.running.is_set():
                            self.logger.info("INIT_FILE_MONITORING: Arrêt du service demandé pendant le scan initial. Scan interrompu.")
                            break

                        # Logique d'exclusion (utilise les attributs d'instance)
                        path_parts_as_str_lower = {str(part).lower() for part in filepath_obj.parts}
                        is_excluded_by_part = any(excluded_part in path_parts_as_str_lower for excluded_part in self.excluded_dir_parts)
                        is_excluded_by_prefix = False
                        for part_component_str in map(str, filepath_obj.parts):
                            if any(part_component_str.startswith(prefix) for prefix in self.excluded_dir_prefixes):
                                is_excluded_by_prefix = True
                                break
                        if is_excluded_by_part or is_excluded_by_prefix:
                            self.logger.debug(f"INITIAL_SCAN_SKIP_EXCLUDED: Ignoré (exclu): {filepath_obj} (part_match={is_excluded_by_part}, prefix_match={is_excluded_by_prefix})")
                            continue
                        # self.logger.debug(f"INITIAL_SCAN_CHECK: Vérification de {filepath_obj}") # Peut être trop verbeux
                        if filepath_obj.is_file():
                            if self._is_file_processable(filepath_obj): # Gère les extensions et autres filtres
                                self.enqueue_file(filepath_obj)
                                initial_scan_added_count += 1
                    self.logger.info(f"INIT_FILE_MONITORING: Scan initial terminé. {initial_scan_added_count} fichiers potentiellement ajoutés à la file d'attente.")
                except PermissionError as e_perm_scan:
                    self.logger.error(f"INIT_FILE_MONITORING: Erreur de permission lors du scan initial de '{CONNAISSANCE_DIR}': {e_perm_scan}. Vérifiez les droits d'accès.", exc_info=False)
                except Exception as e_initial_scan_generic:
                    self.logger.error(f"INIT_FILE_MONITORING: Erreur inattendue durant le scan initial de '{CONNAISSANCE_DIR}': {e_initial_scan_generic}", exc_info=True)


            # --- 2. MISE EN PLACE DE WATCHDOG (si activé et disponible) ---
            service_params_cfg = self.config.get("service_params", DEFAULT_CONFIG.get("service_params", {}))
            watchdog_should_be_enabled_in_config = service_params_cfg.get("watchdog_enabled", True)

            if watchdog_should_be_enabled_in_config and WATCHDOG_AVAILABLE: # WATCHDOG_AVAILABLE est la globale
                self.logger.info("INIT_FILE_MONITORING: Tentative d'initialisation/réinitialisation de Watchdog...")
                try:
                    # Les imports de Observer et FileSystemEventHandler sont au niveau du module cerveau.py
                    # et WATCHDOG_AVAILABLE confirme leur succès.

                    # Arrêter et nettoyer l'ancien observer s'il existe et est en vie
                    if self.watchdog_observer and self.watchdog_observer.is_alive():
                        self.logger.debug("INIT_FILE_MONITORING: Arrêt de l'ancien observer Watchdog...")
                        try:
                            self.watchdog_observer.stop()
                            self.watchdog_observer.join(timeout=2.0)
                            if self.watchdog_observer.is_alive():
                                """TODO: Add docstring."""
                                self.logger.warning("INIT_FILE_MONITORING: L'ancien observer Watchdog n'a pas pu être arrêté dans le délai.")
                            else:
                                self.logger.debug("INIT_FILE_MONITORING: Ancien observer Watchdog arrêté avec succès.")
                        except Exception as e_old_wd_stop_cleanup: # Attraper toute exception lors de l'arrêt
                            self.logger.warning(f"INIT_FILE_MONITORING: Erreur lors de l'arrêt de l'ancien observer Watchdog: {e_old_wd_stop_cleanup}", exc_info=False)

                    # Observer et FileSystemEventHandler sont les variables globales définies en haut du script
                    if Observer and FileSystemEventHandler: # Vérifier qu'ils ne sont pas None
                        self.watchdog_observer = Observer()
                        event_handler_instance = self.AlmaKnowledgeEventHandler(self)
                        self.watchdog_observer.schedule(event_handler_instance, str(CONNAISSANCE_DIR), recursive=True)
                        self.watchdog_observer.start()
                        self.logger.info(f"INIT_FILE_MONITORING: Surveillance Watchdog de '{CONNAISSANCE_DIR}' (ré)activée avec succès.")
                    else:
                        self.logger.error("INIT_FILE_MONITORING: Observer ou FileSystemEventHandler non disponibles (None) malgré WATCHDOG_AVAILABLE=True. Incohérence.")
                        self.config.get("service_params", {})["watchdog_enabled"] = False


                except Exception as e_wd_init_fatal: # Attraper toute exception lors de l'init de Watchdog
                    self.logger.error(f"INIT_FILE_MONITORING: Erreur critique lors de l'initialisation de Watchdog: {e_wd_init_fatal}. Passage au scan périodique uniquement.", exc_info=True)
                    # Mettre à jour la config en mémoire pour refléter que watchdog n'est pas utilisé
                    self.config.get("service_params", {})["watchdog_enabled"] = False

            elif watchdog_should_be_enabled_in_config and not WATCHDOG_AVAILABLE:
                self.logger.warning("INIT_FILE_MONITORING: Watchdog activé dans config mais non disponible globalement (échec import initial). Scan périodique sera utilisé.")
                self.config.get("service_params", {})["watchdog_enabled"] = False # Mettre à jour en mémoire
            else: # Watchdog désactivé dans la config
                self.logger.info("INIT_FILE_MONITORING: Watchdog désactivé dans la configuration. Le scan périodique sera le principal mécanisme de détection en temps réel.")


            # --- 3. LANCEMENT DU SCAN PÉRIODIQUE ---
            # Le scan périodique est toujours lancé. Il sert de fallback robuste et attrape
            # les événements potentiellement manqués par Watchdog ou les changements survenus
            # lorsque le service était arrêté.
            scan_interval_cfg = service_params_cfg.get("file_scan_interval_seconds", DEFAULT_CONFIG["service_params"]["file_scan_interval_seconds"])

            if self.scanner_thread and self.scanner_thread.is_alive():
                self.logger.info("INIT_FILE_MONITORING: Un thread de scan périodique est déjà actif. Il continuera.")
                # La boucle _periodic_scan lit l'intervalle à chaque itération, donc elle s'adaptera
                # si l'intervalle change via un reload_configuration.
                    """TODO: Add docstring."""
            elif not self.running.is_set(): # Ne pas lancer si le service est en train de s'arrêter
                self.logger.info(f"INIT_FILE_MONITORING: Activation du thread de scan périodique (intervalle: {scan_interval_cfg}s).")
                try:
                    self.scanner_thread = threading.Thread(target=self._periodic_scan, daemon=True, name="PeriodicScanner")
                    self.scanner_thread.start()
                    self.logger.info("INIT_FILE_MONITORING: Thread de scan périodique démarré.")
                except Exception as e_start_scanner:
                    self.logger.error(f"INIT_FILE_MONITORING: Échec du démarrage du thread de scan périodique: {e_start_scanner}", exc_info=True)
            else:
                self.logger.info("INIT_FILE_MONITORING: Service en cours d'arrêt, lancement du scan périodique annulé.")

            self.logger.info("INIT_FILE_MONITORING: Initialisation de la surveillance des fichiers terminée.")

    def _periodic_scan(self) -> None:
        # Utiliser self.config qui peut être mis à jour par reload_configuration
        # Donc, récupérer scan_interval à chaque itération de la boucle
        while not self.running.is_set():
            current_scan_interval = self.config.get("service_params", {}).get("file_scan_interval_seconds", 60)
            self.logger.debug(f"PERIODIC_SCAN_CYCLE: Début du scan périodique de {CONNAISSANCE_DIR} (intervalle actuel: {current_scan_interval}s)...")
            try:
                processed_in_this_scan = 0
                for filepath_obj in CONNAISSANCE_DIR.rglob('*'):
                    if self.running.is_set():
                        self.logger.info("Arrêt demandé pendant le scan périodique. Scan interrompu.")
                        break

                    # --- Logique d'exclusion (identique au scan initial) ---
                    path_parts_lower = {str(part).lower() for part in filepath_obj.parts}
                    is_excluded_by_part = any(excluded_part in path_parts_lower for excluded_part in self.excluded_dir_parts)

                    is_excluded_by_prefix = False
                    for part_str in filepath_obj.parts:
                        if any(str(part_str).startswith(prefix) for prefix in self.excluded_dir_prefixes):
                            is_excluded_by_prefix = True
                            break

                    if is_excluded_by_part or is_excluded_by_prefix:
                        self.logger.debug(f"PERIODIC_SCAN_SKIP_EXCLUDED: Ignoré (exclu): {filepath_obj} (part_match={is_excluded_by_part}, prefix_match={is_excluded_by_prefix})")
                        continue
                    # --- Fin Logique d'exclusion ---

                    self.logger.debug(f"PERIODIC_SCAN_CHECK: Vérification de {filepath_obj}")
                    if filepath_obj.is_file(): # Traiter uniquement les fichiers
                        if self._is_file_processable(filepath_obj): # Gère les extensions et autres filtres
                            self.enqueue_file(filepath_obj)
                            processed_in_this_scan += 1
                        # else: _is_file_processable logue déjà la raison du rejet
                self.logger.debug(f"Scan périodique terminé. {processed_in_this_scan} fichiers potentiellement ajoutés à la file d'attente.")
            except Exception as e_periodic_scan:
                self.logger.error(f"Erreur lors du scan périodique: {e_periodic_scan}", exc_info=True)

            # Attendre avant le prochain scan, en utilisant l'intervalle actuel de la config
            self.running.wait(timeout=current_scan_interval)

    def _is_file_processable(self, filepath: Path) -> bool:
        filepath_str = str(filepath.resolve())
        self.logger.debug(f"IS_PROCESSABLE_CHECK: Début vérification pour '{filepath_str}'")

        # 1. Vérification de base du fichier
        if not filepath.exists():
            self.logger.debug(f"IS_PROCESSABLE_REJECT_NOT_FOUND: Fichier '{filepath_str}' non trouvé.")
            return False
        if not filepath.is_file():
            self.logger.debug(f"IS_PROCESSABLE_REJECT_NOT_FILE: '{filepath_str}' n'est pas un fichier.")
            return False

        # 2. Vérification des extensions autorisées
        service_params_cfg = self.config.get("service_params", DEFAULT_CONFIG.get("service_params", {}))
        allowed_extensions = service_params_cfg.get("allowed_file_extensions",
                                                    DEFAULT_CONFIG["service_params"]["allowed_file_extensions"])
        if filepath.suffix.lower() not in allowed_extensions:
            self.logger.debug(f"IS_PROCESSABLE_REJECT_EXTENSION: Extension '{filepath.suffix}' non autorisée pour '{filepath_str}'. Autorisées: {allowed_extensions}")
            return False

        # 3. Vérification de la quarantaine
        if filepath_str in self.file_quarantine:
            q_info = self.file_quarantine[filepath_str]
            if time.time() < q_info.get('quarantined_until', 0.0):
                quarantined_until_iso = datetime.datetime.fromtimestamp(q_info['quarantined_until']).isoformat() if q_info.get('quarantined_until') else "N/A"
                self.logger.debug(f"IS_PROCESSABLE_REJECT_QUARANTINE: '{filepath_str}' en quarantaine jusqu'à {quarantined_until_iso}.")
                return False
            else:
                self.logger.info(f"IS_PROCESSABLE_INFO_QUARANTINE_LIFTED: Fichier '{filepath_str}' sort de quarantaine (sera réévalué).")
                # On ne supprime pas de la quarantaine ici, mais au succès du traitement.

        # 4. Calcul du checksum actuel
        current_checksum = calculate_checksum(filepath)
        if not current_checksum:
            self.logger.warning(f"IS_PROCESSABLE_REJECT_NO_CHECKSUM: Impossible de calculer le checksum pour '{filepath_str}'. Fichier ignoré.")
            return False

        # 5. Vérification du cache en mémoire (session courante)
        with self.processed_files_cache_lock:
            if filepath_str in self.processed_files_cache and self.processed_files_cache[filepath_str] == current_checksum:
                self.logger.debug(f"IS_PROCESSABLE_REJECT_CACHE_SESSION: '{filepath_str}' (CS: {current_checksum}) déjà traité (cache session) et inchangé.")
                return False

        # 6. Vérification dans la KnowledgeBase (sessions précédentes)
        kb_config_section = self.config.get("knowledge_base", DEFAULT_CONFIG.get("knowledge_base", {}))
        # Si la DB n'est pas utilisée, on considère le fichier comme processable s'il a passé les autres tests.
        if not (self.kb_instance and KB_DB_PATH and kb_config_section.get("use_sqlite_db", True)):
            self.logger.info(f"IS_PROCESSABLE_ACCEPT_NO_DB_CHECK: '{filepath_str}' (CS: {current_checksum}) est processable (DB non vérifiée).")
            return True
                """TODO: Add docstring."""

        # Si la DB est utilisée, on vérifie le checksum
        temp_conn_kb_check: Optional[sqlite3.Connection] = None
        db_timeout_cfg = kb_config_section.get("db_timeout_seconds", DEFAULT_CONFIG["knowledge_base"]["db_timeout_seconds"])

        # Variable pour stocker le résultat de la vérification DB
        is_processable_based_on_db = True # Par défaut, on accepte si erreur DB

        try: # --- DEBUT DU TRY POUR LA CONNEXION ET LECTURE DB ---
            self.logger.debug(f"IS_PROCESSABLE_DB_CHECK: Tentative de connexion à la KB pour vérifier '{filepath_str}'.")
            temp_conn_kb_check = sqlite3.connect(f"file:{KB_DB_PATH}?mode=ro&immutable=1", uri=True, timeout=db_timeout_cfg)
            temp_conn_kb_check.row_factory = sqlite3.Row
            try:
                temp_conn_kb_check.execute("PRAGMA journal_mode=WAL;")
            except sqlite3.Error as e_wal_temp:
                 self.logger.debug(f"Note: échec activation WAL sur connexion temporaire ro: {e_wal_temp}")

            kb_checksum = self.kb_instance.get_file_checksum(temp_conn_kb_check, filepath_str)

            if kb_checksum is not None: # Le fichier est connu dans la KB
                if kb_checksum == current_checksum:
                    self.logger.debug(f"IS_PROCESSABLE_REJECT_KB_UNCHANGED: '{filepath_str}' (CS: {current_checksum}) dans KB et inchangé.")
                    is_processable_based_on_db = False # REJETER
                else:
                    self.logger.info(f"IS_PROCESSABLE_ACCEPT_KB_MODIFIED: '{filepath_str}' (CS actuel: {current_checksum}, CS KB: {kb_checksum}) dans KB mais modifié.")
                    is_processable_based_on_db = True # ACCEPTER
            else: # Fichier non trouvé dans la KB
                self.logger.debug(f"IS_PROCESSABLE_INFO_NOT_IN_KB: '{filepath_str}' non trouvé dans la KB. Sera traité si nouveau.")
                is_processable_based_on_db = True # ACCEPTER (car nouveau pour la KB)

        except sqlite3.OperationalError as e_op_sql:
            if "unable to open database file" in str(e_op_sql).lower() or \
               "no such table: files" in str(e_op_sql).lower():
                self.logger.warning(f"IS_PROCESSABLE_WARN_KB_UNAVAILABLE: Base de données SQLite non trouvée ou table 'files' manquante pour '{filepath_str}'. Traité comme nouveau. Erreur: {e_op_sql}")
            else:
                self.logger.error(f"IS_PROCESSABLE_ERROR_KB_CHECK_SQLITE: Erreur opérationnelle SQLite pour '{filepath_str}': {e_op_sql}", exc_info=False)
            is_processable_based_on_db = True # Accepter par défaut si la DB a un problème
        except Exception as e_kb_check_generic:
            self.logger.error(f"IS_PROCESSABLE_ERROR_KB_CHECK_GENERIC: Erreur générique vérification checksum KB pour '{filepath_str}': {e_kb_check_generic}", exc_info=True)
            is_processable_based_on_db = True # Accepter par défaut
        finally: # --- FINALLY POUR LE TRY DE CONNEXION DB ---
            if temp_conn_kb_check:
                try:
                    temp_conn_kb_check.close()
                    self.logger.debug(f"IS_PROCESSABLE_DB_CHECK: Connexion temporaire à la KB fermée pour '{filepath_str}'.")
                except sqlite3.Error:
                    pass # Ignorer les erreurs à la fermeture

        if not is_processable_based_on_db: # Si la vérification DB a explicitement dit de rejeter
            return False

        # Si on arrive ici, le fichier a passé tous les tests ou la vérification DB a conduit à l'accepter
        self.logger.info(f"IS_PROCESSABLE_ACCEPT_FINAL: '{filepath_str}' (CS: {current_checksum}) est processable.")
        return True

    def _process_file_from_queue(self) -> None:
        # Utiliser self.logger directement, car c'est un attribut d'instance.
        # Pas besoin de current_logger = self.logger.

        if not self.file_queue:
            # Logué par MAIN_LOOP_TICK dans la méthode start() si la file est vide.
            # Pas besoin de loguer ici pour éviter la redondance.
            return

        if not self.executor:
            self.logger.warning("PROCESS_QUEUE_SKIP_NO_EXECUTOR: ThreadPoolExecutor non initialisé. Impossible de traiter la file.")
            return

        # Vérifier si l'executor est en cours d'arrêt ou arrêté
        # hasattr(self.executor, '_shutdown') est une vérification d'attribut interne,
        # plus robuste serait de vérifier si l'executor accepte de nouvelles tâches,
        # mais cette vérification est généralement suffisante.
        if hasattr(self.executor, '_shutdown') and self.executor._shutdown: # type: ignore[attr-defined]
            self.logger.info("PROCESS_QUEUE_SKIP_EXECUTOR_SHUTDOWN: ThreadPoolExecutor en cours d'arrêt. Traitement de la file interrompu.")
            return

        # --- Logique de Backpressure ---
        # Lire les paramètres de configuration à chaque appel pour prendre en compte les rechargements
        service_params_cfg = self.config.get("service_params", DEFAULT_CONFIG.get("service_params", {}))
        max_workers_from_config = service_params_cfg.get("max_workers", DEFAULT_CONFIG["service_params"]["max_workers"])
        backpressure_multiplier = service_params_cfg.get("backpressure_active_task_multiplier", DEFAULT_CONFIG["service_params"]["backpressure_active_task_multiplier"])

        # S'assurer que max_workers est au moins 1 pour le calcul
        effective_max_workers = max(1, max_workers_from_config)
        max_pending_tasks_allowed = effective_max_workers * backpressure_multiplier

        with self.active_tasks_lock:
            current_active_tasks_count = len(self.active_tasks)

        if current_active_tasks_count >= max_pending_tasks_allowed:
            self.logger.debug(
                f"PROCESS_QUEUE_PAUSE_BACKPRESSURE: Tâches actives ({current_active_tasks_count}) "
                f">= seuil ({max_pending_tasks_allowed}). Soumission de nouvelles tâches en pause."
            )
            return
        # --- Fin Logique de Backpressure ---

        file_task_info: Optional[Dict[str, Any]] = None
        try:
            # popleft() est une opération atomique sur collections.deque
            file_task_info = self.file_queue.popleft()
            self.logger.info(
                f"PROCESS_QUEUE_POP: Pris '{file_task_info.get('path', 'Chemin inconnu')}' de la file. "
                f"Taille restante: {len(self.file_queue)}"
            )
        except IndexError:
            # Peut arriver si la file est vidée par un autre thread entre la vérification initiale et le pop.
            # Dans notre design actuel (MainThread pop, threads de monitoring append), c'est moins probable
            # mais une bonne garde.
            self.logger.debug("PROCESS_QUEUE_POP_EMPTY_RACE: File vidée entre la vérification et le popleft.")
            return

        # Double vérification, bien que popleft sur une deque vide lève IndexError.
        if not file_task_info or not file_task_info.get("path"):
            self.logger.error("PROCESS_QUEUE_ERROR_NO_TASK_INFO: file_task_info est None ou sans chemin après popleft, ne devrait pas arriver.")
            return

        filepath_str_from_task = file_task_info["path"]
        filepath_obj_for_worker = Path(filepath_str_from_task) # Convertir en Path pour le worker

        self.logger.info(f"PROCESS_QUEUE_SUBMIT: Soumission de la tâche pour '{filepath_obj_for_worker}' au worker.")

        try:
            # Soumettre la tâche au ThreadPoolExecutor.
            # _file_processing_worker est la méthode qui sera exécutée par un thread du pool.
            future_task = self.executor.submit(self._file_processing_worker, filepath_obj_for_worker, file_task_info)

            # Enregistrer la future et le chemin du fichier pour suivi
            with self.active_tasks_lock:
                # Stocker le chemin comme str pour la clé de la future, et le temps de soumission
                self.active_tasks[future_task] = (filepath_str_from_task, time.monotonic())

            # Mettre à jour les statistiques (protégé par lock)
            with self.stats_lock: # Assurez-vous que self.stats_lock est défini dans __init__
                self.stats["tasks_submitted_to_pool"] += 1

            # Ajouter le callback qui sera exécuté quand la tâche (Future) se termine
            future_task.add_done_callback(self._handle_task_result)

            # Log de succès de la soumission (optionnel, mais utile pour le débogage fin)
            # Relire current_active_tasks_count après l'ajout pour un log précis
            with self.active_tasks_lock:
                updated_active_tasks_count = len(self.active_tasks)
            self.logger.debug(
                f"PROCESS_QUEUE_SUBMIT_SUCCESS: Tâche pour '{filepath_obj_for_worker}' soumise. "
                f"Tasks actives (après soumission): {updated_active_tasks_count}"
            )

        except RuntimeError as e_runtime_submit:
            # Peut arriver si l'executor est arrêté ou en cours d'arrêt entre la vérification et le submit.
            self.logger.error(
                f"PROCESS_QUEUE_SUBMIT_FAIL_RUNTIME: RuntimeError lors de la soumission de '{filepath_obj_for_worker}' "
                f"(executor arrêté ou en arrêt ?): {e_runtime_submit}", exc_info=True
            )
            # Remettre la tâche en tête de file pour un traitement ultérieur (prioritaire)
            self.file_queue.appendleft(file_task_info)
            self.logger.info(f"PROCESS_QUEUE_REQUEUE: Tâche pour '{filepath_obj_for_worker}' remise en tête de file suite à une erreur de soumission Runtime.")
        except Exception as e_unexpected_submit:
            self.logger.error(
                f"PROCESS_QUEUE_SUBMIT_FAIL_UNEXPECTED: Erreur inattendue lors de la soumission de '{filepath_obj_for_worker}': {e_unexpected_submit}", exc_info=True
            )
            # Remettre aussi en tête de file par prudence
            self.file_queue.appendleft(file_task_info)
            self.logger.info(f"PROCESS_QUEUE_REQUEUE: Tâche pour '{filepath_obj_for_worker}' remise en tête de file suite à une erreur de soumission inattendue.")

    def _file_processing_worker(self,
                                filepath: Path,
                                task_info: Dict[str, Any]
                               ) -> Tuple[str, bool, Optional[Exception], Dict[str, float], int]:
        """
        Worker exécuté dans un thread du ThreadPoolExecutor pour traiter un fichier unique.
        Gère sa propre connexion à la base de données et la transaction pour ce fichier.
        """
        proposals_count = 0
        stage_timings: Dict[str, float] = {}
        # Créer un logger spécifique pour ce worker et cette tâche, incluant le nom du fichier
        # Cela aide à suivre les logs d'un traitement de fichier spécifique.
        worker_logger_name = f"{MODULE_NAME}.Worker.{threading.current_thread().name}.{filepath.name}"
        worker_logger = logging.getLogger(worker_logger_name)
        worker_logger.info(f"Démarrage worker pour traiter: {filepath}")

        worker_db_conn: Optional[sqlite3.Connection] = None
        transaction_active_by_this_worker = False # Flag pour suivre si CE worker a démarré la transaction
        pipeline_final_success = False # Résultat final du pipeline et des opérations DB
        exception_to_report: Optional[Exception] = None # Pour stocker l'exception principale à remonter

        # Lire la configuration de la base de données à partir de self.config (qui est adapté)
        kb_config_section = self.config.get("knowledge_base", DEFAULT_CONFIG.get("knowledge_base", {}))
        use_sqlite_db_for_this_task = kb_config_section.get("use_sqlite_db", True) and KB_DB_PATH is not None
        db_timeout_for_this_task = kb_config_section.get("db_timeout_seconds", DEFAULT_CONFIG["knowledge_base"]["db_timeout_seconds"])

        try:
            # --- 1. Ouverture de la connexion DB dédiée au worker (si la DB est activée) ---
            if use_sqlite_db_for_this_task and KB_DB_PATH: # S'assurer que KB_DB_PATH est valide
                try:
                    worker_logger.debug(f"Ouverture connexion DB pour: {filepath} (Timeout: {db_timeout_for_this_task}s)")
                    # Utiliser str(KB_DB_PATH) pour la compatibilité
                    worker_db_conn = sqlite3.connect(str(KB_DB_PATH), timeout=db_timeout_for_this_task)
                    worker_db_conn.row_factory = sqlite3.Row # Accès aux colonnes par nom

                    # Configurer la connexion (essentiel pour chaque nouvelle connexion)
                    worker_db_conn.execute("PRAGMA journal_mode=WAL;")
                    worker_db_conn.execute("PRAGMA foreign_keys = ON;")
                    worker_logger.info(f"OK: Connexion DB (WAL, FK) ouverte pour: {filepath}")

                except sqlite3.Error as e_db_connect: # Attraper toutes les erreurs SQLite ici
                    worker_logger.error(f"ÉCHEC SQLite lors de l'ouverture de la connexion DB pour {filepath}: {e_db_connect}", exc_info=True)
                    exception_to_report = e_db_connect
                    # Ne pas retourner ici, laisser le finally fermer la connexion si elle a été partiellement ouverte.
                    # pipeline_final_success reste False.
                except Exception as e_conn_generic: # Autres erreurs potentielles
                    worker_logger.error(f"ÉCHEC (Générique) ouverture connexion DB pour {filepath}: {e_conn_generic}", exc_info=True)
                    exception_to_report = e_conn_generic
                    # pipeline_final_success reste False.

            # Continuer seulement si la connexion DB a été établie (si elle était nécessaire)
            if use_sqlite_db_for_this_task and not worker_db_conn and not exception_to_report:
                # Ce cas ne devrait pas arriver si KB_DB_PATH est valide, mais c'est une sécurité
                err_msg = "Connexion DB requise mais non établie sans exception spécifique."
                worker_logger.error(err_msg)
                exception_to_report = RuntimeError(err_msg)


            # --- 2. Démarrage de la Transaction (si la connexion DB est valide) ---
            if worker_db_conn and not exception_to_report: # Ne pas démarrer de TX si la connexion a échoué
                try:
                    # BEGIN IMMEDIATE pour un verrou exclusif au début, peut aider à éviter des conflits
                    # si d'autres processus tentent d'écrire (bien que moins probable avec WAL).
                    # BEGIN seul est aussi une option (verrou différé).
                    worker_db_conn.execute("BEGIN IMMEDIATE TRANSACTION;")
                    transaction_active_by_this_worker = True
                    worker_logger.info(f"DB TX: Transaction DÉMARRÉE pour: {filepath}")
                except sqlite3.Error as e_begin_tx:
                    worker_logger.error(f"DB TX: Échec BEGIN TRANSACTION pour {filepath}: {e_begin_tx}. Traitement avec DB compromis.", exc_info=True)
                    exception_to_report = e_begin_tx
                    # pipeline_final_success reste False.

            # --- 3. Exécution du pipeline de traitement ---
            # Continuer même si la transaction a échoué ou si la DB n'est pas utilisée,
            # car certaines étapes du pipeline pourraient ne pas dépendre de la DB.
            # FileProcessor et les étapes gèreront worker_db_conn étant None.
            if not exception_to_report or not use_sqlite_db_for_this_task: # Si pas d'erreur critique de DB ou DB non utilisée
                try:
                    processor = FileProcessor(
                        filepath=filepath,
                        config=self.config,
                        pipeline_steps=self.pipeline_steps_instances,
                        kb_instance=self.kb_instance, # L'instance partagée de KnowledgeBase (pour ses méthodes logiques)
                        db_conn_worker=worker_db_conn # La connexion dédiée, peut être None
                    )

                    # run_pipeline exécute les étapes et gère leurs exceptions internes.
                    # Il retourne True si toutes les étapes activées ont réussi.
                    pipeline_run_successful = processor.run_pipeline()
                    stage_timings = processor.pipeline_stage_timings # Récupérer les timings

                    if pipeline_run_successful:
                        # Si le pipeline a réussi, et si nous avions une transaction active, on la commite.
                        if worker_db_conn and transaction_active_by_this_worker:
                            try:
                                worker_db_conn.commit()
                                worker_logger.info(f"DB TX: Transaction COMMITÉE pour {filepath} après pipeline réussi.")
                                pipeline_final_success = True # Succès final confirmé après commit
                            except sqlite3.Error as e_commit:
                                worker_logger.error(f"DB TX: ÉCHEC CRITIQUE du COMMIT pour {filepath} après pipeline réussi: {e_commit}. Données potentiellement non sauvegardées.", exc_info=True)
                                exception_to_report = e_commit
                                pipeline_final_success = False
                                # Tenter un rollback par sécurité, bien que l'état de la TX soit incertain
                                try: worker_db_conn.rollback()
                                except sqlite3.Error: pass
                        elif not use_sqlite_db_for_this_task: # Si la DB n'était pas utilisée, le succès du pipeline est le succès final
                             pipeline_final_success = True
                        # else: pipeline réussi mais pas de transaction à commiter (ex: DB désactivée ou BEGIN a échoué)
                        # Dans ce cas, pipeline_final_success reste False si BEGIN a échoué.

                        # Mettre à jour les caches et stats seulement si TOUT a réussi (y compris le commit)
                        if pipeline_final_success:
                            if processor.checksum: # processor.checksum est calculé dans run_pipeline
                                with self.processed_files_cache_lock: # Protéger l'accès
                                    self.processed_files_cache[str(filepath)] = processor.checksum

                            proposals_count = processor.processed_data.get("proposals_generated_count", 0)

                            if "active_improvements_applied" in processor.processed_data:
                                with self.stats_lock:
                                    self.stats["active_improvements_count"] += len(processor.processed_data["active_improvements_applied"])
                    else: # processor.run_pipeline() a retourné False
                        worker_logger.warning(f"Pipeline a échoué pour {filepath} (retour de run_pipeline() était False).")
                        # L'exception spécifique de l'étape devrait avoir été loguée par FileProcessor ou l'étape elle-même.
                        # On ne stocke pas d'exception ici car elle est interne au pipeline.
                        pipeline_final_success = False
                        # Le rollback sera géré dans le bloc except ou finally si une transaction était active.

                except Exception as e_processor_run: # Erreur majeure dans l'instanciation ou l'appel de run_pipeline
                    worker_logger.critical(f"WORKER: Erreur majeure lors de l'instanciation/exécution de FileProcessor pour {filepath}: {e_processor_run}", exc_info=True)
                    exception_to_report = e_processor_run
                    pipeline_final_success = False

            # Si une exception critique de DB (connexion, BEGIN) est survenue plus tôt,
            # pipeline_final_success est déjà False et exception_to_report est déjà défini.

            # --- 4. Rollback en cas d'échec si une transaction était active ---
            if not pipeline_final_success and worker_db_conn and transaction_active_by_this_worker:
                worker_logger.warning(f"Tentative de ROLLBACK pour {filepath} suite à échec (pipeline_success={pipeline_final_success}, exception: {type(exception_to_report).__name__ if exception_to_report else 'N/A'}).")
                try:
                    worker_db_conn.rollback()
                    worker_logger.info(f"DB TX: Transaction ANNULÉE (rollback) pour {filepath}.")
                except sqlite3.Error as e_rollback_on_fail:
                    worker_logger.error(f"DB TX: Échec du rollback pour {filepath} après échec: {e_rollback_on_fail}", exc_info=True)

            return str(filepath), pipeline_final_success, exception_to_report, stage_timings, proposals_count

        except Exception as e_global_worker_catch: # Un filet de sécurité ultime
            worker_logger.critical(f"WORKER: Erreur fatale et inattendue dans _file_processing_worker pour {filepath}: {e_global_worker_catch}", exc_info=True)
            exception_to_report = e_global_worker_catch
            # Tenter un rollback si une transaction était active et que la connexion existe encore
            if worker_db_conn and transaction_active_by_this_worker:
                try:
                    worker_db_conn.rollback()
                    worker_logger.error(f"DB TX: Transaction ANNULÉE (rollback) pour {filepath} suite à exception fatale globale.")
                except sqlite3.Error as e_rb_fatal:
                     worker_logger.error(f"DB TX: Échec du rollback après erreur fatale globale pour {filepath}: {e_rb_fatal}", exc_info=True)
            return str(filepath), False, exception_to_report, stage_timings, proposals_count

        finally:
            # --- 5. Fermeture de la connexion DB dédiée au worker ---
            if worker_db_conn:
                try:
                    # S'assurer qu'une transaction potentiellement "oubliée" est rollbackée avant de fermer
                    if transaction_active_by_this_worker and worker_db_conn.in_transaction:
                        worker_logger.warning(f"DB TX: Transaction encore active pour {filepath} dans le bloc finally. Tentative de rollback final.")
                        worker_db_conn.rollback()
                    worker_db_conn.close()
                    worker_logger.info(f"Connexion DB fermée pour le worker qui traitait {filepath}")
                except sqlite3.Error as e_db_close_sqlite:
                    worker_logger.error(f"Erreur SQLite lors de la fermeture/rollback final de la connexion DB pour {filepath}: {e_db_close_sqlite}", exc_info=True)
                except Exception as e_db_close_generic:
                     worker_logger.error(f"Erreur générique lors de la fermeture/rollback final de la connexion DB pour {filepath}: {e_db_close_generic}", exc_info=True)

    def _handle_task_result(self, future: Future) -> None:
        """
        Callback exécuté lorsqu'une tâche de traitement de fichier (Future) se termine.
        Met à jour les statistiques, gère les succès et les échecs.
        """
        filepath_str_from_active_tasks: Optional[str] = None
        task_submit_time_mono: Optional[float] = None # Pour calculer le temps de traitement

        # Retirer la future de active_tasks et récupérer les infos associées
        # Cet accès est protégé par active_tasks_lock.
        with self.active_tasks_lock:
            task_details = self.active_tasks.pop(future, None) # (filepath_str, submit_time_mono) ou None
            if task_details:
                filepath_str_from_active_tasks, task_submit_time_mono = task_details

        # Mettre à jour le compteur de tâches complétées (protégé par stats_lock)
        with self.stats_lock: # Assurez-vous que self.stats_lock est défini dans __init__
            self.stats["tasks_completed_from_pool"] += 1

        if not filepath_str_from_active_tasks:
            self.logger.warning(
                "_handle_task_result: Callback de tâche terminé sans informations de fichier associées "
                "(future non trouvée dans active_tasks). Aucune autre stat mise à jour pour cette tâche."
            )
            return

        # Convertir en Path pour les opérations suivantes
        filepath_obj_for_handling = Path(filepath_str_from_active_tasks)
        task_processing_time_seconds: Optional[float] = None
        if task_submit_time_mono is not None:
            task_processing_time_seconds = time.monotonic() - task_submit_time_mono

        try:
            # Vérifier si la tâche a été explicitement annulée
            if future.cancelled():
                self.logger.warning(f"Tâche pour {filepath_obj_for_handling} a été annulée (future.cancelled() est True).")
                with self.stats_lock:
                    self.stats["files_failed"] += 1
                # Pas besoin d'appeler _handle_failed_file ici, car l'annulation est souvent externe
                # ou due à l'arrêt du service.
                return

            # Récupérer le résultat de la tâche. future.result() peut lever :
            # - L'exception levée par la tâche elle-même (si elle a échoué).
            # - CancelledError si la tâche a été annulée avant de commencer.
            # - TimeoutError si un timeout a été défini pour la future (non utilisé directement ici).
            returned_filepath_str, success, exception_obj, stage_timings, proposals_count = future.result()

            # Sanity check: le chemin retourné doit correspondre
            if returned_filepath_str != filepath_str_from_active_tasks:
                self.logger.warning(
                    f"Incohérence de chemin dans _handle_task_result: "
                    f"attendu '{filepath_str_from_active_tasks}', reçu '{returned_filepath_str}'. "
                    f"Utilisation du chemin initialement stocké."
                )

            # Mise à jour des timings des étapes du pipeline
            # self.pipeline_total_timings_samples est un dict. L'accès à un élément de liste
                """TODO: Add docstring."""
            # (append, pop) n'est pas thread-safe si plusieurs threads modifient la MÊME liste.
            # Cependant, les callbacks sont souvent exécutés séquentiellement par l'executor
            # ou par un nombre limité de ses threads. Si un lock dédié devient nécessaire ici,
            # il faudrait l'ajouter (ex: self.pipeline_timings_lock). Pour l'instant, on assume
            # que la contention est faible.
            if stage_timings:
                for stage, duration in stage_timings.items():
                    self.pipeline_total_timings_samples.setdefault(stage, deque(maxlen=1000)).append(duration)
                    # deque(maxlen=1000) gère automatiquement la limite de taille.

            log_suffix = f" (temps total tâche: {task_processing_time_seconds:.2f}s)" if task_processing_time_seconds is not None else ""

            if success:
                self.logger.info(f"Traitement de {filepath_obj_for_handling} terminé avec succès.{log_suffix}")
                with self.stats_lock:
                    self.stats["files_processed_successfully"] += 1
                    self.stats["proposals_generated_total"] += proposals_count

                # Retirer de la quarantaine si succès.
                # L'accès à self.file_quarantine doit être protégé si d'autres threads
                # (comme _is_file_processable ou le rapport d'auto-analyse) le lisent pendant une modification.
                with self.file_quarantine_lock: # Assurez-vous que self.file_quarantine_lock est défini
                    if filepath_str_from_active_tasks in self.file_quarantine:
                        del self.file_quarantine[filepath_str_from_active_tasks]
                        self.logger.info(f"Fichier {filepath_str_from_active_tasks} retiré de la quarantaine après traitement réussi.")
                        # Mettre à jour le compteur de fichiers en quarantaine
                        self.stats["files_in_quarantine_now"] = sum(
                            1 for info in self.file_quarantine.values() if info.get('quarantined_until', 0) > time.time()
                        )
            else:
                # L'exception_obj devrait contenir l'erreur du worker
                self.logger.error(
                    f"Échec du traitement pour {filepath_obj_for_handling}. "
                    f"Exception: {type(exception_obj).__name__ if exception_obj else 'Inconnue'}: {exception_obj}.{log_suffix}",
                    exc_info=exception_obj is not None # Loguer le traceback si une exception est présente
                )
                with self.stats_lock:
                    self.stats["files_failed"] += 1
                # _handle_failed_file gère la mise en quarantaine et la mise à jour de stats["files_in_quarantine_now"]
                self._handle_failed_file(filepath_obj_for_handling)

        except CancelledError: # Spécifiquement si future.result() lève CancelledError
            self.logger.info(f"Tâche de traitement pour {filepath_obj_for_handling} explicitement annulée (attrapé via CancelledError).")
            with self.stats_lock:
                self.stats["files_failed"] += 1
        except Exception as e_future_result: # Attraper toute autre exception de future.result()
            self.logger.error(
                f"Erreur inattendue dans _handle_task_result lors de la récupération du résultat pour {filepath_str_from_active_tasks}: {e_future_result}",
                exc_info=True
                    """TODO: Add docstring."""
            )
            # S'assurer que filepath_str_from_active_tasks est défini avant de l'utiliser
            if filepath_str_from_active_tasks:
                with self.stats_lock:
                    self.stats["files_failed"] += 1
                self._handle_failed_file(Path(filepath_str_from_active_tasks)) # Assurer de passer un Path

    def _handle_failed_file(self, filepath: Path) -> None:
        filepath_str = str(filepath)

        # self.file_quarantine est un dict. setdefault est atomique.
        # L'incrémentation de 'errors' sur une entrée spécifique est aussi atomique
        # car chaque fichier est traité par un seul worker à la fois, donc pas de
        # concurrence sur la *même* clé filepath_str pour cette incrémentation.
        # Un lock serait nécessaire si plusieurs threads pouvaient modifier la même entrée
        # de file_quarantine simultanément, ou si la structure était plus complexe.
        quarantine_entry = self.file_quarantine.setdefault(filepath_str, {'errors': 0, 'quarantined_until': 0.0})
        quarantine_entry['errors'] += 1

        cb_config = self.config.get("circuit_breaker", DEFAULT_CONFIG["circuit_breaker"]) # Accès plus sûr à la config

        if quarantine_entry['errors'] >= cb_config.get("threshold", 3): # Utiliser .get avec défaut
            quarantine_duration = cb_config.get("timeout_seconds", 3600) # Utiliser .get avec défaut
                """TODO: Add docstring."""
            quarantine_until_ts = time.time() + quarantine_duration
            quarantine_entry['quarantined_until'] = quarantine_until_ts

            # MODIFICATION: Protéger la mise à jour de self.stats
            if hasattr(self, 'stats_lock'):
                with self.stats_lock:
                    # Recalculer le nombre de fichiers actuellement en quarantaine
                    # Cette opération (boucle + sum) doit être protégée si self.file_quarantine
                    # peut être modifié par un autre thread pendant l'itération.
                    # Étant donné que del self.file_quarantine[filepath_str] dans _handle_task_result
                    # et les modifications ici sont les principaux points de changement,
                    # et qu'un fichier est traité par un seul worker, le risque est faible
                    # mais un lock plus global sur file_quarantine serait plus sûr pour ce recalcul.
                    # Pour l'instant, on protège juste l'assignation à self.stats.
                    self.stats["files_quarantined_count"] = sum(
                        1 for info in self.file_quarantine.values()
                        if info.get('quarantined_until', 0) > time.time()
                    )
            else: # Fallback si le lock n'est pas implémenté
                self.stats["files_quarantined_count"] = sum(
                    1 for info in self.file_quarantine.values()
                    if info.get('quarantined_until', 0) > time.time()
                )

            self.logger.warning(
                f"Fichier {filepath_str} mis en quarantaine jusqu'à "
                f"{datetime.datetime.fromtimestamp(quarantine_until_ts).isoformat()}. "
                f"Total erreurs: {quarantine_entry['errors']}"
            )
        else:
            self.logger.warning(
                f"Fichier {filepath_str} a échoué. Nombre d'erreurs: {quarantine_entry['errors']}."
            )

    def _handle_deleted_file(self, filepath: Path) -> None:
        filepath_str = str(filepath)
        self.logger.audit(f"Gestion de la suppression du fichier: {filepath_str}")
        if filepath_str in self.processed_files_cache: del self.processed_files_cache[filepath_str]
        if filepath_str in self.file_quarantine: del self.file_quarantine[filepath_str]

        if self.kb_instance and KB_DB_PATH and self.config["knowledge_base"]["use_sqlite_db"]:
            temp_conn_delete: Optional[sqlite3.Connection] = None
            db_timeout = self.config["knowledge_base"].get("db_timeout_seconds", 10)
            try:
                temp_conn_delete = sqlite3.connect(KB_DB_PATH, timeout=db_timeout)
                # CORRECTION: Activer WAL pour cette connexion temporaire
                try: temp_conn_delete.execute("PRAGMA journal_mode=WAL;")
                except sqlite3.Error as e_wal_del: self.logger.debug(f"Note: échec activation WAL sur connexion de suppression: {e_wal_del}")

                self.kb_instance.remove_file_record(temp_conn_delete, filepath_str) # Passe la connexion
            except sqlite3.Error as e_del_db:
                self.logger.error(f"Erreur SQLite lors de la suppression de l'enregistrement KB pour {filepath_str}: {e_del_db}", exc_info=True)
            finally:
                if temp_conn_delete:
                    try: temp_conn_delete.close()
                    except sqlite3.Error: pass
        # ... (reste de la logique pour supprimer les fichiers de propositions, qui est déjà correcte) ...

    def generate_self_report(self) -> Dict[str, Any]:
        uptime = datetime.datetime.now(datetime.timezone.utc) - self.stats["start_time"]
        avg_timings = {stage: sum(samples)/len(samples) if samples else 0 for stage, samples in self.pipeline_total_timings_samples.items()}
        with self.active_tasks_lock:
            num_active_tasks = len(self.active_tasks)

        kb_path_exists = KB_DB_PATH.exists() if KB_DB_PATH else False
        kb_connectable = False
        db_timeout = self.config["knowledge_base"].get("db_timeout_seconds", 2) # Utiliser un timeout court pour un simple test

        if kb_path_exists and self.config["knowledge_base"]["use_sqlite_db"]:
            temp_conn_report: Optional[sqlite3.Connection] = None
            try:
                temp_conn_report = sqlite3.connect(KB_DB_PATH, timeout=db_timeout)
                # Tenter d'activer le mode WAL pour cette connexion de test
                try:
                    temp_conn_report.execute("PRAGMA journal_mode=WAL;")
                except sqlite3.Error as e_wal_report:
                    self.logger.debug(f"Note: échec activation WAL sur connexion temporaire pour generate_self_report: {e_wal_report}")

                temp_conn_report.execute("SELECT 1").fetchone() # Test de connectivité simple
                kb_connectable = True
            except sqlite3.Error as e_db_report:
                self.logger.warning(f"generate_self_report: Impossible de se connecter à la KB pour vérification: {e_db_report}")
                kb_connectable = False
            except Exception as e_gen_report: # Attraper d'autres exceptions potentielles
                self.logger.warning(f"generate_self_report: Erreur générique lors du test de connexion KB: {e_gen_report}")
                kb_connectable = False
            finally:
                if temp_conn_report:
                    try: temp_conn_report.close()
                    except sqlite3.Error: pass

        report = {
            "module_name": MODULE_NAME, "version": MODULE_VERSION,
            "status": "running" if not self.running.is_set() else "stopping",
            "pid": os.getpid(),
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime).split('.')[0],
            "system_info": self.system_resources, # <--- AJOUTER CETTE LIGNE
            "config_summary": {
                "max_workers": self.config.get("service_params", {}).get("max_workers"),
                "kb_path_exists": kb_path_exists,
                "kb_connectable": kb_connectable,
                "spacy_active": bool(self.kb_instance and self.kb_instance.is_spacy_ready),
                "active_pipeline_steps": [s.__class__.__name__ for s in self.pipeline_steps_instances]
            },
            "performance_stats": {
                "file_queue_size": len(self.file_queue),
                "tasks_in_pool_approx": num_active_tasks,
                "tasks_submitted_session": self.stats["tasks_submitted_to_pool"],
                "tasks_completed_session": self.stats["tasks_completed_from_pool"],
                "files_discovered_session": self.stats["files_discovered"],
                "files_processed_successfully_session": self.stats["files_processed_successfully"],
                "files_failed_session": self.stats["files_failed"],
                "files_in_quarantine_now": sum(1 for info in self.file_quarantine.values() if info.get('quarantined_until', 0) > time.time()),
                "proposals_generated_session": self.stats["proposals_generated_total"],
                "active_improvements_applied_session": self.stats["active_improvements_count"],
                "processed_files_cache_size": len(self.processed_files_cache),
                "pipeline_stage_avg_timings_ms": {k: round(v * 1000, 2) for k,v in avg_timings.items()},
            },
            "current_time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        self.logger.audit(f"Rapport d'auto-analyse Cerveau:\n{report_json}")
        return report

    def _handle_deleted_file(self, filepath: Path) -> None:
        """
        Gère la suppression d'un fichier du répertoire Connaissance.
        Supprime ses traces du cache, de la quarantaine, de la KB, et des propositions.
        """
        filepath_str_resolved = str(filepath.resolve())
        self.logger.audit(f"HANDLING_DELETED_FILE: Gestion de la suppression du fichier: {filepath_str_resolved}")

        # 1. Retirer des caches en mémoire (protéger si accès concurrents fréquents)
        with self.processed_files_cache_lock: # Assurez-vous que ce lock est défini
            if filepath_str_resolved in self.processed_files_cache:
                del self.processed_files_cache[filepath_str_resolved]
                self.logger.debug(f"Retiré '{filepath_str_resolved}' de processed_files_cache.")

        with self.file_quarantine_lock: # Assurez-vous que ce lock est défini
            if filepath_str_resolved in self.file_quarantine:
                del self.file_quarantine[filepath_str_resolved]
                self.logger.debug(f"Retiré '{filepath_str_resolved}' de file_quarantine.")
                # Mettre à jour le compteur de fichiers en quarantaine
                with self.stats_lock:
                    self.stats["files_in_quarantine_now"] = sum(
                        1 for info in self.file_quarantine.values()
                        if info.get('quarantined_until', 0.0) > time.time()
                    )

        # 2. Supprimer de la KnowledgeBase (si DB activée)
        kb_config_section = self.config.get("knowledge_base", DEFAULT_CONFIG.get("knowledge_base", {}))
        if self.kb_instance and KB_DB_PATH and kb_config_section.get("use_sqlite_db", True):
            temp_conn_delete: Optional[sqlite3.Connection] = None
            db_timeout_cfg = kb_config_section.get("db_timeout_seconds", DEFAULT_CONFIG["knowledge_base"]["db_timeout_seconds"])
            try:
                # Pas besoin de mode lecture seule ici car on va potentiellement écrire (DELETE)
                temp_conn_delete = sqlite3.connect(str(KB_DB_PATH), timeout=db_timeout_cfg)
                # Activer WAL et FK pour la cohérence, même pour une connexion de suppression
                try:
                    temp_conn_delete.execute("PRAGMA journal_mode=WAL;")
                    temp_conn_delete.execute("PRAGMA foreign_keys = ON;") # Important pour ON DELETE CASCADE
                except sqlite3.Error as e_pragma_del:
                    self.logger.debug(f"Note: échec activation PRAGMAs sur connexion de suppression pour {filepath_str_resolved}: {e_pragma_del}")

                # La méthode remove_file_record doit gérer sa propre transaction (BEGIN, COMMIT/ROLLBACK)
                self.kb_instance.remove_file_record(temp_conn_delete, filepath_str_resolved)
                # remove_file_record logue déjà son succès.

            except sqlite3.Error as e_del_db_sqlite:
                self.logger.error(f"Erreur SQLite lors de la suppression de l'enregistrement KB pour {filepath_str_resolved}: {e_del_db_sqlite}", exc_info=True)
            except Exception as e_del_db_generic:
                self.logger.error(f"Erreur générique lors de la suppression de l'enregistrement KB pour {filepath_str_resolved}: {e_del_db_generic}", exc_info=True)
            finally:
                if temp_conn_delete:
                    try: temp_conn_delete.close()
                    except sqlite3.Error: pass

        # 3. Supprimer les fichiers de propositions associés (logique existante est bonne)
        deleted_proposals_count = 0
        # IMPROVEMENTS_DIR est une globale
        if IMPROVEMENTS_DIR.exists():
            for proposal_file in IMPROVEMENTS_DIR.glob(f"*.ameliorations.json"):
                try:
                    # Lire le contenu pour vérifier le fichier source
                    # Pourrait être optimisé si le nom du fichier de proposition contient le checksum source
                    # de manière fiable. Actuellement, il contient le nom du fichier source.
                    # Si le nom du fichier de proposition est "safe_fn.checksum_source.ameliorations.json"
                    # on pourrait chercher par checksum plus directement.
                    # Pour l'instant, on lit le JSON.
                    with open(proposal_file, 'r', encoding='utf-8') as f_prop:
                        prop_data = json.load(f_prop)

                    # Comparer le chemin résolu
                    if prop_data.get("source_file") == filepath_str_resolved:
                        proposal_file.unlink()
                        deleted_proposals_count += 1
                        self.logger.debug(f"Fichier de proposition '{proposal_file.name}' supprimé pour le fichier source supprimé '{filepath_str_resolved}'.")
                except json.JSONDecodeError:
                    self.logger.warning(f"Impossible de parser le fichier de proposition {proposal_file.name} lors de la vérification pour suppression.")
                except Exception as e_del_prop_file:
                     self.logger.warning(f"Erreur lors de la tentative de suppression du fichier de proposition {proposal_file.name} pour {filepath_str_resolved}: {e_del_prop_file}")

        if deleted_proposals_count > 0:
            self.logger.audit(f"{deleted_proposals_count} fichier(s) de propositions supprimé(s) pour le fichier source supprimé '{filepath_str_resolved}'.")
        else:
            self.logger.debug(f"Aucun fichier de proposition trouvé/supprimé pour '{filepath_str_resolved}'.")

    def generate_self_report(self) -> Dict[str, Any]:
        """Génère un rapport d'auto-analyse complet sur l'état du service."""

        # Utiliser self.stats_lock pour lire les compteurs de manière cohérente
        with self.stats_lock:
            # Créer une copie des stats pour éviter les modifications pendant la construction du rapport
            current_stats = self.stats.copy()
            start_time_from_stats = current_stats.get("start_time", datetime.datetime.now(datetime.timezone.utc))

        uptime = datetime.datetime.now(datetime.timezone.utc) - start_time_from_stats

        # Calcul des timings moyens (deque.append est thread-safe, la lecture ici est OK)
        avg_timings = {
            stage: round((sum(samples) / len(samples)) * 1000, 2) if samples else 0.0
            for stage, samples in self.pipeline_total_timings_samples.items()
        }

        with self.active_tasks_lock:
            num_active_tasks_in_pool = len(self.active_tasks)

        # Vérification de la connectivité DB (utilise une connexion temporaire)
        kb_path_exists = KB_DB_PATH.exists() if KB_DB_PATH else False
        kb_is_connectable_and_valid = False
        db_config = self.config.get("knowledge_base", DEFAULT_CONFIG.get("knowledge_base", {}))
        db_timeout_report = db_config.get("db_timeout_seconds", 2) # Timeout court pour ce test

        if kb_path_exists and db_config.get("use_sqlite_db", True) and KB_DB_PATH:
            temp_conn_report_check: Optional[sqlite3.Connection] = None
            try:
                temp_conn_report_check = sqlite3.connect(f"file:{KB_DB_PATH}?mode=ro&immutable=1", uri=True, timeout=db_timeout_report)
                temp_conn_report_check.execute("SELECT count(*) FROM files LIMIT 1").fetchone() # Teste l'existence de la table 'files'
                kb_is_connectable_and_valid = True
            except sqlite3.Error as e_db_report_check:
                self.logger.warning(f"generate_self_report: Impossible de se connecter à la KB ou table 'files' non trouvée: {e_db_report_check}")
            except Exception as e_gen_report_check:
                self.logger.warning(f"generate_self_report: Erreur générique lors du test de connexion KB: {e_gen_report_check}")
            finally:
                if temp_conn_report_check:
                    try: temp_conn_report_check.close()
                    except sqlite3.Error: pass

        # Compter les fichiers en quarantaine (protégé par lock)
        with self.file_quarantine_lock:
            current_files_in_quarantine = sum(
                1 for info in self.file_quarantine.values()
                if info.get('quarantined_until', 0.0) > time.time()
            )

        # Lire la taille du cache (protégé par lock)
        with self.processed_files_cache_lock:
            current_processed_files_cache_size = len(self.processed_files_cache)

        report = {
            "module_name": MODULE_NAME, "version": MODULE_VERSION,
            "status": "running" if not self.running.is_set() else "stopping",
            "pid": os.getpid(),
            "uptime_seconds": round(uptime.total_seconds(), 2),
            "uptime_human": str(uptime).split('.')[0],
            "system_resources_snapshot": self.system_resources, # Données de psutil
            "configuration_summary": {
                "max_workers_effective": self.config.get("service_params", {}).get("max_workers"),
                "spacy_model_in_use": self.kb_instance.nlp_instance.meta['name'] if self.kb_instance and self.kb_instance.is_spacy_ready and hasattr(self.kb_instance.nlp_instance, 'meta') else "N/A ou non chargé",
                "spacy_active": bool(self.kb_instance and self.kb_instance.is_spacy_ready),
                "knowledge_base_path_exists": kb_path_exists,
                "knowledge_base_connectable_and_valid": kb_is_connectable_and_valid,
                "active_pipeline_steps_count": len(self.pipeline_steps_instances),
                "active_pipeline_steps_names": [s.__class__.__name__ for s in self.pipeline_steps_instances]
            },
            "performance_and_activity_stats": {
                "file_queue_current_size": len(self.file_queue),
                "file_queue_max_size": self.file_queue.maxlen if hasattr(self.file_queue, 'maxlen') else "N/A",
                "tasks_active_in_pool_approx": num_active_tasks_in_pool, # Tâches soumises et non acquittées
                "tasks_submitted_this_session": current_stats.get("tasks_submitted_to_pool", 0),
                "tasks_completed_this_session": current_stats.get("tasks_completed_from_pool", 0),
                "files_discovered_this_session": current_stats.get("files_discovered", 0),
                "files_processed_successfully_this_session": current_stats.get("files_processed_successfully", 0),
                "files_failed_processing_this_session": current_stats.get("files_failed", 0),
                "files_currently_in_quarantine": current_files_in_quarantine,
                "proposals_generated_this_session": current_stats.get("proposals_generated_total", 0),
                "active_improvements_applied_this_session": current_stats.get("active_improvements_count", 0),
                "processed_files_cache_current_size": current_processed_files_cache_size,
                "pipeline_stage_avg_execution_time_ms": avg_timings,
            },
            "timestamp_utc_report_generated": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # Écrire le rapport dans un fichier JSON pour consultation externe (optionnel mais utile)
        try:
            status_file_path = LOG_DIR / "cerveau_status.json" # LOG_DIR est une globale
            with open(status_file_path, 'w', encoding='utf-8') as f_status:
                json.dump(report, f_status, indent=2, ensure_ascii=False, default=str) # default=str pour les objets non sérialisables
            self.logger.debug(f"Rapport d'auto-analyse sauvegardé dans {status_file_path}")
        except Exception as e_write_status:
            self.logger.warning(f"Impossible d'écrire le fichier cerveau_status.json: {e_write_status}")

        # Loguer le rapport (peut être très verbeux, utiliser un niveau INFO ou AUDIT)
        # Pour AUDIT, on peut choisir de ne loguer qu'un résumé.
        # Ici, on logue tout pour l'instant.
        report_json_str = json.dumps(report, indent=2, ensure_ascii=False, default=str)
        self.logger.audit(f"RAPPORT D'AUTO-ANALYSE DU SERVICE CERVEAU:\n{report_json_str}")

        return report

    def _check_service_health(self) -> None:
        """
        Effectue des vérifications de santé périodiques sur les composants critiques du service
        et tente des actions correctives si nécessaire.
        """
        if self.running.is_set(): # Ne rien faire si le service est en train de s'arrêter
            self.logger.debug("HEALTH_CHECK: Service en cours d'arrêt, vérification de santé annulée.")
            return

        self.logger.info("HEALTH_CHECK: Début de la vérification de santé périodique du service...")
        all_ok = True # Flag pour suivre si tout est en ordre

        # --- 1. Vérifier l'état du ThreadPoolExecutor ---
        if self.executor:
            # hasattr(self.executor, '_broken') est une vérification d'attribut interne.
            # Une alternative serait de soumettre une tâche no-op et de voir si elle s'exécute.
            if hasattr(self.executor, '_shutdown') and self.executor._shutdown: # type: ignore[attr-defined]
                self.logger.warning("HEALTH_CHECK_EXECUTOR: ThreadPoolExecutor est marqué comme arrêté ('_shutdown' est True).")
                if not self.running.is_set(): # Ne pas redémarrer si on est en train de s'arrêter
                    self.logger.info("HEALTH_CHECK_EXECUTOR: Tentative de réinitialisation de l'executor car il semble arrêté.")
                    try:
                        self._initialize_executor() # Tenter de le recréer
                        self.logger.info("HEALTH_CHECK_EXECUTOR: ThreadPoolExecutor réinitialisé avec succès.")
                    except Exception as e_reinit_exec:
                        self.logger.critical(f"HEALTH_CHECK_EXECUTOR: Échec critique de la réinitialisation du ThreadPoolExecutor: {e_reinit_exec}", exc_info=True)
                        all_ok = False
            elif hasattr(self.executor, '_broken') and self.executor._broken: # type: ignore[attr-defined] # Moins probable mais possible
                self.logger.critical("HEALTH_CHECK_EXECUTOR: ThreadPoolExecutor est marqué comme 'broken'. Tentative de réinitialisation.")
                if not self.running.is_set():
                    try:
                        self._initialize_executor()
                        self.logger.info("HEALTH_CHECK_EXECUTOR: ThreadPoolExecutor réinitialisé suite à un état 'broken'.")
                    except Exception as e_reinit_exec_broken:
                        self.logger.critical(f"HEALTH_CHECK_EXECUTOR: Échec critique de la réinitialisation du ThreadPoolExecutor (broken): {e_reinit_exec_broken}", exc_info=True)
                        all_ok = False
            else:
                self.logger.debug("HEALTH_CHECK_EXECUTOR: ThreadPoolExecutor semble opérationnel.")
        else: # self.executor est None
            self.logger.warning("HEALTH_CHECK_EXECUTOR: ThreadPoolExecutor n'est pas initialisé. Tentative d'initialisation.")
            if not self.running.is_set():
                try:
                    self._initialize_executor()
                    self.logger.info("HEALTH_CHECK_EXECUTOR: ThreadPoolExecutor initialisé avec succès pendant la vérification de santé.")
                except Exception as e_init_exec_health:
                    self.logger.error(f"HEALTH_CHECK_EXECUTOR: Échec de l'initialisation du ThreadPoolExecutor pendant la vérification de santé: {e_init_exec_health}", exc_info=True)
                    all_ok = False

        # --- 2. Vérifier la connectivité de la base de données (si configurée pour être utilisée) ---
        kb_config_section = self.config.get("knowledge_base", DEFAULT_CONFIG.get("knowledge_base", {}))
        if KB_DB_PATH and kb_config_section.get("use_sqlite_db", True):
            temp_conn_health: Optional[sqlite3.Connection] = None
            db_timeout_health = kb_config_section.get("db_timeout_seconds", 2) # Timeout court pour ce test
            try:
                self.logger.debug(f"HEALTH_CHECK_DB: Test de connexion à {KB_DB_PATH}...")
                # Utiliser mode ro et immutable pour un test non intrusif
                temp_conn_health = sqlite3.connect(f"file:{KB_DB_PATH}?mode=ro&immutable=1", uri=True, timeout=db_timeout_health)
                temp_conn_health.execute("SELECT count(*) FROM files LIMIT 1").fetchone() # Teste l'existence et l'accès à la table 'files'
                self.logger.debug("HEALTH_CHECK_DB: Connexion et requête de test sur la KB réussies.")
            except sqlite3.OperationalError as e_op_db_health:
                 if "unable to open database file" in str(e_op_db_health).lower() or \
                    "no such table: files" in str(e_op_db_health).lower():
                     self.logger.error(f"HEALTH_CHECK_DB: Problème critique - Base de données SQLite non trouvée ou table 'files' manquante à {KB_DB_PATH}. Erreur: {e_op_db_health}")
                     all_ok = False
                 else:
                     self.logger.error(f"HEALTH_CHECK_DB: Erreur opérationnelle SQLite détectée: {e_op_db_health}.", exc_info=False)
                     all_ok = False # Marquer comme un problème potentiel
            except sqlite3.Error as e_db_health: # Autres erreurs SQLite
                self.logger.error(f"HEALTH_CHECK_DB: Problème de santé SQLite détecté: {e_db_health}.", exc_info=False)
                all_ok = False
            except Exception as e_gen_health_db: # Erreurs génériques
                self.logger.error(f"HEALTH_CHECK_DB: Erreur générique lors du test de connexion DB: {e_gen_health_db}", exc_info=True)
                all_ok = False
            finally:
                if temp_conn_health:
                    try: temp_conn_health.close()
                    except sqlite3.Error: pass
        else:
            self.logger.debug("HEALTH_CHECK_DB: Base de données SQLite non active ou chemin non configuré (pas de test effectué).")

        # --- 3. Vérifier les threads de surveillance de fichiers (Watchdog et Scan Périodique) ---
        service_params_cfg = self.config.get("service_params", DEFAULT_CONFIG.get("service_params", {}))
        watchdog_should_be_running = service_params_cfg.get("watchdog_enabled", True) and WATCHDOG_AVAILABLE

        if watchdog_should_be_running:
            if self.watchdog_observer and self.watchdog_observer.is_alive():
                self.logger.debug("HEALTH_CHECK_WATCHDOG: Observateur Watchdog est actif.")
            else:
                self.logger.warning("HEALTH_CHECK_WATCHDOG: Observateur Watchdog configuré mais non actif ! Tentative de redémarrage...")
                all_ok = False
                if not self.running.is_set():
                    # Arrêter l'ancien observer s'il existe mais n'est pas 'alive' (pour nettoyer)
                    if self.watchdog_observer:
                        try: self.watchdog_observer.stop(); self.watchdog_observer.join(timeout=1)
                        except Exception: pass
                    # Tenter de relancer la surveillance complète (qui inclut watchdog)
                    try:
                        self._initialize_file_monitoring() # Cette méthode (re)lance watchdog et le scanner si besoin
                        self.logger.info("HEALTH_CHECK_WATCHDOG: Tentative de redémarrage de la surveillance de fichiers (incluant Watchdog) effectuée.")
                    except Exception as e_restart_watchdog:
                        self.logger.error(f"HEALTH_CHECK_WATCHDOG: Échec du redémarrage de la surveillance de fichiers: {e_restart_watchdog}", exc_info=True)

        # Le scan périodique doit toujours tourner (soit comme principal, soit comme fallback)
        if self.scanner_thread and not self.scanner_thread.is_alive():
            self.logger.warning("HEALTH_CHECK_SCANNER: Le thread de scan périodique ne tourne plus ! Tentative de redémarrage.")
            all_ok = False
            if not self.running.is_set():
                try:
                    # S'assurer que l'ancien thread est bien terminé avant d'en créer un nouveau
                    self.scanner_thread.join(timeout=1) # Attendre un peu qu'il se termine
                    scan_interval_cfg = service_params_cfg.get("file_scan_interval_seconds", DEFAULT_CONFIG["service_params"]["file_scan_interval_seconds"])
                    self.scanner_thread = threading.Thread(target=self._periodic_scan, daemon=True, name="PeriodicScanner_Restarted_HealthCheck")
                    self.scanner_thread.start()
                    self.logger.info(f"HEALTH_CHECK_SCANNER: Thread de scan périodique redémarré (intervalle: {scan_interval_cfg}s).")
                except Exception as e_restart_scan_health:
                    self.logger.error(f"HEALTH_CHECK_SCANNER: Échec du redémarrage du thread de scan périodique: {e_restart_scan_health}", exc_info=True)
        elif not self.scanner_thread and not self.running.is_set(): # Si jamais il n'a pas été initialisé
             self.logger.warning("HEALTH_CHECK_SCANNER: Thread de scan périodique non initialisé. Tentative via _init_file_monitoring.")
             all_ok = False
             try:
                 self._initialize_file_monitoring() # Cela devrait le lancer
             except Exception as e_init_scan_health:
                 self.logger.error(f"HEALTH_CHECK_SCANNER: Échec de l'initialisation du scan périodique via _init_file_monitoring: {e_init_scan_health}", exc_info=True)
        else:
            self.logger.debug("HEALTH_CHECK_SCANNER: Thread de scan périodique semble actif (ou watchdog le remplace).")


        # --- 4. Autres vérifications potentielles ---
        # Exemple: Taille de la file d'attente si elle reste bloquée
        if len(self.file_queue) > 0:
            first_task_info = self.file_queue[0] # Regarder le premier élément sans le retirer
            time_in_queue = time.monotonic() - first_task_info.get('submit_time_mono', time.monotonic())
            # Définir un seuil, par exemple 10 fois l'intervalle de scan ou un temps absolu long
            max_time_in_queue_threshold = self.config.get("service_params", {}).get("file_scan_interval_seconds", 60) * 10
            if time_in_queue > max_time_in_queue_threshold:
                self.logger.warning(
                    f"HEALTH_CHECK_QUEUE: Le premier fichier '{first_task_info.get('path')}' est dans la file depuis {time_in_queue:.0f}s "
                    f"(seuil: {max_time_in_queue_threshold}s). Cela pourrait indiquer un blocage des workers ou de la backpressure excessive."
                )
                all_ok = False

        # Exemple: Espace disque
        # if PSUTIL_AVAILABLE:
        #     disk_usage = psutil.disk_usage(str(BASE_ALMA_DIR))
        #     if disk_usage.percent > 95:
        #         self.logger.critical(f"HEALTH_CHECK_DISK: Espace disque faible pour ALMA ({disk_usage.percent}% utilisé) !")
        #         all_ok = False

        if all_ok:
            self.logger.info("HEALTH_CHECK: Vérification de santé périodique terminée. Tous les indicateurs principaux sont OK.")
        else:
            self.logger.warning("HEALTH_CHECK: Vérification de santé périodique terminée. Au moins un indicateur a signalé un problème potentiel.")

    def start(self) -> None:
        """
        Démarre le service Cerveau, initialise les composants, et lance la boucle principale.
        """
        # --- 1. Préparation Initiale et Enregistrement ---
        self._setup_signal_handlers() # Configurer la gestion des signaux (Ctrl+C, SIGHUP, etc.)

        # Utiliser self.logger pour tous les messages de cette instance
        self.logger.audit(
            f"DÉMARRAGE SERVICE: {MODULE_NAME} v{MODULE_VERSION} (PID: {os.getpid()}). "
            f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, "
            f"OS: {platform.system()} {platform.release()}"
        )
        enregistrer_module(status="démarrage", message="Initialisation du service Cerveau.")

        # --- 2. Initialisation des Composants Critiques ---
        # Cette section est enveloppée dans un try-except pour attraper les erreurs d'initialisation majeures.
        try:
            # Création des répertoires essentiels (idempotent)
            # Utiliser les variables globales de chemin qui sont définies au niveau du module
            paths_to_ensure_exist = [
                CERVEAU_DIR, IMPROVEMENTS_DIR, ACTIVE_IMPROVEMENTS_DIR,
                LOG_DIR, CONNAISSANCE_DIR
            ]
            for dir_path in paths_to_ensure_exist:
                if dir_path: # S'assurer que le chemin est défini
                    dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info("Répertoires de travail vérifiés/créés.")

            # Initialiser le ThreadPoolExecutor (utilise self.config adapté)
            self._initialize_executor()

            # Initialiser la surveillance des fichiers (scan initial + watchdog/scanner périodique)
            # Cette méthode utilise self.config et les attributs d'exclusion.
            self._initialize_file_monitoring()

        except FileNotFoundError as e_dir_not_found:
            self.logger.critical(f"INIT_FAILURE: Répertoire essentiel non trouvé ou impossible à créer: {e_dir_not_found}. Le service ne peut pas démarrer.", exc_info=True)
            enregistrer_module(status="erreur_critique_init", message=f"Échec init (répertoire): {e_dir_not_found}")
            # Pas besoin d'arrêter l'executor ici car il n'a peut-être pas été créé si mkdir a échoué avant.
            return # Sortir de start()
        except Exception as e_critical_init:
            self.logger.critical(f"INIT_FAILURE: Échec critique lors de l'initialisation du service: {e_critical_init}. Le service ne peut pas démarrer.", exc_info=True)
            enregistrer_module(status="erreur_critique_init", message=f"Échec init (général): {e_critical_init}")
            if self.executor: # Tenter d'arrêter l'executor s'il a été partiellement créé
                try: self.executor.shutdown(wait=False, cancel_futures=(sys.version_info >= (3,9)))
                except Exception: pass
            return # Sortir de start()

        # --- 3. Démarrage Effectif de la Boucle Principale ---
        self.running.clear() # Marquer explicitement que le service est en cours d'exécution (non en arrêt)
        enregistrer_module(status="actif", message="Service Cerveau démarré et opérationnel.")
        self.logger.info("Service Cerveau entré dans sa boucle principale de traitement.")

        # Timers pour les tâches périodiques
        last_self_report_time_mono = time.monotonic()
        last_health_check_time_mono = time.monotonic()

        try:
            while not self.running.is_set(): # Boucle principale tant que l'arrêt n'est pas demandé

                # --- A. Log d'activité de la boucle (MAIN_LOOP_TICK) ---
                # Ces lectures sont généralement sûres sans lock pour un simple affichage,
                # mais pour une précision absolue, des locks pourraient être envisagés si
                # ces valeurs étaient utilisées pour des décisions critiques basées sur leur état exact.
                with self.active_tasks_lock:
                    current_active_tasks_in_pool = len(self.active_tasks)
                current_file_queue_size = len(self.file_queue) # len() sur deque est thread-safe

                # Vérifier l'état de l'executor de manière plus sûre
                executor_status_str = "Non prêt ou en arrêt"
                if self.executor:
                    # La vérification _shutdown est interne. Une meilleure façon est de voir s'il peut accepter des tâches,
                    # mais pour un log, c'est souvent suffisant.
                    if not (hasattr(self.executor, '_shutdown') and self.executor._shutdown): # type: ignore[attr-defined]
                        executor_status_str = "Prêt"

                # Lire la config pour la taille max de la file (peut changer si reload)
                current_queue_max_size = self.config.get("service_params", {}).get("file_queue_max_size", 1000)

                self.logger.debug(
                    f"MAIN_LOOP_TICK: File: {current_file_queue_size}/{current_queue_max_size}, "
                    f"Tasks Actives (soumises et non acquittées): {current_active_tasks_in_pool}, "
                    f"Executor: {executor_status_str}"
                )

                # --- B. Traitement des fichiers de la file ---
                if current_file_queue_size > 0 : # Optimisation : n'appeler que si la file n'est pas vide
                    self._process_file_from_queue() # Gère la soumission au pool et la backpressure

                # --- C. Tâches Périodiques (Rapport, Vérification de Santé) ---
                current_monotonic_time = time.monotonic()

                # Rapport d'auto-analyse
                self_report_interval_cfg = self.config.get("service_params", {}).get("self_report_interval_seconds", 3600)
                if current_monotonic_time - last_self_report_time_mono > self_report_interval_cfg:
                    self.logger.info(f"Génération du rapport d'auto-analyse (intervalle: {self_report_interval_cfg}s).")
                    self.generate_self_report() # Cette méthode est conçue pour être thread-safe dans ses lectures
                    last_self_report_time_mono = current_monotonic_time

                # Vérification de santé
                health_check_interval_cfg = self.config.get("service_params", {}).get("health_check_interval_seconds", 900) # Ex: 15 min
                if current_monotonic_time - last_health_check_time_mono > health_check_interval_cfg:
                    self.logger.info(f"Exécution de la vérification de santé (intervalle: {health_check_interval_cfg}s).")
                    self._check_service_health() # Gère ses propres accès et actions correctives
                    last_health_check_time_mono = current_monotonic_time

                # --- D. Pause Adaptative de la Boucle ---
                # Relire les compteurs pour la décision de pause, pour être à jour après _process_file_from_queue
                with self.active_tasks_lock:
                    active_tasks_for_wait = len(self.active_tasks)
                file_queue_for_wait = len(self.file_queue)

                # Pause plus courte si des tâches sont en cours ou en attente, plus longue sinon.
                # Les valeurs 0.1s et 0.5s sont des exemples, peuvent être configurables.
                loop_timeout_wait = 0.1 if file_queue_for_wait > 0 or active_tasks_for_wait > 0 else 0.5
                self.running.wait(timeout=loop_timeout_wait) # Attend un signal d'arrêt ou le timeout

        except Exception as e_main_loop_fatal: # Attraper les exceptions imprévues dans la boucle
            self.logger.critical(f"MAIN_LOOP_FATAL_ERROR: Erreur non gérée et fatale dans la boucle principale du service: {e_main_loop_fatal}", exc_info=True)
            enregistrer_module(status="erreur_boucle_fatale", message=f"Erreur boucle principale: {e_main_loop_fatal}")

        finally:
            # Ce bloc finally s'assure que stop() est appelé, que la boucle se termine normalement
            # (self.running.is_set() est True) ou à cause d'une exception.
            self.logger.info("Sortie de la boucle principale du service Cerveau.")
            # stop() gère l'enregistrement du statut "arrêté" ou "arrêt_en_cours".
            self.stop() # Assurer un arrêt propre de tous les composants

    def stop(self) -> None:
        """
        Arrête proprement le service Cerveau, ses threads de surveillance,
        le pool de workers, et ferme les ressources.
        """
        if self.running.is_set(): # Vérifie si l'arrêt est déjà en cours
            self.logger.info("STOP_SERVICE: Service Cerveau déjà en cours d'arrêt ou arrêté.")
            return

        self.logger.audit("STOP_SERVICE: Arrêt du service Cerveau demandé.")
        self.running.set() # Signaler à toutes les boucles (principale, scanner) de s'arrêter

        # Enregistrer l'état d'arrêt en cours (une seule fois au début de stop)
        enregistrer_module(status="arrêt_en_cours", message="Arrêt du service Cerveau initié.")

        # --- 1. Arrêter les Threads de Surveillance des Fichiers ---
        # (Watchdog et Scanner Périodique)
        # Ils vérifient self.running.is_set() et devraient se terminer.

        # Arrêter Watchdog (s'il est actif et a été initialisé)
        if self.watchdog_observer and hasattr(self.watchdog_observer, 'is_alive') and self.watchdog_observer.is_alive():
            self.logger.info("STOP_WATCHDOG: Tentative d'arrêt de l'observateur Watchdog...")
            try:
                self.watchdog_observer.stop()
                # Donner un timeout raisonnable pour que le thread de l'observer se termine
                self.watchdog_observer.join(timeout=5.0)
                if self.watchdog_observer.is_alive():
                    self.logger.warning("STOP_WATCHDOG_TIMEOUT: L'observateur Watchdog n'a pas pu être arrêté dans le délai de 5s.")
                else:
                    self.logger.info("STOP_WATCHDOG_SUCCESS: Observateur Watchdog arrêté avec succès.")
            except Exception as e_wd_stop:
                self.logger.warning(f"STOP_WATCHDOG_ERROR: Erreur lors de l'arrêt de l'observateur Watchdog: {e_wd_stop}", exc_info=True)
        elif self.watchdog_observer:
            self.logger.debug("STOP_WATCHDOG: Observateur Watchdog non actif ou non initialisé, pas d'arrêt nécessaire.")

        # Arrêter le Scanner Périodique (s'il est actif et a été initialisé)
        if self.scanner_thread and self.scanner_thread.is_alive():
            self.logger.info("STOP_SCANNER: Attente de la fin du thread de scan périodique...")
            # L'intervalle de scan est lu depuis la config pour le timeout du join
            scan_interval_cfg = self.config.get("service_params", {}).get("file_scan_interval_seconds", 60)
            try:
                # Donner un peu plus de temps que l'intervalle de scan pour qu'il termine son cycle actuel
                self.scanner_thread.join(timeout=float(scan_interval_cfg + 5))
                if self.scanner_thread.is_alive():
                    self.logger.warning(f"STOP_SCANNER_TIMEOUT: Le thread de scan périodique n'a pas pu être arrêté dans le délai de {scan_interval_cfg + 5}s.")
                else:
                    self.logger.info("STOP_SCANNER_SUCCESS: Thread de scan périodique arrêté avec succès.")
            except Exception as e_scan_stop:
                self.logger.warning(f"STOP_SCANNER_ERROR: Erreur lors de l'attente du thread de scan périodique: {e_scan_stop}", exc_info=True)
        elif self.scanner_thread:
            self.logger.debug("STOP_SCANNER: Thread de scan périodique non actif ou non initialisé, pas d'arrêt nécessaire.")

        # --- 2. Vider la File d'Attente des Tâches Non Soumises ---
        # Empêche la soumission de nouvelles tâches pendant l'arrêt de l'executor.
        if len(self.file_queue) > 0:
            self.logger.info(f"STOP_QUEUE_CLEAR: Vidage de {len(self.file_queue)} tâche(s) de la file d'attente principale (non soumises).")
            # Mettre à jour les stats pour ces fichiers non traités
            with self.stats_lock:
                self.stats["files_failed"] += len(self.file_queue) # Considérer comme échouées car non traitées
            self.file_queue.clear()

        # --- 3. Gérer les Tâches Actives et Arrêter le ThreadPoolExecutor ---
        if self.executor:
            self.logger.info("STOP_EXECUTOR: Arrêt du pool de workers (ThreadPoolExecutor)...")

            # Annuler les tâches qui sont dans self.active_tasks mais pas encore démarrées par l'executor
            # (celles qui sont dans la file interne de l'executor ou qui n'ont pas encore été pickées par un worker)
            with self.active_tasks_lock:
                cancelled_in_active_tasks = 0
                for fut in list(self.active_tasks.keys()): # Itérer sur une copie
                    if not fut.done() and not fut.running(): # Tâche ni terminée, ni en cours d'exécution
                        if fut.cancel(): # Tente d'annuler; retourne True si succès, False sinon
                            cancelled_in_active_tasks += 1
                            # Le callback _handle_task_result sera appelé avec future.cancelled() == True
                if cancelled_in_active_tasks > 0:
                    self.logger.info(f"STOP_EXECUTOR_CANCEL_ACTIVE: {cancelled_in_active_tasks} tâche(s) dans 'active_tasks' (non encore exécutées) annulée(s).")

            # shutdown(wait=True) attend que toutes les tâches soumises (qui n'ont pas été annulées
            # et qui ont déjà commencé leur exécution) se terminent.
            # cancel_futures=True (Python 3.9+) tente d'annuler les tâches en attente DANS la file interne de l'executor.
            cancel_futures_supported = sys.version_info >= (3, 9)
            self.logger.info(f"STOP_EXECUTOR_SHUTDOWN: Appel à executor.shutdown(wait=True, cancel_futures={cancel_futures_supported}). Attente de la fin des tâches en cours...")
            try:
                self.executor.shutdown(wait=True, cancel_futures=cancel_futures_supported) # type: ignore[call-arg]
                self.logger.info("STOP_EXECUTOR_SUCCESS: Pool de workers (ThreadPoolExecutor) arrêté proprement.")
            except Exception as e_executor_shutdown:
                self.logger.error(f"STOP_EXECUTOR_ERROR: Erreur lors de l'arrêt du ThreadPoolExecutor: {e_executor_shutdown}", exc_info=True)
        else:
            self.logger.info("STOP_EXECUTOR: ThreadPoolExecutor non initialisé, pas d'arrêt nécessaire.")

        # --- 4. Fermeture de la Connexion Principale à la KnowledgeBase (si elle était gérée par CerveauService) ---
        # Dans notre design actuel V20.5.1, CerveauService n'a plus de self.knowledge_base.conn.
        # self.kb_instance est juste une instance de la classe KnowledgeBase.
        # Les connexions DB sont gérées par les workers (_file_processing_worker)
        # ou temporairement par d'autres méthodes (comme _is_file_processable, generate_self_report).
        # Donc, pas de fermeture de connexion DB centralisée ici pour CerveauService.

        # --- 5. Générer un Dernier Rapport et Enregistrer l'État Final ---
        self.logger.info("Génération du rapport final d'auto-analyse avant l'arrêt complet...")
        self.generate_self_report() # Utilise self.stats qui devrait être à jour

        self.logger.audit("STOP_SERVICE_FINALIZED: Service Cerveau arrêté proprement.")
        enregistrer_module(status="arrêté", message="Service Cerveau arrêté proprement.")

        # --- 6. Fermer les Handlers du Logger Global du Module ---
        # Ceci est important pour s'assurer que les fichiers de log sont bien vidés et fermés,
        # surtout si le script est conçu pour être potentiellement relancé dans le même processus hôte
        # (moins courant pour un service, mais une bonne pratique).
        # 'logger' est la variable globale du module cerveau.py.
        self.logger.info("Fermeture des handlers du logger global du module Cerveau...")
        global_logger_instance = logging.getLogger(MODULE_NAME) # Obtenir le logger global

        # Copier la liste des handlers avant de la modifier
        handlers_to_close = global_logger_instance.handlers[:]
        for handler in handlers_to_close:
            self.logger.debug(f"Fermeture du handler de log: {handler}")
            try:
                handler.flush()
                handler.close()
                global_logger_instance.removeHandler(handler)
            except Exception as e_handler_close:
                # Utiliser print ici car le logger lui-même pourrait être dans un état instable
                print(f"WARNING (CerveauService.stop): Erreur lors de la fermeture du handler de log global '{handler}': {e_handler_close}", file=sys.stderr)

        self.logger.info("Tous les handlers du logger global ont été traités pour fermeture.")

# --- BLOC D'EXÉCUTION PRINCIPAL (if __name__ == "__main__":) ---
if __name__ == "__main__":
    # --- 1. Configuration Initiale du Logger pour la Console (Bootstrap Logging) ---
    # Ce handler de console est temporaire, pour les tout premiers messages avant que
    # le logger de fichier ne soit configuré par initialize_paths_and_logging.
    # Il sera retiré et remplacé par les handlers de fichier.
    # 'logger' est la variable globale du module, déjà définie.
    if not logger.handlers: # Configurer seulement si aucun handler n'existe
        _bootstrap_console_handler = logging.StreamHandler(sys.stdout)
        _bootstrap_console_formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)s - %(message)s', # Format simplifié pour le bootstrap
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
        _bootstrap_console_handler.setFormatter(_bootstrap_console_formatter)
        _bootstrap_console_handler.setLevel(logging.INFO) # Niveau INFO pour les messages de démarrage
        logger.addHandler(_bootstrap_console_handler)
        logger.setLevel(logging.INFO) # Niveau du logger lui-même
        logger.info(f"Logger de bootstrap pour console initialisé (temporaire).")

    logger.info(f"LANCEMENT DU SCRIPT: {MODULE_NAME} ({SCRIPT_NAME}) version {MODULE_VERSION}...")

    # --- 2. Vérification Préalable de l'Environnement (Optionnel mais Recommandé) ---
    # S'assurer que ALMA_BASE_DIR est accessible avant de lire la config
    # _base_alma_dir_resolved_for_globals est déjà défini au niveau du module.
    # On peut vérifier ici s'il est valide.
    if not _base_alma_dir_resolved_for_globals.is_dir():
        logger.critical(
            f"CRITICAL_ERROR_BASE_DIR: Le répertoire de base d'ALMA '{_base_alma_dir_resolved_for_globals}' "
            f"(déduit de ALMA_BASE_DIR ou valeur par défaut) n'est pas trouvé ou n'est pas un répertoire. "
            f"Vérifiez la variable d'environnement ALMA_BASE_DIR ou le chemin par défaut dans le script."
        )
        sys.exit(1) # Sortie immédiate si le répertoire de base n'est pas bon

    # --- 3. Chargement de la Configuration Globale de l'Application ---
    # APP_CONFIG (globale) sera remplie par la fusion de DEFAULT_CONFIG et cerveau_config.yaml.
    # CONFIG_FILE_PATH (globale) est utilisée ici.
    logger.info(f"Chargement de la configuration depuis: {CONFIG_FILE_PATH}...")
    try:
        APP_CONFIG = load_configuration(CONFIG_FILE_PATH, DEFAULT_CONFIG)
        logger.info("Configuration APP_CONFIG chargée avec succès.")
    except Exception as e_load_cfg:
        logger.critical(f"CRITICAL_ERROR_LOAD_CONFIG: Échec du chargement de la configuration principale: {e_load_cfg}", exc_info=True)
        sys.exit(1) # Sortie si la config ne peut être chargée

    # --- 4. Initialisation des Chemins Globaux et du Logger de Fichier ---
    # Cet appel est CRUCIAL. Il met à jour les variables globales de chemin
    # (CONNAISSANCE_DIR, LOG_DIR, etc.) avec les valeurs de APP_CONFIG
    # et configure le logger principal avec RotatingFileHandler (retirant le handler de bootstrap).
    logger.info("Initialisation des chemins globaux et du logger de fichier...")
    try:
        initialize_paths_and_logging(APP_CONFIG)
        logger.info("Chemins globaux et logger de fichier initialisés.")
    except Exception as e_init_paths_log:
        # Si cela échoue, on logue sur la console (via le bootstrap logger encore actif ou un print)
        # et on sort, car le logging fichier est compromis.
        bootstrap_logger_or_print = logger.handlers[0] if logger.handlers else print
        msg_crit = f"CRITICAL_ERROR_INIT_PATHS_LOGGING: Échec de l'initialisation des chemins/logger: {e_init_paths_log}"
        if isinstance(bootstrap_logger_or_print, logging.Handler):
            logger.critical(msg_crit, exc_info=True)
        else:
            print(msg_crit, file=sys.stderr)
            if hasattr(e_init_paths_log, '__traceback__'): # Pour Python 3
                 import traceback
                 traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # --- 5. Création des Répertoires de Travail Nécessaires ---
    # Utilise les variables globales de chemin (LOG_DIR, CERVEAU_DIR, etc.) maintenant mises à jour.
    logger.info("Vérification/Création des répertoires de travail...")
    try:
        paths_to_create_in_main = [
            LOG_DIR, CERVEAU_DIR, IMPROVEMENTS_DIR,
            ACTIVE_IMPROVEMENTS_DIR, CONNAISSANCE_DIR
        ]
        for dir_path_main in paths_to_create_in_main:
            if dir_path_main: # S'assurer que le chemin est défini (ex: KB_DB_PATH peut être None)
                dir_path_main.mkdir(parents=True, exist_ok=True)
        logger.info("Répertoires de travail vérifiés/créés avec succès.")
    except OSError as e_mkdirs_main:
        logger.critical(f"CRITICAL_ERROR_MKDIRS: Impossible de créer les répertoires de travail nécessaires: {e_mkdirs_main}", exc_info=True)
        sys.exit(1)

    # --- 6. Vérification de l'Import du Module Core (Diagnostic Précoce) ---
    # ALMA_CORE_AVAILABLE est une globale définie lors de l'import de .Core
    if not ALMA_CORE_AVAILABLE: # Utiliser le flag global
        logger.warning(
            "CORE_MODULE_UNAVAILABLE: Module Core (Cerveau.Core.core) non importé ou non disponible. "
            "Les fonctionnalités d'amélioration active et de liaison de connaissance avancée seront désactivées."
        )
    else:
        logger.info("CORE_MODULE_AVAILABLE: Module Core (Cerveau.Core.core) importé avec succès.")

    # --- 7. Instanciation et Démarrage du Service Cerveau ---
    # Toutes les configurations et les globales sont maintenant prêtes.
    logger.info(f"Instanciation du service CerveauService avec la configuration adaptée...")
    service_instance_main: Optional[CerveauService] = None # Pour le bloc finally
    try:
        service_instance_main = CerveauService(APP_CONFIG)
        logger.info("Service CerveauService instancié. Démarrage du service...")
        service_instance_main.start() # La méthode start() gère l'enregistrement du module "démarrage" et "actif"

    except KeyboardInterrupt: # Ctrl+C
        logger.info("INTERRUPTION_CLAVIER (__main__): Interruption clavier (Ctrl+C) détectée. Arrêt du service...")
        # service_instance_main.stop() sera appelé dans le bloc finally de service_instance_main.start()
        # ou dans le bloc finally ci-dessous si start() n'a pas été complètement atteint.
    except SystemExit as e_sys_exit_main: # sys.exit() appelé ailleurs
        logger.info(f"SYSTEM_EXIT (__main__): Sortie système demandée (code {e_sys_exit_main.code}). Arrêt du service...")
    except FileNotFoundError as e_fnf_service: # Si un chemin critique manque pour le service
        logger.critical(f"SERVICE_START_FILENOTFOUND_ERROR: Fichier/Répertoire essentiel manquant pour le démarrage du service: {e_fnf_service}", exc_info=True)
        enregistrer_module(status="erreur_critique_service", message=f"Fichier manquant: {e_fnf_service}")
    except Exception as e_main_service_fatal: # Toute autre erreur fatale pendant start()
        logger.critical(f"SERVICE_START_FATAL_ERROR: Erreur fatale non gérée lors du démarrage/exécution du service: {e_main_service_fatal}", exc_info=True)
        try:
            enregistrer_module(status="erreur_fatale_service", message=f"Erreur fatale service: {e_main_service_fatal}")
        except Exception as e_reg_fatal_service: # Si même l'enregistrement de l'erreur échoue
            logger.error(f"Impossible d'enregistrer l'erreur fatale du service: {e_reg_fatal_service}")

    finally:
        # Ce bloc finally s'assure que stop() est appelé si le service a été instancié
        # et que sa boucle principale a pu être interrompue avant son propre finally.
        logger.debug("__main__ finally: Vérification de l'état du service pour arrêt final si nécessaire.")
        if service_instance_main and \
           hasattr(service_instance_main, 'running') and \
           not service_instance_main.running.is_set(): # Si running n'est pas déjà à True (signifiant que stop a été appelé)
            logger.info("__main__ finally: Appel de service_instance.stop() pour un nettoyage final (si start() a été interrompu tôt).")
            try:
                service_instance_main.stop()
            except Exception as e_stop_in_finally:
                logger.error(f"Erreur lors de l'appel à stop() dans le bloc finally de __main__: {e_stop_in_finally}", exc_info=True)

        logger.info(f"FIN SCRIPT: Script {MODULE_NAME} ({SCRIPT_NAME}) terminé.")
        # Fermer tous les handlers de logging pour libérer les fichiers proprement.
        # Est particulièrement important si le script est relancé rapidement ou dans des tests.
        logging.shutdown()