# /home/toni/Documents/ALMA/Outils/alma_roadmap_manager.py

"""
---
name: alma_roadmap_manager.py
version: 0.2.0-alpha # Améliorations UI/UX, Parsing V2, Intégration spaCy de base
author: Toni & Gemini AI
description: Gestionnaire de Feuille de Route ALMA - Visualisation, Suivi et Analyse Sémantique des Objectifs.
role: Lire le Rapport Maître, extraire et analyser sémantiquement les tâches, permettre le suivi interactif.
type_execution: gui_app
état: en_développement
last_update: 2025-05-26 # Intégration améliorations V0.2.0
dossier: Outils
tags: [V20, roadmap, tasks, project_management, NLP, spaCy, UI, tkinter]
dependencies: [tkinter, Pillow (pour icônes graphiques si utilisées)]
optional_dependencies: [PyYAML (pour config future), transformers, torch (pour NLP avancé futur)]
---
"""

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox, scrolledtext, simpledialog
import os
import sys
from pathlib import Path
import json
import re # Pour le parsing initial basé sur regex
import hashlib
import traceback
import html # Pour décoder les entités HTML dans les tooltips ou détails
import logging
from typing import Dict, Any, List, Optional, Tuple, TypedDict

# --- Gestion des Dépendances Optionnelles pour l'UI et le NLP ---
try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
    print("INFO (ALMA Roadmap Manager): Bibliothèque Pillow (pour images) disponible.")
except ImportError:
    Image = None # type: ignore
    ImageTk = None # type: ignore
    PILLOW_AVAILABLE = False
    print("AVERTISSEMENT (ALMA Roadmap Manager): Bibliothèque Pillow non trouvée. Les icônes graphiques personnalisées ne seront pas disponibles (utilisation de placeholders texte/emoji).")
    print("                         Pour l'installer : pip install Pillow")

SPACY_AVAILABLE = False
spacy_nlp_sm = None # Instance pour le modèle spaCy léger (fr_core_news_sm)
try:
    import spacy
    SPACY_AVAILABLE = True
    # Le chargement du modèle se fera dans __init__ de la classe principale pour ne pas bloquer l'import
    print("INFO (ALMA Roadmap Manager): Bibliothèque spaCy disponible.")
except ImportError:
    spacy = None # type: ignore
    print(f"AVERTISSEMENT (ALMA Roadmap Manager): Bibliothèque spaCy non trouvée. L'analyse NLP des tâches sera limitée au parsing regex.")
    print("                         Pour l'installer : pip install spacy && python -m spacy download fr_core_news_sm")


# --- Définition des Constantes du Module ---
APP_NAME = "ALMA - Gestionnaire de Feuille de Route"
VERSION = "0.2.0-alpha"
# --- Fin des Constantes du Module ---


# --- Configuration de ALMA_BASE_DIR ---
ALMA_BASE_DIR_DEFAULT_FALLBACK = Path("/home/toni/Documents/ALMA").resolve()
_alma_base_dir_determined = False

# Priorité 1: Déduire du chemin du script actuel
try:
    if '__file__' in globals():
        current_script_path = Path(__file__).resolve()
        potential_alma_base_dir = current_script_path.parent.parent
        if (potential_alma_base_dir / "Cerveau").is_dir() and \
           (potential_alma_base_dir / "Connaissance").is_dir() and \
           (potential_alma_base_dir / "Outils").is_dir():
            ALMA_BASE_DIR = potential_alma_base_dir
            print(f"INFO ({APP_NAME}): ALMA_BASE_DIR déduit du chemin du script : {ALMA_BASE_DIR}")
            _alma_base_dir_determined = True
        else:
            print(f"DEBUG ({APP_NAME}): Déduction de ALMA_BASE_DIR via __file__ a échoué la validation de structure (attendu ALMA/Outils/...).")
    else:
        print(f"DEBUG ({APP_NAME}): __file__ non défini, impossible de déduire ALMA_BASE_DIR du chemin du script.")
except Exception as e_file_deduction:
    print(f"DEBUG ({APP_NAME}): Exception lors de la déduction de ALMA_BASE_DIR via __file__: {e_file_deduction}")

# Priorité 2: Variable d'environnement
if not _alma_base_dir_determined:
    try:
        env_alma_base_dir_str = os.environ["ALMA_BASE_DIR"]
        potential_alma_base_dir = Path(env_alma_base_dir_str).resolve()
        if (potential_alma_base_dir / "Cerveau").is_dir() and \
           (potential_alma_base_dir / "Connaissance").is_dir():
            ALMA_BASE_DIR = potential_alma_base_dir
            print(f"INFO ({APP_NAME}): ALMA_BASE_DIR récupéré depuis l'environnement : {ALMA_BASE_DIR}")
            _alma_base_dir_determined = True
        else:
            print(f"AVERTISSEMENT ({APP_NAME}): ALMA_BASE_DIR de l'environnement ('{env_alma_base_dir_str}') semble incorrect.")
    except KeyError:
        print(f"INFO ({APP_NAME}): Variable d'environnement ALMA_BASE_DIR non définie.")
    except Exception as e_env_deduction:
        print(f"DEBUG ({APP_NAME}): Exception lors de la lecture de ALMA_BASE_DIR depuis l'environnement: {e_env_deduction}")

# Priorité 3: Fallback Absolu Codé en Dur
if not _alma_base_dir_determined:
    ALMA_BASE_DIR = ALMA_BASE_DIR_DEFAULT_FALLBACK
    print(f"AVERTISSEMENT ({APP_NAME}): ALMA_BASE_DIR non déterminé. Utilisation du chemin de fallback absolu : {ALMA_BASE_DIR}")
    if not (ALMA_BASE_DIR / "Cerveau").is_dir() or not (ALMA_BASE_DIR / "Connaissance").is_dir():
        critical_error_msg = (
            f"ERREUR CRITIQUE ({APP_NAME}): Le chemin de fallback pour ALMA_BASE_DIR ({ALMA_BASE_DIR}) est invalide ou la structure du projet ALMA est incorrecte.\n"
            f"Veuillez vérifier la structure ou définir ALMA_BASE_DIR."
        )
        print(critical_error_msg)
        try: # Tenter d'afficher une messagebox même si c'est tôt
            root_temp_error = tk.Tk(); root_temp_error.withdraw()
            messagebox.showerror(f"{APP_NAME} - Erreur Configuration Critique", critical_error_msg)
            root_temp_error.destroy()
        except tk.TclError: pass # Ignorer si l'environnement graphique n'est pas encore prêt
        sys.exit(1)
# --- Fin Configuration ALMA_BASE_DIR ---

# --- Définition des Chemins Clés Basés sur ALMA_BASE_DIR ---
CONNAISSANCE_DIR = ALMA_BASE_DIR / "Connaissance"
RAPPORT_MAITRE_PATH = CONNAISSANCE_DIR / "RapportMaitreprogrammeCerveau.txt"
CERVEAU_DIR = ALMA_BASE_DIR / "Cerveau"
ROADMAP_STATUS_FILE_PATH = CERVEAU_DIR / "alma_roadmap_status.json"
# Chemin pour les icônes (si vous utilisez Pillow et des fichiers images)
ICONS_DIR = ALMA_BASE_DIR / "Outils" / "icons_roadmap" # Suggestion de chemin
# --- Fin Définition des Chemins Clés ---

