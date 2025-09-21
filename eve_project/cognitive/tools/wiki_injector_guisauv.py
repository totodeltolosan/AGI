import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import wikipedia
import arxiv
from typing import Optional, Dict, Any, List, Tuple # Ajoutez Optional ici
# Pour Gutenberg, nous allons anticiper un import conditionnel plus propre
try:
    from gutenberg.acquire import load_etext
    from gutenberg.cleanup import strip_headers
    from gutenberg.query import get_metadata # Ajout pour les titres
    GUTENBERG_AVAILABLE = True
except ImportError:
    GUTENBERG_AVAILABLE = False
    load_etext = None
    strip_headers = None
    get_metadata = None
    print("AVERTISSEMENT: La bibliothèque Gutenberg (gutenbergpy) n'est pas installée. "
          "La source Project Gutenberg sera désactivée.")

import requests
import threading
import os
from pathlib import Path
import re
import time
import sys
import random

# ==============================================================================
# --- APPLICATION CONFIGURATION & METADATA ---
# ==============================================================================
APP_NAME = "ALMA - Injecteur de Connaissances"
VERSION = "1.5.3 Multi-Source (UI & Gutenberg Améliorés V20)" # Mise à jour version
NUM_ARTICLES_TO_FETCH_DEFAULT = 3
MAX_FETCH_ATTEMPTS_PER_SLOT = 5
MAX_TOTAL_RANDOM_ID_GENERATION_ATTEMPTS_GUTENBERG = 50
MAX_DOWNLOAD_ATTEMPTS_PER_ID_GUTENBERG = 2

# ==============================================================================
# --- THEME & STYLING (Inspiration "Genshin-Lite" adaptée) ---
# ==============================================================================

# Palette de couleurs (Reste identique, elle est bien définie)
COLOR_APP_BACKGROUND = "#F7F9FC"
COLOR_FRAME_BACKGROUND = "#E8EFF7"
COLOR_ACCENT_PRIMARY = "#5D9CEC"
COLOR_ACCENT_PRIMARY_ACTIVE = "#4A89DC"
COLOR_TEXT_PRIMARY = "#34495E"
COLOR_TEXT_SECONDARY = "#7F8C8D"
COLOR_SUCCESS = "#2ECC71"
COLOR_WARNING = "#F39C12"
COLOR_ERROR = "#E74C3C"
COLOR_INFO_TEXT = "#3498DB"
COLOR_PROGRESS_BAR_FILL = "#F1C40F"
COLOR_PROGRESS_BAR_BG = COLOR_FRAME_BACKGROUND

# --- Définition des NOMS de Polices et des SPÉCIFICATIONS (Tuples) ---
# Ces variables sont globales et utilisées pour configurer les objets tkfont.Font plus tard.

FONT_FAMILY_PRIMARY_NAME_WISHED = "Noto Sans"  # Ce que l'on souhaite utiliser
FONT_FAMILY_FALLBACK_NAME = "TkDefaultFont"    # Police de secours si la primaire n'est pas trouvée

# Les tuples _DEF stockent les (taille, style) pour chaque type de police.
# La famille de police réelle (souhaitée ou fallback) sera déterminée dans WikiInjectorApp._initialize_fonts
FONT_TITLE_DEF = (18, "bold")
FONT_SUBTITLE_DEF = (12, "bold")
FONT_BODY_BOLD_DEF = (10, "bold")
FONT_BODY_NORMAL_DEF = (10, "normal") # Expliciter "normal" pour weight
FONT_BUTTON_DEF = (10, "bold")
FONT_STATUS_MESSAGE_DEF = (9, "italic") # "italic" est un 'slant'
FONT_TOOLTIP_DEF = (9, "normal")

# --- Variables Globales pour les Objets tkfont.Font ---
# Ces variables seront initialisées avec de VRAIS objets tkfont.Font
# à l'intérieur de la méthode WikiInjectorApp._initialize_fonts,
# APRÈS que la fenêtre racine Tkinter (root) ait été créée.
# On les déclare ici avec un type hint pour la clarté et MyPy.
FONT_TITLE: Optional[tkfont.Font] = None
FONT_SUBTITLE: Optional[tkfont.Font] = None
FONT_BODY_BOLD: Optional[tkfont.Font] = None
FONT_BODY_NORMAL: Optional[tkfont.Font] = None
FONT_BUTTON: Optional[tkfont.Font] = None
FONT_STATUS_MESSAGE: Optional[tkfont.Font] = None
FONT_TOOLTIP: Optional[tkfont.Font] = None

# ==============================================================================
# --- ALMA BASE DIRECTORY & KNOWLEDGE PATH CONFIGURATION ---
# ==============================================================================
# Cette section est déjà bien améliorée et gère les fallbacks.
# Nous nous assurons juste que ALMA_BASE_DIR et CONNAISSANCE_DIR_BASE sont bien
# des objets Path et que TARGET_DIR_BASE_EXISTS est correctement mis à jour.

# Tentative de résolution de ALMA_BASE_DIR depuis la variable d'environnement
try:
    _alma_base_dir_str = os.environ["ALMA_BASE_DIR"]
    _temp_alma_base_dir = Path(_alma_base_dir_str).resolve()
    if not _temp_alma_base_dir.is_dir():
        print(f"AVERTISSEMENT: ALMA_BASE_DIR ('{_alma_base_dir_str}') n'est pas un répertoire valide. Utilisation du fallback.")
        ALMA_BASE_DIR = (Path.home() / "Documents" / "ALMA").resolve()
    else:
        ALMA_BASE_DIR = _temp_alma_base_dir
except KeyError:
    print("INFO: Variable d'environnement ALMA_BASE_DIR non définie. Utilisation du chemin de fallback.")
    ALMA_BASE_DIR = (Path.home() / "Documents" / "ALMA").resolve()

print(f"INFO: ALMA_BASE_DIR final utilisé: {ALMA_BASE_DIR}")

CONNAISSANCE_DIR_BASE = ALMA_BASE_DIR / "Connaissance"
TARGET_DIR_BASE_EXISTS = CONNAISSANCE_DIR_BASE.is_dir() # Vérifier si c'est un répertoire

# Création du dossier de base Connaissance si absent (avec gestion d'erreur améliorée)
if not TARGET_DIR_BASE_EXISTS:
    if CONNAISSANCE_DIR_BASE.exists() and not CONNAISSANCE_DIR_BASE.is_dir():
        # Le chemin existe mais n'est pas un répertoire (c'est un fichier par exemple)
        print(f"ERREUR CRITIQUE: Le chemin pour les connaissances '{CONNAISSANCE_DIR_BASE}' existe mais n'est pas un répertoire.")
        # Dans une application réelle, on pourrait afficher une messagebox et quitter.
        # Pour l'instant, on met TARGET_DIR_BASE_EXISTS à False.
        TARGET_DIR_BASE_EXISTS = False
    else:
        print(f"INFO: Le répertoire de base des connaissances '{CONNAISSANCE_DIR_BASE}' n'existe pas. Tentative de création...")
        try:
            CONNAISSANCE_DIR_BASE.mkdir(parents=True, exist_ok=True)
            TARGET_DIR_BASE_EXISTS = True # Mettre à jour après création réussie
            print(f"INFO: Répertoire '{CONNAISSANCE_DIR_BASE}' créé avec succès.")
        except OSError as e:
            print(f"ERREUR CRITIQUE: Impossible de créer le répertoire '{CONNAISSANCE_DIR_BASE}': {e}")
            TARGET_DIR_BASE_EXISTS = False # La création a échoué


# ==============================================================================
# --- SOURCES CONFIGURATION (Plus structuré) ---
# ==============================================================================
ARXIV_SEARCH_TYPE_KEYWORD = "[Recherche par Mots-clés Libres]" # Pour le menu déroulant arXiv

