# /home/toni/Documents/ALMA/Outils/alma_roadmap_manager.py

"""
---
name: alma_roadmap_manager.py
version: 0.3.0 # V20 NLP Enhanced (Logging, Config, spaCy _lg, Parsing V2.1, UI/UX V0.2.1)
author: Toni & Gemini AI
description: Gestionnaire de Feuille de Route ALMA - Visualisation, Suivi et Analyse Sémantique des Objectifs.
role: Lire le Rapport Maître, extraire et analyser sémantiquement les tâches, permettre le suivi interactif.
type_execution: gui_app
état: en développement actif
last_update: 2025-05-26 # Passage à V0.3.0
dossier: Outils
tags: [V20, roadmap, tasks, project_management, NLP, spaCy, UI, tkinter, logging]
dependencies: [tkinter, Pillow (pour icônes graphiques si utilisées), spacy]
optional_dependencies: [PyYAML (pour config future), transformers, torch (pour NLP avancé futur)]
---
"""

import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox, scrolledtext, simpledialog
import os
import sys
from pathlib import Path
import json
import re
import hashlib
import traceback
import html
import logging # Essentiel pour la journalisation V20
import datetime # Ajouté pour les notes datées
from typing import Dict, Any, List, Optional, Tuple, TypedDict

# --- Définition des Constantes du Module ---
APP_NAME = "ALMA - Gestionnaire de Feuille de Route"
VERSION = "0.3.0"
# --- Fin des Constantes du Module ---

# --- Configuration du Logger pour ce Module ---
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG) # Configurer le niveau par défaut (DEBUG pour le développement)
if not logger.handlers: # Éviter les handlers multiples si le script est rechargé/réexécuté
    _ch_roadmap = logging.StreamHandler(sys.stdout) # Sortie console
    _formatter_roadmap = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)-8s - %(module)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    _ch_roadmap.setFormatter(_formatter_roadmap)
    logger.addHandler(_ch_roadmap)
    logger.info(f"Logger pour {APP_NAME} v{VERSION} initialisé.")
# --- Fin Logger Configuration ---

# --- Gestion des Dépendances Optionnelles pour l'UI et le NLP ---
PILLOW_AVAILABLE = False
Image, ImageTk = None, None
try:
    from PIL import Image as PIL_Image, ImageTk as PIL_ImageTk
    Image = PIL_Image
    ImageTk = PIL_ImageTk
    PILLOW_AVAILABLE = True
    logger.info("Bibliothèque Pillow (pour images) disponible.")
except ImportError:
    logger.warning("Bibliothèque Pillow non trouvée. Les icônes graphiques personnalisées ne seront pas disponibles.")
    logger.info("Pour l'installer : pip install Pillow")

SPACY_AVAILABLE = False
spacy_module_alias = None # Pour stocker le module spaCy importé
try:
    import spacy as spacy_imported_module
    spacy_module_alias = spacy_imported_module
    SPACY_AVAILABLE = True
    logger.info("Bibliothèque spaCy disponible.")
except ImportError:
    logger.warning("Bibliothèque spaCy non trouvée. L'analyse NLP des tâches sera limitée au parsing regex.")
    logger.info("Pour l'installer : pip install spacy && python -m spacy download fr_core_news_sm && python -m spacy download fr_core_news_lg")
spacy = spacy_module_alias # Alias global pour le reste du fichier

# --- Configuration de ALMA_BASE_DIR ---
ALMA_BASE_DIR_DEFAULT_FALLBACK = Path("/home/toni/Documents/ALMA").resolve()
_alma_base_dir_determined = False
ALMA_BASE_DIR: Path

try:
    if '__file__' in globals() and globals()['__file__'] is not None:
        current_script_path = Path(__file__).resolve()
        potential_alma_base_dir = current_script_path.parent.parent
        if (potential_alma_base_dir / "Cerveau").is_dir() and \
           (potential_alma_base_dir / "Connaissance").is_dir() and \
           (potential_alma_base_dir / "Outils").is_dir() and \
           (potential_alma_base_dir / "venv").is_dir():
            ALMA_BASE_DIR = potential_alma_base_dir
            logger.info(f"ALMA_BASE_DIR déduit du chemin du script : {ALMA_BASE_DIR}")
            _alma_base_dir_determined = True
        else:
            logger.debug(f"Déduction de ALMA_BASE_DIR via __file__ a échoué la validation de structure.")
    else:
        logger.debug("__file__ non défini ou None, impossible de déduire ALMA_BASE_DIR du script.")
except Exception as e_file_deduction:
    logger.debug(f"Exception lors de la déduction de ALMA_BASE_DIR via __file__: {e_file_deduction}")

if not _alma_base_dir_determined:
    try:
        env_alma_base_dir_str = os.environ["ALMA_BASE_DIR"]
        potential_alma_base_dir = Path(env_alma_base_dir_str).resolve()
        if (potential_alma_base_dir / "Cerveau").is_dir() and \
           (potential_alma_base_dir / "Connaissance").is_dir():
            ALMA_BASE_DIR = potential_alma_base_dir
            logger.info(f"ALMA_BASE_DIR récupéré depuis l'environnement : {ALMA_BASE_DIR}")
            _alma_base_dir_determined = True
        else:
            logger.warning(f"ALMA_BASE_DIR de l'environnement ('{env_alma_base_dir_str}') semble incorrect.")
    except KeyError:
        logger.info("Variable d'environnement ALMA_BASE_DIR non définie.")
    except Exception as e_env_deduction:
        logger.debug(f"Exception lors de la lecture de ALMA_BASE_DIR depuis l'environnement: {e_env_deduction}")

if not _alma_base_dir_determined:
    ALMA_BASE_DIR = ALMA_BASE_DIR_DEFAULT_FALLBACK
    logger.warning(f"ALMA_BASE_DIR non déterminé. Utilisation du chemin de fallback : {ALMA_BASE_DIR}")
    if not (ALMA_BASE_DIR / "Cerveau").is_dir() or not (ALMA_BASE_DIR / "Connaissance").is_dir():
        critical_error_msg = (
            f"Le chemin de fallback pour ALMA_BASE_DIR ({ALMA_BASE_DIR}) est invalide ou la structure ALMA est incorrecte.\n"
            f"Veuillez définir ALMA_BASE_DIR ou corriger la structure."
        )
        logger.critical(critical_error_msg)
        try:
            root_temp_error = tk.Tk(); root_temp_error.withdraw()
            messagebox.showerror(f"{APP_NAME} - Erreur Configuration Critique", critical_error_msg)
            root_temp_error.destroy()
        except tk.TclError: pass
        sys.exit(1)
# --- Fin Configuration ALMA_BASE_DIR ---

# --- Définition des Chemins Clés Basés sur ALMA_BASE_DIR ---
CONNAISSANCE_DIR = ALMA_BASE_DIR / "Connaissance"
RAPPORT_MAITRE_PATH = CONNAISSANCE_DIR / "RapportMaitreprogrammeCerveau.txt"
CERVEAU_DIR = ALMA_BASE_DIR / "Cerveau"
ROADMAP_STATUS_FILE_PATH = CERVEAU_DIR / "alma_roadmap_status.json"
ICONS_DIR = ALMA_BASE_DIR / "Outils" / "icons_roadmap"
# --- Fin Définition des Chemins Clés ---

# --- Typage pour les Tâches (RoadmapTask TypedDict) ---
class RoadmapTask(TypedDict):
    """
    Structure de données représentant une tâche extraite du Rapport Maître
    et gérée par le Roadmap Manager.
    """
    # --- Informations d'Identification et de Source ---
    id: str
    raw_line_number: int
    source_document: str

    # --- Contenu et Structure ---
    text: str
    full_text: str
    section_path: List[str]

    # --- Métadonnées de Gestion de Projet ---
    priority: Optional[str]
    status: str # "à faire", "en cours", "accomplie", "bloquée", "en attente"
    notes: Optional[str]
    # Potentiels ajouts futurs :
    # assigned_to: Optional[str]
    # due_date: Optional[str] # Date d'échéance (format ISO)
    # estimated_effort: Optional[float] # En heures ou points
    # dependencies: List[str] # Liste d'ID d'autres tâches

    # --- Champs Populés par Analyse NLP ---
    action_verb: Optional[str]      # Verbe principal (lemme)
    action_object: Optional[str]    # Objet principal de l'action
    mentioned_modules: List[str]  # Modules ALMA ou fichiers .py/.sh
    keywords: List[str]           # Mots-clés sémantiques (lemmes)
    task_type_classified: Optional[str] # Ex: "Développement", "BugFix", "Documentation"
    sentiment_task_desc: Optional[Dict[str, Any]] # Ex: {"label": "neutre", "score": 0.1}

    # --- Champs pour l'Interface Utilisateur (UI) ---
    icon_key: Optional[str]       # Clé pour self.task_icons (ex: "task_dev")
    style_tags: List[str]       # Tags pour le style ttk.Treeview
# --- Fin Typage pour les Tâches ---

# Les fonctions de parsing (parse_rapport_maitre_v2) et de gestion d'état (load/save_roadmap_status)
# ainsi que la classe RoadmapManagerApp viendront après ce bloc.
# (Suite du Bloc 1 - Imports, Constantes, TypedDict, Logger)