# --- Typage pour les Tâches ---
# ... (RoadmapTask TypedDict reste ici, comme avant)
class RoadmapTask(TypedDict):
    """
    Structure de données représentant une tâche extraite du Rapport Maître
    et gérée par le Roadmap Manager.
    """
    # --- Informations d'Identification et de Source ---
    id: str                       # Identifiant unique de la tâche (ex: hash MD5 de son contenu/position)
    raw_line_number: int          # Numéro de ligne original dans le Rapport Maître (pour référence/débogage)
    source_document: str          # Nom du document source (ex: "RapportMaitreprogrammeCerveau.txt")

    # --- Contenu et Structure ---
    text: str                     # Texte principal/nettoyé de la tâche (ex: après la puce Markdown)
    full_text: str                # Ligne(s) brute(s) originale(s) du rapport pour cette tâche (contexte complet)
    section_path: List[str]       # Chemin hiérarchique des sections/titres menant à cette tâche
                                  # Ex: ["Phase 1", "Objectif X", "Sous-Objectif Y"]

    # --- Métadonnées de Gestion de Projet ---
    priority: Optional[str]       # Priorité extraite ou assignée (ex: "Haute", "Moyenne", "Basse", "Normale")
    status: str                   # Statut actuel de la tâche (ex: "à faire", "en cours", "accomplie", "bloquée", "en attente")
    notes: Optional[str]          # Notes ou commentaires ajoutés par l'utilisateur (Toni)
    # Potentiels ajouts futurs pour la gestion de projet :
    # assigned_to: Optional[str]
    # due_date: Optional[str] # Date d'échéance (format ISO)
    # estimated_effort: Optional[float] # En heures ou points
    # dependencies: List[str] # Liste d'ID d'autres tâches dont celle-ci dépend

    # --- Champs Populés par Analyse NLP (Parseur V2+ et au-delà) ---
    action_verb: Optional[str]          # Verbe principal décrivant l'action de la tâche (ex: "implémenter", "corriger")
    action_object: Optional[str]        # Objet principal de l'action (ex: "filtrage NER", "module X")
    mentioned_modules: List[str]      # Liste des modules ALMA explicitement mentionnés (ex: ["cerveau.py", "parlealma.py"])
    keywords: List[str]               # Mots-clés sémantiques extraits de la description de la tâche
    task_type_classified: Optional[str] # Type de tâche classifié par NLP (ex: "Développement", "BugFix", "Documentation", "Recherche", "Test", "Configuration")
    sentiment_task_desc: Optional[Dict[str, Any]] # Analyse de sentiment de la description de la tâche elle-même

    # --- Champs pour l'Interface Utilisateur (UI) ---
    icon_key: Optional[str]           # Clé pour rechercher une icône dans self.task_icons (ex: "task_dev", "phase_icon", "bug_icon")
    style_tags: List[str]             # Liste de tags pour appliquer des styles spécifiques dans le ttk.Treeview
                                      # (ex: ["priority_high", "status_inprogress", "module_parlealma"])
    # Le dernier élément de style_tags était coupé, je le complète :
    # style_tags: List[str]         # Pour le style dans le Treeview (ex: "priority_high", "status_inprogress")"status_inprogress")

# --- Définition des Chemins Clés ---
CONNAISSANCE_DIR = ALMA_BASE_DIR / "Connaissance"
RAPPORT_MAITRE_PATH = CONNAISSANCE_DIR / "RapportMaitreprogrammeCerveau.txt"
CERVEAU_DIR = ALMA_BASE_DIR / "Cerveau" # Pour le fichier d'état
ROADMAP_STATUS_FILE_PATH = CERVEAU_DIR / "alma_roadmap_status.json"

# --- Typage pour les Tâches ---
class RoadmapTask(TypedDict):
    id: str           # Identifiant unique (ex: hash du texte ou section_numero_ligne)
    text: str         # Le texte brut de la tâche
    full_text: str    # Le texte complet de la tâche avec son contexte (si parsé)
    source_document: str # Toujours RapportMaitreprogrammeCerveau.txt pour l'instant
    section_path: List[str] # Hiérarchie des titres ex: ["Phase 1", "Objectif X", "Sous-Objectif Y"]
    priority: Optional[str]
    status: str       # "à faire", "en cours", "accomplie"
    notes: Optional[str]
    raw_line_number: int # Pour référence

# --- Fonctions de Parsing (Amélioré pour V0.2.0-alpha) ---
def parse_rapport_maitre_v2(report_content: str, nlp_instance: Optional[Any]) -> List[RoadmapTask]:
    """
    Parse le contenu du Rapport Maître pour extraire une liste de tâches structurées.
    V0.2.0: Extraction améliorée basée sur Markdown, mots-clés, et NLP spaCy de base.
    """
    tasks: List[RoadmapTask] = []
    current_section_path: List[str] = []
    lines = report_content.splitlines()

    # Regex pour les titres Markdown (plus robustes pour les espaces et les # multiples)
    h_regex = re.compile(r"^\s*(#+)\s+([^#].*)$") # Capture le niveau de # et le titre

    # Regex pour les items de liste (tâches) - gère les indentations pour les sous-tâches
    task_item_regex = re.compile(r"^(\s*)[-\*]\s+(.*)$")

    # Regex pour les mots-clés dans les tâches (plus de flexibilité pour les séparateurs)
    priority_regex = re.compile(r"\b(Priorité|PRIORITÉ)\s*[:=\-]?\s*(Haute|Élevée|Moyenne|Normale|Basse)\b", re.IGNORECASE)
    module_regex = re.compile(r"\b(Module|MODULE|Composant)\s*[:=\-]?\s*([\w_.-]+(?:\.py)?)\b", re.IGNORECASE)
    livrable_regex = re.compile(r"\b(Livrable|LIVRABLE|Objectif Clé)\s*[:=\-]?\s*(.+)\b", re.IGNORECASE)
    # Le statut sera géré par le fichier alma_roadmap_status.json, pas extrait du texte ici.

    # Modules ALMA connus (pour aider à l'extraction de mentioned_modules)
    known_alma_modules = [
        "cerveau.py", "core.py", "explorateur_kb.py", "wiki_injector_gui.py",
        "alma_launcher.py", "sentiments_alma.py", "actuateurs_alma.py",
        "raisonneur.py", "parlealma.py", "alma_sync_agent.py", # Ajout de l'agent de synchro
        "alma_security_agent.py", "alma_youtube_agent.py", "alma_learning_interface.py" # Futurs
    ]


    current_task_buffer: Optional[Dict[str, Any]] = None # Pour gérer les tâches sur plusieurs lignes

    def finalize_current_task(buffer: Optional[Dict[str, Any]]):
        if buffer:
            # Générer l'ID basé sur le texte complet de la tâche
            buffer["id"] = hashlib.md5(
                f"{'/'.join(buffer['section_path'])}_{buffer['text']}_{buffer['raw_line_number']}".encode()
            ).hexdigest()[:16]

            # Initialiser tous les champs de RoadmapTask
            final_task: RoadmapTask = {
                "id": buffer["id"],
                "text": buffer["text"].strip(),
                "full_text": buffer["full_text"].strip(),
                "source_document": RAPPORT_MAITRE_PATH.name,
                "section_path": list(buffer["section_path"]),
                "priority": buffer.get("priority", "Normale"), # Défaut à Normale
                "status": "à faire", # Statut par défaut
                "notes": buffer.get("notes"),
                "raw_line_number": buffer["raw_line_number"],
                "action_verb": None,
                "action_object": None,
                "mentioned_modules": buffer.get("mentioned_modules", []),
                "keywords": [],
                "task_type_classified": None,
                "icon_key": "task_default", # Icône par défaut
                "style_tags": []
            }
            if final_task["priority"] == "Haute" or final_task["priority"] == "Élevée": final_task["style_tags"].append("priority_high")
            elif final_task["priority"] == "Moyenne": final_task["style_tags"].append("priority_medium")
            elif final_task["priority"] == "Basse": final_task["style_tags"].append("priority_low")

            # Analyse NLP de base avec spaCy si disponible
            if nlp_instance and final_task["text"]:
                try:
                    doc = nlp_instance(final_task["text"]) # Utiliser l'instance passée (ex: fr_core_news_sm)

                    # Verbe d'action (simple heuristique : premier verbe non auxiliaire)
                    for token in doc:
                        if token.pos_ == "VERB" and token.lemma_ not in ["être", "avoir"]: # Exclure auxiliaires courants
                            final_task["action_verb"] = token.lemma_
                            break

                    # Mots-clés (noms, adjectifs, verbes propres significatifs)
                    final_task["keywords"] = list(set(
                        token.lemma_.lower() for token in doc
                        if token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"] and
                           not token.is_stop and not token.is_punct and len(token.lemma_) > 2
                    ))[:5] # Top 5 uniques

                    # Modules ALMA mentionnés (en plus de la regex)
                    for ent in doc.ents: # Si le NER du modèle léger trouve quelque chose
                        if ent.label_ == "ORG" or ent.label_ == "PRODUCT" or ent.label_ == "WORK_OF_ART":
                            if ent.text in known_alma_modules and ent.text not in final_task["mentioned_modules"]:
                                final_task["mentioned_modules"].append(ent.text)
                    for token in doc: # Recherche par nom de fichier
                         if token.text in known_alma_modules and token.text not in final_task["mentioned_modules"]:
                                final_task["mentioned_modules"].append(token.text)


                    # Type de tâche (placeholder pour une classification future)
                    if any(kw in final_task["text"].lower() for kw in ["corriger", "bug", "erreur"]):
                        final_task["task_type_classified"] = "BugFix"
                        final_task["icon_key"] = "task_bug"
                    elif any(kw in final_task["text"].lower() for kw in ["implémenter", "développer", "créer", "ajouter"]):
                        final_task["task_type_classified"] = "Développement"
                        final_task["icon_key"] = "task_dev"
                    elif any(kw in final_task["text"].lower() for kw in ["documenter", "documentation", "rédiger rapport"]):
                        final_task["task_type_classified"] = "Documentation"
                        final_task["icon_key"] = "task_doc"
                    elif any(kw in final_task["text"].lower() for kw in ["rechercher", "investiguer", "analyser", "explorer"]):
                        final_task["task_type_classified"] = "Recherche"
                        final_task["icon_key"] = "task_research"
                    elif any(kw in final_task["text"].lower() for kw in ["tester", "valider"]):
                        final_task["task_type_classified"] = "Test"
                        final_task["icon_key"] = "task_test"


                except Exception as e_nlp_task_parse:
                    print(f"AVERTISSEMENT ({APP_NAME}): Erreur NLP mineure sur tâche (L{buffer['raw_line_number']}): {e_nlp_task_parse}")

            tasks.append(final_task)
            return True # Indique qu'un buffer a été finalisé
        return False


    for line_num, line_text in enumerate(lines):
        m_h = h_regex.match(line_text)
        m_task = task_item_regex.match(line_text)

        if m_h:
            finalize_current_task(current_task_buffer) # Finaliser la tâche précédente si elle existe
            current_task_buffer = None

            level = len(m_h.group(1)) # Nombre de '#'
            title = m_h.group(2).strip()
            if level == 1: current_section_path = [title]
            elif level == 2: current_section_path = current_section_path[:1] + [title]
            elif level == 3: current_section_path = current_section_path[:2] + [title]
            elif level == 4: current_section_path = current_section_path[:3] + [title]
            # Les titres H4 peuvent aussi être des tâches si on le décide,
            # pour l'instant, ils définissent juste le chemin de section.

        elif m_task: # Si c'est un item de liste
            task_content_after_bullet = m_task.group(2).strip()
            indent_level = len(m_task.group(1)) # Niveau d'indentation de la puce

            if not task_content_after_bullet: continue # Ignorer les puces vides

            # Si c'est un nouvel item de liste de premier niveau (ou si pas de buffer), on commence une nouvelle tâche
            if not current_task_buffer or indent_level == 0: # Approximation simple pour l'instant
                finalize_current_task(current_task_buffer) # Finaliser la tâche précédente

                priority_match = priority_regex.search(task_content_after_bullet)
                priority_val = priority_match.group(2).capitalize() if priority_match and len(priority_match.groups()) > 1 else "Normale"

                module_match = module_regex.search(task_content_after_bullet)
                mentioned_module_list = [module_match.group(2)] if module_match else []

                livrable_match = livrable_regex.search(task_content_after_bullet)
                notes_val = livrable_match.group(2).strip() if livrable_match else None

                current_task_buffer = {
                    "text": task_content_after_bullet,
                    "full_text": line_text.strip(), # Ligne complète initiale
                    "section_path": list(current_section_path),
                    "priority": priority_val,
                    "notes": notes_val,
                    "raw_line_number": line_num + 1,
                    "mentioned_modules": mentioned_module_list
                }
            elif current_task_buffer: # Si c'est une continuation de la tâche précédente (ligne indentée)
                current_task_buffer["text"] += "\n" + task_content_after_bullet # Ajouter au texte
                current_task_buffer["full_text"] += "\n" + line_text.strip() # Ajouter au full_text
                # Ré-évaluer la priorité et les modules si mentionnés dans les lignes suivantes
                priority_match_cont = priority_regex.search(task_content_after_bullet)
                if priority_match_cont: current_task_buffer["priority"] = priority_match_cont.group(2).capitalize()

                module_match_cont = module_regex.search(task_content_after_bullet)
                if module_match_cont and module_match_cont.group(2) not in current_task_buffer["mentioned_modules"]:
                    current_task_buffer["mentioned_modules"].append(module_match_cont.group(2))

        elif current_task_buffer and line_text.strip() and not m_h: # Si c'est une ligne non vide, pas un titre, et qu'on a un buffer de tâche
            # On considère que c'est une continuation de la description de la tâche en cours
            current_task_buffer["text"] += "\n" + line_text.strip()
            current_task_buffer["full_text"] += "\n" + line_text.strip()

        elif not line_text.strip() and current_task_buffer : # Ligne vide, pourrait signifier la fin d'une tâche multiligne
            finalize_current_task(current_task_buffer)
            current_task_buffer = None


    finalize_current_task(current_task_buffer) # Finaliser la toute dernière tâche s'il en reste une

    print(f"INFO ({APP_NAME}): {len(tasks)} tâches structurées extraites du Rapport Maître (Parseur V1.1 + NLP Base).")
    return tasks