SOURCES_CONFIG = {
    "wikipedia": {
        "display_name": "Wikipédia (FR)",
        "fetch_function_name": "fetch_wikipedia_articles", # Nom de la fonction de fetch
        "target_dir_suffix": "wiki_auto_imports",
        "ui_elements": { # Décrit les éléments UI nécessaires
            "query_input_type": "entry", # "entry", "category_menu", "none"
            "query_label": "Mots-clés (optionnel, sinon aléatoire) :",
        },
        "requires_query_for_non_random": False, # Si True, une query est nécessaire si on ne veut pas aléatoire
        "supports_random": True
    },
    "arxiv": {
        "display_name": "arXiv (Résumés Scientifiques)",
        "fetch_function_name": "fetch_arxiv_abstracts",
        "target_dir_suffix": "arxiv_auto_imports",
        "ui_elements": {
            "query_input_type": "category_menu_with_keyword_entry", # Type spécial
            "category_label": "Domaine arXiv :",
            "keyword_label": "Mots-clés (si domaine non choisi) :",
            "categories": { # Clé lisible: code arXiv (utilisé pour la query)
                "Intelligence Artificielle (cs.AI)": "cs.AI",
                "Calcul et Langage (cs.CL)": "cs.CL",
                "Vision par Ordinateur (cs.CV)": "cs.CV",
                "Apprentissage Machine (cs.LG)": "cs.LG",
                "Systèmes Multi-Agents (cs.MA)": "cs.MA",
                "Robotique (cs.RO)": "cs.RO",
                "Astrophysique - Galaxies (astro-ph.GA)": "astro-ph.GA",
                "Maths - Combinatoire (math.CO)": "math.CO",
                "Maths - Théorie des Nombres (math.NT)": "math.NT",
                "Physique Quantique (quant-ph)": "quant-ph"
            }
        },
        "requires_query_for_non_random": True, # Il faut soit une catégorie, soit des mots-clés
        "supports_random": True # On simule l'aléatoire en choisissant une catégorie
    },
    "gutenberg": {
        "display_name": "Project Gutenberg (Livres Libres)",
        "fetch_function_name": "fetch_gutenberg_books",
        "target_dir_suffix": "gutenberg_auto_imports",
        "ui_elements": {
            "query_input_type": "entry",
            "query_label": "ID Livre (optionnel, sinon aléatoire) :",
        },
        "requires_query_for_non_random": False, # On peut laisser vide pour aléatoire
        "supports_random": GUTENBERG_AVAILABLE # Aléatoire seulement si la lib est là
    }
}

# Désactiver la source Gutenberg si la bibliothèque n'est pas disponible
if not GUTENBERG_AVAILABLE:
    if "gutenberg" in SOURCES_CONFIG:
        # On pourrait la supprimer ou la marquer comme désactivée
        # Pour l'instant, on la laisse mais sa fonction de fetch ne fera rien d'utile
        # Ou mieux, on la retire de la liste des sources affichables
        # Cela sera géré dans la création de l'UI
        pass


# Initialisation spécifique à Wikipédia
try:
    wikipedia.set_lang("fr")
except Exception as e:
    print(f"ERREUR: Impossible de configurer la langue pour Wikipédia: {e}")
    # On pourrait désactiver la source Wikipédia ici si c'est critique

# --- Fin Configuration ---

# Gestion de ALMA_BASE_DIR
try:
    ALMA_BASE_DIR = Path(os.environ["ALMA_BASE_DIR"]).resolve()
    CONNAISSANCE_DIR_BASE = ALMA_BASE_DIR / "Connaissance"
    TARGET_DIR_BASE_EXISTS = CONNAISSANCE_DIR_BASE.exists()
except KeyError:
    ALMA_BASE_DIR = (Path.home() / "Documents" / "ALMA").resolve()
    CONNAISSANCE_DIR_BASE = ALMA_BASE_DIR / "Connaissance"
    TARGET_DIR_BASE_EXISTS = False

# Configuration des Sources
ARXIV_SEARCH_TYPE_KEYWORD = "[Recherche par Mots-clés]"
SOURCES_CONFIG = {
    "wikipedia": {
        "display_name": "Wikipédia (FR)",
        "target_dir_suffix": "wiki_auto_imports",
        "query_label_default": "Mots-clés Wiki (optionnel, sinon aléatoire) :",
        "requires_query": False,
        "categories": {}
    },
    "arxiv": {
        "display_name": "arXiv (Résumés)",
        "target_dir_suffix": "arxiv_auto_imports",
        "query_label_default": "Mots-clés arXiv :", # Utilisé si on tape des mots-clés
        "query_label_category": "Catégorie arXiv :", # Utilisé si on choisit une catégorie
        "requires_query": False, # Devient False car on peut faire aléatoire
        "categories": { # Exemples de catégories arXiv populaires (Clé lisible: code arXiv)
            "Intelligence Artificielle": "cs.AI",
            "Calcul et Langage": "cs.CL",
            "Vision par Ordinateur": "cs.CV",
            "Apprentissage Machine": "cs.LG",
            "Systèmes Multi-Agents": "cs.MA",
            "Robotique": "cs.RO",
            "Astrophysique (Galaxies)": "astro-ph.GA",
            "Mathématiques (Combinatoire)": "math.CO",
            "Mathématiques (Théorie des Nombres)": "math.NT",
            "Physique Quantique": "quant-ph"
        }
    },
    "gutenberg": {
        "display_name": "Project Gutenberg (Livres)",
        "target_dir_suffix": "gutenberg_auto_imports",
        "query_label_default": "ID Livre Gutenberg (optionnel, sinon aléatoire) :",
        "requires_query": False,
        "categories": {}
    }
}

wikipedia.set_lang("fr")
# --- Fin Configuration ---

def sanitize_filename(title: str, max_len: int = 100) -> str:
    """TODO: Add docstring."""
    title = str(title).strip()
    title = re.sub(r'[\n\r]+', ' ', title)
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    title = title.replace(" ", "_")
    title = title.replace("'", "")
    # Éviter les points multiples ou les points en début/fin qui peuvent poser problème
    title = re.sub(r'\.+', '.', title).strip('.')
    if not title: title = "fichier_sans_titre"
    return title[:max_len]

    """TODO: Add docstring."""
def get_target_dir_for_source(source_key: str) -> Path:
    suffix = SOURCES_CONFIG.get(source_key, {}).get("target_dir_suffix", "default_imports")
    return CONNAISSANCE_DIR_BASE / suffix

MAX_FETCH_ATTEMPTS_PER_SLOT = 5 # Nombre de tentatives pour remplir un "slot" d'article
    """TODO: Add docstring."""