# --- Fonctions de Parsing (Amélioré pour V0.3.0 - V20 NLP Enhanced) ---
def parse_rapport_maitre_v2(report_content: str, nlp_instance: Optional[Any]) -> List[RoadmapTask]:
    """
    Parse le contenu du Rapport Maître pour extraire une liste de tâches structurées.
    V0.3.0: Utilise fr_core_news_lg (si disponible via nlp_instance) pour une meilleure
            extraction NLP (verbe/objet via dépendances, NER plus précis pour modules).
    """
    logger.info(f"Début du parsing du Rapport Maître (longueur: {len(report_content)} chars).")
    tasks: List[RoadmapTask] = []
    current_section_path: List[str] = []
    lines = report_content.splitlines()

    # Regex pour les titres Markdown (H1 à H4)
    h_regex = re.compile(r"^\s*(#{1,4})\s+([^#].*)$") # Niveaux 1 à 4
    # Regex pour les items de liste (tâches)
    task_item_regex = re.compile(r"^(\s*)[-\*]\s+(.*)$")

    # Regex pour extraire les métadonnées des tâches
    priority_regex = re.compile(r"\b(Priorité|PRIORITÉ)\s*[:=\-]?\s*(Haute|Élevée|Moyenne|Normale|Basse)\b", re.IGNORECASE)
    module_regex = re.compile(
        r"""\b(?:Module|MODULE|Composant|SCRIPT|Fichier|Classe|Service)\s*[:=\-]?\s*
        (
            (?:[\w_.-]+[/\\:])*     # Chemin optionnel
            [\w_.-]+                # Nom principal
            (?:\.py|\.sh|\.md|\.txt|\.yaml|\.json)? # Extension optionnelle
        )\b""",
        re.IGNORECASE | re.VERBOSE
    )
    livrable_regex = re.compile(r"\b(Livrable|LIVRABLE|Objectif Clé|Résultat Attendu|Sortie|Cible)\s*[:=\-]?\s*(.+)\b", re.IGNORECASE)

    # Liste de modules/fichiers/classes ALMA connus pour aider le NER et le filtrage regex
    known_alma_components_patterns_str = [
        r"cerveau\.py", r"Core/core\.py", r"core\.py", r"explorateur_kb\.py", r"wiki_injector_gui\.py",
        r"alma_launcher\.py", r"sentiments_alma\.py", r"actuateurs_alma\.py",
        r"raisonneur\.py", r"parlealma\.py", r"alma_sync_agent\.py",
        r"alma_security_agent\.py", r"alma_youtube_agent\.py", r"alma_learning_interface\.py",
        r"RapportMaitreprogrammeCerveau\.txt", r"cerveau_config\.yaml", r"launcher_config\.yaml",
        r"KnowledgeBase", r"TextImprover", r"KnowledgeLinker", r"NLUEngine", r"DialogueManager",
        r"CerveauService", r"PipelineStepInterface", r"FileProcessor", r"RoadmapManagerApp",
        r"ALMA" # Le nom du projet lui-même
    ]
    compiled_known_alma_components_regex = [re.compile(r"\b" + pattern + r"\b", re.IGNORECASE) for pattern in known_alma_components_patterns_str]


    current_task_buffer: Optional[Dict[str, Any]] = None

    def finalize_current_task(buffer: Optional[Dict[str, Any]]):
        nonlocal tasks
        if not buffer or not buffer.get("text","").strip(): # Ne pas finaliser un buffer vide
            return False

        buffer["id"] = hashlib.md5(
            f"{'/'.join(buffer['section_path'])}_{buffer['text'].strip()}_{buffer['raw_line_number']}".encode()
        ).hexdigest()[:16]

        final_task: RoadmapTask = {
            "id": buffer["id"],
            "text": buffer["text"].strip(),
            "full_text": buffer["full_text"].strip(),
            "source_document": RAPPORT_MAITRE_PATH.name,
            "section_path": list(buffer["section_path"]),
            "priority": buffer.get("priority", "Normale"),
            "status": "à faire", # Statut par défaut lors du parsing initial
            "notes": buffer.get("notes"),
            "raw_line_number": buffer["raw_line_number"],
            "action_verb": None,
            "action_object": None,
            "mentioned_modules": sorted(list(set(buffer.get("mentioned_modules", [])))),
            "keywords": [],
            "task_type_classified": None,
            "sentiment_task_desc": None,
            "icon_key": "task_default",
            "style_tags": []
        }

        priority_val = final_task.get("priority")
        if priority_val in ["Haute", "Élevée"]: final_task["style_tags"].append("priority_Haute.Treeitem")
        elif priority_val == "Moyenne": final_task["style_tags"].append("priority_Moyenne.Treeitem")
        elif priority_val == "Basse": final_task["style_tags"].append("priority_Basse.Treeitem")
        else: final_task["style_tags"].append("priority_Normale.Treeitem")

        if nlp_instance and final_task["text"]:
            nlp_model_name = nlp_instance.meta.get('name', 'inconnu') if hasattr(nlp_instance, 'meta') else 'inconnu'
            logger.debug(f"Analyse NLP pour tâche L{buffer['raw_line_number']} (modèle: {nlp_model_name}) : '{final_task['text'][:80]}...'")
            try:
                doc = nlp_instance(final_task["text"])

                # 1. Verbe d'Action et Objet
                if hasattr(doc, 'has_annotation') and doc.has_annotation("DEP"):
                    root_verb_token = next((token for token in doc if token.dep_ == "ROOT" and token.pos_ == "VERB"), None)
                    if root_verb_token:
                        final_task["action_verb"] = root_verb_token.lemma_
                        obj_texts = []
                        for child in root_verb_token.children:
                            if child.dep_ in ["obj", "dobj", "pobj", "obl", "attr", "acomp", "xcomp"]:
                                obj_texts.append(" ".join(t.text for t in child.subtree).strip())
                        if obj_texts: final_task["action_object"] = " ; ".join(obj_texts) # Concaténer si plusieurs objets
                    else: logger.debug(f"Aucun verbe ROOT trouvé pour tâche L{buffer['raw_line_number']}")
                else:
                    first_verb = next((token for token in doc if token.pos_ == "VERB" and token.lemma_ not in ["être", "avoir"]), None)
                    if first_verb: final_task["action_verb"] = first_verb.lemma_
                    logger.debug(f"Analyse de dépendance non disponible/utilisée pour L{buffer['raw_line_number']}, fallback verbe: {final_task['action_verb']}")

                # 2. Modules ALMA Mentionnés (NER + Regex sur les tokens)
                current_mentioned_modules = set(final_task.get("mentioned_modules", [])) # Partir de ceux trouvés par regex
                if hasattr(doc, 'ents'):
                    for ent in doc.ents:
                        for pattern_regex in compiled_known_alma_components_regex:
                            if pattern_regex.search(ent.text):
                                current_mentioned_modules.add(ent.text.strip())
                                break
                # Recherche par token aussi pour les noms de fichiers exacts
                for token in doc:
                    if token.text in known_alma_components_set: # Comparer avec le set pour efficacité
                         current_mentioned_modules.add(token.text)
                final_task["mentioned_modules"] = sorted(list(current_mentioned_modules))

                # 3. Mots-Clés (Lemmes Noms/Adjectifs significatifs)
                final_task["keywords"] = sorted(list(set(
                    token.lemma_.lower() for token in doc
                    if token.pos_ in ["NOUN", "PROPN", "ADJ"] and
                       not token.is_stop and not token.is_punct and len(token.lemma_) > 3 and
                       (final_task["action_verb"] and token.lemma_ != final_task["action_verb"])
                )))[:7]

                # 4. Classification du Type de Tâche et Icône
                text_lower = final_task["text"].lower()
                verb_lower = final_task["action_verb"].lower() if final_task["action_verb"] else ""
                # (Logique de classification par mots-clés et icon_key identique à V0.2.0,
                # mais elle bénéficiera d'un meilleur action_verb si _lg est utilisé)
                # ... (votre logique de if/elif pour task_type_classified et icon_key) ...
                # Assurez-vous que cette logique est complète ici
                if any(kw in text_lower or kw in verb_lower for kw in ["corriger", "bug", "erreur", "résoudre", "fixer", "réparer"]):
                    final_task["task_type_classified"] = "BugFix / Correction"; final_task["icon_key"] = "task_bug"
                elif any(kw in text_lower or kw in verb_lower for kw in ["implémenter", "développer", "créer", "ajouter", "construire", "mettre en place", "intégrer"]):
                    final_task["task_type_classified"] = "Développement / Implémentation"; final_task["icon_key"] = "task_dev"
                # ... (ajouter toutes les autres conditions ici) ...
                else:
                    final_task["task_type_classified"] = "Générique / Autre"; final_task["icon_key"] = "task_default"


            except Exception as e_nlp_task_parse:
                logger.warning(f"Erreur NLP sur tâche L{buffer['raw_line_number']} ('{final_task['text'][:30]}...'): {e_nlp_task_parse}", exc_info=False)

            tasks.append(final_task)
            return True
        return False

    # Boucle principale de parsing des lignes
    for line_num, line_text in enumerate(lines):
        line_stripped_for_empty_check = line_text.strip() # Pour vérifier les lignes vides
        m_h = h_regex.match(line_text)
        m_task = task_item_regex.match(line_text)

        if m_h:
            if finalize_current_task(current_task_buffer): current_task_buffer = None
            level = len(m_h.group(1))
            title = m_h.group(2).strip()
            current_section_path = current_section_path[:level-1] + [title]
        elif m_task:
            task_content_after_bullet = m_task.group(2).strip()
            if not task_content_after_bullet: continue

            if finalize_current_task(current_task_buffer): current_task_buffer = None # Finaliser la précédente avant de commencer une nouvelle

            priority_match = priority_regex.search(task_content_after_bullet)
            priority_val = priority_match.group(2).capitalize() if priority_match and len(priority_match.groups()) > 1 else "Normale"

            mentioned_module_list_regex = [match.group(1) for match in module_regex.finditer(task_content_after_bullet)] # Group 1 est le nom capturé
            mentioned_module_list_filtered = []
            for mod_candidate in mentioned_module_list_regex:
                for pattern_regex_known in compiled_known_alma_components_regex:
                    if pattern_regex_known.search(mod_candidate):
                        mentioned_module_list_filtered.append(mod_candidate.strip())
                        break

            livrable_match = livrable_regex.search(task_content_after_bullet)
            objectif_cle_val = livrable_match.group(2).strip() if livrable_match else None

            current_task_buffer = {
                "text": task_content_after_bullet,
                "full_text": line_text.strip(),
                "section_path": list(current_section_path),
                "priority": priority_val,
                "notes": objectif_cle_val,
                "raw_line_number": line_num + 1,
                "mentioned_modules": sorted(list(set(mentioned_module_list_filtered)))
            }
        elif current_task_buffer and line_stripped_for_empty_check and not m_h: # Continuation de tâche
            current_task_buffer["text"] += "\n" + line_stripped_for_empty_check
            current_task_buffer["full_text"] += "\n" + line_text # Garder l'indentation originale pour full_text

            priority_match_cont = priority_regex.search(line_text)
            if priority_match_cont: current_task_buffer["priority"] = priority_match_cont.group(2).capitalize()

            module_matches_cont = [match.group(1) for match in module_regex.finditer(line_text)]
            for mod_candidate in module_matches_cont:
                for pattern_regex_known in compiled_known_alma_components_regex:
                    if pattern_regex_known.search(mod_candidate) and mod_candidate.strip() not in current_task_buffer["mentioned_modules"]:
                        current_task_buffer["mentioned_modules"].append(mod_candidate.strip())
                        break
            current_task_buffer["mentioned_modules"] = sorted(list(set(current_task_buffer["mentioned_modules"])))

        elif not line_stripped_for_empty_check and current_task_buffer: # Ligne vide
            if finalize_current_task(current_task_buffer): current_task_buffer = None

    finalize_current_task(current_task_buffer) # Pour la toute dernière tâche

    nlp_model_name_used = nlp_instance.meta.get('name', 'inconnu') if nlp_instance and hasattr(nlp_instance, 'meta') else 'NLP Désactivé'
    logger.info(f"{len(tasks)} tâches structurées extraites du Rapport Maître (Parseur V2.1 + NLP {nlp_model_name_used}).")
    return tasks

