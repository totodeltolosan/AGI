import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import wikipedia
import arxiv
from typing import Optional, Dict, Any, List, Tuple
import traceback

# --- Import et Gestion de la Disponibilité de Gutenberg (MODIFIÉ POUR DÉSACTIVER PROPREMENT) ---
GUTENBERG_AVAILABLE = False # Par défaut, Gutenberg est désactivé
load_etext = None
strip_headers = None
get_metadata = None

# Commentaire : Nous désactivons l'import de Gutenberg pour l'instant
# car la bibliothèque gutenbergpy et/ou ses dépendances (comme httpsproxy-urllib2)
# causent une SyntaxError avec Python 3.12 en raison de l'utilisation de code Python 2 (urllib2).
# Pour permettre au reste de l'application de fonctionner, nous forçons GUTENBERG_AVAILABLE à False.
# Une future investigation pourrait chercher une alternative à gutenbergpy ou un fork corrigé.

print("INFO: La source Project Gutenberg est actuellement désactivée dans cette version de l'injecteur "
      "en raison de problèmes de compatibilité de la bibliothèque 'gutenbergpy' avec Python 3.12.")
# Fin du bloc Gutenberg

import requests # Nécessaire pour wikipedia et arxiv
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
VERSION = "1.5.4 (Gutenberg Désactivé, Réécriture Complète)" # Mise à jour version
NUM_ARTICLES_TO_FETCH_DEFAULT = 3
MAX_FETCH_ATTEMPTS_PER_SLOT = 5
MAX_TOTAL_RANDOM_ID_GENERATION_ATTEMPTS_GUTENBERG = 50 # Garder pour si Gutenberg est réactivé
MAX_DOWNLOAD_ATTEMPTS_PER_ID_GUTENBERG = 2 # Garder pour si Gutenberg est réactivé

# ==============================================================================
# --- THEME & STYLING (Inspiration "Genshin-Lite" adaptée) ---
# ==============================================================================
COLOR_APP_BACKGROUND = "#F7F9FC"
COLOR_FRAME_BACKGROUND = "#E8EFF7"
COLOR_ACCENT_PRIMARY = "#5D9CEC"
COLOR_ACCENT_PRIMARY_ACTIVE = "#4A89DC"
COLOR_TEXT_PRIMARY = "#34495E"
COLOR_TEXT_SECONDARY = "#7F8C8D"
COLOR_SUCCESS_TEXT = "#27AE60" # Renommé pour clarté vs COLOR_SUCCESS pour bg
COLOR_WARNING_TEXT = "#F39C12"
COLOR_ERROR_TEXT = "#C0392B" # Renommé pour clarté
COLOR_INFO_TEXT = "#3498DB"
COLOR_PROGRESS_BAR_FILL = "#F1C40F"
COLOR_PROGRESS_BAR_BG = COLOR_FRAME_BACKGROUND

FONT_FAMILY_PRIMARY_NAME_WISHED = "Noto Sans"
FONT_FAMILY_FALLBACK_NAME = "TkDefaultFont"

FONT_TITLE_DEF = (18, "bold")
FONT_SUBTITLE_DEF = (12, "bold")
FONT_BODY_BOLD_DEF = (10, "bold")
FONT_BODY_NORMAL_DEF = (10, "normal")
FONT_BUTTON_DEF = (10, "bold")
FONT_STATUS_MESSAGE_DEF = (9, "italic")
FONT_TOOLTIP_DEF = (9, "normal")

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
TARGET_DIR_BASE_EXISTS = CONNAISSANCE_DIR_BASE.is_dir()

if not TARGET_DIR_BASE_EXISTS:
    if CONNAISSANCE_DIR_BASE.exists() and not CONNAISSANCE_DIR_BASE.is_dir():
        print(f"ERREUR CRITIQUE: Le chemin pour les connaissances '{CONNAISSANCE_DIR_BASE}' existe mais n'est pas un répertoire.")
        TARGET_DIR_BASE_EXISTS = False
    else:
        print(f"INFO: Le répertoire de base des connaissances '{CONNAISSANCE_DIR_BASE}' n'existe pas. Tentative de création...")
        try:
            CONNAISSANCE_DIR_BASE.mkdir(parents=True, exist_ok=True)
            TARGET_DIR_BASE_EXISTS = True
            print(f"INFO: Répertoire '{CONNAISSANCE_DIR_BASE}' créé avec succès.")
        except OSError as e:
            print(f"ERREUR CRITIQUE: Impossible de créer le répertoire '{CONNAISSANCE_DIR_BASE}': {e}")
            TARGET_DIR_BASE_EXISTS = False

# ==============================================================================
# --- SOURCES CONFIGURATION (Plus structuré) ---
# ==============================================================================
ARXIV_SEARCH_TYPE_KEYWORD = "[Recherche par Mots-clés Libres]"