def fetch_wikipedia_articles(app_instance, query: str, num_to_fetch: int, target_dir: Path):
    articles_downloaded_this_run = 0
    max_search_results_multiplier = 5 # Obtenir plus de candidats

    page_titles_candidates = []
    if query:
        app_instance.update_status(f"Wiki: Recherche '{query[:30]}...'")
        try:
            search_results = wikipedia.search(query, results=num_to_fetch * max_search_results_multiplier)
            if not search_results:
                app_instance.update_status(f"Wiki: Aucun résultat pour '{query}'.", "warning")
                return 0
            page_titles_candidates = search_results
        except Exception as e_search:
            app_instance.update_status(f"Wiki: Erreur recherche '{query}': {e_search}", "error")
            return 0
    else:
        app_instance.update_status(f"Wiki: Recherche aléatoire de {num_to_fetch} article(s)...", "info")


    processed_titles_in_session = set()

    for i in range(num_to_fetch):
        if articles_downloaded_this_run >= num_to_fetch: break
        article_successfully_fetched_for_slot = False
        attempts_for_slot = 0

        while not article_successfully_fetched_for_slot and attempts_for_slot < MAX_FETCH_ATTEMPTS_PER_SLOT:
            attempts_for_slot += 1
            page_title_to_process = ""
            try:
                if query: # Recherche par mots-clés
                    if not page_titles_candidates:
                        app_instance.update_status(f"Wiki: Plus de candidats pour '{query}'.", "info")
                        return articles_downloaded_this_run # On a épuisé les candidats
                    page_title_to_process = page_titles_candidates.pop(0)
                    if page_title_to_process in processed_titles_in_session:
                        continue # Prochain candidat
                else: # Recherche aléatoire
                    page_title_to_process = wikipedia.random(pages=1)
                    if page_title_to_process in processed_titles_in_session:
                        if attempts_for_slot < MAX_FETCH_ATTEMPTS_PER_SLOT: continue # Réessayer pour ce slot aléatoire
                        else: break # Trop de tentatives pour ce slot

                processed_titles_in_session.add(page_title_to_process)
                app_instance.update_status(f"({articles_downloaded_this_run+1}/{num_to_fetch}) Wiki: {page_title_to_process[:35]}...")
                page = wikipedia.page(page_title_to_process, auto_suggest=False, redirect=True)
                filename = sanitize_filename(page.title) + "_WIKI.txt" # Ajout suffixe pour clarté
                filepath = target_dir / filename

                if filepath.exists():
                    app_instance.update_status(f"Wiki Existe: '{filename[:30]}...'.", "info")
                    if query: article_successfully_fetched_for_slot = False; break # Si query, on a épuisé un candidat
                    else: continue # Si random, on veut un autre article

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# SOURCE: Wikipédia\n# TITRE: {page.title}\n# URL: {page.url}\n\n{page.content}")
                articles_downloaded_this_run += 1
                app_instance.update_progress(articles_downloaded_this_run)
                app_instance.update_status(f"Wiki OK: '{page.title[:30]}...' ({articles_downloaded_this_run}/{num_to_fetch})", "success")
                article_successfully_fetched_for_slot = True
                time.sleep(0.1) # Politesse envers l'API
            except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError) as e_wiki:
                app_instance.update_status(f"Wiki Erreur '{page_title_to_process[:30]}...': {type(e_wiki).__name__}", "warning")
            except requests.exceptions.RequestException as e_req:
                app_instance.update_status(f"Wiki Erreur Réseau: {type(e_req).__name__}", "error")
                messagebox.showerror("Erreur Réseau", f"Problème de connexion à Wikipédia:\n{e_req}")
                return articles_downloaded_this_run # Arrêter pour erreur réseau
            except Exception as e_gen_wiki:
                app_instance.update_status(f"Wiki Erreur Inattendue: {str(e_gen_wiki)[:30]}...", "error")
                print(f"Erreur Wiki Inattendue (Titre: {page_title_to_process}): {e_gen_wiki}")

            if not article_successfully_fetched_for_slot and attempts_for_slot < MAX_FETCH_ATTEMPTS_PER_SLOT:
                time.sleep(0.2) # Petite pause avant de retenter

        if not article_successfully_fetched_for_slot:
             app_instance.update_status(f"Wiki: Échec pour obtenir l'article {i+1} après {MAX_FETCH_ATTEMPTS_PER_SLOT} tentatives.", "warning")
                 """TODO: Add docstring."""
    return articles_downloaded_this_run

def fetch_arxiv_abstracts(app_instance, query: str, num_to_fetch: int, target_dir: Path):
    articles_downloaded_this_run = 0

    search_query_arxiv = query.strip()
    if not search_query_arxiv: # Si la query est vide (mode aléatoire simulé)
        app_instance.update_status(f"arXiv: Mode aléatoire activé (catégorie surprise !).", "info")
        # Choisir une catégorie au hasard parmi celles définies
        random_category_key = random.choice(list(SOURCES_CONFIG["arxiv"]["categories"].keys()))
        search_query_arxiv = SOURCES_CONFIG["arxiv"]["categories"][random_category_key]
        app_instance.update_status(f"arXiv: Recherche aléatoire dans '{random_category_key}' ({search_query_arxiv})...", "info")
    else:
        app_instance.update_status(f"arXiv: Recherche '{search_query_arxiv[:30]}...', max {num_to_fetch}", "info")
        # Normaliser si c'est un code catégorie sans "cat:"
        if re.match(r"^[a-z\-\.]+$", search_query_arxiv) and not search_query_arxiv.startswith("cat:"):
            search_query_arxiv = f"cat:{search_query_arxiv}"
        elif " " in search_query_arxiv and not any(op in search_query_arxiv for op in ["AND", "OR", "NOT"]):
            # Si mots-clés multiples, les joindre par AND pour une recherche plus ciblée
            search_query_arxiv = " AND ".join(search_query_arxiv.split())


    try:
        search = arxiv.Search(
            query=search_query_arxiv,
            max_results=num_to_fetch * 2, # Obtenir un peu plus pour avoir une marge si certains existent déjà
            sort_by=arxiv.SortCriterion.SubmittedDate if not query.strip() else arxiv.SortCriterion.Relevance # Date pour aléatoire, Pertinence pour query
        )
        results_iterator = search.results()

        processed_arxiv_ids_in_session = set()

        for _i in range(num_to_fetch * MAX_FETCH_ATTEMPTS_PER_SLOT): # Boucle avec plus de tentatives globales
            if articles_downloaded_this_run >= num_to_fetch: break
            try:
                result = next(results_iterator)
                if result.entry_id in processed_arxiv_ids_in_session:
                    continue
                processed_arxiv_ids_in_session.add(result.entry_id)
            except StopIteration:
                app_instance.update_status(f"arXiv: Plus de résultats pour '{search_query_arxiv}'. {articles_downloaded_this_run} trouvés.", "info")
                break
            except requests.exceptions.RequestException as e_req:
                app_instance.update_status(f"arXiv Erreur Réseau: {type(e_req).__name__}", "error")
                messagebox.showerror("Erreur Réseau", f"Problème de connexion à arXiv.org:\n{e_req}")
                return articles_downloaded_this_run
            except Exception as e_arxiv_iter:
                app_instance.update_status(f"arXiv Erreur itération: {str(e_arxiv_iter)[:30]}...", "error")
                print(f"Erreur itération résultats arXiv: {e_arxiv_iter}"); time.sleep(0.5); continue

            try:
                title = result.title
                app_instance.update_status(f"({articles_downloaded_this_run+1}/{num_to_fetch}) arXiv: {title[:35]}...")
                filename = sanitize_filename(f"{result.entry_id.split('/')[-1]}_{title}") + "_ARXIV.txt"
                filepath = target_dir / filename

                if filepath.exists():
                    app_instance.update_status(f"arXiv Existe: '{filename[:30]}...'. Recherche du suivant.", "info")
                    continue

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# SOURCE: arXiv\n# TITRE: {title}\n# AUTEURS: {', '.join(str(a) for a in result.authors)}\n# ID ARXIV: {result.entry_id}\n")
                    f.write(f"# PUBLIÉ: {result.published.strftime('%Y-%m-%d') if result.published else 'N/A'}\n# MIS À JOUR: {result.updated.strftime('%Y-%m-%d') if result.updated else 'N/A'}\n")
                    f.write(f"# CATÉGORIES PRIMAIRES: {result.primary_category}\n")
                    all_categories = ", ".join(result.categories) if result.categories else "N/A"
                    f.write(f"# TOUTES CATÉGORIES: {all_categories}\n")
                    f.write(f"# RÉSUMÉ (ABSTRACT):\n{result.summary.replace(' EOL ', '\n')}\n\n") # Remplacer EOL par newline
                    if result.comment: f.write(f"# COMMENTAIRES: {result.comment}\n")
                    if result.journal_ref: f.write(f"# RÉFÉRENCE JOURNAL: {result.journal_ref}\n")
                    if result.doi: f.write(f"# DOI: {result.doi}\n")
                    f.write(f"# URL PAGE ARXIV: {result.entry_id}\n")
                    f.write(f"# URL PDF: {result.pdf_url if result.pdf_url else 'N/A'}\n")

                articles_downloaded_this_run += 1
                app_instance.update_progress(articles_downloaded_this_run)
                app_instance.update_status(f"arXiv OK: '{title[:30]}...' ({articles_downloaded_this_run}/{num_to_fetch})", "success")
                time.sleep(0.3) # Politesse envers l'API arXiv
            except Exception as e_process_arxiv:
                app_instance.update_status(f"arXiv Erreur traitement: {str(e_process_arxiv)[:30]}...", "error")
                print(f"Erreur traitement résultat arXiv '{getattr(result, 'title', 'Inconnu')}': {e_process_arxiv}"); time.sleep(0.5)

    except Exception as e_search_init_arxiv:
        app_instance.update_status(f"Erreur init recherche arXiv: {str(e_search_init_arxiv)[:30]}", "error")
            """TODO: Add docstring."""
        print(f"Erreur initialisation recherche arXiv pour '{search_query_arxiv}': {e_search_init_arxiv}")
    return articles_downloaded_this_run