# --- Fonctions de Gestion de l'État des Tâches ---
def load_roadmap_status() -> Dict[str, RoadmapTask]:
    """Charge l'état des tâches depuis le fichier JSON, en validant la structure."""
    logger.debug(f"Tentative de chargement de l'état des tâches depuis {ROADMAP_STATUS_FILE_PATH}...")
    tasks_by_id: Dict[str, RoadmapTask] = {}
    default_task_fields: RoadmapTask = { # Pour compléter les tâches chargées si des champs manquent
        "id": "", "text": "", "full_text": "", "source_document": RAPPORT_MAITRE_PATH.name,
        "section_path": [], "priority": None, "status": "à faire", "notes": None,
        "raw_line_number": 0, "action_verb": None, "action_object": None,
        "mentioned_modules": [], "keywords": [], "task_type_classified": None,
        "sentiment_task_desc": None, "icon_key": "task_default", "style_tags": []
    }
    if ROADMAP_STATUS_FILE_PATH.exists():
        try:
            with open(ROADMAP_STATUS_FILE_PATH, 'r', encoding='utf-8') as f:
                data_from_file = json.load(f)

            # Gérer l'ancien format (liste) et le nouveau (dictionnaire)
            # et valider/compléter chaque tâche
            tasks_to_process = []
            if isinstance(data_from_file, list):
                logger.info("Ancien format de sauvegarde (liste) détecté. Conversion...")
                tasks_to_process = data_from_file
            elif isinstance(data_from_file, dict):
                tasks_to_process = list(data_from_file.values()) # Convertir le dict en liste de tâches

            for task_dict_loaded in tasks_to_process:
                if isinstance(task_dict_loaded, dict) and "id" in task_dict_loaded:
                    # Créer une nouvelle tâche en partant des défauts et en surchargeant avec les valeurs chargées
                    validated_task: RoadmapTask = default_task_fields.copy() # type: ignore # mypy peut se plaindre ici
                    validated_task.update(task_dict_loaded) # type: ignore
                    tasks_by_id[validated_task["id"]] = validated_task
                else:
                    logger.warning(f"Item invalide ignoré lors du chargement de {ROADMAP_STATUS_FILE_PATH}: {task_dict_loaded}")

            logger.info(f"État de {len(tasks_by_id)} tâches chargé et validé depuis {ROADMAP_STATUS_FILE_PATH}.")
        except json.JSONDecodeError as e_json:
            logger.error(f"Erreur de décodage JSON pour {ROADMAP_STATUS_FILE_PATH}: {e_json}. Démarrage avec un état vide.", exc_info=True)
        except Exception as e_load:
            logger.error(f"Impossible de charger l'état des tâches depuis {ROADMAP_STATUS_FILE_PATH}: {e_load}", exc_info=True)
    else:
        logger.info(f"Fichier d'état {ROADMAP_STATUS_FILE_PATH} non trouvé. Démarrage avec un état vide.")
    return tasks_by_id