SOURCES_CONFIG = {
    "wikipedia": {
        "display_name": "Wikipédia (FR)",
        "fetch_function_name": "fetch_wikipedia_articles",
        "target_dir_suffix": "wiki_auto_imports",
        "ui_elements": {
            "query_input_type": "entry",
            "query_label": "Mots-clés (optionnel, sinon aléatoire) :",
        },
        "requires_query_for_non_random": False,
        "supports_random": True
    },
    "arxiv": {
        "display_name": "arXiv (Résumés Scientifiques)",
        "fetch_function_name": "fetch_arxiv_abstracts",
        "target_dir_suffix": "arxiv_auto_imports",
        "ui_elements": {
            "query_input_type": "category_menu_with_keyword_entry",
            "category_label": "Domaine arXiv :",
            "keyword_label": "Mots-clés (si domaine non choisi) :",
            "categories": {
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
        "requires_query_for_non_random": True,
        "supports_random": True
    },
    "gutenberg": {
        "display_name": "Project Gutenberg (Livres Libres)",
        "fetch_function_name": "fetch_gutenberg_books",
        "target_dir_suffix": "gutenberg_auto_imports",
        "ui_elements": {
            "query_input_type": "entry",
            "query_label": "ID Livre (optionnel, sinon aléatoire) :",
        },
        "requires_query_for_non_random": False,
        "supports_random": GUTENBERG_AVAILABLE # Sera False, donc le mode aléatoire ne sera pas proposé si la source était active
    }
}

# Initialisation spécifique à Wikipédia
try:
    wikipedia.set_lang("fr")
except Exception as e:
    print(f"ERREUR: Impossible de configurer la langue pour Wikipédia: {e}")

# --- Fin de la section de configuration globale ---

def sanitize_filename(title: str, max_len: int = 100) -> str:
    title = str(title).strip()
    title = re.sub(r'[\n\r]+', ' ', title)
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    title = title.replace(" ", "_")
    title = title.replace("'", "")
    title = re.sub(r'\.+', '.', title).strip('.')
    if not title: title = "fichier_sans_titre"
    return title[:max_len]

def get_target_dir_for_source(source_key: str) -> Path:
    suffix = SOURCES_CONFIG.get(source_key, {}).get("target_dir_suffix", "default_imports")
    return CONNAISSANCE_DIR_BASE / suffix

# --- Fonctions de Fetch (Intégralement reprises de votre V1.5.3, avec corrections mineures) ---

def fetch_wikipedia_articles(app_instance, query: str, num_to_fetch: int, target_dir: Path):
    articles_downloaded_this_run = 0
    # Multiplicateur pour la recherche initiale si une query est fournie,
    # afin d'avoir plus de candidats en cas de PageError ou DisambiguationError.
    # Pour le mode aléatoire, on ne fait pas de recherche initiale de liste.
    max_search_results_multiplier_if_query = 5
    page_titles_candidates = [] # Liste des titres potentiels si une query est fournie

    if query:
        app_instance.update_status(f"Wiki: Recherche '{query[:30]}...' pour {num_to_fetch} article(s).")
        try:
            # On récupère plus de résultats pour avoir une marge de manœuvre
            search_results = wikipedia.search(query, results=num_to_fetch * max_search_results_multiplier_if_query)
            if not search_results:
                app_instance.update_status(f"Wiki: Aucun résultat pour '{query}'.", "warning")
                return 0 # Aucun article ne sera téléchargé
            page_titles_candidates = search_results
            app_instance.update_status(f"Wiki: {len(page_titles_candidates)} candidats trouvés pour '{query}'.", "info")
        except requests.exceptions.RequestException as e_req_search:
            app_instance.update_status(f"Wiki: Erreur Réseau (recherche): {type(e_req_search).__name__}", "error")
            messagebox.showerror("Erreur Réseau", f"Problème de connexion à Wikipédia lors de la recherche:\n{e_req_search}")
            return 0
        except Exception as e_search: # Autres erreurs de la bibliothèque wikipedia
            app_instance.update_status(f"Wiki: Erreur recherche '{query}': {type(e_search).__name__}", "error")
            print(f"ERREUR WIKIPEDIA SEARCH (Query: '{query}'):")
            traceback.print_exc()
            return 0
    else: # Mode aléatoire
        app_instance.update_status(f"Wiki: Recherche aléatoire de {num_to_fetch} article(s)...", "info")

    processed_titles_in_session = set() # Pour éviter de traiter plusieurs fois le même titre dans cette session

    # Boucle principale pour remplir les 'num_to_fetch' slots demandés
    for slot_number in range(num_to_fetch):
        if articles_downloaded_this_run >= num_to_fetch: # Double sécurité
            break

        article_successfully_fetched_for_this_slot = False
        attempts_for_this_slot = 0 # Tentatives pour remplir CE slot spécifique

        # Boucle de tentatives pour trouver et télécharger UN article pour le slot actuel
        while not article_successfully_fetched_for_this_slot and attempts_for_this_slot < MAX_FETCH_ATTEMPTS_PER_SLOT:
            attempts_for_this_slot += 1
            page_title_to_process = "" # Initialiser avant le try

            try:
                if query: # Mode recherche par mots-clés
                    if not page_titles_candidates:
                        app_instance.update_status(f"Wiki: Plus de candidats disponibles pour '{query}' (slot {slot_number + 1}).", "info")
                        # On ne peut plus remplir de slots si on n'a plus de candidats
                        # On retourne ce qui a été téléchargé jusqu'à présent.
                        return articles_downloaded_this_run

                    page_title_to_process = page_titles_candidates.pop(0) # Prend le prochain candidat
                    if page_title_to_process in processed_titles_in_session:
                        # Ce candidat a déjà été traité (succès ou échec définitif) dans cette session.
                        # On continue pour essayer le prochain candidat de la liste pour ce slot.
                        app_instance.update_status(f"Wiki: Candidat '{page_title_to_process[:30]}...' déjà traité. Suivant.", "info")
                        attempts_for_this_slot -=1 # Ne compte pas comme une vraie tentative pour ce slot
                        continue
                else: # Mode aléatoire
                    # On cherche un nouveau titre aléatoire à chaque tentative pour ce slot
                    page_title_to_process = wikipedia.random(pages=1)
                    if page_title_to_process in processed_titles_in_session:
                        # Titre aléatoire déjà traité, on réessaie (la boucle `attempts_for_this_slot` gère la limite)
                        app_instance.update_status(f"Wiki (aléatoire): Titre '{page_title_to_process[:30]}...' déjà traité. Nouveau tirage.", "info")
                        if attempts_for_this_slot < MAX_FETCH_ATTEMPTS_PER_SLOT : continue
                        else: break # Limite de tentatives pour ce slot atteinte

                # À ce point, page_title_to_process est un titre qu'on va essayer de traiter
                app_instance.update_status(f"({articles_downloaded_this_run + 1}/{num_to_fetch}) Wiki: Essai '{page_title_to_process[:35]}...' (tentative {attempts_for_this_slot}/{MAX_FETCH_ATTEMPTS_PER_SLOT} pour ce slot)")

                # Marquer comme traité pour cette session pour ne pas le reprendre
                processed_titles_in_session.add(page_title_to_process)

                page = wikipedia.page(page_title_to_process, auto_suggest=False, redirect=True)

                filename = sanitize_filename(page.title) + "_WIKI.txt"
                filepath = target_dir / filename

                if filepath.exists():
                    app_instance.update_status(f"Wiki Existe: '{filename[:30]}...'.", "info")
                    # Si le fichier existe déjà:
                    # - En mode query, ce candidat est "brûlé". On doit essayer le prochain candidat pour ce slot.
                    # - En mode aléatoire, on veut un NOUVEAU titre.
                    # Dans les deux cas, on ne considère pas le slot comme rempli par ce titre.
                    # On sort de la boucle de DL pour ce titre, mais la boucle `attempts_for_this_slot` continuera.
                    # Ou, si on est en mode query, on veut que la boucle externe `page_titles_candidates.pop(0)` continue.
                    # La logique actuelle de ne rien faire ici et de laisser la boucle `attempts_for_this_slot` continuer
                    # (ou `page_titles_candidates.pop(0)`) est correcte.
                    # On ne met PAS article_successfully_fetched_for_this_slot = True
                    continue # Passe à la prochaine tentative pour ce slot (ou prochain candidat si query)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# SOURCE: Wikipédia\n# TITRE: {page.title}\n# URL: {page.url}\n\n{page.content}")

                articles_downloaded_this_run += 1
                app_instance.update_progress(articles_downloaded_this_run)
                app_instance.update_status(f"Wiki OK: '{page.title[:30]}...' ({articles_downloaded_this_run}/{num_to_fetch})", "success")
                article_successfully_fetched_for_this_slot = True # Succès pour ce slot !
                time.sleep(0.1) # Politesse

            except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError) as e_wiki:
                app_instance.update_status(f"Wiki Erreur (Titre: '{page_title_to_process[:30]}...'): {type(e_wiki).__name__}", "warning")
                # L'article n'est pas valide, on continue les tentatives pour ce slot avec un autre titre (si possible)
            except requests.exceptions.RequestException as e_req:
                app_instance.update_status(f"Wiki Erreur Réseau: {type(e_req).__name__}", "error")
                messagebox.showerror("Erreur Réseau", f"Problème de connexion à Wikipédia:\n{e_req}")
                return articles_downloaded_this_run # Arrêter tout le fetch pour cette source
            except Exception as e_gen_wiki:
                error_message_short = f"Wiki Erreur Inattendue (Titre: {page_title_to_process[:30]}...)"
                app_instance.update_status(error_message_short, "error")
                print(f"ERREUR WIKI INATTENDUE (Titre Complet: '{page_title_to_process}'):")
                traceback.print_exc()
                # On continue les tentatives pour ce slot avec un autre titre (si possible)

            if not article_successfully_fetched_for_this_slot and attempts_for_this_slot < MAX_FETCH_ATTEMPTS_PER_SLOT:
                time.sleep(0.2) # Petite pause avant la prochaine tentative pour ce slot

        # Fin de la boucle de tentatives pour UN slot
        if not article_successfully_fetched_for_this_slot:
             app_instance.update_status(f"Wiki: Échec final pour remplir le slot d'article {slot_number + 1} après {MAX_FETCH_ATTEMPTS_PER_SLOT} tentatives.", "warning")
             # Si on est en mode query et qu'on n'a pas réussi à remplir ce slot,
             # et qu'on n'a plus de candidats, la boucle externe (for slot_number) s'arrêtera
             # ou la condition if not page_titles_candidates: return ... le fera.

    return articles_downloaded_this_run

def fetch_arxiv_abstracts(app_instance, query: str, num_to_fetch: int, target_dir: Path):
    articles_downloaded_this_run = 0
    search_query_arxiv_original = query.strip() # Garder la query originale pour les logs
    search_query_arxiv_for_api = search_query_arxiv_original # Sera modifié pour l'API

    source_config_arxiv = SOURCES_CONFIG.get("arxiv", {})
    categories_arxiv_map = source_config_arxiv.get("ui_elements", {}).get("categories", {})

    # Déterminer le mode de recherche et préparer la query pour l'API
    is_random_mode = not search_query_arxiv_for_api # Mode aléatoire si la query est vide
    sort_criterion = arxiv.SortCriterion.Relevance # Par défaut pour les recherches par mots-clés

    if is_random_mode:
        app_instance.update_status(f"arXiv: Mode aléatoire activé.", "info")
        if categories_arxiv_map:
            random_category_display_name = random.choice(list(categories_arxiv_map.keys()))
            search_query_arxiv_for_api = categories_arxiv_map[random_category_display_name] # Code catégorie pour l'API
            sort_criterion = arxiv.SortCriterion.SubmittedDate # Plus récent pour une catégorie aléatoire
            app_instance.update_status(f"arXiv: Recherche aléatoire dans '{random_category_display_name}' ({search_query_arxiv_for_api})...", "info")
        else:
            app_instance.update_status(f"arXiv: Aucune catégorie définie pour le mode aléatoire.", "warning")
            return 0
    else: # Query fournie par l'utilisateur
        app_instance.update_status(f"arXiv: Recherche '{search_query_arxiv_for_api[:30]}...', max {num_to_fetch}", "info")
        # Normalisation de la query pour l'API arXiv
        # Si la query est un code catégorie connu (ex: "cs.AI") mais sans "cat:", on l'ajoute.
        # Sinon, on suppose que c'est une recherche par mots-clés.
        is_likely_category_code = search_query_arxiv_for_api in categories_arxiv_map.values()

        if is_likely_category_code and not search_query_arxiv_for_api.startswith("cat:"):
            search_query_arxiv_for_api = f"cat:{search_query_arxiv_for_api}"
            sort_criterion = arxiv.SortCriterion.SubmittedDate # Plus récent pour une catégorie spécifique
        elif " " in search_query_arxiv_for_api and not any(op in search_query_arxiv_for_api.upper() for op in ["AND", "OR", "NOT"]):
            # Si mots-clés multiples sans opérateurs, les joindre par AND pour l'API
            search_query_arxiv_for_api = " AND ".join(search_query_arxiv_for_api.split())
            # sort_criterion reste Relevance

    try:
        # On demande un peu plus de résultats pour avoir une marge si certains sont déjà téléchargés ou invalides
        # Augmenter le multiplicateur pour avoir plus de chances, surtout en mode aléatoire ou catégories larges
        results_to_request_from_api = num_to_fetch * 3

        search = arxiv.Search(
            query=search_query_arxiv_for_api,
            max_results=results_to_request_from_api,
            sort_by=sort_criterion
        )

        # Utiliser list(search.results()) peut être plus simple si le nombre de résultats n'est pas énorme,
        # mais l'itérateur est plus économe en mémoire si max_results est très grand.
        # Pour la robustesse, on va essayer de récupérer tous les résultats d'un coup dans une liste.
        # La bibliothèque arxiv gère déjà une forme de pagination interne si nécessaire.

        all_api_results = []
        app_instance.update_status(f"arXiv: Récupération des résultats pour '{search_query_arxiv_for_api[:30]}...'")
        try:
            for r in search.results(): # Itérer pour construire la liste
                all_api_results.append(r)
                if len(all_api_results) >= results_to_request_from_api: # Sécurité
                    break
            if not all_api_results:
                app_instance.update_status(f"arXiv: Aucun résultat API pour '{search_query_arxiv_for_api}'.", "warning")
                return 0
        except requests.exceptions.RequestException as e_req_results:
            app_instance.update_status(f"arXiv: Erreur Réseau (récupération résultats): {type(e_req_results).__name__}", "error")
            messagebox.showerror("Erreur Réseau", f"Problème de connexion à arXiv.org lors de la récupération des résultats:\n{e_req_results}")
            return 0
        except arxiv.arxiv.UnexpectedEmptyPageError as e_empty_page:
            app_instance.update_status(f"arXiv: Page vide inattendue pour '{search_query_arxiv_for_api}'. (Souvent dû à une query trop restrictive ou une erreur arXiv)", "warning")
            print(f"Erreur arXiv (UnexpectedEmptyPageError) pour query '{search_query_arxiv_for_api}': {e_empty_page}")
            return 0
        except Exception as e_arxiv_results_fetch:
            app_instance.update_status(f"arXiv: Erreur récupération résultats: {str(e_arxiv_results_fetch)[:30]}...", "error")
            print(f"ERREUR RÉCUPÉRATION RÉSULTATS ARXIV (Query: '{search_query_arxiv_for_api}'):")
            traceback.print_exc()
            return 0

        app_instance.update_status(f"arXiv: {len(all_api_results)} candidats potentiels trouvés. Traitement...", "info")

        processed_arxiv_ids_in_session = set()

        # Boucle principale pour essayer de remplir les 'num_to_fetch' slots
        for result_candidate in all_api_results:
            if articles_downloaded_this_run >= num_to_fetch:
                break # Assez d'articles téléchargés

            result = result_candidate # Pour la clarté du code qui suit

            if not hasattr(result, 'entry_id') or not hasattr(result, 'title') or not hasattr(result, 'summary'):
                app_instance.update_status(f"arXiv: Résultat API incomplet ignoré.", "warning")
                print(f"AVERTISSEMENT: Résultat arXiv incomplet: {result}")
                continue

            if result.entry_id in processed_arxiv_ids_in_session:
                continue # Déjà traité ou tenté dans cette session

            processed_arxiv_ids_in_session.add(result.entry_id)

            try:
                title = result.title.strip() # Nettoyer le titre
                app_instance.update_status(f"({articles_downloaded_this_run + 1}/{num_to_fetch}) arXiv: Traitement '{title[:35]}...'")

                # Construire un nom de fichier unique et informatif
                # Utiliser l'ID arXiv qui est unique, puis le titre.
                arxiv_id_clean = result.entry_id.split('/')[-1].replace('.', '_') # ex: 2305_12345v1
                filename = sanitize_filename(f"{arxiv_id_clean}_{title}") + "_ARXIV.txt"
                filepath = target_dir / filename

                if filepath.exists():
                    app_instance.update_status(f"arXiv Existe: '{filename[:30]}...'. Ignoré.", "info")
                    continue # On ne retélécharge pas, on passe au candidat suivant pour remplir les slots

                # Écriture du contenu dans le fichier
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# SOURCE: arXiv\n")
                    f.write(f"# TITRE: {title}\n")
                    f.write(f"# AUTEURS: {', '.join(str(a) for a in result.authors)}\n")
                    f.write(f"# ID ARXIV: {result.entry_id}\n")
                    f.write(f"# PUBLIÉ: {result.published.strftime('%Y-%m-%d') if result.published else 'N/A'}\n")
                    f.write(f"# MIS À JOUR: {result.updated.strftime('%Y-%m-%d') if result.updated else 'N/A'}\n")
                    f.write(f"# CATÉGORIE PRIMAIRE: {result.primary_category}\n")
                    all_categories = ", ".join(result.categories) if result.categories else "N/A"
                    f.write(f"# TOUTES CATÉGORIES: {all_categories}\n")
                    f.write(f"# RÉSUMÉ (ABSTRACT):\n{result.summary.strip().replace(' EOL ', '\n')}\n\n") # strip() sur summary
                    if result.comment: f.write(f"# COMMENTAIRES: {result.comment.strip()}\n")
                    if result.journal_ref: f.write(f"# RÉFÉRENCE JOURNAL: {result.journal_ref.strip()}\n")
                    if result.doi: f.write(f"# DOI: {result.doi.strip()}\n")
                    f.write(f"# URL PAGE ARXIV: {result.entry_id}\n") # C'est l'URL de la page de résumé
                    f.write(f"# URL PDF: {result.pdf_url if result.pdf_url else 'N/A'}\n")

                articles_downloaded_this_run += 1
                app_instance.update_progress(articles_downloaded_this_run)
                app_instance.update_status(f"arXiv OK: '{title[:30]}...' ({articles_downloaded_this_run}/{num_to_fetch})", "success")
                time.sleep(0.33) # Politesse envers l'API arXiv (environ 3 requêtes par seconde max)

            except requests.exceptions.RequestException as e_req_dl: # Erreur réseau pendant le traitement d'un résultat (rare ici car le contenu est déjà dans 'result')
                app_instance.update_status(f"arXiv: Erreur Réseau (traitement résultat): {type(e_req_dl).__name__}", "error")
                # Pas besoin de retourner ici, on peut essayer le prochain résultat de l'API
            except AttributeError as e_attr: # Si un champ attendu de 'result' est manquant
                app_instance.update_status(f"arXiv: Résultat malformé pour '{getattr(result, 'entry_id', 'ID inconnu')}': {e_attr}", "warning")
                print(f"ERREUR ATTRIBUT ARXIV (ID: {getattr(result, 'entry_id', 'ID inconnu')}): {e_attr}")
                traceback.print_exc()
            except Exception as e_process_arxiv:
                app_instance.update_status(f"arXiv: Erreur traitement '{getattr(result, 'title', 'Titre inconnu')[:30]}...': {type(e_process_arxiv).__name__}", "error")
                print(f"ERREUR TRAITEMENT RÉSULTAT ARXIV (ID: {getattr(result, 'entry_id', 'ID inconnu')}, Titre: '{getattr(result, 'title', 'Titre inconnu')}'):")
                traceback.print_exc()
                time.sleep(0.5) # Petite pause si une erreur de traitement survient

    except requests.exceptions.RequestException as e_req_search_init: # Erreur réseau lors de l'appel à arxiv.Search()
        app_instance.update_status(f"arXiv: Erreur Réseau (init recherche): {type(e_req_search_init).__name__}", "error")
        messagebox.showerror("Erreur Réseau", f"Problème de connexion initial à arXiv.org:\n{e_req_search_init}")
    except Exception as e_search_init_arxiv: # Autres erreurs lors de l'initialisation de arxiv.Search()
        app_instance.update_status(f"arXiv: Erreur init recherche: {type(e_search_init_arxiv).__name__}", "error")
        print(f"ERREUR INITIALISATION RECHERCHE ARXIV (Query API: '{search_query_arxiv_for_api}'):")
        traceback.print_exc()

    return articles_downloaded_this_run

def fetch_gutenberg_books(app_instance, query: str, num_to_fetch: int, target_dir: Path):
    if not GUTENBERG_AVAILABLE:
        app_instance.update_status("Gutenberg désactivé (bibliothèque non fonctionnelle).", "warning")
        # messagebox.showwarning("Source Désactivée", "La source Project Gutenberg est actuellement indisponible en raison de problèmes techniques avec la bibliothèque sous-jacente.")
        return 0 # Retourner 0 si la bibliothèque n'est pas disponible

    articles_downloaded_this_run = 0
    processed_book_ids_in_session = set()
    book_id_specific = None
    is_specific_id_mode = False

    if query.strip().isdigit():
        try:
            book_id_specific = int(query.strip())
            is_specific_id_mode = True
            if num_to_fetch > 1:
                app_instance.update_status(f"Gutenberg: ID {book_id_specific} spécifié. Téléchargement de 1 livre maximum.", "info")
            num_to_fetch = 1
            app_instance.update_status(f"Gutenberg: Recherche ID spécifique: {book_id_specific}", "info")
        except ValueError:
            app_instance.update_status("Gutenberg: ID de livre fourni invalide. Passage en mode aléatoire.", "warning")
            # query est implicitement vide pour le reste de la logique, donc mode aléatoire

    if not is_specific_id_mode:
        app_instance.update_status(f"Gutenberg: Recherche aléatoire de {num_to_fetch} livre(s)...", "info")

    for slot_index in range(num_to_fetch):
        if articles_downloaded_this_run >= num_to_fetch: break
        book_successfully_fetched_for_slot = False
        attempts_to_find_new_random_id = 0 # Renommé pour clarté

        # Boucle pour trouver un ID de livre valide (si en mode aléatoire)
        while not book_successfully_fetched_for_slot and \
              (is_specific_id_mode or attempts_to_find_new_random_id < MAX_TOTAL_RANDOM_ID_GENERATION_ATTEMPTS_GUTENBERG):
            current_book_id_to_try = None
            if is_specific_id_mode:
                if slot_index > 0: break # On a déjà traité l'ID spécifique au premier tour
                current_book_id_to_try = book_id_specific
                if current_book_id_to_try in processed_book_ids_in_session:
                    app_instance.update_status(f"Gutenberg: ID {current_book_id_to_try} déjà traité/tenté.", "info")
                    break # On ne retente pas un ID spécifique déjà traité dans cette exécution
            else: # Mode aléatoire
                attempts_to_find_new_random_id += 1
                current_book_id_to_try = random.randint(1, 72000) # Plage large pour Gutenberg
                if current_book_id_to_try in processed_book_ids_in_session:
                    if attempts_to_find_new_random_id < MAX_TOTAL_RANDOM_ID_GENERATION_ATTEMPTS_GUTENBERG:
                        continue # Cet ID aléatoire a déjà été traité, en prendre un autre
                    else:
                        app_instance.update_status(f"Gutenberg: Limite d'essais d'ID aléatoires atteinte pour le slot {slot_index + 1}.", "warning")
                        break # Sortir de la boucle de recherche d'ID pour ce slot

            if current_book_id_to_try is None: # S'assurer qu'on a un ID
                break

            # Ajouter l'ID aux IDs traités pour cette session pour éviter de le reprendre en aléatoire
            # ou de le retenter indéfiniment en mode spécifique s'il échoue définitivement.
            # C'est important de le faire ici, AVANT la boucle de téléchargement pour cet ID.
            if current_book_id_to_try not in processed_book_ids_in_session:
                 processed_book_ids_in_session.add(current_book_id_to_try)
            # else: # Si c'est un ID spécifique qui était déjà dans processed_ids, la logique `break` plus haut l'a géré.
                  # Si c'est un ID aléatoire qui était déjà là, le `continue` plus haut l'a géré.

            # Tentatives de téléchargement pour cet ID spécifique
            download_attempts_for_this_id = 0
            while not book_successfully_fetched_for_slot and download_attempts_for_this_id < MAX_DOWNLOAD_ATTEMPTS_PER_ID_GUTENBERG:
                download_attempts_for_this_id += 1
                try:
                    app_instance.update_status(f"({articles_downloaded_this_run + 1}/{num_to_fetch}) Gutenberg ID: {current_book_id_to_try} (DL essai {download_attempts_for_this_id})...")
                    book_title = None
                    if get_metadata: # Vérifier si la fonction est disponible (suite à l'import conditionnel)
                        try:
                            title_meta = get_metadata('title', current_book_id_to_try)
                            if title_meta: book_title = list(title_meta)[0]
                        except Exception as e_meta:
                            app_instance.update_status(f"Gutenberg ID {current_book_id_to_try}: Titre non récupérable ({str(e_meta)[:20]}...).", "info")
                            print(f"Info Gutenberg: Erreur récupération titre pour ID {current_book_id_to_try}: {e_meta}")
                    book_title_for_filename = book_title if book_title else f"Book_ID_{current_book_id_to_try}"

                    if not load_etext or not strip_headers: # Double vérification, devrait être géré par GUTENBERG_AVAILABLE
                        raise RuntimeError("Fonctions Gutenberg essentielles non disponibles (load_etext ou strip_headers).")

                    text = strip_headers(load_etext(current_book_id_to_try)).strip()
                    if not text:
                        app_instance.update_status(f"Gutenberg ID {current_book_id_to_try}: Contenu vide ou texte non trouvé.", "warning")
                        break # Sortir de la boucle de DL pour cet ID, il est probablement invalide
                    filename = sanitize_filename(book_title_for_filename) + "_GUT.txt"
                    filepath = target_dir / filename
                    if filepath.exists():
                        app_instance.update_status(f"Gutenberg Existe: '{filename}'.", "info")
                        if is_specific_id_mode:
                            book_successfully_fetched_for_slot = False; break # Arrêter pour ID spécifique
                        else:
                            # En mode aléatoire, si le fichier existe, on veut un autre ID.
                            # On sort de cette boucle de DL pour que la boucle externe cherche un nouvel ID.
                            break
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
                except requests.exceptions.HTTPError as e_http: # gutenbergpy utilise requests
                     app_instance.update_status(f"Gutenberg ID {current_book_id_to_try}: Erreur HTTP {e_http.response.status_code}.", "warning")
                     break # ID probablement mauvais, sortir de la boucle de DL
                except Exception as e_gutenberg:
                    app_instance.update_status(f"Gutenberg ID {current_book_id_to_try} Erreur: {str(e_gutenberg)[:30]}...", "error")
                    print(f"Erreur Gutenberg (ID: {current_book_id_to_try}): {e_gutenberg}")
                    if "Text Ebook Not Available" in str(e_gutenberg) or "No Etext Found" in str(e_gutenberg):
                        break # ID mauvais, sortir de la boucle de DL
                if not book_successfully_fetched_for_slot and download_attempts_for_this_id < MAX_DOWNLOAD_ATTEMPTS_PER_ID_GUTENBERG:
                    time.sleep(1.5) # Pause avant de retenter le MÊME ID
            if is_specific_id_mode and not book_successfully_fetched_for_slot: break # Si ID spécifique a échoué, on arrête pour ce slot
        if not book_successfully_fetched_for_slot:
            status_msg_fail = f"Gutenberg: Échec final pour livre {slot_index + 1}/{num_to_fetch}."
            if is_specific_id_mode and book_id_specific: status_msg_fail += f" (ID: {book_id_specific})"
            app_instance.update_status(status_msg_fail, "warning")
            if is_specific_id_mode: break # Si ID spécifique a échoué, on n'essaie pas plus pour Gutenberg
    return articles_downloaded_this_run

def fetch_and_save_thread_target_main(app_instance, source_key: str, query: str, num_articles_requested: int):
    # Utiliser num_articles_requested pour éviter la confusion avec la variable locale dans les fetchers

    app_instance.update_status(f"Initialisation du thread pour {source_key}...", "info")

    target_dir_for_source = get_target_dir_for_source(source_key)

    # Vérification et création du dossier cible (déjà bien géré)
    if not TARGET_DIR_BASE_EXISTS:
        # Ce cas devrait être rare car vérifié au démarrage de l'app, mais bonne sécurité
        error_msg_kb_base = "Erreur: Dossier Connaissance de base non accessible ou non créé."
        app_instance.update_status(error_msg_kb_base, "error")
        # Pas de messagebox ici car c'est dans un thread, l'UI principale gère déjà l'alerte initiale
        app_instance.enable_button()
        return

    if not target_dir_for_source.exists():
        try:
            target_dir_for_source.mkdir(parents=True, exist_ok=True)
            print(f"INFO: Dossier cible '{target_dir_for_source}' créé par le thread.")
            app_instance.update_status(f"Dossier '{target_dir_for_source.name}' créé.", "info")
        except OSError as e:
            error_msg_target_dir = f"Erreur création dossier cible {target_dir_for_source.name}: {e}"
            app_instance.update_status(error_msg_target_dir, "error")
            # Pas de messagebox ici car dans un thread, mais loguer l'erreur
            print(f"ERREUR THREAD: {error_msg_target_dir}")
            app_instance.enable_button()
            return

    articles_actually_fetched_count = 0 # Renommé pour clarté
    fetch_function_name_str = SOURCES_CONFIG.get(source_key, {}).get("fetch_function_name")

    if not fetch_function_name_str:
        app_instance.update_status(f"Aucune fonction de fetch définie pour {source_key}.", "error")
        app_instance.enable_button()
        return

    fetch_function = globals().get(fetch_function_name_str)
    if not callable(fetch_function):
        app_instance.update_status(f"Fonction de fetch '{fetch_function_name_str}' non trouvée/callable pour {source_key}.", "error")
        app_instance.enable_button()
        return

    # Exécution de la fonction de fetch spécifique
    try:
        articles_actually_fetched_count = fetch_function(
            app_instance, query, num_articles_requested, target_dir_for_source
        )
    except Exception as e_fetch_general:
        # Ce bloc catch est une sécurité si la fonction de fetch elle-même lève une exception non gérée
        # Normalement, les fonctions de fetch devraient gérer leurs propres exceptions et retourner un compte.
        error_msg_fetch_call = f"Erreur majeure lors de l'appel à {fetch_function_name_str} pour {source_key}: {type(e_fetch_general).__name__}"
        app_instance.update_status(error_msg_fetch_call, "error")
        print(f"ERREUR CRITIQUE DANS THREAD (appel fetch_function pour {source_key}):")
        traceback.print_exc() # Imprimer la trace complète
        articles_actually_fetched_count = 0 # S'assurer que le compte est à 0 en cas d'erreur majeure

    # Logique pour les messages finaux et la mise à jour de l'UI
    source_name_display = SOURCES_CONFIG.get(source_key, {}).get("display_name", source_key.capitalize())

    # Construire query_display de manière plus robuste
    query_for_display = query.strip()
    if source_key == "arxiv" and hasattr(app_instance, 'category_var') and \
       app_instance.category_var.get() != ARXIV_SEARCH_TYPE_KEYWORD and app_instance.category_var.get():
        query_for_display = app_instance.category_var.get() # Utiliser le nom de la catégorie affichée
    elif not query_for_display and SOURCES_CONFIG.get(source_key, {}).get("supports_random", False):
        query_for_display = "(mode aléatoire)"
    elif not query_for_display: # Si query vide et pas de mode aléatoire explicite (ou échec du mode aléatoire)
        query_for_display = "(aucune requête spécifiée)"


    final_status_msg = ""
    final_box_title = ""
    final_box_msg = ""
    final_message_type = "info" # Pour le message de statut

    # Assurer que articles_actually_fetched_count ne dépasse pas num_articles_requested pour les messages
    # Cela corrige l'incohérence "5 sur 3"
    effective_articles_for_message = min(articles_actually_fetched_count, num_articles_requested)

    if num_articles_requested <= 0: # Cas où l'utilisateur a entré 0 ou moins
        final_status_msg = f"{source_name_display}: Nombre d'articles demandé invalide ({num_articles_requested})."
        final_box_title = "Nombre Invalide"
        final_box_msg = f"Le nombre d'articles à récupérer doit être supérieur à 0."
        final_message_type = "error"
        # Pas de messagebox.showerror ici car déjà géré dans start_fetching,
        # mais on prépare le message de statut.
        # En fait, start_fetching devrait empêcher d'arriver ici avec num_articles_requested <= 0.
        # Mais une double sécurité est bien.
    elif effective_articles_for_message == num_articles_requested:
        final_status_msg = f"{source_name_display}: Terminé ! {effective_articles_for_message} article(s) téléchargé(s) {query_for_display}."
        final_box_title = "Succès du Téléchargement"
        final_box_msg = (f"{effective_articles_for_message} article(s) de {source_name_display} "
                         f"ont été téléchargé(s) avec succès {query_for_display} dans :\n"
                         f"{target_dir_for_source.resolve()}")
        # Utiliser app_instance.root.after pour appeler messagebox depuis le thread principal
        app_instance.root.after(0, lambda: messagebox.showinfo(final_box_title, final_box_msg))
    elif effective_articles_for_message > 0:
        final_status_msg = (f"{source_name_display}: Partiel. {effective_articles_for_message}/{num_articles_requested} "
                            f"article(s) téléchargé(s) {query_for_display}.")
        final_box_title = "Téléchargement Partiellement Terminé"
        final_box_msg = (f"Seulement {effective_articles_for_message} sur {num_articles_requested} article(s) "
                         f"de {source_name_display} ont pu être téléchargé(s) {query_for_display}.")
        app_instance.root.after(0, lambda: messagebox.showwarning(final_box_title, final_box_msg))
        final_message_type = "warning"
    else: # effective_articles_for_message == 0
        final_status_msg = f"{source_name_display}: Échec. Aucun article récupéré {query_for_display}."
        final_box_title = "Échec du Téléchargement"
        final_box_msg = f"Aucun article de {source_name_display} n'a pu être récupéré {query_for_display}."
        app_instance.root.after(0, lambda: messagebox.showerror(final_box_title, final_box_msg))
        final_message_type = "error"

    app_instance.update_status(final_status_msg, final_message_type)
    app_instance.enable_button() # Réactiver le bouton de lancement
    app_instance.update_progress(effective_articles_for_message) # Mettre à jour la barre de progression avec le compte effectif

class WikiInjectorApp:
    def _initialize_fonts(self):
        global FONT_TITLE, FONT_SUBTITLE, FONT_BODY_BOLD, FONT_BODY_NORMAL, \
               FONT_BUTTON, FONT_STATUS_MESSAGE, FONT_TOOLTIP
        actual_font_family_to_use = FONT_FAMILY_PRIMARY_NAME_WISHED
        try:
            tkfont.Font(family=FONT_FAMILY_PRIMARY_NAME_WISHED, size=10)
            print(f"INFO: Police primaire '{FONT_FAMILY_PRIMARY_NAME_WISHED}' trouvée et sera utilisée.")
        except tk.TclError:
            print(f"AVERTISSEMENT: Police primaire '{FONT_FAMILY_PRIMARY_NAME_WISHED}' non trouvée. Utilisation de '{FONT_FAMILY_FALLBACK_NAME}'.")
            actual_font_family_to_use = FONT_FAMILY_FALLBACK_NAME
        def get_font_creation_options(font_def_tuple: Tuple[int, str]) -> Dict[str, Any]:
            options = {"size": font_def_tuple[0]}
            if len(font_def_tuple) > 1:
                style_str = font_def_tuple[1].lower()
                if "bold" in style_str: options["weight"] = "bold"
                if "italic" in style_str: options["slant"] = "italic"
            return options
        FONT_TITLE = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_TITLE_DEF))
        FONT_SUBTITLE = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_SUBTITLE_DEF))
        FONT_BODY_BOLD = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_BODY_BOLD_DEF))
        FONT_BODY_NORMAL = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_BODY_NORMAL_DEF))
        FONT_BUTTON = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_BUTTON_DEF))
        FONT_STATUS_MESSAGE = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_STATUS_MESSAGE_DEF))
        FONT_TOOLTIP = tkfont.Font(family=actual_font_family_to_use, **get_font_creation_options(FONT_TOOLTIP_DEF))

    def __init__(self, root_window):
        self.root = root_window
        self.root.title(f"{APP_NAME} - v{VERSION}")
        self.root.geometry("650x520")
        self.root.configure(bg=COLOR_APP_BACKGROUND)
        self._initialize_fonts()
        style = ttk.Style(self.root)
        style.theme_use('clam') # Un thème ttk qui est souvent disponible et plus moderne
        style.configure("TFrame", background=COLOR_APP_BACKGROUND)
        style.configure("TLabel", foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY_NORMAL, background=COLOR_APP_BACKGROUND)
        style.configure("Title.TLabel", font=FONT_TITLE, foreground=COLOR_TEXT_PRIMARY, background=COLOR_APP_BACKGROUND)
        style.configure("Status.TLabel", font=FONT_STATUS_MESSAGE, wraplength=620, background=COLOR_APP_BACKGROUND)
        style.configure("Bold.TLabel", font=FONT_BODY_BOLD, foreground=COLOR_TEXT_PRIMARY, background=COLOR_APP_BACKGROUND)
        style.configure("TButton", font=FONT_BUTTON, borderwidth=1)
        style.map("TButton",
                  background=[('!disabled', COLOR_ACCENT_PRIMARY), ('active', COLOR_ACCENT_PRIMARY_ACTIVE),
                              ('pressed', COLOR_ACCENT_PRIMARY_ACTIVE), ('disabled', '#BFBFBF')],
                  foreground=[('!disabled', 'white'), ('disabled', COLOR_TEXT_SECONDARY)],
                  relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        style.configure("Gold.Horizontal.TProgressbar", troughcolor=COLOR_PROGRESS_BAR_BG,
                        bordercolor=COLOR_TEXT_SECONDARY, background=COLOR_PROGRESS_BAR_FILL)
        style.configure("TLabelFrame", background=COLOR_FRAME_BACKGROUND, foreground=COLOR_TEXT_PRIMARY,
                        font=FONT_BODY_BOLD, borderwidth=1, relief="groove")
        style.configure("TLabelFrame.Label", font=FONT_BODY_BOLD, foreground=COLOR_TEXT_PRIMARY,
                        background=COLOR_FRAME_BACKGROUND)
        style.configure("TOptionMenu", font=FONT_BODY_NORMAL) # Appliquer la police aux OptionMenu

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(expand=True, fill=tk.BOTH)
        title_label = ttk.Label(main_frame, text="Injecteur de Connaissances ALMA", style="Title.TLabel", anchor="center")
        title_label.pack(pady=(0, 15), fill=tk.X)
        config_frame = ttk.LabelFrame(main_frame, text="Options de Récupération", padding="10")
        config_frame.pack(fill=tk.X, pady=10)

        ttk.Label(config_frame, text="Source :", style="Bold.TLabel").grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        self.source_key_var = tk.StringVar() # Sera mis par on_source_change
        self.available_source_keys = [key for key in SOURCES_CONFIG.keys() if not (key == "gutenberg" and not GUTENBERG_AVAILABLE)]
        source_display_names = [SOURCES_CONFIG[key]["display_name"] for key in self.available_source_keys]
        self.source_display_to_key_map = {SOURCES_CONFIG[key]["display_name"]: key for key in self.available_source_keys}

        default_display_name_val = ""
        if source_display_names: # S'il y a au moins une source disponible
            if "wikipedia" in self.available_source_keys: # Préférer Wikipedia comme défaut si dispo
                default_display_name_val = SOURCES_CONFIG["wikipedia"]["display_name"]
            else: # Sinon, prendre la première source disponible dans la liste
                default_display_name_val = source_display_names[0]
        self.current_source_display_var = tk.StringVar(value=default_display_name_val)

        initial_option_menu_value = self.current_source_display_var.get() if source_display_names else " (Aucune Source) "
        options_for_menu = source_display_names if source_display_names else [" (Aucune Source) "]
        self.source_menu = ttk.OptionMenu(config_frame, self.current_source_display_var,
                                     initial_option_menu_value, *options_for_menu, command=self.on_source_change)
        self.source_menu.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        if not source_display_names:
            self.source_menu.config(state=tk.DISABLED)
            self.current_source_display_var.set(" (Aucune Source Disponible) ")

        self.category_query_label = ttk.Label(config_frame, text="Texte du Label Dynamique", style="Bold.TLabel")
        self.category_query_label.grid(row=1, column=0, padx=(0,10), pady=5, sticky="w")
        self.query_widget_frame = ttk.Frame(config_frame)
        self.query_widget_frame.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.query_widget_frame.columnconfigure(0, weight=1) # Pour que Entry/OptionMenu s'étendent
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(self.query_widget_frame, textvariable=self.query_var, width=45, font=FONT_BODY_NORMAL)
        self.category_var = tk.StringVar()
        self.category_menu = ttk.OptionMenu(self.query_widget_frame, self.category_var, "", command=self.on_arxiv_category_change)

        ttk.Label(config_frame, text="Nombre :", style="Bold.TLabel").grid(row=2, column=0, padx=(0,10), pady=5, sticky="w")
        self.num_articles_var = tk.IntVar(value=NUM_ARTICLES_TO_FETCH_DEFAULT)
        self.num_articles_spinbox = ttk.Spinbox(config_frame, from_=1, to=200,
                                           textvariable=self.num_articles_var, width=7,
                                           command=self.update_max_progress, font=FONT_BODY_NORMAL)
        self.num_articles_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        config_frame.columnconfigure(1, weight=1) # Permet à la colonne des widgets de s'étendre

        self.fetch_button = ttk.Button(main_frame, text="Lancer la Récupération", command=self.start_fetching, width=30)
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

        self.on_source_change() # Appel initial pour configurer l'UI pour la source par défaut

        if not TARGET_DIR_BASE_EXISTS: # Vérifier après l'init de status_label_widget_ref
             self.update_status(f"ALMA_BASE_DIR non défini ou {CONNAISSANCE_DIR_BASE} non trouvé/créé.", "error")
             self.fetch_button.config(state=tk.DISABLED)
             # Le messagebox d'erreur critique est géré dans if __name__ == "__main__"

    def _update_option_menu(self, option_menu_widget, string_var, new_default_value, new_options_list):
        """Met à jour un ttk.OptionMenu avec de nouvelles options et une nouvelle valeur par défaut."""
        # S'assurer que la nouvelle valeur par défaut est dans la liste des options
        if new_default_value not in new_options_list and new_options_list:
            string_var.set(new_options_list[0]) # Prend la première option si le défaut n'est pas valide
        else:
            string_var.set(new_default_value)

        menu = option_menu_widget["menu"]
        menu.delete(0, "end")
        for option in new_options_list:
            if option_menu_widget == self.category_menu:
                 menu.add_command(label=option, command=lambda val=option: (string_var.set(val), self.on_arxiv_category_change()))
            else: # Pour self.source_menu
                 menu.add_command(label=option, command=lambda val=option: (string_var.set(val), self.on_source_change())) # Assurer que on_source_change est appelé

    def on_source_change(self, event=None): # event=None pour l'appel initial
        selected_display_name = self.current_source_display_var.get()
        if selected_display_name in self.source_display_to_key_map:
            source_key = self.source_display_to_key_map[selected_display_name]
            self.source_key_var.set(source_key)
        elif self.available_source_keys: # Si le display name n'est pas mappé (ex: "Aucune source")
            self.source_key_var.set(self.available_source_keys[0]) # Fallback sur la première source dispo
            self.current_source_display_var.set(SOURCES_CONFIG[self.available_source_keys[0]]["display_name"]) # Mettre à jour l'affichage
        else:
            self.source_key_var.set("") # Aucune source valide

        self.query_var.set("")
        self.category_var.set("")
        self.update_ui_for_source()

    def on_arxiv_category_change(self, event=None):
        self.update_ui_for_source()

    def update_ui_for_source(self):
        source_key = self.source_key_var.get()
        if not source_key or source_key not in SOURCES_CONFIG:
            self.category_query_label.config(text="Source non valide ou non sélectionnée.")
            self.query_entry.pack_forget()
            self.category_menu.pack_forget()
            self.fetch_button.config(state=tk.DISABLED)
            return

        self.fetch_button.config(state=tk.NORMAL)
        source_config = SOURCES_CONFIG[source_key]
        source_config_ui = source_config.get("ui_elements", {})
        query_input_type = source_config_ui.get("query_input_type", "entry")

        self.query_entry.pack_forget()
        self.category_menu.pack_forget()

        if query_input_type == "entry":
            self.category_query_label.config(text=source_config_ui.get("query_label", "Requête :"))
            self.query_entry.pack(fill=tk.X, expand=True)
        elif query_input_type == "category_menu_with_keyword_entry":
            arxiv_categories_dict = source_config_ui.get("categories", {})
            arxiv_categories_display = [ARXIV_SEARCH_TYPE_KEYWORD] + list(arxiv_categories_dict.keys())

            current_cat_val = self.category_var.get()
            # Mettre à jour le menu avec les bonnes options et la valeur par défaut
            self._update_option_menu(self.category_menu, self.category_var,
                                     current_cat_val if current_cat_val in arxiv_categories_display else arxiv_categories_display[0],
                                     arxiv_categories_display)

            self.category_menu.pack(fill=tk.X, expand=True) # Afficher le menu catégorie
            if self.category_var.get() == ARXIV_SEARCH_TYPE_KEYWORD:
                self.category_query_label.config(text=source_config_ui.get("keyword_label", "Mots-clés :"))
                self.query_entry.pack(fill=tk.X, expand=True, pady=(5,0))
            else:
                self.category_query_label.config(text=source_config_ui.get("category_label", "Catégorie :"))
                # query_entry est déjà caché
        elif query_input_type == "none":
             self.category_query_label.config(text=source_config_ui.get("query_label", "Prêt (aucune requête nécessaire)."))
        self.update_max_progress()

    def update_max_progress(self):
        try:
            num_articles = self.num_articles_var.get()
            if num_articles <= 0: num_articles = 1 # Assurer un maximum > 0
        except tk.TclError: # Si la valeur n'est pas un entier valide
            num_articles = NUM_ARTICLES_TO_FETCH_DEFAULT
            self.num_articles_var.set(num_articles) # Réinitialiser la variable
        self.progress_bar.config(maximum=num_articles)
        self.progress_var.set(0) # Réinitialiser la progression

    def start_fetching(self):
            self.fetch_button.config(state=tk.DISABLED)
            self.progress_var.set(0) # Réinitialiser la progression au début

            source_key = self.source_key_var.get()
            if not source_key or source_key not in SOURCES_CONFIG:
                messagebox.showerror("Erreur de Source", "Veuillez sélectionner une source valide dans le menu déroulant.")
                self.enable_button()
                return

            source_config = SOURCES_CONFIG[source_key]
            source_display_name = source_config.get("display_name", source_key.capitalize())

            try:
                num_articles_to_request = self.num_articles_var.get()
                if num_articles_to_request <= 0:
                    messagebox.showerror("Erreur d'Entrée", "Le nombre d'éléments à récupérer doit être supérieur à 0.")
                    self.enable_button()
                    return
            except tk.TclError: # Erreur si la valeur du Spinbox n'est pas un entier
                messagebox.showerror("Erreur d'Entrée", "Le nombre d'éléments à récupérer est invalide. Veuillez entrer un nombre entier.")
                self.num_articles_var.set(NUM_ARTICLES_TO_FETCH_DEFAULT) # Réinitialiser à une valeur sûre
                self.enable_button()
                return

            self.update_max_progress() # S'assurer que la barre est configurée pour le bon nombre

            query_to_use_for_api = "" # La requête qui sera passée à la fonction de fetch
            query_display_for_status = "" # Ce qui sera affiché dans la barre de statut

            query_input_type = source_config.get("ui_elements", {}).get("query_input_type", "entry")

            if query_input_type == "entry":
                query_to_use_for_api = self.query_var.get().strip()
                query_display_for_status = query_to_use_for_api if query_to_use_for_api else "(mode aléatoire)"

            elif query_input_type == "category_menu_with_keyword_entry":
                selected_arxiv_category_display = self.category_var.get() # Nom affiché de la catégorie
                arxiv_categories_map = source_config.get("ui_elements", {}).get("categories", {})

                if selected_arxiv_category_display == ARXIV_SEARCH_TYPE_KEYWORD or not selected_arxiv_category_display:
                    # Mode recherche par mots-clés ou si aucune catégorie n'est sélectionnée (devrait pas arriver si bien initialisé)
                    query_to_use_for_api = self.query_var.get().strip()
                    query_display_for_status = query_to_use_for_api if query_to_use_for_api else "(catégorie arXiv aléatoire)"
                    # Si query_to_use_for_api est vide ici, fetch_arxiv_abstracts choisira une catégorie aléatoire
                else: # Une catégorie spécifique est sélectionnée
                    query_to_use_for_api = arxiv_categories_map.get(selected_arxiv_category_display, "") # C'est le code catégorie pour l'API
                    query_display_for_status = selected_arxiv_category_display # Afficher le nom de la catégorie

            elif query_input_type == "none": # Ex: Gutenberg en mode aléatoire si l'ID est vide
                # La query_var peut contenir un ID pour Gutenberg. Si elle est vide, c'est aléatoire.
                query_to_use_for_api = self.query_var.get().strip() # Pour Gutenberg, la query est l'ID
                query_display_for_status = f"ID: {query_to_use_for_api}" if query_to_use_for_api else "(mode aléatoire)"

            # Vérification finale si une requête est nécessaire et absente
            # (pour les sources qui ne supportent pas un mode aléatoire implicite si la query est vide)
            requires_query = source_config.get("requires_query_for_non_random", False)
            supports_random_if_query_empty = source_config.get("supports_random", False)

            if requires_query and not query_to_use_for_api and not supports_random_if_query_empty:
                # Ce cas signifie : la source a besoin d'une query, la query est vide, ET la source ne supporte pas
                # un mode aléatoire implicite si la query est vide.
                messagebox.showwarning("Entrée Requise",
                                    f"Une requête ou sélection est requise pour {source_display_name}.")
                self.enable_button()
                return
            elif requires_query and not query_to_use_for_api and source_key == "arxiv" and self.category_var.get() == ARXIV_SEARCH_TYPE_KEYWORD:
                # Cas spécifique pour arXiv: si "Mots-clés Libres" est sélectionné mais le champ est vide
                messagebox.showwarning("Entrée Requise",
                                    f"Veuillez entrer des mots-clés pour la recherche arXiv ou sélectionner une catégorie.")
                self.enable_button()
                return


            # Affiner le message de statut initial
            status_action_description = ""
            if query_to_use_for_api and query_display_for_status != "(mode aléatoire)" and query_display_for_status != "(catégorie arXiv aléatoire)":
                status_action_description = f"pour '{query_display_for_status[:30]}...'"
            elif query_display_for_status: # Contient déjà "(mode aléatoire)" ou une catégorie
                status_action_description = query_display_for_status
            else: # Fallback si tout est vide (devrait être rare)
                status_action_description = "(paramètres non spécifiés)"


            self.update_status(f"Démarrage ({source_display_name}): Récupération de {num_articles_to_request} article(s) {status_action_description}", "info")

            fetch_thread = threading.Thread(
                target=fetch_and_save_thread_target_main,
                args=(self, source_key, query_to_use_for_api, num_articles_to_request),
                daemon=True
            )
            fetch_thread.start()

    def update_progress(self, value):
        self.root.after(0, lambda: self.progress_var.set(value))

    def update_status(self, text, level="info"):
        color = COLOR_TEXT_PRIMARY # Couleur par défaut
        if level == "success": color = COLOR_STATUS_SUCCESS
        elif level == "warning": color = COLOR_WARNING_TEXT
        elif level == "error": color = COLOR_ERROR_TEXT
        elif level == "info": color = COLOR_INFO_TEXT

        if hasattr(self, 'status_label_widget_ref') and self.status_label_widget_ref: # Vérifier si le widget existe
            self.root.after(0, lambda w=self.status_label_widget_ref, c=color: w.config(foreground=c))
        self.root.after(0, lambda: self.status_label_var.set(text))

    def enable_button(self):
        self.root.after(0, lambda: self.fetch_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    if "ALMA_BASE_DIR" not in os.environ:
        print(f"INFO: Variable d'environnement ALMA_BASE_DIR non définie.")
        print(f"INFO: Utilisation du chemin de fallback pour ALMA_BASE_DIR: {ALMA_BASE_DIR}")
    if not TARGET_DIR_BASE_EXISTS:
        critical_error_message = (
            f"ERREUR CRITIQUE: Le répertoire de base des connaissances '{CONNAISSANCE_DIR_BASE}'\n"
            f"n'a pas pu être trouvé ou créé.\n\n"
            f"Veuillez vérifier les permissions ou définir ALMA_BASE_DIR correctement.\n"
            f"L'application ne peut pas continuer sans ce répertoire."
        )
        print(critical_error_message)
        # Créer une racine Tkinter temporaire pour afficher la messagebox si elle n'existe pas déjà
        temp_root_error_init = tk.Tk()
        temp_root_error_init.withdraw() # Cacher la fenêtre racine temporaire
        messagebox.showerror(f"{APP_NAME} - Erreur de Configuration", critical_error_message)
        temp_root_error_init.destroy()
        sys.exit(1) # Quitter après l'erreur critique
    else:
        print(f"INFO: Répertoire de base des connaissances utilisé: {CONNAISSANCE_DIR_BASE}")

    print("INFO: Vérification des dépendances Python...")
    missing_libs_map = { # Nom d'import: nom package pip
        "wikipedia": "wikipedia",
        "arxiv": "arxiv",
        "requests": "requests",
    }
    missing_libs_to_install = []
    for lib_import, lib_pip_name in missing_libs_map.items():
        try:
            __import__(lib_import)
        except ImportError:
            missing_libs_to_install.append(lib_pip_name)

    if not GUTENBERG_AVAILABLE: # Gutenberg est géré différemment car il cause une SyntaxError
        # On informe juste, on ne l'ajoute pas à la liste à installer car on l'a désactivé
        print("INFO: La source Gutenberg est désactivée. Pour l'utiliser, la bibliothèque 'gutenbergpy' (et ses dépendances corrigées) serait nécessaire.")

    if missing_libs_to_install:
        missing_libs_str = "\n - ".join(sorted(list(set(missing_libs_to_install))))
        error_message = (
            f"Dépendances Python manquantes ou non importables :\n\n - {missing_libs_str}\n\n"
            f"Veuillez les installer dans votre environnement virtuel, par exemple avec pip :\n"
            f"pip install {' '.join(sorted(list(set(missing_libs_to_install))))}"
        )
        print(f"ERREUR: {error_message}")
        temp_root_error_deps = tk.Tk(); temp_root_error_deps.withdraw()
        messagebox.showerror(f"{APP_NAME} - Dépendances Manquantes", error_message)
        temp_root_error_deps.destroy(); sys.exit(1)
    else:
        print("INFO: Toutes les dépendances Python essentielles (pour Wiki/arXiv) semblent être présentes.")

    print(f"INFO: Lancement de {APP_NAME} v{VERSION}...")
    root = None
    try:
        root = tk.Tk()
        app = WikiInjectorApp(root)
        root.mainloop()
        print(f"INFO: {APP_NAME} terminé proprement.")
    except Exception as e_main_app:
        error_title = f"{APP_NAME} - Erreur d'Exécution"
        error_details = f"Une erreur inattendue est survenue:\n\n{type(e_main_app).__name__}: {e_main_app}\n\n" \
                        f"Veuillez consulter la console pour plus de détails (traceback)."
        print(f"ERREUR CRITIQUE DANS L'APPLICATION: {error_title}\n{error_details}")
        import traceback
        traceback.print_exc()
        # Essayer d'afficher une messagebox même si la racine principale a un problème
        if root and root.winfo_exists(): # Vérifier si la fenêtre principale existe encore
            try: messagebox.showerror(error_title, error_details)
            except tk.TclError: # Si la racine est en train d'être détruite
                 pass # Ne rien faire de plus
        else: # Si la racine n'a pas pu être créée ou est déjà détruite
            temp_root_error_runtime = tk.Tk(); temp_root_error_runtime.withdraw()
            messagebox.showerror(error_title, error_details)
            temp_root_error_runtime.destroy()
        sys.exit(1)