def fetch_gutenberg_books(app_instance, query: str, num_to_fetch: int, target_dir: Path):
    articles_downloaded_this_run = 0
    processed_book_ids_in_session = set() # Garde une trace des ID déjà traités (succès ou échec définitif) dans cette session

    book_id_specific = None
    is_specific_id_mode = False

    if query.strip().isdigit():
        try:
            book_id_specific = int(query.strip())
            is_specific_id_mode = True
            if num_to_fetch > 1:
                app_instance.update_status(f"Gutenberg: ID {book_id_specific} spécifié. Téléchargement de 1 livre maximum.", "info")
            num_to_fetch = 1 # On ne télécharge qu'une fois un ID spécifique
            app_instance.update_status(f"Gutenberg: Recherche ID spécifique: {book_id_specific}", "info")
        except ValueError:
            app_instance.update_status("Gutenberg: ID de livre fourni invalide. Passage en mode aléatoire.", "warning")
            # query est implicitement vide, donc le mode aléatoire sera activé

    if not is_specific_id_mode:
        app_instance.update_status(f"Gutenberg: Recherche aléatoire de {num_to_fetch} livre(s)...", "info")

    # Boucle principale pour chaque "slot" de livre à télécharger
    for slot_index in range(num_to_fetch):
        if articles_downloaded_this_run >= num_to_fetch:
            break # On a déjà le nombre de livres demandés

        book_successfully_fetched_for_slot = False

        # Logique pour obtenir un ID de livre à essayer pour ce slot
        # Si mode ID spécifique, on n'essaie qu'une fois.
        # Si mode aléatoire, on essaie plusieurs ID jusqu'à succès ou limite.

        attempts_to_find_new_random_id = 0

        while not book_successfully_fetched_for_slot and \
              (is_specific_id_mode or attempts_to_find_new_random_id < MAX_TOTAL_RANDOM_ID_GENERATION_ATTEMPTS):

            if is_specific_id_mode:
                if slot_index > 0: # On a déjà traité l'ID spécifique au premier tour
                    break
                current_book_id_to_try = book_id_specific
                if current_book_id_to_try in processed_book_ids_in_session: # Déjà traité dans un appel précédent de start_fetching
                    app_instance.update_status(f"Gutenberg: ID {current_book_id_to_try} déjà traité/tenté dans cette session.", "info")
                    break # On ne retente pas un ID spécifique déjà traité
            else: # Mode aléatoire
                attempts_to_find_new_random_id += 1
                current_book_id_to_try = random.randint(1, 72000) # Plage des ID Gutenberg
                if current_book_id_to_try in processed_book_ids_in_session:
                    if attempts_to_find_new_random_id < MAX_TOTAL_RANDOM_ID_GENERATION_ATTEMPTS:
                        continue # Cet ID aléatoire a déjà été traité, en prendre un autre
                    else:
                        app_instance.update_status(f"Gutenberg: Limite d'essais d'ID aléatoires atteinte pour le slot {slot_index + 1}.", "warning")
                        break # Sortir de la boucle de recherche d'ID pour ce slot

            if current_book_id_to_try is None: # Ne devrait pas arriver ici
                break

            # Marquer cet ID comme "en cours de tentative" pour cette session,
            # pour ne pas le reprendre en aléatoire si le téléchargement échoue définitivement pour lui.
            # On l'ajoute ici, car même si le téléchargement échoue pour une raison "définitive" (ex: 404),
            # on ne veut pas le reprendre en aléatoire.
            if current_book_id_to_try not in processed_book_ids_in_session:
                 processed_book_ids_in_session.add(current_book_id_to_try)
            else: # Si c'est un ID spécifique qui était déjà dans processed, on ne fait rien de plus pour ce slot.
                  # Si c'est un ID aléatoire qui était déjà là (ne devrait pas arriver à cause du `continue` plus haut), on loge.
                if not is_specific_id_mode:
                    print(f"DEBUG Gutenberg: ID aléatoire {current_book_id_to_try} déjà dans processed_ids, mais on continue la tentative de DL.")


            # Tentatives de téléchargement pour cet ID spécifique
            download_attempts_for_this_id = 0
            while not book_successfully_fetched_for_slot and download_attempts_for_this_id < MAX_DOWNLOAD_ATTEMPTS_PER_ID_GUTENBERG:
                download_attempts_for_this_id += 1
                try:
                    app_instance.update_status(f"({articles_downloaded_this_run + 1}/{num_to_fetch}) Gutenberg ID: {current_book_id_to_try} (DL essai {download_attempts_for_this_id})...")

                    # Tenter de récupérer le titre via les métadonnées
                    book_title = None
                    try:
                        # Note: get_metadata peut être lent ou échouer si le cache n'est pas construit
                        # ou si l'ID n'a pas de métadonnées facilement accessibles.
                        # Il est préférable de mettre un timeout ou de le faire dans un thread si c'est trop long.
                        # Pour l'instant, on essaie directement.
                        title_meta = get_metadata('title', current_book_id_to_try)
                        if title_meta:
                            book_title = list(title_meta)[0] # get_metadata retourne un set
                    except Exception as e_meta:
                        app_instance.update_status(f"Gutenberg ID {current_book_id_to_try}: Titre non récupérable ({str(e_meta)[:20]}...). Utilisation de l'ID.", "info")
                        print(f"Info Gutenberg: Erreur récupération titre pour ID {current_book_id_to_try}: {e_meta}")

                    book_title_for_filename = book_title if book_title else f"Book_ID_{current_book_id_to_try}"

                    text = strip_headers(load_etext(current_book_id_to_try)).strip()

                    if not text:
                        app_instance.update_status(f"Gutenberg ID {current_book_id_to_try}: Contenu vide ou texte non trouvé.", "warning")
                        # Si contenu vide, cet ID est probablement invalide ou non disponible en texte plein.
                        # Inutile de retenter le téléchargement pour cet ID.
                        break # Sortir de la boucle while download_attempts_for_this_id

                    filename = sanitize_filename(book_title_for_filename) + "_GUT.txt"
                    filepath = target_dir / filename

                    if filepath.exists():
                        app_instance.update_status(f"Gutenberg Existe: '{filename}'.", "info")
                        # Si c'est un ID spécifique, on s'arrête. Si c'est aléatoire, on veut un *autre* livre.
                        if is_specific_id_mode:
                            book_successfully_fetched_for_slot = False # Marquer comme non réussi pour ce slot car déjà existant
                            break # Sortir de la boucle while download_attempts_for_this_id
                        else:
                            # En mode aléatoire, si le fichier existe, on veut un autre ID, donc on sort de cette boucle de DL
                            # et la boucle externe `while not book_successfully_fetched_for_slot` continuera de chercher un nouvel ID.
                            break # Sortir de la boucle while download_attempts_for_this_id pour essayer un autre ID aléatoire

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"# SOURCE: Project Gutenberg\n")
                        if book_title: f.write(f"# TITRE: {book_title}\n")
                        else: f.write(f"# TITRE (approximatif): {book_title_for_filename}\n")
                        f.write(f"# ID GUTENBERG: {current_book_id_to_try}\n\n")
                        f.write(text)

                    articles_downloaded_this_run += 1
                    app_instance.update_progress(articles_downloaded_this_run)
                    app_instance.update_status(f"Gutenberg OK: '{filename}' ({articles_downloaded_this_run}/{num_to_fetch})", "success")
                    book_successfully_fetched_for_slot = True # Succès pour ce slot !
                    # Pas besoin de `processed_book_ids_in_session.add` ici, car il est ajouté avant la boucle de DL

                except requests.exceptions.HTTPError as e_http:
                     app_instance.update_status(f"Gutenberg ID {current_book_id_to_try}: Erreur HTTP {e_http.response.status_code}.", "warning")
                     # Erreur HTTP (ex: 404 Not Found) signifie que l'ID est probablement mauvais.
                     break # Sortir de la boucle while download_attempts_for_this_id
                except Exception as e_gutenberg:
                    # Inclut les erreurs de la bibliothèque gutenberg si l'ID n'existe pas
                    # ou si load_etext échoue pour d'autres raisons.
                    app_instance.update_status(f"Gutenberg ID {current_book_id_to_try} Erreur: {str(e_gutenberg)[:30]}...", "error")
                    print(f"Erreur Gutenberg (ID: {current_book_id_to_try}): {e_gutenberg}")
                    # Si c'est une erreur "Text Ebook Not Available" ou similaire, l'ID est mauvais.
                    if "Text Ebook Not Available" in str(e_gutenberg) or "No Etext Found" in str(e_gutenberg):
                        break # Sortir de la boucle while download_attempts_for_this_id
                    # Pour d'autres erreurs, on peut laisser la boucle de DL retenter si MAX_DOWNLOAD_ATTEMPTS_PER_ID > 1

                if not book_successfully_fetched_for_slot and download_attempts_for_this_id < MAX_DOWNLOAD_ATTEMPTS_PER_ID:
                    time.sleep(1.5) # Pause plus longue avant de retenter le téléchargement pour le MÊME ID

            # Fin de la boucle while download_attempts_for_this_id (tentatives de téléchargement pour current_book_id_to_try)
            # Si on est en mode ID spécifique et qu'on a échoué ici, on sort de la boucle principale pour ce slot.
            if is_specific_id_mode and not book_successfully_fetched_for_slot:
                break # Sortir de la boucle while not book_successfully_fetched_for_slot (recherche d'ID)

        # Fin de la boucle while not book_successfully_fetched_for_slot (recherche d'ID pour le slot actuel)
        if not book_successfully_fetched_for_slot:
            status_msg_fail = f"Gutenberg: Échec final pour obtenir le livre {slot_index + 1}/{num_to_fetch}."
            if is_specific_id_mode and book_id_specific: status_msg_fail += f" (ID: {book_id_specific})"
            app_instance.update_status(status_msg_fail, "warning")
            if is_specific_id_mode: # Si l'ID spécifique a échoué, on n'essaie pas plus pour Gutenberg
                """TODO: Add docstring."""
                break

    return articles_downloaded_this_run