def save_roadmap_status(tasks_by_id: Dict[str, RoadmapTask]):
    """Sauvegarde l'état actuel des tâches dans le fichier JSON, en s'assurant que tous les champs sont présents."""
    logger.debug(f"Tentative de sauvegarde de l'état de {len(tasks_by_id)} tâches vers {ROADMAP_STATUS_FILE_PATH}...")
    default_task_fields: RoadmapTask = { # Pour s'assurer que tous les champs sont là
        "id": "", "text": "", "full_text": "", "source_document": RAPPORT_MAITRE_PATH.name,
        "section_path": [], "priority": None, "status": "à faire", "notes": None,
        "raw_line_number": 0, "action_verb": None, "action_object": None,
        "mentioned_modules": [], "keywords": [], "task_type_classified": None,
        "sentiment_task_desc": None, "icon_key": "task_default", "style_tags": []
    }
    validated_tasks_to_save: Dict[str, RoadmapTask] = {}
    for task_id, task_data in tasks_by_id.items():
        # Créer une nouvelle tâche en partant des défauts et en surchargeant
        complete_task_data: RoadmapTask = default_task_fields.copy() # type: ignore
        complete_task_data.update(task_data) # type: ignore
        validated_tasks_to_save[task_id] = complete_task_data

    try:
        CERVEAU_DIR.mkdir(parents=True, exist_ok=True)
        with open(ROADMAP_STATUS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(validated_tasks_to_save, f, indent=2, ensure_ascii=False)
        logger.info(f"État des tâches ({len(validated_tasks_to_save)} items) sauvegardé dans {ROADMAP_STATUS_FILE_PATH}.")
    except Exception as e_save:
        logger.error(f"Impossible de sauvegarder l'état des tâches dans {ROADMAP_STATUS_FILE_PATH}: {e_save}", exc_info=True)

# La classe RoadmapManagerApp viendra après ce bloc.
# (Suite du Bloc 2 - Fonctions de Parsing et Gestion d'État)

# --- Classe Principale de l'Application GUI ---
class RoadmapManagerApp:
    def __init__(self, root_window: tk.Tk):
        self.root = root_window
        self.root.title(f"{APP_NAME} - v{VERSION}")
        self.root.geometry("1250x900") # Légèrement agrandi pour plus d'aisance
        self.root.minsize(900, 700)

        # Utiliser le logger global du module, configuré au début du script
        self.logger = logger
        self.logger.info(f"Initialisation de RoadmapManagerApp v{VERSION}...")

        # --- Initialisation des Variables d'Instance ---
        self.tasks_from_report: List[RoadmapTask] = []
        self.tasks_status_by_id: Dict[str, RoadmapTask] = {}
        self.task_icons: Dict[str, Any] = {} # Sera peuplé par _load_icons
        self.nlp_spacy_roadmap: Optional[Any] = None # Instance spaCy
        self.current_selected_task_id: Optional[str] = None

        # Polices et Style (seront initialisés par la méthode dédiée)
        self.font_app_title: Optional[tkfont.Font] = None
        self.font_frame_title: Optional[tkfont.Font] = None
        self.font_text_normal: Optional[tkfont.Font] = None
        self.font_text_small: Optional[tkfont.Font] = None
        self.font_button: Optional[tkfont.Font] = None
        self.font_tree_heading: Optional[tkfont.Font] = None
        self.font_tree_item: Optional[tkfont.Font] = None
        self.font_detail_label: Optional[tkfont.Font] = None
        self.font_detail_text: Optional[tkfont.Font] = None
        self.font_tree_item_strikethrough: Optional[tkfont.Font] = None
        self.style: Optional[ttk.Style] = None
        self.task_tree_tags_configured = False # Flag pour configurer les tags du Treeview une seule fois

        # --- Configuration de l'Apparence et des Outils ---
        self._initialize_fonts_and_styles() # Doit être appelé avant _setup_ui
        self._initialize_nlp()              # Charger spaCy (fr_core_news_lg en priorité)
        self._load_icons()                  # Charger les icônes (texte/emoji ou images)

        # --- Configuration de l'Interface Utilisateur ---
        self._setup_ui() # Construit les widgets

        # --- Chargement Initial des Données ---
        self.load_and_display_roadmap() # Peuple le Treeview

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.logger.info("RoadmapManagerApp initialisée avec succès.")

    def _initialize_fonts_and_styles(self):
        """Initialise les polices et les styles ttk pour l'application."""
        self.logger.debug("Initialisation des polices et des styles...")
        # Définition des couleurs (Palette V20 "Genshin-Lite" adaptée)
        self.color_app_bg = "#F7F9FC"         # Fond général très clair
        self.color_frame_bg = "#E8EFF7"       # Fond des cadres et zones groupées
        self.color_tree_bg = "#FFFFFF"        # Fond du Treeview
        self.color_text_primary = "#34495E"   # Texte principal (foncé)
        self.color_text_secondary = "#7F8C8D" # Texte secondaire (gris)
        self.color_accent = "#5D9CEC"         # Bleu accent principal
        self.color_accent_active = self.darken_color(self.color_accent, 0.85) # Pour hover/press
        self.color_button_text = "#FFFFFF"    # Texte des boutons sur fond accent

        self.color_priority_high = "#E74C3C"  # Rouge plus affirmé
        self.color_priority_medium = "#F39C12" # Orange
        self.color_priority_low = "#2ECC71"   # Vert
        self.color_priority_normale = self.color_text_secondary

        self.color_status_accomplie = "#95A5A6" # Gris pour accompli
        self.color_status_en_cours = self.color_accent # Bleu
        self.color_status_a_faire = self.color_text_primary
        self.color_status_bloquee = "#C0392B"   # Rouge foncé pour bloqué
        self.color_status_en_attente = "#8E44AD" # Violet pour en attente

        self.root.configure(bg=self.color_app_bg)

        font_family_wished = "Noto Sans" # Police moderne et lisible
        font_family_fallback = tkfont.nametofont("TkDefaultFont").cget("family")
        actual_font_family = font_family_wished
        try:
            tkfont.Font(family=font_family_wished, size=10) # Test simple
            self.logger.info(f"Police primaire '{font_family_wished}' trouvée et sera utilisée.")
        except tk.TclError:
            self.logger.warning(f"Police primaire '{font_family_wished}' non trouvée. Utilisation de '{font_family_fallback}'.")
            actual_font_family = font_family_fallback

        # Définition des objets Font de l'instance
        self.font_app_title = tkfont.Font(family=actual_font_family, size=18, weight="bold")
        self.font_frame_title = tkfont.Font(family=actual_font_family, size=11, weight="bold") # Un peu plus petit
        self.font_text_normal = tkfont.Font(family=actual_font_family, size=10)
        self.font_text_small = tkfont.Font(family=actual_font_family, size=9)
        self.font_button = tkfont.Font(family=actual_font_family, size=10, weight="bold")
        self.font_tree_heading = tkfont.Font(family=actual_font_family, size=10, weight="bold")
        self.font_tree_item = tkfont.Font(family=actual_font_family, size=9)
        self.font_detail_label = tkfont.Font(family=actual_font_family, size=9, weight="bold")
        self.font_detail_text = tkfont.Font(family=actual_font_family, size=9)
        try:
            self.font_tree_item_strikethrough = tkfont.Font(family=actual_font_family, size=9, overstrike=True)
        except tk.TclError:
            self.logger.warning("Style 'overstrike' non supporté. Les tâches accomplies seront colorées mais non barrées.")
            self.font_tree_item_strikethrough = self.font_tree_item # Fallback

        # Configuration des Styles ttk
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam') # 'clam' ou 'alt' sont de bons choix modernes

        self.style.configure(".", font=self.font_text_normal, background=self.color_app_bg, foreground=self.color_text_primary)
        self.style.configure("TFrame", background=self.color_app_bg)
        self.style.configure("TLabel", background=self.color_app_bg, foreground=self.color_text_primary, font=self.font_text_normal)
        self.style.configure("Header.TLabel", font=self.font_app_title, foreground=self.color_text_primary)
        self.style.configure("FrameTitle.TLabel", font=self.font_frame_title, foreground=self.color_accent)

        self.style.configure("TButton", font=self.font_button, padding=(10, 6), relief=tk.RAISED, borderwidth=1)
        self.style.map("TButton",
                       background=[('!disabled', self.color_accent), ('active', self.color_accent_active), ('disabled', self.color_frame_bg)],
                       foreground=[('!disabled', self.color_button_text), ('disabled', self.color_text_secondary)])

        self.style.configure("Treeview.Heading", font=self.font_tree_heading, padding=(5,3), relief=tk.FLAT, background=self.color_frame_bg, borderwidth=0)
        self.style.map("Treeview.Heading", relief=[('active','groove'),('pressed','sunken')])
        self.style.configure("Treeview", rowheight=24, font=self.font_tree_item,
                             background=self.color_tree_bg, fieldbackground=self.color_tree_bg, foreground=self.color_text_primary)
        self.style.map("Treeview",
                       background=[('selected', self.color_accent_active)], # Couleur de sélection plus foncée
                       foreground=[('selected', self.color_button_text)])

        self.style.configure("TLabelFrame", background=self.color_frame_bg, borderwidth=1, relief="solid", padding=10)
        self.style.configure("TLabelFrame.Label", background=self.color_frame_bg, foreground=self.color_text_primary, font=self.font_frame_title)

        self.style.configure("TScrollbar", troughcolor=self.color_frame_bg, background=self.color_accent, borderwidth=0, arrowsize=14)
        self.style.map("TScrollbar", background=[('active', self.color_accent_active)])
        self.logger.debug("Polices et styles ttk initialisés.")
        # La configuration des tags du Treeview se fera dans _ensure_treeview_tags_configured
        # une fois que self.task_tree est créé.

    def _ensure_treeview_tags_configured(self):
        """Configure les tags de style pour les items du ttk.Treeview.
           Doit être appelée après la création de self.task_tree."""
        if self.task_tree_tags_configured or not hasattr(self, 'task_tree') or self.task_tree is None:
            return

        self.logger.debug("Configuration des tags de style pour le Treeview...")
        # Styles pour les sections
        self.task_tree.tag_configure("section_style", font=tkfont.Font(family=self.font_tree_item.cget("family"), size=self.font_tree_item.cget("size")+1, weight="bold"), foreground=self.color_accent)

        # Style de base pour les tâches
        self.task_tree.tag_configure("task.Treeitem", font=self.font_tree_item)

        # Styles pour les statuts
        self.task_tree.tag_configure("status_accomplie.Treeitem", font=self.font_tree_item_strikethrough, foreground=self.color_status_accomplie)
        self.task_tree.tag_configure("status_en_cours.Treeitem", font=tkfont.Font(family=self.font_tree_item.cget("family"), size=self.font_tree_item.cget("size"), weight="bold"), foreground=self.color_status_en_cours)
        self.task_tree.tag_configure("status_a_faire.Treeitem", foreground=self.color_status_a_faire)
        self.task_tree.tag_configure("status_bloquée.Treeitem", font=tkfont.Font(family=self.font_tree_item.cget("family"), size=self.font_tree_item.cget("size"), weight="bold", slant="italic"), foreground=self.color_status_bloquee)
        self.task_tree.tag_configure("status_en_attente.Treeitem", font=tkfont.Font(family=self.font_tree_item.cget("family"), size=self.font_tree_item.cget("size"), slant="italic"), foreground=self.color_status_en_attente)

        # Styles pour les priorités
        bold_priority_font = tkfont.Font(family=self.font_tree_item.cget("family"), size=self.font_tree_item.cget("size"), weight="bold")
        self.task_tree.tag_configure("priority_Haute.Treeitem", font=bold_priority_font, foreground=self.color_priority_high)
        self.task_tree.tag_configure("priority_Élevée.Treeitem", font=bold_priority_font, foreground=self.color_priority_high) # Synonyme
        self.task_tree.tag_configure("priority_Moyenne.Treeitem", foreground=self.color_priority_medium)
        self.task_tree.tag_configure("priority_Normale.Treeitem", foreground=self.color_priority_normale)
        self.task_tree.tag_configure("priority_Basse.Treeitem", foreground=self.color_priority_low)

        self.task_tree_tags_configured = True
        self.logger.debug("Tags de style Treeview configurés avec succès.")

    def _initialize_nlp(self):
        """
        Initialise le modèle spaCy (fr_core_news_lg en priorité, puis fr_core_news_sm)
        pour l'analyse des tâches du rapport.
        """
        self.logger.info("Initialisation du moteur NLP (spaCy) pour Roadmap Manager...")
        if not (SPACY_AVAILABLE and spacy): # Utiliser l'alias global spacy
            self.nlp_spacy_roadmap = None
            self.logger.warning("Bibliothèque spaCy non disponible. L'analyse NLP des tâches sera limitée.")
            return

        # Modèles à essayer, par ordre de préférence
        # Les chemins absolus sont des fallbacks si le chargement par nom échoue
        # Assurez-vous que les versions des modèles correspondent à votre installation
        models_to_try = [
            {"name": "fr_core_news_lg", "path": ALMA_BASE_DIR / "venv/lib/python3.12/site-packages/fr_core_news_lg/fr_core_news_lg-3.8.0"}, # Ajuster la version si besoin
            {"name": "fr_core_news_sm", "path": ALMA_BASE_DIR / "venv/lib/python3.12/site-packages/fr_core_news_sm/fr_core_news_sm-3.8.0"}  # Ajuster la version si besoin
        ]

        # Configuration des pipes à désactiver
        # Pour le Roadmap Manager, le parser est TRES utile pour action_verb/action_object.
        # Le NER est utile pour mentioned_modules. On garde donc tout pour _lg.
        # Pour _sm, on peut désactiver le NER s'il est trop bruyant, mais le parser est léger.
        disabled_pipes_config = {
            "fr_core_news_lg": ["textcat"], # Désactiver seulement textcat si présent
            "fr_core_news_sm": ["ner"]      # Pour _sm, on peut désactiver NER
        }

        nlp_instance_loaded: Optional[Any] = None
        loaded_model_name_str = "Aucun"

        for model_info in models_to_try:
            model_name = model_info["name"]
            model_path = model_info["path"]
            # Utiliser les pipes désactivés spécifiques au modèle, ou une liste vide si non défini
            disabled_pipes = disabled_pipes_config.get(model_name, [])

            self.logger.info(f"Tentative de chargement du modèle spaCy '{model_name}' par NOM (pipes désactivés: {disabled_pipes or 'aucun'})...")
            try:
                nlp_instance_loaded = spacy.load(model_name, disable=disabled_pipes)
                loaded_model_name_str = model_name
                self.logger.info(f"SUCCÈS: Modèle spaCy '{nlp_instance_loaded.meta['name']}' v{nlp_instance_loaded.meta['version']} chargé par NOM.")
                break # Arrêter dès qu'un modèle est chargé avec succès
            except OSError as e_load_name:
                self.logger.warning(f"ÉCHEC chargement '{model_name}' par NOM: {e_load_name}")
                if "[E050]" in str(e_load_name) and model_path.is_dir(): # Vérifier is_dir() pour le chemin
                    self.logger.info(f"Tentative de chargement de '{model_name}' par CHEMIN ABSOLU: {model_path}")
                    try:
                        nlp_instance_loaded = spacy.load(model_path, disable=disabled_pipes)
                        loaded_model_name_str = model_name
                        self.logger.info(f"SUCCÈS: Modèle spaCy '{model_name}' (version locale '{nlp_instance_loaded.meta['version']}') chargé par CHEMIN ABSOLU.")
                        break
                    except Exception as e_load_path:
                        self.logger.error(f"ERREUR chargement '{model_name}' par CHEMIN ABSOLU '{model_path}': {e_load_path}", exc_info=True)
                # Continuer pour essayer le prochain modèle si échec par nom et chemin

        self.nlp_spacy_roadmap = nlp_instance_loaded
        if self.nlp_spacy_roadmap:
             self.logger.info(f"Moteur NLP pour Roadmap Manager activé avec le modèle '{loaded_model_name_str}'. Pipeline: {self.nlp_spacy_roadmap.pipe_names}")
             # Ajuster max_length si nécessaire (important pour _lg sur des descriptions de tâches longues)
             # Pour le Roadmap Manager, les textes de tâches sont courts, donc moins critique que pour cerveau.py
             if hasattr(self.nlp_spacy_roadmap, 'max_length') and self.nlp_spacy_roadmap.max_length < 500000: # Si la limite est basse
                 try: self.nlp_spacy_roadmap.max_length = 500000 # Mettre une limite raisonnable
                 except Exception as e_max_len: self.logger.error(f"Impossible d'ajuster nlp_spacy_roadmap.max_length: {e_max_len}")
        else:
             self.logger.error(f"ÉCHEC FINAL du chargement de tous les modèles spaCy configurés pour Roadmap Manager. L'analyse NLP des tâches sera limitée ou désactivée.")

    def _load_icons(self):
        """Charge les icônes (texte/emoji ou images via Pillow)."""
        self.logger.debug("Chargement des icônes...")
        default_icons = {
            "phase": "❖", "objectif": "🎯", "sous_objectif": "↳",
            "task_default": "📄", "task_dev": "💻", "task_bug": "🐞", "task_doc": "📖",
            "task_research": "🔬", "task_test": "🧪", "task_config": "⚙️", "task_ui": "🎨",
            "task_refactor": "♻️", "task_meeting": "👥", "task_planning": "🗓️",
            "status_accomplie_prefix": "✅ ", "status_en_cours_prefix": "⏳ ",
            "status_a_faire_prefix": "⚪ ", "status_bloquée_prefix": "🚫 ",
            "status_en_attente_prefix": "⏸️ "
        }
        self.task_icons = default_icons.copy()

        if PILLOW_AVAILABLE and Image and ImageTk:
            self.logger.info(f"Pillow disponible. Tentative de chargement des icônes image depuis {ICONS_DIR}...")
            icon_files_to_load = {
                "phase": "phase_icon", "objectif": "objectif_icon", "sous_objectif": "sub_objectif_icon",
                "task_default": "task_default_icon", "task_dev": "task_dev_icon", "task_bug": "task_bug_icon",
                "task_doc": "task_doc_icon", "task_research": "task_research_icon",
                "task_test": "task_test_icon", "task_config": "task_config_icon",
                "task_ui": "task_ui_icon", "task_refactor": "task_refactor_icon",
                "task_meeting": "task_meeting_icon", "task_planning": "task_planning_icon",
                # Pour les statuts, on utilise des préfixes emoji, mais on pourrait avoir des images
                # "img_status_accomplie": "status_done_icon",
            }
            loaded_image_count = 0
            if ICONS_DIR.is_dir():
                for icon_key, filename_stem in icon_files_to_load.items():
                    icon_file_path = ICONS_DIR / f"{filename_stem}.png"
                    if icon_file_path.is_file():
                        try:
                            img = Image.open(icon_file_path).resize((16, 16), PIL_Image.Resampling.LANCZOS)
                            self.task_icons[icon_key] = ImageTk.PhotoImage(img)
                            loaded_image_count += 1
                        except Exception as e_img_load:
                            self.logger.error(f"Impossible de charger/traiter l'image {icon_file_path} pour clé '{icon_key}': {e_img_load}")
                    # else: self.logger.debug(f"Fichier icône {icon_file_path} non trouvé pour clé '{icon_key}'.")
            else:
                self.logger.warning(f"Dossier d'icônes {ICONS_DIR} non trouvé. Aucune icône image ne sera chargée.")

            if loaded_image_count > 0: self.logger.info(f"{loaded_image_count} icônes image chargées.")
            else: self.logger.info("Aucune icône image personnalisée chargée. Utilisation des placeholders texte/emoji.")
        else:
            self.logger.info("Pillow non disponible. Utilisation des icônes texte/emoji par défaut.")

        # Assurer que toutes les clés d'icônes nécessaires ont une valeur
        for key_needed in default_icons.keys(): # Itérer sur les clés des défauts
            if key_needed not in self.task_icons:
                self.task_icons[key_needed] = default_icons.get(key_needed, "❓")
        self.logger.debug(f"Dictionnaire d'icônes finalisé.")


    def darken_color(self, hex_color: str, factor: float = 0.85) -> str:
        if not isinstance(hex_color, str) or not hex_color.startswith('#') or len(hex_color) not in [4, 7]: # Gérer #RGB
            self.logger.warning(f"Format de couleur hexadécimal invalide pour darken_color: '{hex_color}'.")
            return "#333333"

        hex_color_long = hex_color
        if len(hex_color) == 4: # Convertir #RGB en #RRGGBB
            hex_color_long = f"#{hex_color[1]*2}{hex_color[2]*2}{hex_color[3]*2}"

        try:
            r_int = int(hex_color_long[1:3], 16)
            g_int = int(hex_color_long[3:5], 16)
            b_int = int(hex_color_long[5:7], 16)
            r_dark = max(0, min(255, int(r_int * factor)))
            g_dark = max(0, min(255, int(g_int * factor)))
            b_dark = max(0, min(255, int(b_int * factor)))
            return f"#{r_dark:02x}{g_dark:02x}{b_dark:02x}"
        except ValueError:
            self.logger.warning(f"Erreur de conversion de couleur hexadécimale pour darken_color: '{hex_color}'.")
            return "#333333"

    # La méthode _on_closing et les méthodes d'action utilisateur (_setup_ui, etc.) viendront dans les blocs suivants.
# (Suite du Bloc 3 - __init__ et Méthodes d'Initialisation)

    # --- Méthodes de Configuration de l'Interface Utilisateur ---
    def _setup_ui(self):
        """Construit l'interface utilisateur principale de l'application."""
        self.logger.debug("Configuration de l'interface utilisateur (_setup_ui)...")

        main_frame = ttk.Frame(self.root, padding="10 10 10 10") # Padding uniforme
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Titre de l'Application ---
        title_label = ttk.Label(main_frame, text=APP_NAME, style="Header.TLabel", anchor="center")
        title_label.pack(pady=(0, 20), fill=tk.X) # Augmenter le padding inférieur

        # --- Panneau de Contrôle Supérieur (Rafraîchir, futurs filtres) ---
        control_top_frame = ttk.Frame(main_frame) # Pas besoin de padding ici, les widgets en auront
        control_top_frame.pack(fill=tk.X, pady=(0, 10))

        refresh_button = ttk.Button(control_top_frame, text="🔄 Rafraîchir depuis Rapport Maître",
                                    command=self.load_and_display_roadmap)
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        # Placeholder pour futurs filtres globaux (ex: par priorité, par statut)
        # filter_label = ttk.Label(control_top_frame, text="Filtres:", font=self.font_text_small)
        # filter_label.pack(side=tk.LEFT, padx=(10,5))
        # ... (widgets de filtre)

        # --- Zone Principale avec PanedWindow pour Treeview et Détails ---
        main_paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        main_paned_window.pack(expand=True, fill=tk.BOTH, pady=(0, 5))

        # --- 1. Conteneur pour le Treeview (panneau supérieur du PanedWindow) ---
        tree_container_frame = ttk.LabelFrame(main_paned_window, text="📋 Feuille de Route Détaillée",
                                             style="TLabelFrame", padding="5")
        main_paned_window.add(tree_container_frame, weight=65) # 65% de la hauteur initiale

        self.task_tree = ttk.Treeview(
            tree_container_frame,
            columns=("text", "priority", "status", "notes_preview"),
            show="tree headings", # Affiche seulement les headings, pas la colonne #0 vide par défaut
            style="Treeview" # Appliquer le style de base
        )
        # Configuration des Headings
        self.task_tree.heading("#0", text="📂 Section / 📝 Tâche (ID Ligne)") # Colonne pour l'arborescence
        self.task_tree.heading("text", text="Description de la Tâche")
        self.task_tree.heading("priority", text="Priorité")
        self.task_tree.heading("status", text="Statut")
        self.task_tree.heading("notes_preview", text="Aperçu des Notes")

        # Configuration des Colonnes
        self.task_tree.column("#0", width=350, minwidth=280, stretch=tk.NO, anchor="w")
        self.task_tree.column("text", width=450, minwidth=300, stretch=tk.YES, anchor="w")
        self.task_tree.column("priority", width=100, minwidth=80, stretch=tk.NO, anchor="center")
        self.task_tree.column("status", width=120, minwidth=100, stretch=tk.NO, anchor="center")
        self.task_tree.column("notes_preview", width=200, minwidth=150, stretch=tk.NO, anchor="w")

        # Scrollbars pour le Treeview
        vsb_tree = ttk.Scrollbar(tree_container_frame, orient="vertical", command=self.task_tree.yview)
        hsb_tree = ttk.Scrollbar(tree_container_frame, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=vsb_tree.set, xscrollcommand=hsb_tree.set)

        # Placement du Treeview et des Scrollbars dans tree_container_frame
        tree_container_frame.grid_rowconfigure(0, weight=1)
        tree_container_frame.grid_columnconfigure(0, weight=1)
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        vsb_tree.grid(row=0, column=1, sticky="ns")
        hsb_tree.grid(row=1, column=0, sticky="ew")

        # Liaisons d'événements pour le Treeview
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.task_tree.bind("<Double-1>", self.on_tree_double_click)
        # S'assurer que les tags sont configurés après la création de self.task_tree
        self._ensure_treeview_tags_configured()


        # --- 2. Panneau de Détails de la Tâche (panneau inférieur du PanedWindow) ---
        detail_lf = ttk.LabelFrame(main_paned_window, text="🔍 Détails de la Tâche Sélectionnée",
                                   style="TLabelFrame", padding="10")
        main_paned_window.add(detail_lf, weight=35) # 35% de la hauteur initiale

        self.task_detail_text = scrolledtext.ScrolledText(
            detail_lf, height=12, width=80, # Augmenter un peu la hauteur par défaut
            font=self.font_detail_text, wrap=tk.WORD,
            state=tk.DISABLED, relief=tk.SOLID, borderwidth=1,
            bg=self.color_tree_bg, fg=self.color_text_primary, # Utiliser les couleurs du thème
            padx=5, pady=5 # Ajouter un peu de padding interne
        )
        self.task_detail_text.pack(fill=tk.BOTH, expand=True) # Utiliser pack ici car c'est le seul widget

        # Configuration des tags pour le widget Text (déplacé vers _ensure_treeview_tags_configured pour centralisation)
        # mais on peut les réaffirmer ici si self.task_detail_text est recréé.
        # Pour l'instant, on suppose qu'ils sont configurés une fois.

        # --- Panneau d'Actions sur la Tâche Sélectionnée (sous le PanedWindow) ---
        action_frame = ttk.Frame(main_frame, padding="10 5 10 5") # Padding uniforme
        action_frame.pack(fill=tk.X, pady=(10, 5)) # Espacement au-dessus

        action_buttons_config = [
            ("✔ Marquer Accomplie", self.mark_task_done, self.color_priority_low), # Vert
            ("⏳ Marquer En Cours", self.mark_task_inprogress, self.color_accent),  # Bleu
            ("⚪ Marquer À Faire", self.mark_task_todo, self.color_text_secondary), # Gris
            ("🚫 Marquer Bloquée", self.mark_task_blocked, self.color_priority_high), # Rouge (NOUVEAU)
            ("⏸️ Marquer En Attente", self.mark_task_pending, self.color_status_en_attente), # Violet (NOUVEAU)
            ("✎ Note", self.add_edit_note_to_task, "#6c757d") # Gris neutre
        ]

        for i, (text, cmd, color) in enumerate(action_buttons_config):
            # Créer un style unique pour chaque bouton coloré si nécessaire, ou appliquer directement
            # Pour simplifier, on peut ne pas colorer les boutons d'action eux-mêmes
            # mais se fier aux couleurs des statuts dans le Treeview.
            # Si on veut des boutons colorés :
            # style_name = f"ActionBtn.{text.replace(' ','')}.TButton"
            # self.style.configure(style_name, background=color, foreground=self.color_button_text if color != self.color_text_secondary else self.color_text_primary)
            # btn = ttk.Button(action_frame, text=text, command=cmd, style=style_name)
            btn = ttk.Button(action_frame, text=text, command=cmd) # Style par défaut TButton
            btn.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
            action_frame.grid_columnconfigure(i, weight=1) # Pour que les boutons s'étendent


        # --- Zone pour "Soumettre Texte Brut" (sous le Panneau d'Actions) ---
        submit_text_lf = ttk.LabelFrame(main_frame, text="📝 Soumettre Nouveau Texte pour Analyse de Tâches",
                                        style="TLabelFrame", padding="10")
        submit_text_lf.pack(fill=tk.X, pady=(10, 5))

        self.raw_text_input = scrolledtext.ScrolledText(
            submit_text_lf, height=6, width=70, # Un peu plus haut
            font=self.font_text_normal, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1,
            bg=self.color_tree_bg, fg=self.color_text_primary, padx=5, pady=5
        )
        self.raw_text_input.pack(pady=(5,10), fill=tk.X, expand=True) # Espacement

        analyze_text_button = ttk.Button(submit_text_lf, text="💡 Analyser et Suggérer des Tâches",
                                         command=self.analyze_submitted_text)
        analyze_text_button.pack(pady=(0,5)) # Espacement

        self.logger.debug("Interface utilisateur (_setup_ui) configurée.")

    # Les autres méthodes de RoadmapManagerApp (load_and_display_roadmap, _populate_treeview, etc.)
    # viendront dans les blocs suivants.
# (Suite du Bloc 4 - Méthode _setup_ui)

    # --- Méthodes de Chargement et d'Affichage des Données ---
    def load_and_display_roadmap(self):
        """
        Charge les tâches depuis le Rapport Maître, fusionne avec l'état sauvegardé,
        et met à jour l'affichage du Treeview.
        """
        self.logger.info("Chargement et affichage de la feuille de route...")
        self.current_selected_task_id = None # Réinitialiser la sélection
        if hasattr(self, 'task_detail_text') and self.task_detail_text: # S'assurer que le widget existe
            self.on_task_select() # Vider le panneau de détails

        if not RAPPORT_MAITRE_PATH.exists():
            self.logger.error(f"Fichier Rapport Maître introuvable à {RAPPORT_MAITRE_PATH}")
            messagebox.showerror("Erreur Fichier", f"Rapport Maître introuvable:\n{RAPPORT_MAITRE_PATH}")
            return
        try:
            with open(RAPPORT_MAITRE_PATH, 'r', encoding='utf-8') as f:
                report_content = f.read()
        except Exception as e_read_report:
            self.logger.error(f"Impossible de lire le Rapport Maître: {e_read_report}", exc_info=True)
            messagebox.showerror("Erreur Lecture Rapport", f"Impossible de lire le Rapport Maître:\n{e_read_report}")
            return

        # Parser le rapport pour obtenir la liste fraîche des tâches
        # self.nlp_spacy_roadmap est initialisé dans __init__ via _initialize_nlp()
        self.tasks_from_report = parse_rapport_maitre_v2(report_content, self.nlp_spacy_roadmap)

        # Charger les statuts et notes sauvegardés
        saved_statuses = load_roadmap_status() # C'est un Dict[str, RoadmapTask]

        # Fusionner les tâches du rapport avec les statuts sauvegardés
        self.tasks_status_by_id.clear() # Vider l'ancien état en mémoire

        processed_ids_from_report = set()

        for task_from_report_data in self.tasks_from_report:
            task_id = task_from_report_data["id"]
            processed_ids_from_report.add(task_id)

            # Commencer avec les données fraîches du rapport (qui incluent la dernière analyse NLP)
            current_task_state: RoadmapTask = task_from_report_data.copy() # type: ignore

            if task_id in saved_statuses:
                # Si un état sauvegardé existe, prioriser son statut et ses notes
                saved_task_data = saved_statuses[task_id]
                current_task_state["status"] = saved_task_data.get("status", task_from_report_data["status"])
                current_task_state["notes"] = saved_task_data.get("notes", task_from_report_data["notes"])
                # Conserver les autres champs (NLP, etc.) du parsing frais si le fichier de statut est plus ancien
                # ou si on décide que le parsing frais a toujours la priorité pour ces champs.
                # Pour l'instant, on écrase les champs NLP du statut sauvegardé par ceux du parsing frais.
                # On pourrait ajouter une logique de "plus récent" si les fichiers de statut avaient un timestamp.

            self.tasks_status_by_id[task_id] = current_task_state

        # Ajouter les tâches qui sont dans le fichier de statut mais plus dans le rapport (marquées comme "archivées"?)
        # Ou les supprimer du fichier de statut pour le garder propre. Pour l'instant, on ne les ajoute pas au Treeview.
        # On pourrait loguer les tâches orphelines.
        orphan_task_ids = [task_id for task_id in saved_statuses if task_id not in processed_ids_from_report]
        if orphan_task_ids:
            self.logger.info(f"{len(orphan_task_ids)} tâches trouvées dans le fichier d'état mais plus dans le Rapport Maître. Elles ne seront pas affichées mais leur état est conservé si elles réapparaissent.")
            # Pour les conserver dans self.tasks_status_by_id (au cas où elles reviendraient avec le même ID) :
            for orphan_id in orphan_task_ids:
                self.tasks_status_by_id[orphan_id] = saved_statuses[orphan_id]


        self._populate_treeview() # Mettre à jour l'affichage
        save_roadmap_status(self.tasks_status_by_id) # Sauvegarder l'état fusionné/nettoyé
        self.logger.info(f"Feuille de route chargée et affichée ({len(self.tasks_from_report)} tâches du rapport, {len(self.tasks_status_by_id)} tâches gérées en état).")

    def _populate_treeview(self):
        """Peuple le ttk.Treeview avec les tâches hiérarchisées, en utilisant les icônes et styles."""
        if not hasattr(self, 'task_tree') or self.task_tree is None:
            self.logger.error("Tentative de peupler le Treeview avant sa création.")
            return

        self.logger.debug("Peuplement du Treeview...")
        self.task_tree.delete(*self.task_tree.get_children())
        self._ensure_treeview_tags_configured() # S'assurer que les tags sont prêts

        section_nodes_iid_map: Dict[Tuple[str, ...], str] = {}

        # Utiliser self.tasks_status_by_id qui contient l'état fusionné et le plus à jour
        # Trier les tâches par numéro de ligne pour assurer l'ordre du rapport maître
        # Sauf si elles ne sont plus dans le rapport, auquel cas elles n'ont pas de raw_line_number fiable.
        # On va afficher uniquement les tâches présentes dans self.tasks_from_report pour garder l'ordre.

        tasks_to_display = sorted(self.tasks_from_report, key=lambda t: t['raw_line_number'])

        for task_data_merged in tasks_to_display: # Utiliser les tâches parsées pour l'ordre et la structure
            task_id = task_data_merged['id']
            # Récupérer l'état le plus à jour (statut, notes) depuis self.tasks_status_by_id
            task_data_for_display = self.tasks_status_by_id.get(task_id, task_data_merged)


            parent_node_tree_id = ""
            for i, section_name_raw in enumerate(task_data_for_display["section_path"]):
                section_name = section_name_raw.strip()
                current_path_as_tuple = tuple(task_data_for_display["section_path"][:i+1])

                section_level_icon = ""
                if i == 0: section_level_icon = self.task_icons.get("phase", "❖")
                elif i == 1: section_level_icon = self.task_icons.get("objectif", "🎯")
                else: section_level_icon = self.task_icons.get("sous_objectif", "↳")

                section_display_name_with_icon = f"{section_level_icon} {section_name}"

                if current_path_as_tuple not in section_nodes_iid_map:
                    section_iid_str = "_section_" + hashlib.md5("_".join(current_path_as_tuple).encode()).hexdigest()[:12]
                    inserted_node_id = self.task_tree.insert(
                        parent_node_tree_id, "end", iid=section_iid_str,
                        text=section_display_name_with_icon,
                        values=("", "", "", ""), # Colonnes vides pour les sections
                        tags=("section_style",), open=True
                    )
                    section_nodes_iid_map[current_path_as_tuple] = inserted_node_id
                parent_node_tree_id = section_nodes_iid_map[current_path_as_tuple]

            # Préparation des données de la tâche pour l'affichage
            task_text_display = task_data_for_display["text"][:100] + "..." if len(task_data_for_display["text"]) > 100 else task_data_for_display["text"]
            priority_display = task_data_for_display.get("priority", "Normale") or "Normale"
            status_display = task_data_for_display.get("status", "à faire")
            notes_preview_display = (task_data_for_display.get("notes", "") or "")[:35]
            if len(task_data_for_display.get("notes", "") or "") > 35: notes_preview_display += "..."


            task_icon_key = task_data_for_display.get("icon_key", "task_default")
            task_type_icon = self.task_icons.get(task_icon_key, self.task_icons.get("task_default", "📄"))
            if isinstance(task_type_icon, str) and task_type_icon.startswith("status_"): # Ne pas utiliser un préfixe de statut comme icône de type
                task_type_icon = self.task_icons.get("task_default", "📄")


            status_prefix_key = f"status_{status_display.replace(' ','_').replace('é','e')}_prefix" # Normaliser pour clé
            status_icon_prefix = self.task_icons.get(status_prefix_key, "")

            tree_item_text_col0 = f"{status_icon_prefix}{task_type_icon} L{task_data_for_display['raw_line_number']}: {task_data_for_display['id'][:8]}..."

            current_style_tags = ["task.Treeitem"]
            status_tag_name = f"status_{status_display.replace(' ','_').replace('é','e')}.Treeitem"
            current_style_tags.append(status_tag_name)

            priority_value_for_tag = task_data_for_display.get("priority")
            if priority_value_for_tag:
                # Normaliser "Élevée" en "Haute" pour le tag si besoin, ou gérer les deux
                normalized_priority_for_tag = priority_value_for_tag.replace('Élevée', 'Haute').replace(' ','_')
                priority_tag_name = f"priority_{normalized_priority_for_tag}.Treeitem"
                current_style_tags.append(priority_tag_name)

            if status_display == "accomplie" and self.font_tree_item_strikethrough != self.font_tree_item : # Appliquer seulement si la police overstrike est différente
                current_style_tags.append("text_strikethrough.Treeitem")

            self.task_tree.insert(
                parent_node_tree_id, "end", iid=task_data_for_display["id"],
                text=tree_item_text_col0,
                values=(task_text_display, priority_display, status_display, notes_preview_display),
                tags=tuple(set(current_style_tags)), # set pour éviter doublons
                open=False
            )
        self.logger.debug(f"Treeview peuplé avec {len(tasks_to_display)} tâches.")


    def on_task_select(self, event: Optional[Any] = None): # event peut être None si appelé manuellement
        """Affiche les détails de la tâche sélectionnée dans le panneau de détails."""
        if not hasattr(self, 'task_detail_text') or self.task_detail_text is None: return

        self.task_detail_text.config(state=tk.NORMAL)
        self.task_detail_text.delete("1.0", tk.END)
        self._ensure_treeview_tags_configured() # S'assurer que les tags du panneau de détail sont aussi prêts

        selected_id = self.current_selected_task_id # Utiliser l'ID stocké lors de la sélection réelle
                                                 # ou celui mis à jour par get_selected_task_id_from_tree si appelé par l'event

        # Si appelé par l'event, mettre à jour current_selected_task_id
        if event:
            selected_items_from_event = self.task_tree.selection()
            if selected_items_from_event:
                selected_id = selected_items_from_event[0]
                self.current_selected_task_id = selected_id if not selected_id.startswith("_section_") else None
            else:
                self.current_selected_task_id = None
                selected_id = None


        if selected_id and selected_id in self.tasks_status_by_id:
            task = self.tasks_status_by_id[selected_id]

            def add_detail(label: str, value: Any, label_tags: Tuple[str, ...] =("bold",), value_tags: Tuple[str, ...] =()):
                if value is not None and (isinstance(value, (str, int, float)) or (isinstance(value, list) and value)):
                    self.task_detail_text.insert(tk.END, f"{label}: ", label_tags)
                    if isinstance(value, list) and label in ["Modules ALMA (NLP)", "Mots-Clés (NLP)", "Tags de Style Treeview"]:
                        for idx, item in enumerate(value):
                            tag_to_apply = "module_tag" if label.startswith("Modules") else ("keyword_tag" if label.startswith("Mots-Clés") else ())
                            self.task_detail_text.insert(tk.END, str(item), tag_to_apply)
                            if idx < len(value) - 1: self.task_detail_text.insert(tk.END, ", ")
                        self.task_detail_text.insert(tk.END, "\n")
                    elif isinstance(value, dict) and label == "Sentiment Description (NLP)":
                        self.task_detail_text.insert(tk.END, f"Label: {value.get('label','N/A')}, Score: {value.get('score','N/A'):.2f}\n", value_tags)
                    else:
                        self.task_detail_text.insert(tk.END, f"{html.unescape(str(value))}\n", value_tags)

            self.task_detail_text.insert(tk.END, f"Détails de la Tâche (ID: {task['id']})\n", "h_section")
            add_detail("Ligne Rapport Maître", task['raw_line_number'])
            add_detail("Chemin Section", ' / '.join(task['section_path']), value_tags=("italic",))
            add_detail("Priorité", task.get('priority', 'N/A'))
            add_detail("Statut", task['status'])
            self.task_detail_text.insert(tk.END, "\n")

            self.task_detail_text.insert(tk.END, "Description Complète (Rapport Maître):\n", "h_section")
            self.task_detail_text.insert(tk.END, f"{html.unescape(task['full_text'])}\n\n", ("detail_text_main",))

            if task.get('notes'):
                self.task_detail_text.insert(tk.END, "Notes de Toni:\n", "h_section")
                self.task_detail_text.insert(tk.END, f"{html.unescape(task['notes'])}\n\n")

            nlp_details_present = any(task.get(k) for k in ["action_verb", "action_object", "mentioned_modules", "keywords", "task_type_classified", "sentiment_task_desc"])
            if nlp_details_present:
                self.task_detail_text.insert(tk.END, "Analyse Sémantique (NLP):\n", "h_section")
                add_detail("Verbe d'Action", task.get('action_verb'))
                add_detail("Objet de l'Action", task.get('action_object'))
                add_detail("Modules ALMA (NLP)", task.get('mentioned_modules'))
                add_detail("Mots-Clés (NLP)", task.get('keywords'))
                add_detail("Type Tâche (Classifié)", task.get('task_type_classified'))
                add_detail("Sentiment Description (NLP)", task.get('sentiment_task_desc'))

            # Pour le débogage, afficher les tags de style
            # add_detail("Tags de Style Treeview", task.get('style_tags'))

        elif selected_id and selected_id.startswith("_section_"):
            # Récupérer le texte du nœud de section (qui inclut l'icône)
            section_display_text = self.task_tree.item(selected_id, "text").strip()
            self.task_detail_text.insert(tk.END, "Section Sélectionnée:\n", "h_section")
            self.task_detail_text.insert(tk.END, section_display_text)
        else: # Aucune tâche ou section valide sélectionnée
            self.task_detail_text.insert(tk.END, "Sélectionnez une tâche dans la liste pour afficher ses détails.")

        self.task_detail_text.config(state=tk.DISABLED)
        self.logger.debug(f"Panneau de détails mis à jour pour la sélection : {selected_id or 'Aucune'}")


    def on_tree_double_click(self, event: Any): # event est un objet Event de Tkinter
        """Gère le double-clic sur un item du Treeview pour déplier/replier les sections."""
        item_id = self.task_tree.identify_row(event.y)
        if item_id and item_id.startswith("_section_"):
            try:
                is_open = self.task_tree.item(item_id, "open")
                # L'option "open" attend un booléen ou 0/1.
                self.task_tree.item(item_id, open=not bool(is_open)) # Convertir en bool avant d'inverser
                self.logger.debug(f"Double-clic sur section {item_id}, nouvel état open: {not bool(is_open)}")
            except tk.TclError as e_tcl:
                self.logger.warning(f"Erreur Tcl en accédant à l'item {item_id} lors du double-clic: {e_tcl}")
            except Exception as e_dc:
                 self.logger.error(f"Erreur inattendue lors du double-clic sur {item_id}: {e_dc}", exc_info=True)

    # Les méthodes d'action (mark_task_done, etc.) et _on_closing viendront dans le Bloc 6.
# (Suite du Bloc 5 - Méthodes de Chargement et d'Affichage)

    # --- Méthodes d'Action Utilisateur et de Gestion ---
    def get_selected_task_id_from_tree(self, show_messagebox_if_none: bool = True) -> Optional[str]:
        """
        Récupère l'ID de la tâche actuellement sélectionnée dans le Treeview.
        Retourne None si aucune tâche n'est sélectionnée ou si une section est sélectionnée.
        Affiche optionnellement un messagebox si aucune tâche n'est sélectionnée.
        """
        selected_items = self.task_tree.selection()
        if not selected_items:
            if show_messagebox_if_none:
                messagebox.showinfo("Aucune Sélection", "Veuillez d'abord sélectionner une tâche dans la liste.", parent=self.root)
            self.logger.debug("get_selected_task_id_from_tree: Aucune sélection dans le Treeview.")
            return None

        item_id = selected_items[0] # Prend le premier item sélectionné

        # Les sections ont des IID commençant par "_section_"
        if item_id.startswith("_section_"):
            if show_messagebox_if_none:
                messagebox.showinfo("Sélection Invalide", "Vous avez sélectionné une section. Veuillez sélectionner une tâche spécifique.", parent=self.root)
            self.logger.debug(f"get_selected_task_id_from_tree: Sélection d'une section ('{item_id}') ignorée.")
            return None

        # Vérifier si l'ID correspond bien à une tâche gérée (sécurité)
        if item_id not in self.tasks_status_by_id:
            self.logger.warning(f"get_selected_task_id_from_tree: ID sélectionné ('{item_id}') non trouvé dans tasks_status_by_id.")
            if show_messagebox_if_none:
                 messagebox.showwarning("Erreur Sélection", f"L'ID de tâche sélectionné '{item_id}' est inconnu.", parent=self.root)
            return None

        self.logger.debug(f"get_selected_task_id_from_tree: Tâche sélectionnée ID: {item_id}")
        return item_id

    def _update_task_status_and_refresh(self, task_id: str, new_status: str, note_update: Optional[str] = None, overwrite_note: bool = False):
        """
        Met à jour le statut et optionnellement la note d'une tâche, sauvegarde et rafraîchit l'UI.
        note_update: Texte à ajouter ou la nouvelle note si overwrite_note est True.
        overwrite_note: Si True, la note_update remplace la note existante. Sinon, elle est ajoutée.
        """
        if task_id in self.tasks_status_by_id:
            self.logger.info(f"Mise à jour tâche ID '{task_id}': nouveau statut='{new_status}', update_note='{note_update}', overwrite={overwrite_note}")
            task_data = self.tasks_status_by_id[task_id]
            task_data["status"] = new_status

            if note_update is not None:
                if overwrite_note:
                    task_data["notes"] = note_update.strip() if note_update.strip() else None
                else: # Ajouter le suffixe
                    current_note = task_data.get("notes", "") or ""
                    # Nettoyer les anciens suffixes de date pour ce statut avant d'ajouter le nouveau
                    if new_status == "accomplie":
                        current_note = re.sub(r"\s*\(Accomplie le .*?\)\s*","", current_note, flags=re.IGNORECASE).strip()
                    elif new_status == "en cours":
                        current_note = re.sub(r"\s*\(Débutée le .*?\)\s*","", current_note, flags=re.IGNORECASE).strip()

                    new_note_composed = f"{current_note} {note_update.strip()}".strip()
                    task_data["notes"] = new_note_composed if new_note_composed else None

            save_roadmap_status(self.tasks_status_by_id)
            self._populate_treeview() # Rafraîchit tout l'arbre pour refléter les changements de style/icône

            # Re-sélectionner l'item et mettre à jour le panneau de détails
            if self.task_tree.exists(task_id):
                self.task_tree.selection_set(task_id)
                self.task_tree.focus(task_id) # Mettre le focus sur l'item
                self.current_selected_task_id = task_id # Assurer que c'est bien l'ID sélectionné
            self.on_task_select() # Mettre à jour le panneau de détails
            self.logger.info(f"Tâche '{task_id}' marquée comme '{new_status}' et UI rafraîchie.")
        else:
            self.logger.error(f"Tentative de mise à jour du statut pour tâche ID inconnu: {task_id}")

    def mark_task_done(self):
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            self._update_task_status_and_refresh(task_id, "accomplie", f"(Accomplie le {datetime.date.today().isoformat()})")

    def mark_task_inprogress(self):
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            self._update_task_status_and_refresh(task_id, "en cours", f"(Débutée le {datetime.date.today().isoformat()})")

    def mark_task_todo(self):
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            # Nettoyer la note des mentions "Accomplie" ou "Débutée"
            note = self.tasks_status_by_id[task_id].get("notes", "") or ""
            note_cleaned = re.sub(r"\s*\((?:Accomplie|Débutée) le .*?\)\s*","", note, flags=re.IGNORECASE).strip()
            self._update_task_status_and_refresh(task_id, "à faire", note_cleaned if note_cleaned else "", overwrite_note=True)

    def mark_task_blocked(self): # NOUVELLE MÉTHODE
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            self._update_task_status_and_refresh(task_id, "bloquée", f"(Bloquée le {datetime.date.today().isoformat()})")

    def mark_task_pending(self): # NOUVELLE MÉTHODE
        task_id = self.get_selected_task_id_from_tree()
        if task_id:
            self._update_task_status_and_refresh(task_id, "en attente", f"(Mise en attente le {datetime.date.today().isoformat()})")

    def add_edit_note_to_task(self):
        task_id = self.get_selected_task_id_from_tree()
        if task_id and task_id in self.tasks_status_by_id:
            task_data = self.tasks_status_by_id[task_id]
            task_text_preview = task_data['text'][:70] + "..." if len(task_data['text']) > 70 else task_data['text']
            current_notes = task_data.get("notes", "") or ""

            # Utiliser une fenêtre Toplevel pour une boîte de dialogue plus grande pour les notes
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Note pour Tâche ID: {task_id[:8]}...")
            dialog.geometry("500x350")
            dialog.transient(self.root) # La rend modale par rapport à la fenêtre principale
            dialog.grab_set() # Empêche l'interaction avec la fenêtre principale
            dialog.resizable(False, False)

            ttk.Label(dialog, text=f"Note pour la tâche (L{task_data['raw_line_number']}):\n'{task_text_preview}'", wraplength=480).pack(pady=10)

            note_text_widget = scrolledtext.ScrolledText(dialog, width=55, height=10, font=self.font_text_normal, wrap=tk.WORD)
            note_text_widget.insert(tk.END, current_notes)
            note_text_widget.pack(pady=5, padx=10, expand=True, fill=tk.BOTH)
            note_text_widget.focus_set()

            new_note_ref = {"value": None} # Utiliser un dictionnaire pour passer par référence

            def on_ok():
                new_note_ref["value"] = note_text_widget.get("1.0", tk.END).strip()
                dialog.destroy()

            def on_cancel():
                dialog.destroy() # new_note_ref["value"] restera None

            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="Annuler", command=on_cancel).pack(side=tk.LEFT, padx=10)

            self.root.wait_window(dialog) # Attendre que la dialogue soit fermée

            new_note_final = new_note_ref["value"]
            if new_note_final is not None: # Si l'utilisateur a cliqué OK (même si la note est vide)
                self._update_task_status_and_refresh(task_id, task_data["status"], new_note_final, overwrite_note=True)
                self.logger.info(f"Note mise à jour pour la tâche '{task_id}'.")
        elif task_id: # Si get_selected_task_id_from_tree a retourné un ID mais qu'il n'est pas dans le dict
             self.logger.error(f"Tentative d'ajout de note pour tâche ID '{task_id}' non trouvée dans l'état actuel.")


    def analyze_submitted_text(self):
        """
        Analyse le texte soumis par l'utilisateur pour suggérer de nouvelles tâches.
        V0.3.0: Extraction basique de phrases candidates.
        """
        text_to_analyze = self.raw_text_input.get("1.0", tk.END).strip()
        if not text_to_analyze:
            messagebox.showinfo("Texte Vide", "Veuillez entrer du texte à analyser pour suggérer des tâches.", parent=self.root)
            return

        if not self.nlp_spacy_roadmap:
            messagebox.showwarning("Analyse Limitée", "Le module spaCy n'est pas chargé. L'analyse du texte soumis sera très limitée ou non effectuée.", parent=self.root)
            self.logger.warning("Tentative d'analyse de texte soumis sans spaCy chargé.")
            return

        self.logger.info(f"Analyse du texte soumis (longueur: {len(text_to_analyze)} chars) pour suggestion de tâches...")
        doc = self.nlp_spacy_roadmap(text_to_analyze)
        suggested_tasks_texts: List[str] = []
        for sent in doc.sents:
            sentence_text = sent.text.strip()
            # Heuristique simple : une phrase qui pourrait être une tâche
            # (contient un verbe, pas trop courte, pas une question simple)
            if len(sentence_text.split()) > 3 and any(token.pos_ == "VERB" for token in sent) and not sentence_text.endswith("?"):
                suggested_tasks_texts.append(sentence_text)

        if not suggested_tasks_texts:
            messagebox.showinfo("Analyse Texte Soumis", "Aucune tâche potentielle n'a pu être clairement extraite de ce texte.", parent=self.root)
            self.logger.info("Aucune tâche suggérée à partir du texte soumis.")
            return

        # Afficher les suggestions dans une nouvelle fenêtre Toplevel
        dialog = tk.Toplevel(self.root)
        dialog.title("Suggestions de Tâches Issues du Texte")
        dialog.geometry("600x400")
        dialog.transient(self.root); dialog.grab_set()

        ttk.Label(dialog, text="Les tâches suivantes ont été suggérées à partir de votre texte.\nCochez celles que vous souhaitez ajouter à la feuille de route :", wraplength=580).pack(pady=10)

        tasks_frame = ttk.Frame(dialog)
        tasks_frame.pack(pady=5, padx=10, expand=True, fill=tk.BOTH)

        task_vars: List[tk.BooleanVar] = []
        for i, task_text_suggestion in enumerate(suggested_tasks_texts):
            var = tk.BooleanVar(value=True) # Pré-cocher par défaut
            task_vars.append(var)
            # Utiliser un LabelFrame pour chaque tâche pour mieux grouper si on ajoute des options par tâche plus tard
            task_lf = ttk.LabelFrame(tasks_frame, text=f"Suggestion {i+1}")
            task_lf.pack(fill=tk.X, pady=2)
            cb = ttk.Checkbutton(task_lf, text=task_text_suggestion[:100] + ("..." if len(task_text_suggestion)>100 else ""), variable=var, wraplength=500)
            cb.pack(side=tk.LEFT, padx=5, pady=2)

        added_tasks_ref = {"count": 0}
        def on_add_selected_tasks():
            tasks_to_add_final: List[RoadmapTask] = []
            current_max_line_num = max(t['raw_line_number'] for t in self.tasks_status_by_id.values()) if self.tasks_status_by_id else 0

            for i, var in enumerate(task_vars):
                if var.get(): # Si la tâche est cochée
                    new_task_text = suggested_tasks_texts[i]
                    current_max_line_num +=1 # Pour un numéro de ligne unique (approximatif)

                    # Utiliser une section par défaut ou demander à l'utilisateur
                    default_section = ["Nouvelles Tâches Soumises"]

                    # Créer un ID unique (basé sur le texte et un timestamp pour éviter collisions)
                    task_id = hashlib.md5(f"{'/'.join(default_section)}_{new_task_text}_{time.time()}".encode()).hexdigest()[:16]

                    # Appliquer une analyse NLP basique sur le texte de la nouvelle tâche
                    new_task_nlp_data: RoadmapTask = { # Initialiser avec les champs minimaux
                        "id": task_id, "text": new_task_text, "full_text": new_task_text,
                        "source_document": "Soumission Utilisateur", "section_path": default_section,
                        "priority": "Moyenne", "status": "à faire", "notes": f"Suggérée depuis texte soumis le {datetime.date.today().isoformat()}",
                        "raw_line_number": current_max_line_num,
                        "action_verb": None, "action_object": None, "mentioned_modules": [],
                        "keywords": [], "task_type_classified": "Générique", "sentiment_task_desc": None,
                        "icon_key": "task_default", "style_tags": ["priority_Moyenne.Treeitem"]
                    }
                    # (On pourrait appeler une sous-partie de finalize_current_task pour le NLP ici)
                    # Pour l'instant, on laisse les champs NLP à leurs valeurs par défaut.
                    tasks_to_add_final.append(new_task_nlp_data)

            if tasks_to_add_final:
                for new_task_obj in tasks_to_add_final:
                    self.tasks_status_by_id[new_task_obj['id']] = new_task_obj
                save_roadmap_status(self.tasks_status_by_id)
                self.load_and_display_roadmap() # Recharger pour inclure les nouvelles tâches
                added_tasks_ref["count"] = len(tasks_to_add_final)
                self.logger.info(f"{len(tasks_to_add_final)} nouvelles tâches ajoutées depuis le texte soumis.")
            dialog.destroy()

        button_frame_dialog = ttk.Frame(dialog)
        button_frame_dialog.pack(pady=10)
        ttk.Button(button_frame_dialog, text="Ajouter Sélection", command=on_add_selected_tasks).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame_dialog, text="Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

        self.root.wait_window(dialog)
        if added_tasks_ref["count"] > 0:
            messagebox.showinfo("Tâches Ajoutées", f"{added_tasks_ref['count']} tâche(s) suggérée(s) ont été ajoutée(s) à la feuille de route.", parent=self.root)


    def _on_closing(self):
        """Gère la fermeture de la fenêtre principale."""
        self.logger.info("Demande de fermeture de l'application Roadmap Manager.")
        if messagebox.askokcancel("Quitter", f"Voulez-vous quitter {APP_NAME} ?\nL'état actuel des tâches sera sauvegardé.", parent=self.root):
            save_roadmap_status(self.tasks_status_by_id)
            self.logger.info("Application Roadmap Manager fermée par l'utilisateur.")
            self.root.destroy()
        else:
            self.logger.debug("Fermeture de l'application annulée par l'utilisateur.")

    # Le bloc if __name__ == "__main__": viendra dans le Bloc 7 (final).