# --- Fonctions de Gestion de l'État des Tâches ---
def load_roadmap_status() -> Dict[str, RoadmapTask]:
    """Charge l'état des tâches depuis le fichier JSON."""
    tasks_by_id: Dict[str, RoadmapTask] = {}
    if ROADMAP_STATUS_FILE_PATH.exists():
        try:
            with open(ROADMAP_STATUS_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list): # Ancien format peut-être
                    for task_dict in data:
                        if isinstance(task_dict, dict) and "id" in task_dict:
                            tasks_by_id[task_dict["id"]] = task_dict # type: ignore
                elif isinstance(data, dict): # Nouveau format {id: task_object}
                     tasks_by_id = data
            print(f"INFO ({APP_NAME}): État de {len(tasks_by_id)} tâches chargé depuis {ROADMAP_STATUS_FILE_PATH}.")
        except Exception as e:
            print(f"ERREUR ({APP_NAME}): Impossible de charger l'état des tâches depuis {ROADMAP_STATUS_FILE_PATH}: {e}")
    return tasks_by_id

def save_roadmap_status(tasks_by_id: Dict[str, RoadmapTask]):
    """Sauvegarde l'état actuel des tâches dans le fichier JSON."""
    try:
        CERVEAU_DIR.mkdir(parents=True, exist_ok=True) # S'assurer que le dossier Cerveau existe
        with open(ROADMAP_STATUS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(tasks_by_id, f, indent=2, ensure_ascii=False)
        print(f"INFO ({APP_NAME}): État des tâches sauvegardé dans {ROADMAP_STATUS_FILE_PATH}.")
    except Exception as e:
        print(f"ERREUR ({APP_NAME}): Impossible de sauvegarder l'état des tâches dans {ROADMAP_STATUS_FILE_PATH}: {e}")

# --- Classe Principale de l'Application GUI ---
class RoadmapManagerApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title(f"{APP_NAME} - v{VERSION}")
        self.root.geometry("1100x800") # Encore un peu plus large pour le confort
        self.root.minsize(850, 650)

        # --- Initialisation des Variables d'Instance ---
        self.tasks_from_report: List[RoadmapTask] = []
        self.tasks_status_by_id: Dict[str, RoadmapTask] = {}
        self.task_icons: Dict[str, Any] = {}
        self.nlp_spacy_roadmap: Optional[Any] = None
        self.current_selected_task_id: Optional[str] = None # Pour suivre la sélection

        # --- Configuration de l'Apparence et des Outils ---
        self._initialize_fonts_and_styles()
        self._initialize_nlp()
        self._load_icons()

        # --- Configuration de l'Interface Utilisateur ---
        self._setup_ui()

        # --- Chargement Initial des Données ---
        self.load_and_display_roadmap()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _initialize_fonts_and_styles(self):
        """Initialise les polices et les styles ttk pour l'application."""
        # Définition des couleurs (similaire à wiki_injector_gui.py pour cohérence)
        self.color_app_bg = "#F0F2F5" # Gris très clair pour le fond
        self.color_frame_bg = "#E4E6EB" # Gris un peu plus soutenu
        self.color_tree_bg = "#FFFFFF"
        self.color_text_primary = "#1C1E21" # Presque noir
        self.color_text_secondary = "#546E7A" # Un peu plus foncé pour meilleure lisibilité
        self.color_accent = "#0D6EFD" # Bleu Bootstrap plus vif
        self.color_accent_active = self.darken_color(self.color_accent, 0.85)
        self.color_button_text = "white"

        self.color_priority_high = "#DC3545" # Rouge Bootstrap
        self.color_priority_medium = "#FFC107" # Jaune Bootstrap
        self.color_priority_low = "#198754"  # Vert Bootstrap
        self.color_priority_normale = self.color_text_secondary

        self.color_status_accomplie = "#6C757D" # Gris Bootstrap
        self.color_status_en_cours = self.color_accent # Bleu pour en cours
        self.color_status_a_faire = self.color_text_primary # Couleur par défaut
        self.color_status_bloquee = "#B71C1C" # Rouge très foncé pour bloqué

        self.root.configure(bg=self.color_app_bg)

        font_family_wished = "Noto Sans" # ou "Segoe UI" si vous préférez
        font_family_fallback = tkfont.nametofont("TkDefaultFont").cget("family")
        actual_font_family = font_family_wished
        try:
            tkfont.Font(family=font_family_wished, size=10) # Test simple
            print(f"INFO ({APP_NAME}): Police primaire '{font_family_wished}' trouvée.")
        except tk.TclError:
            print(f"AVERTISSEMENT ({APP_NAME}): Police '{font_family_wished}' non trouvée. Utilisation de '{font_family_fallback}'.")
            actual_font_family = font_family_fallback

        # --- MODIFICATION ICI : Assigner à self.nom_police ---
        self.font_app_title = tkfont.Font(family=actual_font_family, size=18, weight="bold")
        self.font_frame_title = tkfont.Font(family=actual_font_family, size=12, weight="bold")
        self.font_text_normal = tkfont.Font(family=actual_font_family, size=10) # Assignation à self.
        self.font_text_small = tkfont.Font(family=actual_font_family, size=9)
        self.font_button = tkfont.Font(family=actual_font_family, size=10, weight="bold")
        self.font_tree_heading = tkfont.Font(family=actual_font_family, size=10, weight="bold")
        self.font_tree_item = tkfont.Font(family=actual_font_family, size=9)
        self.font_detail_label = tkfont.Font(family=actual_font_family, size=9, weight="bold")
        self.font_detail_text = tkfont.Font(family=actual_font_family, size=9)
        # self.font_status_bar = tkfont.Font(family=actual_font_family, size=8) # Si on ajoute une barre de statut

        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        self.style.configure(".", font=self.font_text_normal, background=self.color_app_bg, foreground=self.color_text_primary) # Maintenant self.font_text_normal existe
        self.style.configure("TFrame", background=self.color_app_bg)
        self.style.configure("TLabel", background=self.color_app_bg, foreground=self.color_text_primary, font=self.font_text_normal) # Utiliser self.font_text_normal
        self.style.configure("Header.TLabel", font=self.font_app_title, foreground=self.color_text_primary) # Utiliser self.font_app_title
        self.style.configure("FrameTitle.TLabel", font=self.font_frame_title, foreground=self.color_accent) # Utiliser self.font_frame_title

        self.style.configure("TButton", font=self.font_button, padding=(10, 6), relief=tk.RAISED, borderwidth=1) # Utiliser self.font_button
        self.style.map("TButton",
                       background=[('!disabled', self.color_accent), ('active', self.color_accent_active)],
                       foreground=[('!disabled', self.color_button_text)])

        self.style.configure("Treeview.Heading", font=self.font_tree_heading, padding=5, relief=tk.FLAT, background=self.color_frame_bg, borderwidth=0, lightcolor=self.color_frame_bg, darkcolor=self.color_frame_bg) # Utiliser self.font_tree_heading
        self.style.map("Treeview.Heading", relief=[('active','groove'),('pressed','sunken')])
        self.style.configure("Treeview", rowheight=25, font=self.font_tree_item, # Utiliser self.font_tree_item
                             background=self.color_tree_bg, fieldbackground=self.color_tree_bg, foreground=self.color_text_primary)

        self.style.configure("TLabelFrame", background=self.color_frame_bg, borderwidth=1, relief="solid", padding=10)
        self.style.configure("TLabelFrame.Label", background=self.color_frame_bg, foreground=self.color_text_primary, font=self.font_frame_title) # Utiliser self.font_frame_title

        self.style.configure("TScrollbar", troughcolor=self.color_frame_bg, background=self.color_accent, borderwidth=0, arrowsize=14)
        self.style.map("TScrollbar", background=[('active', self.color_accent_active)])

        # Styles pour le Treeview (tags)
        self.style.configure("section.Treeitem", font=(actual_font_family, 10, "bold"))
        self.style.configure("task.Treeitem")
        self.style.configure("status_accomplie.Treeitem", foreground=self.color_status_accomplie)
        self.style.configure("status_en_cours.Treeitem", foreground=self.color_status_en_cours, font=(actual_font_family, 9, "bold"))
        self.style.configure("status_a_faire.Treeitem", foreground=self.color_status_a_faire)
        self.style.configure("status_bloquée.Treeitem", foreground=self.color_status_bloquee, font=(actual_font_family, 9, "italic bold"))
        self.style.configure("priority_Haute.Treeitem", foreground=self.color_priority_high, font=(actual_font_family, 9, "bold"))
        self.style.configure("priority_Élevée.Treeitem", foreground=self.color_priority_high, font=(actual_font_family, 9, "bold"))
        self.style.configure("priority_Moyenne.Treeitem", foreground=self.color_priority_medium)
        self.style.configure("priority_Normale.Treeitem", foreground=self.color_priority_normale)
        self.style.configure("priority_Basse.Treeitem", foreground=self.color_priority_low)

        # Police pour le texte barré (overstrike)
        try:
            self.font_tree_item_strikethrough = tkfont.Font(family=actual_font_family, size=9, overstrike=True)
            self.style.configure("text_strikethrough.Treeitem", font=self.font_tree_item_strikethrough, foreground=self.color_status_accomplie)
        except tk.TclError:
            print(f"AVERTISSEMENT ({APP_NAME}): Style 'overstrike' non supporté. Utilisation de couleur pour tâches accomplies.")
            self.style.configure("text_strikethrough.Treeitem", foreground=self.color_status_accomplie) # Juste la couleur


    def _initialize_nlp(self):
        """
        Initialise le modèle spaCy (fr_core_news_sm par défaut) pour l'analyse
        des tâches du rapport. Tente de charger par nom, puis par chemin absolu en fallback.
        """
        # S'assurer que self.logger est disponible (doit être initialisé dans __init__)
        # Si __init__ n'a pas self.logger = logging.getLogger(f"{APP_NAME}.App"),
        # il faudrait l'ajouter ou utiliser print() ici.
        # Pour cet exemple, je suppose que self.logger existe.
        logger_instance = getattr(self, 'logger', logging.getLogger(f"{APP_NAME}.NLPInit"))


        if not (SPACY_AVAILABLE and spacy):
            self.nlp_spacy_roadmap = None
            logger_instance.info("spaCy non disponible globalement ou échec de l'import initial. Analyse NLP des tâches désactivée.")
            return

        model_to_load_name = "fr_core_news_sm"
        # Chemin absolu vers le modèle (ajustez si la version de fr_core_news_sm change)
        # Il est crucial que ce chemin pointe vers le répertoire du modèle versionné, ex: fr_core_news_sm-3.8.0
        CHEMIN_MODELE_SPACY_SM_SPECIFIQUE = ALMA_BASE_DIR / "venv/lib/python3.12/site-packages/fr_core_news_sm/fr_core_news_sm-3.8.0"

        nlp_instance_loaded: Optional[Any] = None # Pour stocker le modèle chargé

        # Déterminer les pipes à désactiver. Pour _sm, on peut souvent tout garder
        # car il est léger. Le parser peut être utile pour des analyses de tâches plus fines.
        # Si on veut vraiment alléger : disabled_pipes = ["ner", "parser"] (mais on perd ces capacités)
        # Pour l'instant, on ne désactive rien pour _sm pour maximiser ses capacités.
        disabled_pipes: List[str] = []

        # Tentative 1: Charger par nom de package (le plus courant)
        logger_instance.info(f"Tentative de chargement du modèle spaCy '{model_to_load_name}' par NOM (pipes désactivés: {disabled_pipes or 'aucun'})...")
        try:
            nlp_instance_loaded = spacy.load(model_to_load_name, disable=disabled_pipes)
            logger_instance.info(f"SUCCÈS: Modèle spaCy '{nlp_instance_loaded.meta['name']}' v{nlp_instance_loaded.meta['version']} chargé par NOM.")
        except OSError as e_load_name:
            logger_instance.warning(f"ÉCHEC du chargement de '{model_to_load_name}' par NOM: {type(e_load_name).__name__} - {e_load_name}")
            if "[E052]" in str(e_load_name): # Erreur spécifique "Can't find model directory"
                # Tentative 2: Charger par chemin absolu
                if CHEMIN_MODELE_SPACY_SM_SPECIFIQUE.exists() and CHEMIN_MODELE_SPACY_SM_SPECIFIQUE.is_dir():
                    logger_instance.info(f"Tentative de chargement de '{model_to_load_name}' par CHEMIN ABSOLU: {CHEMIN_MODELE_SPACY_SM_SPECIFIQUE}")
                    try:
                        nlp_instance_loaded = spacy.load(CHEMIN_MODELE_SPACY_SM_SPECIFIQUE, disable=disabled_pipes)
                        logger_instance.info(f"SUCCÈS: Modèle spaCy '{model_to_load_name}' (via chemin) chargé par CHEMIN ABSOLU.")
                    except Exception as e_load_path:
                        logger_instance.error(f"ERREUR: Impossible de charger '{model_to_load_name}' par CHEMIN ABSOLU '{CHEMIN_MODELE_SPACY_SM_SPECIFIQUE}': {type(e_load_path).__name__} - {e_load_path}")
                        traceback.print_exc() # Afficher la trace complète pour le débogage
                else:
                    logger_instance.error(f"ERREUR: Modèle '{model_to_load_name}' non trouvé par nom, et le chemin absolu configuré ({CHEMIN_MODELE_SPACY_SM_SPECIFIQUE}) est inexistant ou n'est pas un répertoire.")
            else: # Autre OSError non liée à E052
                logger_instance.error(f"ERREUR OS inattendue lors du chargement de '{model_to_load_name}' par nom: {type(e_load_name).__name__} - {e_load_name}")
                traceback.print_exc()
        except Exception as e_other_load: # Autres erreurs (ex: ImportError si une dépendance spaCy manque, ou ModelsNotFound si importé)
            logger_instance.error(f"ERREUR inattendue lors du chargement du modèle spaCy '{model_to_load_name}': {type(e_other_load).__name__} - {e_other_load}")
            traceback.print_exc()

        self.nlp_spacy_roadmap = nlp_instance_loaded

        if self.nlp_spacy_roadmap:
             logger_instance.info(f"Pipeline spaCy ACTIF pour Roadmap Manager: {self.nlp_spacy_roadmap.pipe_names}")
             # Optionnel: ajuster max_length si nécessaire, bien que pour _sm ce soit moins un problème
             # nlp_config_global = getattr(self, 'global_config', {}).get("nlp", {}) # Si on avait accès à une config globale
             # spacy_max_len_config = nlp_config_global.get("spacy_max_text_length", 1_000_000)
             # if hasattr(self.nlp_spacy_roadmap, 'max_length') and spacy_max_len_config > self.nlp_spacy_roadmap.max_length:
             #     try:
             #         self.nlp_spacy_roadmap.max_length = spacy_max_len_config
             #     except Exception as e_max_len:
             #         logger_instance.error(f"Impossible d'ajuster nlp_spacy_roadmap.max_length: {e_max_len}")
        else:
             logger_instance.error(f"ÉCHEC FINAL du chargement du modèle spaCy '{model_to_load_name}' pour Roadmap Manager. L'analyse NLP des tâches sera désactivée ou limitée.")

    def _load_icons(self):
        """
        Charge les icônes nécessaires pour l'interface.
        Utilise des placeholders texte/emoji par défaut, puis tente de charger des images
        si Pillow est disponible et que les fichiers images existent dans ICONS_DIR.
        """
        # Définition des placeholders texte/emoji par défaut
        default_icons = {
            "phase": "❖",         # Pour les sections de Phase
            "objectif": "➞",      # Pour les sections d'Objectif
            "sous_objectif": "↳", # Pour les sous-sections/sous-objectifs
            "task_default": "📄",   # Tâche générique
            "task_dev": "💻",      # Développement
            "task_bug": "🐞",      # Correction de bug
            "task_doc": "📖",      # Documentation
            "task_research": "🔬",  # Recherche/Analyse
            "task_test": "🧪",     # Test/Validation
            "task_config": "⚙️",   # Configuration/Paramétrage
            "task_ui": "🎨",       # Interface Utilisateur
            "task_refactor": "♻️", # Refactorisation
            "task_meeting": "👥",  # Réunion/Discussion
            # Icônes pour les statuts (seront préfixées au texte de la tâche ou utilisées pour colorer)
            "status_accomplie_prefix": "✅ ",
            "status_en_cours_prefix": "⏳ ",
            "status_a_faire_prefix": "⚪ ", # Ou une chaîne vide si on ne veut pas de préfixe
            "status_bloquée_prefix": "🚫 ",
            # Clés pour les images (si Pillow est utilisé)
            "img_phase": None,
            "img_objectif": None,
            "img_task_default": None,
            # ... ajouter d'autres clés pour les images spécifiques si nécessaire
        }
        self.task_icons = default_icons.copy() # Commencer avec les défauts

        if PILLOW_AVAILABLE and Image and ImageTk: # Image et ImageTk sont importés globalement si PILLOW_AVAILABLE
            print(f"INFO ({APP_NAME}): Pillow disponible. Tentative de chargement des icônes image depuis {ICONS_DIR}...")
            icon_files_to_load = {
                # Clé dans self.task_icons : Nom du fichier image (sans extension, suppose .png)
                "phase": "phase_icon",           # Sera self.task_icons["phase"] = ImageTk.PhotoImage(...)
                "objectif": "objectif_icon",
                "task_default": "task_default_icon",
                "task_dev": "task_dev_icon",
                "task_bug": "task_bug_icon",
                "task_doc": "task_doc_icon",
                "task_research": "task_research_icon",
                "task_test": "task_test_icon",
                "task_config": "task_config_icon",
                "task_ui": "task_ui_icon",
                "task_refactor": "task_refactor_icon",
                "task_meeting": "task_meeting_icon",
                # Icônes pour les statuts (si on veut des images au lieu des préfixes emoji)
                # "status_accomplie_img": "status_done_icon",
                # "status_en_cours_img": "status_inprogress_icon",
            }

            loaded_image_count = 0
            for icon_key, filename_stem in icon_files_to_load.items():
                icon_file_path = ICONS_DIR / f"{filename_stem}.png" # Suppose des .png
                if icon_file_path.exists() and icon_file_path.is_file():
                    try:
                        # Ouvrir, redimensionner (ex: 16x16), et créer l'objet PhotoImage
                        img = Image.open(icon_file_path).resize((16, 16), Image.Resampling.LANCZOS)
                        self.task_icons[icon_key] = ImageTk.PhotoImage(img) # Remplace le placeholder texte/emoji
                        loaded_image_count += 1
                    except Exception as e_img_load:
                        print(f"ERREUR ({APP_NAME}): Impossible de charger ou de traiter l'image {icon_file_path}: {e_img_load}")
                        # self.task_icons[icon_key] conservera sa valeur par défaut (texte/emoji)
                else:
                    print(f"DEBUG ({APP_NAME}): Fichier icône image {icon_file_path} non trouvé pour la clé '{icon_key}'. Utilisation du placeholder.")

            if loaded_image_count > 0:
                print(f"INFO ({APP_NAME}): {loaded_image_count} icônes image chargées avec succès.")
            else:
                print(f"INFO ({APP_NAME}): Aucune icône image personnalisée n'a été chargée. Utilisation des placeholders texte/emoji.")
        else:
            print(f"INFO ({APP_NAME}): Pillow non disponible. Utilisation des icônes texte/emoji par défaut.")

        # Assurer que toutes les clés d'icônes de base ont une valeur (même si c'est le placeholder)
        for key in ["phase", "objectif", "task_default", "task_dev", "task_bug", "task_doc", "task_research", "task_test", "task_config", "task_ui", "task_refactor", "task_meeting"]:
            if key not in self.task_icons:
                self.task_icons[key] = self.task_icons.get("task_default", "📄") # Fallback sur l'icône de tâche par défaut

        print(f"DEBUG ({APP_NAME}): Dictionnaire d'icônes finalisé: {list(self.task_icons.keys())}")

    def darken_color(self, hex_color, factor=0.85):
        if not isinstance(hex_color, str) or not hex_color.startswith('#') or len(hex_color) != 7: return "#333333"
        try:
            r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
            r, g, b = [max(0, min(255, int(c * factor))) for c in (r,g,b)]
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#333333"

    def _on_closing(self):
        if messagebox.askokcancel("Quitter", f"Voulez-vous quitter {APP_NAME} ?\nLes états des tâches modifiés sont sauvegardés automatiquement."):
            save_roadmap_status(self.tasks_status_by_id) # Sauvegarde finale pour être sûr
            self.root.destroy()

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text=APP_NAME, style="Header.TLabel", anchor="center").pack(pady=(0,15), fill=tk.X)

        # --- Panneau de Contrôle Supérieur ---
        control_top_frame = ttk.Frame(main_frame, padding="5")
        control_top_frame.pack(fill=tk.X, pady=(0,10))
        refresh_button = ttk.Button(control_top_frame, text="🔄 Rafraîchir depuis Rapport Maître", command=self.load_and_display_roadmap)
        refresh_button.pack(side=tk.LEFT, padx=(0,10))
        # (Place pour futurs filtres)

        # --- Zone d'Affichage des Tâches (Treeview) ---
        tree_container_frame = ttk.Frame(main_frame)
        tree_container_frame.pack(expand=True, fill=tk.BOTH, pady=(0,10))
        self.task_tree = ttk.Treeview(
            tree_container_frame,
            columns=("text", "priority", "status", "notes_preview"),
            show="tree headings"
        )
        self.task_tree.heading("#0", text="📂 Section / 📝 Tâche (ID Ligne)")
        self.task_tree.heading("text", text="Description")
        self.task_tree.heading("priority", text="Priorité")
        self.task_tree.heading("status", text="Statut")
        self.task_tree.heading("notes_preview", text="Aperçu Notes")

        self.task_tree.column("#0", width=320, minwidth=250, stretch=tk.NO, anchor="w")
        self.task_tree.column("text", width=400, minwidth=250, stretch=tk.YES, anchor="w")
        self.task_tree.column("priority", width=90, minwidth=70, stretch=tk.NO, anchor="center")
        self.task_tree.column("status", width=110, minwidth=90, stretch=tk.NO, anchor="center")
        self.task_tree.column("notes_preview", width=180, minwidth=120, stretch=tk.NO, anchor="w")

        vsb = ttk.Scrollbar(tree_container_frame, orient="vertical", command=self.task_tree.yview)
        hsb = ttk.Scrollbar(tree_container_frame, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_container_frame.grid_rowconfigure(0, weight=1)
        tree_container_frame.grid_columnconfigure(0, weight=1)
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.task_tree.bind("<Double-1>", self.on_tree_double_click)

        # --- Panneau de Détails de la Tâche Sélectionnée ---
        detail_lf = ttk.LabelFrame(main_frame, text="🔍 Détails de la Tâche Sélectionnée", padding="10")
        detail_lf.pack(fill=tk.BOTH, expand=False, pady=(5,10), ipady=5)
        self.task_detail_text = scrolledtext.ScrolledText(
            detail_lf, height=10, width=80, font=self.font_detail_text, wrap=tk.WORD,
            state=tk.DISABLED, relief=tk.SOLID, borderwidth=1,
            bg="#FEFEFE", fg=self.color_text_primary
        )
        self.task_detail_text.pack(pady=5, fill=tk.BOTH, expand=True)
        self.task_detail_text.tag_configure("bold", font=self.font_detail_label)
        self.task_detail_text.tag_configure("italic", font=(self.font_detail_text.cget("family"), self.font_detail_text.cget("size"), "italic"))
        self.task_detail_text.tag_configure("h_section", font=(self.font_detail_text.cget("family"), self.font_detail_text.cget("size")+1, "bold"), foreground=self.color_accent, spacing1=6, spacing3=3)
        self.task_detail_text.tag_configure("keyword_tag", background="#DDDDDD", foreground=self.color_text_primary, relief="raised", borderwidth=1, font=self.font_text_small)
        self.task_detail_text.tag_configure("module_tag", background=self.color_accent, foreground=self.color_button_text, relief="raised", borderwidth=1, font=self.font_text_small)


        # --- Panneau d'Actions sur la Tâche Sélectionnée ---
        action_frame = ttk.Frame(main_frame, padding="5")
        action_frame.pack(fill=tk.X, pady=5)
        action_buttons = [
            ("✔ Marquer Accomplie", self.mark_task_done),
            ("⏳ Marquer En Cours", self.mark_task_inprogress), # NOUVEAU BOUTON
            ("⚪ Marquer À Faire", self.mark_task_todo),
            ("✎ Ajouter/Mod. Note", self.add_edit_note_to_task)
        ]
        for text, cmd in action_buttons:
            ttk.Button(action_frame, text=text, command=cmd).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- Zone pour "Soumettre Texte Brut" ---
        submit_text_lf = ttk.LabelFrame(main_frame, text="📝 Soumettre Nouveau Texte pour Analyse de Tâches", padding="10")
        submit_text_lf.pack(fill=tk.X, pady=(10,5), ipady=5)
        self.raw_text_input = scrolledtext.ScrolledText(submit_text_lf, height=5, width=70, font=self.font_text_normal, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1, bg="#FEFEFE", fg=self.color_text_primary)
        self.raw_text_input.pack(pady=5, fill=tk.X, expand=True)
        analyze_text_button = ttk.Button(submit_text_lf, text="💡 Analyser et Suggérer Tâches", command=self.analyze_submitted_text)
        analyze_text_button.pack(pady=(5,0))

    def load_and_display_roadmap(self):
        print(f"INFO ({APP_NAME}): Chargement de la feuille de route...")
        self.current_selected_task_id = None # Réinitialiser la sélection
        self.on_task_select() # Vider le panneau de détails

        if not RAPPORT_MAITRE_PATH.exists():
            messagebox.showerror("Erreur Fichier", f"Rapport Maître introuvable:\n{RAPPORT_MAITRE_PATH}")
            return
        try:
            with open(RAPPORT_MAITRE_PATH, 'r', encoding='utf-8') as f: report_content = f.read()
        except Exception as e:
            messagebox.showerror("Erreur Lecture Rapport", f"Impossible de lire Rapport Maître:\n{e}"); return

        self.tasks_from_report = parse_rapport_maitre_v2(report_content, self.nlp_spacy_roadmap) # Appel à V2
        self.tasks_status_by_id = load_roadmap_status()

        for i, task_in_report in enumerate(self.tasks_from_report):
            task_id = task_in_report["id"]
            if task_id in self.tasks_status_by_id:
                # Prioriser le statut et les notes sauvegardés
                saved_task = self.tasks_status_by_id[task_id]
                self.tasks_from_report[i]["status"] = saved_task.get("status", task_in_report["status"])
                self.tasks_from_report[i]["notes"] = saved_task.get("notes", task_in_report["notes"])
                # Mettre à jour l'entrée dans tasks_status_by_id avec le texte frais du rapport
                self.tasks_status_by_id[task_id].update(self.tasks_from_report[i])
            else:
                self.tasks_status_by_id[task_id] = task_in_report

        self._populate_treeview()
        save_roadmap_status(self.tasks_status_by_id)
        print(f"INFO ({APP_NAME}): Feuille de route chargée et affichée ({len(self.tasks_from_report)} tâches du rapport).")

    def _populate_treeview(self):
        """Peuple le ttk.Treeview avec les tâches hiérarchisées, en utilisant les icônes et styles."""
        self.task_tree.delete(*self.task_tree.get_children()) # Vider l'arbre avant de repeupler

        # Dictionnaire pour garder une trace des iid des nœuds de section déjà créés
        # Clé: tuple du chemin de section (ex: ("Phase 1", "Objectif X"))
        # Valeur: iid de l'item du Treeview pour cette section
        section_nodes_iid_map: Dict[Tuple[str, ...], str] = {}

        for task_data in self.tasks_from_report:
            # --- 1. Création/Récupération des Nœuds de Section Parents ---
            parent_node_tree_id = "" # ID du parent dans le Treeview (racine si vide)

            # Construire le texte affiché pour la section actuelle de la tâche
            # et s'assurer que tous les nœuds parents existent dans le Treeview.
            # section_path_display_text = "" # Pour construire le texte du nœud section

            for i, section_name_raw in enumerate(task_data["section_path"]):
                section_name = section_name_raw.strip()
                current_path_as_tuple = tuple(task_data["section_path"][:i+1]) # Ex: ("Phase 1",) puis ("Phase 1", "Objectif X")

                # Déterminer l'icône pour ce niveau de section
                section_level_icon = ""
                if i == 0: # Phase (niveau 1 de section_path)
                    section_level_icon = self.task_icons.get("phase", "❖")
                elif i == 1: # Objectif (niveau 2)
                    section_level_icon = self.task_icons.get("objectif", "➞")
                else: # Sous-objectif ou plus profond
                    section_level_icon = self.task_icons.get("sous_objectif", "↳")

                section_display_name_with_icon = f"{section_level_icon} {section_name}"

                if current_path_as_tuple not in section_nodes_iid_map:
                    # Ce nœud de section n'existe pas encore, le créer
                    # Utiliser un hash du chemin de section pour un iid unique et stable pour les sections
                    section_iid_str = "_section_" + hashlib.md5("_".join(current_path_as_tuple).encode()).hexdigest()[:12]

                    # Insérer le nœud de section dans le Treeview
                    # La colonne "#0" (texte) affichera le nom de la section avec son icône.
                    # Les autres colonnes (values) sont vides pour les sections.
                    inserted_node_id = self.task_tree.insert(
                        parent_node_tree_id,  # Parent de ce nœud de section
                        "end",
                        iid=section_iid_str,
                        text=section_display_name_with_icon,
                        values=("", "", "", ""), # Valeurs vides pour les colonnes de tâche
                        tags=("section_style",), # Appliquer le style des sections
                        open=True # Déplier les sections par défaut (peut être changé)
                    )
                    section_nodes_iid_map[current_path_as_tuple] = inserted_node_id
                    parent_node_tree_id = inserted_node_id # Le nouveau parent pour le prochain niveau
                else:
                    # Le nœud de section existe déjà, récupérer son iid pour être le parent
                    parent_node_tree_id = section_nodes_iid_map[current_path_as_tuple]

            # --- 2. Préparation des Données de la Tâche pour l'Affichage ---
            task_text_for_display = task_data["text"][:100] + "..." if len(task_data["text"]) > 100 else task_data["text"]
            task_priority_display = task_data.get("priority", "Normale") or "Normale" # Assurer une valeur
            task_status_display = task_data.get("status", "à faire")

            notes_text = task_data.get("notes", "") or ""
            task_notes_preview = notes_text[:35] + "..." if len(notes_text) > 35 else notes_text

            # Déterminer l'icône de la tâche et le préfixe de statut
            task_icon_key = task_data.get("icon_key", "task_default") # Ex: "task_dev", "task_bug"
            task_type_icon = self.task_icons.get(task_icon_key, self.task_icons.get("task_default", "📄"))

            status_prefix_key = f"status_{task_status_display.replace(' ','_')}_prefix" # ex: "status_en_cours_prefix"
            status_icon_prefix = self.task_icons.get(status_prefix_key, "") # Préfixe emoji pour le statut

            # Colonne #0 pour la tâche : Préfixe Statut + Icône Type + Ligne + Début ID
            tree_item_text_col0 = f"{status_icon_prefix}{task_type_icon} L{task_data['raw_line_number']}: {task_data['id'][:8]}..."

            # --- 3. Construction des Tags de Style pour l'Item de Tâche ---
            current_style_tags = ["task.Treeitem"] # Style de base pour toutes les tâches

            # Tag pour le statut
            status_tag = f"status_{task_status_display.replace(' ','_')}.Treeitem"
            current_style_tags.append(status_tag)

            # Tag pour la priorité
            priority_value = task_data.get("priority")
            if priority_value:
                priority_tag = f"priority_{priority_value.replace(' ','_')}.Treeitem" # ex: priority_Haute.Treeitem
                current_style_tags.append(priority_tag)

            # Si la tâche est accomplie, ajouter un tag pour le style barré (overstrike)
            # Ce tag doit être configuré dans _initialize_fonts_and_styles
            if task_status_display == "accomplie":
                current_style_tags.append("text_strikethrough.Treeitem")


            # --- 4. Insertion de l'Item de Tâche dans le Treeview ---
            self.task_tree.insert(
                parent_node_tree_id, # Parent (dernier nœud de section créé/trouvé)
                "end",
                iid=task_data["id"], # ID unique de la tâche
                text=tree_item_text_col0, # Contenu pour la colonne #0
                values=(
                    task_text_for_display,
                    task_priority_display,
                    task_status_display, # Le statut textuel est toujours utile
                    task_notes_preview
                ),
                tags=tuple(current_style_tags), # Appliquer les tags de style
                open=False # Les tâches individuelles sont repliées par défaut
            )

        # --- 5. Configuration Finale des Tags de Style (appelée une fois après avoir peuplé) ---
        # Ceci est déjà dans _initialize_fonts_and_styles, mais s'assurer que les polices sont prêtes.
        # On peut ajouter des tags spécifiques ici si besoin.
        # Exemple pour le texte barré (si la police supporte 'overstrike')
        try:
            strikethrough_font = tkfont.Font(family=self.font_tree_item.cget("family"),
                                             size=self.font_tree_item.cget("size"),
                                             overstrike=True)
            self.task_tree.tag_configure("text_strikethrough.Treeitem", font=strikethrough_font, foreground=self.color_status_accomplie)
        except tk.TclError: # Au cas où 'overstrike' ne serait pas supporté par toutes les polices/thèmes
            print(f"AVERTISSEMENT ({APP_NAME}): Le style 'overstrike' pour les polices n'est pas supporté. Les tâches accomplies ne seront pas barrées.")
            self.task_tree.tag_configure("text_strikethrough.Treeitem", foreground=self.color_status_accomplie) # Juste la couleur

    def on_task_select(self, event=None):
        self.task_detail_text.config(state=tk.NORMAL)
        self.task_detail_text.delete("1.0", tk.END)

        selected_items = self.task_tree.selection()
        if not selected_items:
            self.task_detail_text.insert(tk.END, "Aucune tâche sélectionnée.")
            self.task_detail_text.config(state=tk.DISABLED)
            self.current_selected_task_id = None
            return

        item_id = selected_items[0]
        if item_id.startswith("_section_"):
            section_path_str = self.task_tree.item(item_id, "text").strip()
            self.task_detail_text.insert(tk.END, f"Section Sélectionnée:\n", "h_section")
            self.task_detail_text.insert(tk.END, section_path_str)
            self.current_selected_task_id = None
        elif item_id in self.tasks_status_by_id:
            self.current_selected_task_id = item_id
            task = self.tasks_status_by_id[item_id]

            self.task_detail_text.insert(tk.END, f"Détails de la Tâche (ID: {task['id']})\n", "h_section")
            self.task_detail_text.insert(tk.END, f"Ligne Rapport Maître: ", "bold"); self.task_detail_text.insert(tk.END, f"{task['raw_line_number']}\n")
            self.task_detail_text.insert(tk.END, f"Chemin Section: ", "bold"); self.task_detail_text.insert(tk.END, f"{' / '.join(task['section_path'])}\n")
            self.task_detail_text.insert(tk.END, f"Priorité: ", "bold"); self.task_detail_text.insert(tk.END, f"{task.get('priority', 'N/A')}\n")
            self.task_detail_text.insert(tk.END, f"Statut: ", "bold"); self.task_detail_text.insert(tk.END, f"{task['status']}\n\n")

            self.task_detail_text.insert(tk.END, "Description Complète (Rapport Maître):\n", "bold")
            self.task_detail_text.insert(tk.END, f"{task['full_text']}\n\n")

            if task.get('notes'):
                self.task_detail_text.insert(tk.END, "Notes de Toni:\n", "bold")
                self.task_detail_text.insert(tk.END, f"{task['notes']}\n\n")

            if task.get('action_verb'): self.task_detail_text.insert(tk.END, f"Action (NLP): ", "bold"); self.task_detail_text.insert(tk.END, f"{task['action_verb']}\n")
            if task.get('mentioned_modules'):
                self.task_detail_text.insert(tk.END, f"Modules ALMA (NLP): ", "bold")
                for mod in task['mentioned_modules']: self.task_detail_text.insert(tk.END, f"{mod} ", "module_tag"); self.task_detail_text.insert(tk.END, " ")
                self.task_detail_text.insert(tk.END, "\n")
            if task.get('keywords'):
                self.task_detail_text.insert(tk.END, f"Mots-Clés (NLP): ", "bold")
                for kw in task['keywords']: self.task_detail_text.insert(tk.END, f"{kw} ", "keyword_tag"); self.task_detail_text.insert(tk.END, " ")
                self.task_detail_text.insert(tk.END, "\n")
            if task.get('task_type_classified'): self.task_detail_text.insert(tk.END, f"Type Tâche (NLP): ", "bold"); self.task_detail_text.insert(tk.END, f"{task['task_type_classified']}\n")
        else:
            self.task_detail_text.insert(tk.END, "Tâche non trouvée dans les données d'état.")
            self.current_selected_task_id = None

        self.task_detail_text.config(state=tk.DISABLED)

    def on_tree_double_click(self, event):
        """
        Gère le double-clic sur un item du Treeview.
        Si l'item est une section (identifiée par un iid commençant par "_section_"),
        il inverse son état ouvert/fermé (déplié/replié).
        """
        # identify_row(event.y) retourne l'iid de l'item à la position y du clic
        item_id = self.task_tree.identify_row(event.y)

        if item_id: # S'assurer qu'un item a bien été cliqué
            # Vérifier si l'iid de l'item commence par "_section_", ce qui est notre convention
            # pour les nœuds de section que nous avons créés dans _populate_treeview.
            # Les tâches ont des iid qui sont des hashs MD5.
            if item_id.startswith("_section_"):
                try:
                    # Récupérer l'état actuel "open" de l'item (True si déplié, False si replié)
                    is_open = self.task_tree.item(item_id, "open")

                    # Inverser l'état "open"
                    # self.task_tree.item(item_id, open=0) # Pourrait aussi fonctionner pour fermer
                    # self.task_tree.item(item_id, open=1) # Pourrait aussi fonctionner pour ouvrir
                    self.task_tree.item(item_id, open=not is_open)

                    # Log de débogage optionnel
                    # self.logger.debug(f"Double-clic sur section {item_id}, nouvel état open: {not is_open}")
                except tk.TclError:
                    # Peut arriver si l'item_id n'est plus valide pour une raison quelconque,
                    # bien que peu probable si identify_row l'a retourné.
                    # print(f"DEBUG ({APP_NAME}): Erreur Tcl en accédant à l'item {item_id} lors du double-clic.")
                    pass # Ignorer silencieusement pour l'instant
            # else:
                # Si ce n'est pas une section, on pourrait vouloir faire autre chose au double-clic sur une tâche,
                # par exemple, ouvrir une fenêtre d'édition détaillée. Pour l'instant, on ne fait rien.
                # print(f"DEBUG ({APP_NAME}): Double-clic sur tâche {item_id}, aucune action définie.")
                # pass

    def get_selected_task_id_from_tree(self, show_messagebox_if_none: bool = True) -> Optional[str]: # Renommé
        # ... (code de get_selected_task_id, inchangé)
        selected_items = self.task_tree.selection()
        if not selected_items:
            if show_messagebox_if_none: messagebox.showinfo("Aucune Sélection", "Veuillez sélectionner une tâche.")
            return None
        item_id = selected_items[0]
        if item_id.startswith("_section_"):
            if show_messagebox_if_none: messagebox.showinfo("Sélection Invalide", "Veuillez sélectionner une tâche, pas une section.")
            return None
        return item_id


    def _update_task_status_and_refresh(self, task_id: str, new_status: str, note_suffix: Optional[str] = None):
        """Met à jour le statut d'une tâche, ajoute une note optionnelle, sauvegarde et rafraîchit."""
        if task_id in self.tasks_status_by_id:
            self.tasks_status_by_id[task_id]["status"] = new_status
            if note_suffix:
                current_note = self.tasks_status_by_id[task_id].get("notes", "") or ""
                # Éviter d'ajouter la date si déjà présente (simple vérification)
                if not note_suffix.strip() in current_note:
                    self.tasks_status_by_id[task_id]["notes"] = f"{current_note} {note_suffix}".strip()
            save_roadmap_status(self.tasks_status_by_id)
            self._populate_treeview() # Rafraîchit tout l'arbre
            self.on_task_select() # Met à jour le panneau de détails pour la tâche (potentiellement dé-sélectionnée)
            print(f"INFO ({APP_NAME}): Tâche '{task_id}' marquée comme {new_status}.")
        else:
            print(f"ERREUR ({APP_NAME}): Tentative de mise à jour du statut pour tâche ID inconnu: {task_id}")


    def mark_task_done(self):
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            self._update_task_status_and_refresh(task_id, "accomplie", f"(Accomplie le {datetime.date.today().isoformat()})")

    def mark_task_inprogress(self): # NOUVELLE MÉTHODE
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            self._update_task_status_and_refresh(task_id, "en cours", f"(Débutée le {datetime.date.today().isoformat()})")

    def mark_task_todo(self):
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            # On pourrait vouloir nettoyer la note des mentions "Accomplie" ou "Débutée"
            note = self.tasks_status_by_id[task_id].get("notes", "") or ""
            note_cleaned = re.sub(r"\s*\(Accomplie le .*?\)\s*","", note, flags=re.IGNORECASE)
            note_cleaned = re.sub(r"\s*\(Débutée le .*?\)\s*","", note_cleaned, flags=re.IGNORECASE).strip()
            self.tasks_status_by_id[task_id]["notes"] = note_cleaned if note_cleaned else None
            self._update_task_status_and_refresh(task_id, "à faire")


    def add_edit_note_to_task(self):
        task_id = self.get_selected_task_id_from_tree()
        if task_id and task_id in self.tasks_status_by_id:
            task_text_preview = self.tasks_status_by_id[task_id]['text'][:70] + "..." if len(self.tasks_status_by_id[task_id]['text']) > 70 else self.tasks_status_by_id[task_id]['text']
            current_notes = self.tasks_status_by_id[task_id].get("notes", "") or ""

            new_note = simpledialog.askstring(
                "Ajouter/Modifier Note",
                f"Note pour la tâche (L{self.tasks_status_by_id[task_id]['raw_line_number']} - ID: {task_id[:8]}...):\n'{task_text_preview}'",
                initialvalue=current_notes,
                parent=self.root,
                width=60 # Augmenter la largeur de la boîte de dialogue
            )
            if new_note is not None:
                self.tasks_status_by_id[task_id]["notes"] = new_note.strip() if new_note else None # Mettre None si vide
                save_roadmap_status(self.tasks_status_by_id)
                self._populate_treeview()
                self.on_task_select() # Pour rafraîchir le panneau de détails
                print(f"INFO ({APP_NAME}): Note mise à jour pour la tâche '{task_id}'.")

    def analyze_submitted_text(self):
        text_to_analyze = self.raw_text_input.get("1.0", tk.END).strip()
        if not text_to_analyze:
            messagebox.showinfo("Texte Vide", "Veuillez entrer du texte à analyser pour suggérer des tâches.")
            return

        if not self.nlp_spacy_roadmap:
            messagebox.showwarning("Analyse Limitée", "Le module spaCy n'est pas chargé. L'analyse du texte soumis sera très basique ou non effectuée.")
            # On pourrait quand même faire une tentative de parsing regex ici si spaCy est absent
            print(f"INFO ({APP_NAME}): Tentative d'analyse de texte soumis sans spaCy (non implémenté en détail).")
            return

        print(f"INFO ({APP_NAME}): Analyse du texte soumis (longueur: {len(text_to_analyze)} chars)...")
        # Ici, on appliquerait une logique similaire à parse_rapport_maitre_v2
        # pour trouver des phrases qui ressemblent à des tâches.
        # Pour l'instant, juste un placeholder.

        # Exemple de ce qu'on pourrait faire :
        # doc = self.nlp_spacy_roadmap(text_to_analyze)
        # suggested_tasks_texts = [sent.text for sent in doc.sents if len(sent.text.split()) > 5 and any(token.pos_ == "VERB" for token in sent)]

        # if suggested_tasks_texts:
        #     response = messagebox.askyesnocancel("Suggestions de Tâches",
        #                                       f"{len(suggested_tasks_texts)} tâches potentielles trouvées. Voulez-vous les ajouter à la feuille de route ?\n\n" +
        #                                       "\n - ".join(suggested_tasks_texts[:3]) + ("..." if len(suggested_tasks_texts)>3 else ""))
        #     if response is True:
        #         # Logique pour ajouter ces tâches à self.tasks_status_by_id et sauvegarder
        #         pass
        # else:
        #     messagebox.showinfo("Analyse Texte Soumis", "Aucune tâche évidente n'a pu être extraite de ce texte.")

        messagebox.showinfo("Fonctionnalité en Développement",
                              "L'analyse sémantique du texte soumis pour extraire et suggérer de nouvelles tâches\n"
                              "est en cours de développement (V2+ avec Transformers ou spaCy avancé).\n\n"
                              f"Texte soumis (pourrait être loggué ou traité basiquement):\n'{text_to_analyze[:100]}...'")
        print(f"INFO ({APP_NAME}): Texte soumis pour analyse : '{text_to_analyze[:100]}...'")



# --- Main Execution ---
if __name__ == "__main__":
    print(f"--- {APP_NAME} v{VERSION} ---")
    # Vérification de ALMA_BASE_DIR (déjà faite au niveau du module, mais on peut la renforcer ici)
    if not ALMA_BASE_DIR.is_dir() or not (ALMA_BASE_DIR / "Cerveau").is_dir():
        # Le message d'erreur critique est déjà géré plus haut si ALMA_BASE_DIR est invalide
        # On s'assure juste que le script ne continue pas si c'est le cas.
        # Cette condition est une double sécurité.
        print(f"ERREUR FATALE: ALMA_BASE_DIR ({ALMA_BASE_DIR}) n'est pas configuré correctement. Arrêt de {APP_NAME}.")
        sys.exit(1)

    if not RAPPORT_MAITRE_PATH.exists():
        critical_error_message = (
            f"ERREUR CRITIQUE: Le fichier Rapport Maître est introuvable à :\n{RAPPORT_MAITRE_PATH}\n\n"
            f"Ce fichier est essentiel pour le fonctionnement du Gestionnaire de Feuille de Route.\n"
            f"Veuillez vérifier son emplacement."
        )
        print(critical_error_message)
        temp_root_error_rm = tk.Tk(); temp_root_error_rm.withdraw()
        messagebox.showerror(f"{APP_NAME} - Fichier Manquant", critical_error_message)
        temp_root_error_rm.destroy(); sys.exit(1)

    root = None
    try:
        root = tk.Tk()
        app = RoadmapManagerApp(root)
        root.mainloop()
        print(f"INFO ({APP_NAME}): Terminé proprement.")
    except Exception as e_main_app:
        error_title = f"{APP_NAME} - Erreur d'Exécution"
        error_details = f"Une erreur inattendue est survenue:\n\n{type(e_main_app).__name__}: {e_main_app}"
        print(f"ERREUR CRITIQUE DANS {APP_NAME}: {error_title}\n{error_details}")
        traceback.print_exc()
        if root and root.winfo_exists():
            try: messagebox.showerror(error_title, error_details)
            except tk.TclError: pass
        else:
            temp_root_error_runtime = tk.Tk(); temp_root_error_runtime.withdraw()
            messagebox.showerror(error_title, error_details)
            temp_root_error_runtime.destroy()
        sys.exit(1)