def fetch_and_save_thread_target_main(app_instance, source_key: str, query: str, num_articles: int):
    target_dir_for_source = get_target_dir_for_source(source_key)

    if not TARGET_DIR_BASE_EXISTS:
        try: CONNAISSANCE_DIR_BASE.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            app_instance.update_status(f"Erreur création {CONNAISSANCE_DIR_BASE}: {e}", "error")
            messagebox.showerror("Erreur Dossier", f"Impossible de créer le dossier de base des connaissances:\n{CONNAISSANCE_DIR_BASE}\n\n{e}")
            app_instance.enable_button(); return

    if not target_dir_for_source.exists():
        try: target_dir_for_source.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            app_instance.update_status(f"Erreur création {target_dir_for_source.name}: {e}", "error")
            messagebox.showerror("Erreur Dossier", f"Impossible de créer le dossier cible:\n{target_dir_for_source}\n\n{e}")
            app_instance.enable_button(); return

    articles_fetched_count = 0
    if source_key == "wikipedia":
        articles_fetched_count = fetch_wikipedia_articles(app_instance, query, num_articles, target_dir_for_source)
    elif source_key == "arxiv":
        articles_fetched_count = fetch_arxiv_abstracts(app_instance, query, num_articles, target_dir_for_source)
    elif source_key == "gutenberg":
        articles_fetched_count = fetch_gutenberg_books(app_instance, query, num_articles, target_dir_for_source)

    source_name_display = SOURCES_CONFIG.get(source_key, {}).get("display_name", source_key.capitalize())
    query_display = f"pour '{query[:30]}...'" if query else "en mode aléatoire"

    final_message_type = "info"
    if articles_fetched_count == num_articles:
        final_status_msg = f"{source_name_display}: Terminé ! {articles_fetched_count} éléments téléchargés {query_display}."
        final_box_msg = f"{articles_fetched_count} éléments de {source_name_display} ont été téléchargés avec succès dans\n{target_dir_for_source.resolve()}"
        messagebox.showinfo("Succès", final_box_msg)
    elif articles_fetched_count > 0:
        final_status_msg = f"{source_name_display}: Partiel. {articles_fetched_count}/{num_articles} éléments téléchargés {query_display}."
        final_box_msg = f"Seulement {articles_fetched_count} sur {num_articles} éléments de {source_name_display} ont pu être téléchargés {query_display}."
        messagebox.showwarning("Partiellement Terminé", final_box_msg); final_message_type = "warning"
    else:
        final_status_msg = f"{source_name_display}: Échec. Aucun élément récupéré {query_display}."
        final_box_msg = f"Aucun élément de {source_name_display} n'a pu être téléchargé {query_display}."
        messagebox.showerror("Échec", final_box_msg); final_message_type = "error"
            """TODO: Add docstring."""

    app_instance.update_status(final_status_msg, final_message_type)
    app_instance.enable_button()
    app_instance.update_progress(articles_fetched_count) # Mettre à jour une dernière fois