# (Suite du Bloc 6 - Méthodes d'Action Utilisateur et Fermeture)

# --- Main Execution Block ---
if __name__ == "__main__":
    # Le logger global du module a déjà été configuré au début du script (Bloc 1)
    logger.info(f"--- Lancement de {APP_NAME} v{VERSION} ---")

    # Vérification critique de ALMA_BASE_DIR (déjà faite dans le Bloc 1, mais une
    # double vérification ici avant de lancer la GUI est une bonne pratique)
    # La variable ALMA_BASE_DIR est définie au niveau du module.
    if not ALMA_BASE_DIR.is_dir() or \
       not (ALMA_BASE_DIR / "Cerveau").is_dir() or \
       not (ALMA_BASE_DIR / "Connaissance").is_dir():
        # Ce message d'erreur est déjà géré de manière plus détaillée dans le Bloc 1
        # lors de la détermination de ALMA_BASE_DIR, incluant une messagebox.
        # Ici, on logue juste et on quitte si, pour une raison imprévue,
        # ALMA_BASE_DIR est devenu invalide après l'initialisation du module.
        critical_error_msg_main = f"ALMA_BASE_DIR ({ALMA_BASE_DIR}) n'est pas configuré correctement ou la structure du projet est corrompue. Arrêt de {APP_NAME}."
        logger.critical(critical_error_msg_main)
        # Pas besoin de messagebox ici si le Bloc 1 l'a déjà fait.
        sys.exit(1)
    else:
        logger.info(f"Utilisation de ALMA_BASE_DIR: {ALMA_BASE_DIR}")


    # Vérification de l'existence du Rapport Maître
    if not RAPPORT_MAITRE_PATH.exists():
        critical_error_message_rm = (
            f"Le fichier Rapport Maître est introuvable à l'emplacement attendu :\n{RAPPORT_MAITRE_PATH}\n\n"
            f"Ce fichier est essentiel pour le fonctionnement du Gestionnaire de Feuille de Route.\n"
            f"Veuillez vérifier son emplacement ou le chemin configuré."
        )
        logger.critical(critical_error_message_rm)
        # Tenter d'afficher une messagebox même si la racine Tk n'est pas encore là
        # pour les erreurs bloquantes avant même de créer la fenêtre principale.
        try:
            root_temp_error_rm_main = tk.Tk()
            root_temp_error_rm_main.withdraw() # Cacher la fenêtre racine temporaire
            messagebox.showerror(f"{APP_NAME} - Fichier Maître Manquant", critical_error_message_rm)
            root_temp_error_rm_main.destroy()
        except tk.TclError as e_tk_early_error:
            logger.error(f"Impossible d'afficher la messagebox d'erreur Tkinter (TclError): {e_tk_early_error}")
        except Exception as e_early_error_display:
             logger.error(f"Erreur inattendue lors de la tentative d'affichage de la messagebox d'erreur: {e_early_error_display}")
        sys.exit(1)
    else:
        logger.info(f"Fichier Rapport Maître trouvé à: {RAPPORT_MAITRE_PATH}")

    root_window_main: Optional[tk.Tk] = None # Pour le bloc finally
    try:
        logger.debug("Création de la fenêtre Tkinter principale...")
        root_window_main = tk.Tk()
        logger.debug("Instanciation de RoadmapManagerApp...")
        app = RoadmapManagerApp(root_window_main)
        logger.info("Lancement de la boucle principale Tkinter (mainloop)...")
        root_window_main.mainloop()
        logger.info(f"{APP_NAME} terminé proprement après fermeture de la fenêtre.")
    except Exception as e_main_app_runtime:
        # Ce bloc capture les erreurs qui pourraient survenir PENDANT l'initialisation
        # de RoadmapManagerApp ou pendant la boucle mainloop (bien que plus rare pour mainloop elle-même).
        error_title_runtime = f"{APP_NAME} - Erreur d'Exécution Majeure"
        error_details_runtime = f"Une erreur inattendue et majeure est survenue lors de l'exécution de l'application:\n\n{type(e_main_app_runtime).__name__}: {e_main_app_runtime}"

        logger.critical(f"ERREUR CRITIQUE DANS L'APPLICATION {APP_NAME}: {error_title_runtime}\n{error_details_runtime}", exc_info=True)
        # traceback.print_exc() # Le logger avec exc_info=True le fait déjà.

        # Tenter d'afficher une messagebox si possible
        if root_window_main and root_window_main.winfo_exists():
            try:
                messagebox.showerror(error_title_runtime, error_details_runtime, parent=root_window_main)
            except tk.TclError: pass # Si la racine est en train d'être détruite
            except Exception as e_msgbox_final: logger.error(f"Impossible d'afficher la messagebox d'erreur finale: {e_msgbox_final}")
        else: # Si la racine n'a pas pu être créée ou est déjà détruite
            # On pourrait tenter une racine temporaire, mais si l'erreur est dans Tkinter, ça peut échouer.
            # Le log critique est le plus important ici.
            pass
        sys.exit(1) # Quitter avec un code d'erreur