class WikiInjectorApp:
    def _initialize_fonts(self): # Déplacé en premier pour la lisibilité, car __init__ l'appelle tôt
        """Initialise les objets tkfont.Font globaux après la création de la fenêtre racine."""
        # Rendre les globales modifiables dans cette portée de fonction
        global FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY_NORMAL, \
               FONT_BUTTON, FONT_STATUS_MESSAGE, FONT_TOOLTIP, \
               FONT_FAMILY_PRIMARY_NAME_WISHED, FONT_FAMILY_FALLBACK_NAME, \
               FONT_TITLE_DEF, FONT_SUBTITLE_DEF, FONT_BODY_BOLD_DEF, FONT_BODY_NORMAL_DEF, \
               FONT_BUTTON_DEF, FONT_STATUS_MESSAGE_DEF, FONT_TOOLTIP_DEF

        actual_font_family_to_use = FONT_FAMILY_PRIMARY_NAME_WISHED
        try:
            # Test simple pour voir si la police souhaitée est disponible avec Tkinter
            tkfont.Font(family=FONT_FAMILY_PRIMARY_NAME_WISHED, size=10)
            print(f"INFO: Police primaire '{FONT_FAMILY_PRIMARY_NAME_WISHED}' trouvée et sera utilisée.")
                """TODO: Add docstring."""
        except tk.TclError:
            print(f"AVERTISSEMENT: Police primaire '{FONT_FAMILY_PRIMARY_NAME_WISHED}' non trouvée. Utilisation de la police de fallback '{FONT_FAMILY_FALLBACK_NAME}'.")
            actual_font_family_to_use = FONT_FAMILY_FALLBACK_NAME
            # Les tuples _DEF (taille, style) restent les mêmes, seule la famille change lors de l'instanciation.

        # Fonction utilitaire pour parser les tuples _DEF et retourner les options pour tkfont.Font
        def get_font_creation_options(font_def_tuple: Tuple[int, str]) -> Dict[str, Any]:
            options = {"size": font_def_tuple[0]} # Le premier élément est toujours la taille
            if len(font_def_tuple) > 1:
                style_str = font_def_tuple[1].lower() # Style string (ex: "bold", "italic", "bold italic")
                if "bold" in style_str:
                    options["weight"] = "bold"
                if "italic" in style_str:
                    options["slant"] = "italic"
                # On pourrait ajouter "underline", "overstrike" si besoin
            return options

        # Créer les objets tkfont.Font en utilisant la famille de police déterminée
        # et les spécifications (taille, style) des tuples _DEF.
        FONT_TITLE = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_TITLE_DEF))
        FONT_SUBTITLE = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_SUBTITLE_DEF))
        FONT_BODY_BOLD = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_BODY_BOLD_DEF))
            """TODO: Add docstring."""
        FONT_BODY_NORMAL = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_BODY_NORMAL_DEF))
        FONT_BUTTON = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_BUTTON_DEF))
        FONT_STATUS_MESSAGE = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_STATUS_MESSAGE_DEF))
        FONT_TOOLTIP = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_TOOLTIP_DEF))


    def __init__(self, root_window):
        self.root = root_window
        self.root.title(f"{APP_NAME} - v{VERSION}")
        self.root.geometry("650x520")
        self.root.configure(bg=COLOR_APP_BACKGROUND) # UTILISATION DE LA NOUVELLE CONSTANTE

        # --- Initialisation des Polices (CRUCIAL : APRÈS root ET AVANT style) ---
        self._initialize_fonts() # Appel à la méthode qui crée les objets tkfont.Font

        # --- Styles ttk ---
        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure("TFrame", background=COLOR_APP_BACKGROUND)
        style.configure("TLabel", foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY_NORMAL, background=COLOR_APP_BACKGROUND)
        style.configure("Title.TLabel", font=FONT_TITLE, foreground=COLOR_TEXT_PRIMARY, background=COLOR_APP_BACKGROUND)
        style.configure("Status.TLabel", font=FONT_STATUS_MESSAGE, wraplength=620, background=COLOR_APP_BACKGROUND) # Couleur texte gérée par update_status
        style.configure("Bold.TLabel", font=FONT_BODY_BOLD, foreground=COLOR_TEXT_PRIMARY, background=COLOR_APP_BACKGROUND)

        style.configure("TButton", font=FONT_BUTTON, borderwidth=1)
        style.map("TButton",
                  background=[('!disabled', COLOR_ACCENT_PRIMARY),
                              ('active', COLOR_ACCENT_PRIMARY_ACTIVE),
                              ('pressed', COLOR_ACCENT_PRIMARY_ACTIVE),
                              ('disabled', '#BFBFBF')],
                  foreground=[('!disabled', 'white'),
                              ('disabled', COLOR_TEXT_SECONDARY)],
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

        style.configure("Gold.Horizontal.TProgressbar",
                        troughcolor=COLOR_PROGRESS_BAR_BG,
                        bordercolor=COLOR_TEXT_SECONDARY,
                        background=COLOR_PROGRESS_BAR_FILL)

        style.configure("TLabelFrame",
                        background=COLOR_FRAME_BACKGROUND,
                        foreground=COLOR_TEXT_PRIMARY,
                        font=FONT_BODY_BOLD, # Police pour le titre du LabelFrame
                        borderwidth=1,
                        relief="groove")
        style.configure("TLabelFrame.Label", # Style spécifique pour le texte du titre du LabelFrame
                        font=FONT_BODY_BOLD,
                        foreground=COLOR_TEXT_PRIMARY,
                        background=COLOR_FRAME_BACKGROUND) # Assurer que le fond du label est celui du cadre

        font=FONT_BODY_NORMAL
        # Note: La couleur de fond/texte des OptionMenu est difficile à surcharger de manière fiable avec ttk
        # On se concentre sur la police. Le thème 'clam' devrait donner un aspect correct.

        # --- Création des Widgets ---
        main_frame = ttk.Frame(self.root, padding="15") # Le style "TFrame" s'applique ici
        main_frame.pack(expand=True, fill=tk.BOTH)

        title_label = ttk.Label(main_frame, text="Injecteur de Connaissances ALMA", style="Title.TLabel", anchor="center")
        title_label.pack(pady=(0, 15), fill=tk.X)

        config_frame = ttk.LabelFrame(main_frame, text="Options de Récupération", padding="10") # Le style "TLabelFrame" s'applique
        config_frame.pack(fill=tk.X, pady=10)

        # --- Ligne 0: Source ---
        ttk.Label(config_frame, text="Source :", style="Bold.TLabel").grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")

        self.source_key_var = tk.StringVar(value="wikipedia")
        self.available_source_keys = [key for key in SOURCES_CONFIG.keys() if not (key == "gutenberg" and not GUTENBERG_AVAILABLE)]
        source_display_names = [SOURCES_CONFIG[key]["display_name"] for key in self.available_source_keys]

        self.source_display_to_key_map = {SOURCES_CONFIG[key]["display_name"]: key for key in self.available_source_keys}

        # Déterminer le nom d'affichage par défaut pour la source
        default_display_name_val = "" # Valeur si aucune source n'est disponible
        if "wikipedia" in self.available_source_keys:
            default_display_name_val = SOURCES_CONFIG["wikipedia"]["display_name"]
        elif source_display_names: # S'il y a des sources disponibles mais pas wikipedia
            default_display_name_val = source_display_names[0]
        # Si source_display_names est vide, default_display_name_val restera ""

        self.current_source_display_var = tk.StringVar(value=default_display_name_val)

        # Valeur initiale à afficher dans l'OptionMenu
        initial_option_menu_value = self.current_source_display_var.get() if source_display_names else " (Aucune Source) "
        # Options à afficher dans le menu déroulant
        options_for_menu = source_display_names if source_display_names else [" (Aucune Source) "]


        self.source_menu = ttk.OptionMenu(config_frame,
                                     self.current_source_display_var,
                                     initial_option_menu_value, # Valeur initiale affichée
                                     *options_for_menu,         # Options dans le menu déroulant
                                     command=self.on_source_change) # VIRGULE MANQUANTE AJOUTÉE ICI
                                     # Plus de style personnalisé ici pour éviter l'erreur TclError Layout

        self.source_menu.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Vérifier s'il y a des sources affichables et désactiver le menu si ce n'est pas le cas
        if not source_display_names: # CORRIGÉ : Ajout de ':' et indentation correcte
            self.source_menu.config(state=tk.DISABLED)
            self.current_source_display_var.set(" (Aucune Source Disponible) ") # Message plus clair

        # --- Ligne 1: Catégorie/Requête ---
        self.category_query_label = ttk.Label(config_frame, text="Texte du Label Dynamique", style="Bold.TLabel")
        self.category_query_label.grid(row=1, column=0, padx=(0,10), pady=5, sticky="w")

        self.query_widget_frame = ttk.Frame(config_frame) # Le style "TFrame" s'applique
        self.query_widget_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.query_widget_frame.columnconfigure(0, weight=1)

        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(self.query_widget_frame, textvariable=self.query_var, width=45, font=FONT_BODY_NORMAL) # Utilisation de FONT_BODY_NORMAL

        self.category_var = tk.StringVar()
        self.category_menu = ttk.OptionMenu(self.query_widget_frame, self.category_var, "",
                                            command=self.on_arxiv_category_change
                                            )

        # --- Ligne 2: Nombre d'articles ---
        ttk.Label(config_frame, text="Nombre :", style="Bold.TLabel").grid(row=2, column=0, padx=(0,10), pady=5, sticky="w")
        self.num_articles_var = tk.IntVar(value=NUM_ARTICLES_TO_FETCH_DEFAULT)
        self.num_articles_spinbox = ttk.Spinbox(config_frame, from_=1, to=200,
                                           textvariable=self.num_articles_var, width=7,
                                           command=self.update_max_progress, font=FONT_BODY_NORMAL) # Utilisation de FONT_BODY_NORMAL
        self.num_articles_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        config_frame.columnconfigure(1, weight=1)

        self.fetch_button = ttk.Button(main_frame, text="Lancer la Récupération", command=self.start_fetching, width=30) # Le style "TButton" s'applique
        self.fetch_button.pack(pady=(20, 10), ipady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate",
                                            variable=self.progress_var, style="Gold.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=10)

        self.status_label_var = tk.StringVar()
        self.status_label_var.set("Prêt à collecter des connaissances !")
        status_label_widget = ttk.Label(main_frame, textvariable=self.status_label_var, style="Status.TLabel", anchor="center")
        status_label_widget.pack(pady=(10,0), fill=tk.X, expand=True)
        self.status_label_widget_ref = status_label_widget

        self.update_ui_for_source()

        if not TARGET_DIR_BASE_EXISTS:
             self.update_status(f"ALMA_BASE_DIR non défini ou {CONNAISSANCE_DIR_BASE} non trouvé/créé.", "error")
             self.fetch_button.config(state=tk.DISABLED)

        # --- Ligne 2: Nombre d'articles ---
        self.num_articles_var = tk.IntVar(value=NUM_ARTICLES_TO_FETCH_DEFAULT)
        self.num_articles_spinbox = ttk.Spinbox(config_frame, from_=1, to=200, # Renommé pour clarté
                                           textvariable=self.num_articles_var, width=7,
                                           command=self.update_max_progress, font=FONT_BODY_NORMAL)
        self.num_articles_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        config_frame.columnconfigure(1, weight=1)

        self.fetch_button = ttk.Button(main_frame, text="Lancer la Récupération", command=self.start_fetching, width=30)
        self.fetch_button.pack(pady=(20, 10), ipady=5) # Plus d'espace avant le bouton

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate",
                                            variable=self.progress_var, style="Gold.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=10)

        self.status_label_var = tk.StringVar()
        self.status_label_var.set("Prêt à collecter des connaissances !")
        status_label_widget = ttk.Label(main_frame, textvariable=self.status_label_var, style="Status.TLabel", anchor="center")
        status_label_widget.pack(pady=(10,0), fill=tk.X, expand=True)
        self.status_label_widget_ref = status_label_widget

        self.update_ui_for_source() # Appel initial pour configurer l'UI pour la source par défaut

        if not TARGET_DIR_BASE_EXISTS:
             self.update_status(f"ALMA_BASE_DIR non défini ou {CONNAISSANCE_DIR_BASE} non trouvé.", "warning")
             # Le messagebox est bon ici

    def _update_option_menu(self, option_menu_widget, string_var, new_default_value, new_options_list):
        """Met à jour un ttk.OptionMenu avec de nouvelles options et une nouvelle valeur par défaut."""
        string_var.set(new_default_value) # Définir la nouvelle valeur par défaut

        menu = option_menu_widget["menu"] # Obtenir l'objet menu interne
        menu.delete(0, "end") # Effacer toutes les anciennes options

        for option in new_options_list:
            # La lambda est cruciale pour que la bonne valeur soit passée au command
            # et pour redéclencher la mise à jour de l'UI si c'est le menu arXiv
            if option_menu_widget == self.category_menu: # Cas spécifique du menu catégorie arXiv
                 menu.add_command(label=option, command=lambda val=option: (string_var.set(val), self.on_arxiv_category_change()))
            else: # Cas général (pour le menu source, bien que ses options soient fixes au début)
                 menu.add_command(label=option, command=tk._setit(string_var, option))


    def on_source_change(self, event=None):
        """Appelé uniquement lorsque le menu principal 'Source :' change."""
        selected_display_name = self.current_source_display_var.get()
        source_key = self.source_display_to_key_map[selected_display_name]
        self.source_key_var.set(source_key)

        # Réinitialiser les variables de requête spécifiques à la source précédente
        self.query_var.set("")
        self.category_var.set("") # Important pour arXiv

        self.update_ui_for_source()

    def on_arxiv_category_change(self, event=None):
        """Appelé uniquement lorsque la sélection dans le menu catégorie d'arXiv change."""
        # Cette fonction met simplement à jour l'UI. La valeur de self.category_var est déjà mise à jour par le command de l'OptionMenu.
        self.update_ui_for_source() # Réutilise la logique principale de mise à jour UI

    def update_ui_for_source(self):
        """Met à jour l'interface (label de requête, champ de saisie/menu catégorie)
           en fonction de la source actuellement sélectionnée et, pour arXiv, de la catégorie sélectionnée."""
        source_key = self.source_key_var.get()
        if not source_key: source_key = "wikipedia" # Fallback

        source_config = SOURCES_CONFIG[source_key]

        # Cacher tous les widgets de query spécifiques par défaut
        self.query_entry.pack_forget()
        self.category_menu.pack_forget()

        if source_key == "wikipedia":
            self.category_query_label.config(text=source_config["query_label_default"])
            self.query_entry.pack(fill=tk.X, expand=True)

        elif source_key == "arxiv":
            arxiv_categories_display = [ARXIV_SEARCH_TYPE_KEYWORD] + list(source_config["categories"].keys())

            # Mettre à jour les options et la valeur sélectionnée du menu catégorie arXiv
            # Si self.category_var n'a pas de valeur ou une valeur invalide, la mettre par défaut
            if not self.category_var.get() or self.category_var.get() not in arxiv_categories_display:
                self._update_option_menu(self.category_menu, self.category_var, arxiv_categories_display[0], arxiv_categories_display)
            else: # Juste pour s'assurer que le menu est bien peuplé même si la var est déjà bonne
                self._update_option_menu(self.category_menu, self.category_var, self.category_var.get(), arxiv_categories_display)

            self.category_menu.pack(fill=tk.X, expand=True) # Toujours afficher le menu pour arXiv

            if self.category_var.get() == ARXIV_SEARCH_TYPE_KEYWORD:
                self.category_query_label.config(text=source_config["query_label_default"]) # "Mots-clés arXiv :"
                self.query_entry.pack(fill=tk.X, expand=True, pady=(5,0)) # Afficher le champ texte, avec un petit padding
            else:
                self.category_query_label.config(text=source_config["query_label_category"]) # "Catégorie arXiv :"
                self.query_entry.pack_forget() # Cacher le champ texte

    """TODO: Add docstring."""
        elif source_key == "gutenberg":
            self.category_query_label.config(text=source_config["query_label_default"])
            self.query_entry.pack(fill=tk.X, expand=True)

        self.update_max_progress()


    def update_max_progress(self):
        # ... (inchangé, c'est bien)
        try:
            """TODO: Add docstring."""
            num_articles = self.num_articles_var.get()
            if num_articles <= 0: num_articles = 1
        except tk.TclError:
            num_articles = NUM_ARTICLES_TO_FETCH_DEFAULT
            self.num_articles_var.set(num_articles)
        self.progress_bar.config(maximum=num_articles)
        self.progress_var.set(0)

    def start_fetching(self):
        # ... (inchangé, la logique de récupération de query_to_use était déjà correcte)
        self.fetch_button.config(state=tk.DISABLED)
        source_key = self.source_key_var.get()
        source_config = SOURCES_CONFIG[source_key]

        query_to_use = ""
        try:
            num_articles = self.num_articles_var.get()
            if num_articles <= 0:
                messagebox.showerror("Erreur d'Entrée", "Le nombre d'éléments doit être > 0.")
                self.enable_button(); return
        except tk.TclError:
            messagebox.showerror("Erreur d'Entrée", "Nombre d'éléments invalide.")
            self.enable_button(); return

        if source_key == "wikipedia":
            query_to_use = self.query_var.get().strip()
        elif source_key == "arxiv":
            selected_arxiv_category_display = self.category_var.get()
            if selected_arxiv_category_display == ARXIV_SEARCH_TYPE_KEYWORD or not selected_arxiv_category_display:
                query_to_use = self.query_var.get().strip()
                # Si query_to_use est vide ici, fetch_arxiv_abstracts choisira une catégorie aléatoire
            else:
                query_to_use = source_config["categories"][selected_arxiv_category_display]
        elif source_key == "gutenberg":
            query_to_use = self.query_var.get().strip()

        if source_config["requires_query"] and not query_to_use and \
           not (source_key == "arxiv" and (self.category_var.get() != ARXIV_SEARCH_TYPE_KEYWORD and self.category_var.get())):
            # La condition pour "requires_query" est un peu plus complexe pour arXiv
            # Si c'est arXiv et qu'une catégorie est sélectionnée, query_to_use sera le code catégorie, donc pas vide.
            # Si c'est arXiv et [Mots-clés] et que query_var est vide, alors c'est aléatoire (pas requires_query)
            if not (source_key == "arxiv" and not self.query_var.get().strip() and \
                    (self.category_var.get() == ARXIV_SEARCH_TYPE_KEYWORD or not self.category_var.get())):
                 messagebox.showwarning("Entrée Requise", f"Une requête ou sélection est requise pour {source_config['display_name']}.")
                 self.enable_button()
                 return

        self.update_max_progress()
        self.progress_var.set(0)

        query_display_for_status = query_to_use[:25]
        if source_key == "arxiv" and self.category_var.get() != ARXIV_SEARCH_TYPE_KEYWORD and self.category_var.get():
            """TODO: Add docstring."""
            query_display_for_status = self.category_var.get()[:25] # Afficher le nom de la catégorie
        elif not query_to_use:
            query_display_for_status = "(aléatoire)"
                """TODO: Add docstring."""

        self.update_status(f"Démarrage ({source_config['display_name']}): '{query_display_for_status}...' ({num_articles})", "info")

        fetch_thread = threading.Thread(target=fetch_and_save_thread_target_main, args=(self, source_key, query_to_use, num_articles), daemon=True)
        fetch_thread.start()

    def update_progress(self, value):
        # ... (inchangé)
        self.root.after(0, lambda: self.progress_var.set(value))

    def update_status(self, text, level="info"):
        """TODO: Add docstring."""
        # ... (inchangé, c'est bien)
        color = COLOR_TEXT
        if level == "success": color = "#27AE60"
        elif level == "warning": color = "#F39C12"
        elif level == "error": color = "#C0392B"
        elif level == "info": color = "#2980B9"

        if hasattr(self, 'status_label_widget_ref') and self.status_label_widget_ref:
            self.root.after(0, lambda w=self.status_label_widget_ref, c=color: w.config(foreground=c))
        self.root.after(0, lambda: self.status_label_var.set(text))

    def enable_button(self):
        # ... (inchangé)
        self.root.after(0, lambda: self.fetch_button.config(state=tk.NORMAL))

# ==============================================================================
# --- POINT D'ENTRÉE DE L'APPLICATION ---
# ==============================================================================
if __name__ == "__main__":
    # --- 1. Vérification et Configuration de ALMA_BASE_DIR ---
    # La logique de définition de ALMA_BASE_DIR et CONNAISSANCE_DIR_BASE
    # a déjà été faite au niveau global du module. Ici, nous vérifions sa validité
    # et informons l'utilisateur si des fallbacks ont été utilisés ou si des problèmes persistent.

    if "ALMA_BASE_DIR" not in os.environ:
        # Ce message est utile si le script est lancé sans que la variable d'env soit explicitement définie
        # (par exemple, pas via le .desktop configuré ou un script de lancement)
        print(f"INFO: Variable d'environnement ALMA_BASE_DIR non définie.")
        print(f"INFO: Utilisation du chemin de fallback pour ALMA_BASE_DIR: {ALMA_BASE_DIR}")

    if not TARGET_DIR_BASE_EXISTS: # Ce flag a été mis à jour après la tentative de création
        # Si même après la tentative de création (faite au niveau global), le dossier n'existe pas
        critical_error_message = (
            f"ERREUR CRITIQUE: Le répertoire de base des connaissances '{CONNAISSANCE_DIR_BASE}'\n"
            f"n'a pas pu être trouvé ou créé.\n\n"
            f"Veuillez vérifier les permissions ou définir ALMA_BASE_DIR correctement.\n"
            f"L'application ne peut pas continuer sans ce répertoire."
        )
        print(critical_error_message)
        # Pour une application GUI, il est préférable d'afficher une messagebox
        # avant de quitter, mais cela nécessite une racine Tkinter.
        # On va créer une racine temporaire juste pour ce message.
        temp_root_error_init = tk.Tk()
        temp_root_error_init.withdraw() # Cacher la fenêtre racine temporaire
        messagebox.showerror(f"{APP_NAME} - Erreur de Configuration", critical_error_message)
        temp_root_error_init.destroy()
        sys.exit(1)
    else:
        print(f"INFO: Répertoire de base des connaissances utilisé: {CONNAISSANCE_DIR_BASE}")

    # --- 2. Vérification des Dépendances Python Essentielles ---
    print("INFO: Vérification des dépendances Python...")
    missing_libs = []
    # Utiliser un dictionnaire pour mapper le nom de l'import au nom du package pip
    # Cela rend le message d'installation plus précis.
    dependency_map = {
        "wikipedia": "wikipedia",
        "arxiv": "arxiv",
        "requests": "requests",
        # Pour Gutenberg, on vérifie le flag global GUTENBERG_AVAILABLE
        # qui a été défini lors des imports conditionnels en haut du script.
    }

    try: import wikipedia
    except ImportError: missing_libs.append(dependency_map["wikipedia"])

    try: import arxiv
    except ImportError: missing_libs.append(dependency_map["arxiv"])

    try: import requests
    except ImportError: missing_libs.append(dependency_map["requests"])

    # Vérification spécifique pour Gutenberg basée sur le flag
    if not GUTENBERG_AVAILABLE:
        missing_libs.append("gutenbergpy (ou python-gutenberg)") # Nom du package pip probable

    if missing_libs:
        missing_libs_str = "\n - ".join(sorted(list(set(missing_libs)))) # Dédoublonner et trier
        error_message = (
            f"Dépendances Python manquantes ou non importables :\n\n - {missing_libs_str}\n\n"
            f"Veuillez les installer dans votre environnement virtuel, par exemple avec pip :\n"
            f"pip install {' '.join(sorted(list(set(missing_libs))))}" # Message d'installation
        )
        print(f"ERREUR: {error_message}")
        temp_root_error_deps = tk.Tk()
        temp_root_error_deps.withdraw()
        messagebox.showerror(f"{APP_NAME} - Dépendances Manquantes", error_message)
        temp_root_error_deps.destroy()
        sys.exit(1)
    else:
        print("INFO: Toutes les dépendances Python essentielles semblent être présentes.")

    # --- 3. Lancement de l'Application Tkinter ---
    print(f"INFO: Lancement de {APP_NAME} v{VERSION}...")
    root = None # Initialiser à None
    try:
        root = tk.Tk()
        app = WikiInjectorApp(root)
        root.mainloop()
        print(f"INFO: {APP_NAME} terminé proprement.")
    except Exception as e_main_app:
        # Attraper les erreurs inattendues pendant l'exécution de l'app GUI
        error_title = f"{APP_NAME} - Erreur d'Exécution"
        error_details = f"Une erreur inattendue est survenue:\n\n{type(e_main_app).__name__}: {e_main_app}\n\n" \
                        f"Veuillez consulter la console pour plus de détails (traceback)."
        print(f"ERREUR CRITIQUE DANS L'APPLICATION: {error_title}\n{error_details}")
        import traceback
        traceback.print_exc() # Afficher le traceback complet en console

        if root and root.winfo_exists(): # Si la fenêtre existe encore, afficher un message
            messagebox.showerror(error_title, error_details)
        else: # Si la fenêtre n'a pas pu être créée ou est déjà détruite
            temp_root_error_runtime = tk.Tk()
            temp_root_error_runtime.withdraw()
            messagebox.showerror(error_title, error_details)
            temp_root_error_runtime.destroy()
        sys.exit(1)