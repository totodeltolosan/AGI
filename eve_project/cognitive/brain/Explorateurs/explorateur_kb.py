#!/usr/bin/env python3
# explorateur_kb.py

"""
---
name: explorateur_kb.py
version: 0.3.1-beta # Correction recherche par ID, robustesse mineure
author: Toni & Gemini AI
description: Outil CLI pour explorer la KnowledgeBase d'ALMA Cerveau.
role: Inspection et validation de la KnowledgeBase
type_execution: cli
état: en développement actif
last_update: 2025-05-24
dossier: ALMA/Cerveau/Explorateurs/
tags: [V20, alma, connaissance, explorateur, cli, sqlite, yaml, csv]
dependencies: [PyYAML (optionnel pour lire cerveau_config.yaml)]
---
"""

import argparse
import sqlite3
import json
import logging
from pathlib import Path
import os
import sys
import re
import datetime
import csv
from typing import Optional, List, Dict, Any, Tuple, Union

try:
    import yaml
    PYYAML_AVAILABLE = True
except ImportError:
    yaml = None # type: ignore
    PYYAML_AVAILABLE = False

# Configuration du logger pour ce module spécifique
logger = logging.getLogger("ALMA.ExplorateurKB")

# Configuration par défaut pour les chemins si cerveau_config.yaml n'est pas lisible
DEFAULT_EXPLORER_CONFIG: Dict[str, Any] = {
    "paths": {
        "cerveau_dir_suffix": "Cerveau",
        "knowledge_base_filename": "cerveau_knowledge.sqlite",
        "improvements_subdir": "ameliorations_proposees",
        "connaissance_dir_suffix": "Connaissance"
    },
    "db_timeout_seconds": 10
}
EXPLORER_APP_CONFIG: Dict[str, Any] = {} # Sera peuplé par load_cerveau_configuration_for_explorer


def load_cerveau_configuration_for_explorer() -> None:
    """
    Tente de charger les configurations de chemin et DB depuis cerveau_config.yaml.
    Met à jour EXPLORER_APP_CONFIG en conséquence.
    """
    global EXPLORER_APP_CONFIG
    # Commence avec une copie fraîche des défauts pour s'assurer que toutes les clés sont là
    current_config = json.loads(json.dumps(DEFAULT_EXPLORER_CONFIG)) # Deep copy

    base_alma_dir_str = os.getenv("ALMA_BASE_DIR")
    config_source_message = "Utilisation des chemins et paramètres DB par défaut pour l'explorateur."

    if not base_alma_dir_str:
        logger.warning("ALMA_BASE_DIR non défini. " + config_source_message)
        EXPLORER_APP_CONFIG = current_config
        return

    base_alma_dir = Path(base_alma_dir_str)
    # Utilise cerveau_dir_suffix du DEFAULT_CONFIG pour trouver cerveau_config.yaml
    cerveau_config_path = base_alma_dir / DEFAULT_EXPLORER_CONFIG["paths"]["cerveau_dir_suffix"] / "cerveau_config.yaml"

    if PYYAML_AVAILABLE and cerveau_config_path.exists():
        try:
            with open(cerveau_config_path, 'r', encoding='utf-8') as f_cfg:
                loaded_cerveau_config = yaml.safe_load(f_cfg) # type: ignore

            if loaded_cerveau_config and isinstance(loaded_cerveau_config, dict):
                # Met à jour current_config avec les valeurs de cerveau_config.yaml si elles existent
                paths_from_cerveau = loaded_cerveau_config.get("paths", {})
                kb_from_cerveau = loaded_cerveau_config.get("knowledge_base", {})

                current_config["paths"]["cerveau_dir_suffix"] = paths_from_cerveau.get("cerveau_dir_suffix", current_config["paths"]["cerveau_dir_suffix"])
                current_config["paths"]["knowledge_base_filename"] = kb_from_cerveau.get("db_name", current_config["paths"]["knowledge_base_filename"])
                current_config["paths"]["improvements_subdir"] = paths_from_cerveau.get("improvements_subdir", current_config["paths"]["improvements_subdir"])
                current_config["paths"]["connaissance_dir_suffix"] = paths_from_cerveau.get("connaissance_dir_suffix", current_config["paths"]["connaissance_dir_suffix"])
                current_config["db_timeout_seconds"] = kb_from_cerveau.get("db_timeout_seconds", current_config["db_timeout_seconds"])

                config_source_message = f"Configuration de l'explorateur mise à jour depuis {cerveau_config_path}"
            else:
                config_source_message = f"Fichier {cerveau_config_path} vide ou mal formaté. " + config_source_message
        except Exception as e_cfg:
            config_source_message = f"Erreur lors de la lecture de {cerveau_config_path}: {e_cfg}. " + config_source_message
    else:
        if not PYYAML_AVAILABLE: config_source_message = "PyYAML non disponible. " + config_source_message
        elif not cerveau_config_path.exists(): config_source_message = f"{cerveau_config_path} non trouvé. " + config_source_message

    logger.info(config_source_message)
    EXPLORER_APP_CONFIG = current_config


def get_db_path(args_db_path: Optional[str]) -> Optional[Path]:
    """Détermine le chemin vers la base de données SQLite."""
    if args_db_path:
        db_p = Path(args_db_path)
        if db_p.exists() and db_p.is_file():
            logger.debug(f"Utilisation du chemin DB fourni par argument: {db_p.resolve()}")
            return db_p.resolve()
        else:
            logger.error(f"Chemin DB fourni (--db-path '{args_db_path}') non valide ou fichier inexistant.")
            return None

    base_alma_dir_str = os.getenv("ALMA_BASE_DIR")
    if not base_alma_dir_str:
        logger.error("Variable d'environnement ALMA_BASE_DIR non définie et --db-path non fourni.")
        return None

    base_alma_dir = Path(base_alma_dir_str)

    # S'assurer que EXPLORER_APP_CONFIG est peuplé
    if not EXPLORER_APP_CONFIG or "paths" not in EXPLORER_APP_CONFIG:
        logger.error("EXPLORER_APP_CONFIG n'est pas initialisé correctement avant get_db_path.")
        return None

    paths_config = EXPLORER_APP_CONFIG.get("paths", DEFAULT_EXPLORER_CONFIG["paths"])

    cerveau_dir = base_alma_dir / paths_config["cerveau_dir_suffix"]
    kb_filename = paths_config["knowledge_base_filename"]
    kb_path = cerveau_dir / kb_filename

    if kb_path.exists() and kb_path.is_file():
        logger.debug(f"Chemin DB déduit de ALMA_BASE_DIR et config: {kb_path.resolve()}")
        return kb_path.resolve()
    else:
        logger.error(f"Base de données non trouvée à l'emplacement déduit: {kb_path.resolve()}")
        logger.error(f"  (Basé sur ALMA_BASE_DIR='{base_alma_dir}', cerveau_dir_suffix='{paths_config['cerveau_dir_suffix']}', db_name='{kb_filename}')")
        return None

def connect_db(db_path: Path) -> Optional[sqlite3.Connection]:
    """Connecte à la base de données SQLite en mode lecture seule."""
    db_timeout = EXPLORER_APP_CONFIG.get("db_timeout_seconds", DEFAULT_EXPLORER_CONFIG["db_timeout_seconds"])
    try:
        # Utilisation de f-string pour construire la chaîne de connexion URI
        conn_str = f"file:{db_path}?mode=ro&immutable=1"
        conn = sqlite3.connect(conn_str, uri=True, timeout=db_timeout)
        conn.row_factory = sqlite3.Row
        # Le mode WAL est généralement défini par l'application qui écrit (cerveau.py)
        # Le lecteur en bénéficiera automatiquement si la DB est déjà en mode WAL.
        # conn.execute("PRAGMA journal_mode=WAL;") # Peut causer une erreur en mode ro si la DB n'est pas déjà WAL
        logger.info(f"Connecté à la KnowledgeBase (lecture seule): {db_path} (timeout: {db_timeout}s)")
        return conn
    except sqlite3.OperationalError as e_op:
        logger.error(f"Erreur opérationnelle SQLite lors de la connexion à {db_path} (ex: fichier non trouvé, permissions, mode ro impossible): {e_op}")
        return None
    except sqlite3.Error as e:
        logger.error(f"Erreur de connexion SQLite à {db_path}: {e}", exc_info=True)
        return None

def format_output(data: Any, output_format: str = "text", title: Optional[str] = None) -> None:
    """Formate et affiche les données pour la console ou en JSON."""
    if output_format == "json":
        output_data_json = data
        if title:
            # Utiliser un nom de clé plus cohérent pour le JSON
            title_key = title.lower().replace(' ', '_').replace(':', '')
            output_data_json = {title_key: data}
        try:
            print(json.dumps(output_data_json, indent=2, ensure_ascii=False, default=str))
        except TypeError as e_json:
            logger.error(f"Erreur de sérialisation JSON: {e_json}. Affichage partiel ou brut.")
            print(str(output_data_json)) # Afficher la représentation str en cas d'échec
        return

    # Formatage texte
    if title:
        print(f"\n--- {title.replace('_', ' ').title()} ---")

    if isinstance(data, list):
        if not data:
            print("  Aucune donnée à afficher.")
        elif not data or not isinstance(data[0], dict): # Si ce n'est pas une liste de dictionnaires
            for item in data: print(f"  - {item}")
        else: # C'est une liste de dictionnaires, afficher comme un tableau
            headers = list(data[0].keys())
            if not headers: print("  Données vides (pas de colonnes)."); return

            col_widths = {h: len(str(h)) for h in headers}
            for row_dict in data:
                for h in headers: col_widths[h] = max(col_widths[h], len(str(row_dict.get(h, ''))))

            header_line = " | ".join(f"{str(h).upper():<{col_widths[h]}}" for h in headers)
            print(header_line)
            print("-" * len(header_line))
            for row_dict in data:
                print(" | ".join(f"{str(row_dict.get(h, '')):<{col_widths[h]}}" for h in headers))
    elif isinstance(data, dict):
        if not data:
            print("  Aucune donnée à afficher.")
        else:
            for key, value in data.items():
                key_formatted = str(key).replace('_', ' ').title()
                if isinstance(value, list) or (isinstance(value, dict) and key != "fichier_principal"): # Éviter la récursion infinie pour le titre principal
                    format_output(value, "text", title=key_formatted) # Récursion pour les sous-structures
                else:
                    print(f"  {key_formatted}: {value if value is not None else ''}")
    elif data is None: # Cas où data est None explicitement
        print("  Aucune donnée à afficher." if not title else f"  {str(title).replace('_', ' ').title()}: Aucune")
    else: # Pour les autres types de données (str, int, etc.)
        print(data)


def get_config_paths() -> Dict[str, Path]:
    """Récupère les chemins configurés (Connaissance, Cerveau, Propositions)."""
    base_alma_dir_str = os.getenv("ALMA_BASE_DIR")
    if not base_alma_dir_str:
        logger.critical("ALMA_BASE_DIR n'est pas défini. Impossible de déduire les chemins de configuration.")
        sys.exit(1) # C'est critique pour cette fonction

    base_alma_dir = Path(base_alma_dir_str)

    if not EXPLORER_APP_CONFIG or "paths" not in EXPLORER_APP_CONFIG:
        # S'assurer que load_cerveau_configuration_for_explorer a été appelé
        logger.critical("EXPLORER_APP_CONFIG n'est pas initialisé. Appelez load_cerveau_configuration_for_explorer() au début.")
        sys.exit(1)

    cfg_paths_explorer = EXPLORER_APP_CONFIG.get("paths", DEFAULT_EXPLORER_CONFIG["paths"])

    return {
        "cerveau_dir": (base_alma_dir / cfg_paths_explorer["cerveau_dir_suffix"]).resolve(),
        "improvements_dir": (base_alma_dir / cfg_paths_explorer["cerveau_dir_suffix"] / cfg_paths_explorer["improvements_subdir"]).resolve(),
        "connaissance_dir": (base_alma_dir / cfg_paths_explorer["connaissance_dir_suffix"]).resolve()
    }

def get_filepath_by_id(db_conn: sqlite3.Connection, file_id: int) -> Optional[str]:
    """Récupère le filepath pour un file_id donné."""
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT filepath FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        return row['filepath'] if row else None
    except sqlite3.Error as e:
        logger.error(f"Erreur SQLite lors de la récupération du chemin pour file_id {file_id}: {e}")
        return None

def _get_file_data_and_proposals(
    db_conn: sqlite3.Connection,
    file_id_to_query: Optional[int],
    filepath_to_query_str: Optional[str],
    config_paths: Dict[str, Path],
    verbose: bool
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Fonction interne pour récupérer les données d'un fichier et ses propositions."""
    cursor = db_conn.cursor()
    file_data_row: Optional[sqlite3.Row] = None

    if file_id_to_query is not None:
        logger.debug(f"Recherche du fichier par ID: {file_id_to_query}")
        cursor.execute("SELECT id, filepath, checksum, last_processed_utc, size_bytes, encoding, embedding FROM files WHERE id = ?", (file_id_to_query,))
        file_data_row = cursor.fetchone()
        if not file_data_row:
            logger.warning(f"Aucun fichier trouvé avec l'ID {file_id_to_query}.")
            return None, None
    elif filepath_to_query_str is not None:
        logger.debug(f"Recherche du fichier par chemin: {filepath_to_query_str}")
        cursor.execute("SELECT id, filepath, checksum, last_processed_utc, size_bytes, encoding, embedding FROM files WHERE filepath = ?", (filepath_to_query_str,))
        file_data_row = cursor.fetchone()
        if not file_data_row:
            # Le message d'erreur sera géré par la fonction appelante
            return None, None
    else:
        logger.error("Ni file_id ni filepath_str fournis à _get_file_data_and_proposals.")
        return None, None

    file_data = dict(file_data_row) # type: ignore
    file_id = file_data["id"]
    file_checksum = file_data["checksum"]

    if file_data.get("embedding"):
        file_data["embedding_present"] = True
        file_data["embedding_size_bytes"] = len(file_data["embedding"])
    else:
        file_data["embedding_present"] = False
    if "embedding" in file_data: del file_data["embedding"] # Ne pas l'afficher directement

    # Récupération des propositions
    improvements_dir_path = config_paths["improvements_dir"]
    original_filepath_from_db = Path(file_data['filepath']) # Utiliser le chemin de la DB
    original_filename_in_kb = original_filepath_from_db.name

    safe_filename = re.sub(r'[^\w\.\-]', '_', original_filename_in_kb)
    proposal_filename = f"{safe_filename}.{file_checksum}.ameliorations.json"
    proposal_filepath = improvements_dir_path / proposal_filename
    proposals_data: Dict[str, Any] = {}

    if proposal_filepath.exists():
        try:
            with open(proposal_filepath, 'r', encoding='utf-8') as f_prop:
                prop_data_content = json.load(f_prop)
            proposals_list = prop_data_content.get("proposals", [])
            summary: Dict[str, int] = {}
            for p_item in proposals_list:
                summary[p_item.get("type", "inconnu")] = summary.get(p_item.get("type", "inconnu"), 0) + 1

            proposals_data["fichier_propositions"] = str(proposal_filepath.resolve())
            proposals_data["resume_par_type"] = summary if summary else "Aucun type"
            proposals_data["total_propositions"] = len(proposals_list)
            if verbose:
                proposals_data["details_top_10"] = proposals_list[:10]
                if len(proposals_list) > 10:
                    proposals_data["details_top_10"].append({"message": f"... et {len(proposals_list) - 10} autres."}) # type: ignore
        except Exception as e_prop:
            proposals_data = {"erreur_lecture_propositions": str(e_prop), "fichier_attendu": str(proposal_filepath)}
    else:
        proposals_data = {"message": "Fichier de propositions non trouvé.", "fichier_attendu": str(proposal_filepath)}

    return file_data, proposals_data

# --- Fonctions pour les Commandes CLI ---
def handle_file_info(conn: sqlite3.Connection, identifier_or_path_arg: str, output_format: str, verbose: bool) -> None:
    """TODO: Add docstring."""
    logger.info(f"Récupération des informations pour l'argument: '{identifier_or_path_arg}' (verbose: {verbose})")
    config_paths = get_config_paths()

    file_id_to_query: Optional[int] = None
    path_to_query_str: Optional[str] = None
    original_filename_display = identifier_or_path_arg # Pour les messages d'erreur

    if identifier_or_path_arg.isdigit():
        try:
            file_id_to_query = int(identifier_or_path_arg)
            logger.debug(f"Argument '{identifier_or_path_arg}' interprété comme ID de fichier: {file_id_to_query}")
            # On récupérera le nom de fichier plus tard si l'ID est valide
        except ValueError: # Ne devrait pas arriver avec isdigit mais par sécurité
            logger.warning(f"Argument '{identifier_or_path_arg}' ressemble à un ID mais n'est pas un entier valide. Traitement comme chemin.")
            # Tombe dans la logique de chemin ci-dessous
            pass # Pour que path_to_query_str soit défini

    if file_id_to_query is None: # Si ce n'est pas un ID ou si la conversion a échoué
        path_arg_obj = Path(identifier_or_path_arg)
        connaissance_dir_abs = config_paths["connaissance_dir"]

        if path_arg_obj.is_absolute():
            filepath_to_query_obj = path_arg_obj.resolve()
            try:
                # Vérifie si le chemin absolu est bien un sous-chemin de Connaissance
                filepath_to_query_obj.relative_to(connaissance_dir_abs)
            except ValueError:
                logger.warning(f"Le chemin absolu fourni '{filepath_to_query_obj}' n'est PAS un sous-chemin du dossier Connaissance attendu '{connaissance_dir_abs}'. La recherche se fera sur le chemin exact fourni.")
        else:
            # Les chemins relatifs sont interprétés par rapport au dossier Connaissance
            filepath_to_query_obj = (connaissance_dir_abs / path_arg_obj).resolve()

        path_to_query_str = str(filepath_to_query_obj)
        original_filename_display = Path(path_to_query_str).name # Pour l'affichage du titre
        logger.debug(f"Argument '{identifier_or_path_arg}' interprété comme chemin de fichier: '{path_to_query_str}'")

    file_data, proposals_data = _get_file_data_and_proposals(
        conn, file_id_to_query, path_to_query_str, config_paths, verbose
    )

    if not file_data:
        message = f"Aucune information trouvée pour l'identifiant/chemin '{identifier_or_path_arg}'."
        if path_to_query_str and file_id_to_query is None : # Si c'était un chemin et non un ID
             message = f"Fichier '{path_to_query_str}' (interprété depuis '{identifier_or_path_arg}') non trouvé dans la table 'files'."
        logger.warning(message)
        format_output({"erreur": message} if output_format == "json" else message, output_format)
        return

    # Si on a cherché par ID, on a maintenant le vrai nom de fichier
    if file_id_to_query is not None:
        original_filename_display = Path(file_data['filepath']).name

    display_data: Dict[str, Any] = {}
    display_data["fichier_principal"] = file_data

    file_id = file_data["id"] # Assuré d'être présent si file_data n'est pas None
    cursor = conn.cursor()

    cursor.execute("SELECT meta_key, meta_value FROM metadata WHERE file_id = ? ORDER BY meta_key", (file_id,))
    display_data["metadonnees_extraites"] = [dict(row) for row in cursor.fetchall()] or "Aucune"

    ent_limit = 200 if verbose else 50
    cursor.execute(f"SELECT entity_text, entity_type, COUNT(*) as occurrences FROM named_entities WHERE file_id = ? GROUP BY LOWER(entity_text), entity_type ORDER BY occurrences DESC, entity_text LIMIT {ent_limit}", (file_id,))
    display_data[f"entites_nommees_top_{ent_limit}"] = [dict(row) for row in cursor.fetchall()] or "Aucune"

    tok_limit = 50 if verbose else 10
    tok_cols = "token_text, lemma, pos, is_significant" if verbose else "token_text, lemma, pos" # is_significant est bool
    cursor.execute(f"SELECT {tok_cols} FROM linguistic_tokens WHERE file_id = ? AND is_significant = 1 ORDER BY id LIMIT {tok_limit}", (file_id,))
    tokens_res = [dict(row) for row in cursor.fetchall()]
    if verbose: # Convertir bool en int pour affichage si verbose
        for t in tokens_res:
            if 'is_significant' in t: t['is_significant'] = 1 if t['is_significant'] else 0
    display_data[f"apercu_tokens_significatifs_{tok_limit}"] = tokens_res or "Aucun"

    display_data["propositions_amelioration"] = proposals_data

    format_output(display_data, output_format, title=f"Informations pour {original_filename_display}")


    """TODO: Add docstring."""
def handle_find_entity(conn: sqlite3.Connection, entity_text: str, entity_type: Optional[str], case_sensitive_text: bool, output_format: str, verbose: bool, limit: int) -> None:
    logger.info(f"Recherche entité '{entity_text}' (type: {entity_type or 'tout'}, sensible_casse_texte_texte: {case_sensitive_text}, verbose: {verbose}, limite: {limit})")

    query_select_parts = ["SELECT DISTINCT f.id as file_id", "f.filepath"]
    if verbose:
        query_select_parts.extend(["ne.entity_text as matched_entity", "ne.entity_type as matched_type", "f.last_processed_utc", "f.checksum"])

    query_select = ", ".join(query_select_parts)
    query_from_join = " FROM files f JOIN named_entities ne ON f.id = ne.file_id WHERE "
    params: List[Any] = []

    # Utiliser LIKE pour une recherche partielle, mais seulement si l'utilisateur inclut des wildcards
    # Sinon, une recherche exacte (insensible à la casse par défaut) est plus performante.
    text_operator = "LIKE" if "%" in entity_text else "="
    entity_text_param = entity_text # Si '=', pas besoin de %%. Si LIKE, l'utilisateur met les %%.

    text_condition = f"LOWER(ne.entity_text) {text_operator} LOWER(?)" if not case_sensitive_text else f"ne.entity_text {text_operator} ?"
    params.append(entity_text_param)

    type_condition = ""
    if entity_type:
        type_condition = " AND ne.entity_type = ?" # Le type est généralement stocké en MAJUSCULES
        params.append(entity_type.upper())

    query = query_select + query_from_join + text_condition + type_condition
    query += " ORDER BY f.last_processed_utc DESC LIMIT ?;"
    params.append(limit)

    cursor = conn.cursor()
    logger.debug(f"Exécution SQL pour find-entity: {query} avec params: {params}")
    try:
        cursor.execute(query, tuple(params))
        found_items = [dict(row) for row in cursor.fetchall()]
        format_output(found_items if found_items else "Aucun fichier trouvé contenant cette entité avec ces critères.", output_format, title=f"Fichiers Contenant L'Entité '{entity_text}'")
    except sqlite3.Error as e_sql:
        logger.error(f"Erreur SQLite lors de la recherche d'entité: {e_sql}", exc_info=True)
        format_output({"erreur_sql": str(e_sql)}, output_format)

    """TODO: Add docstring."""

def handle_list_files(
    conn: sqlite3.Connection, output_format: str, verbose: bool, limit: int, sort_by: str, order: str,
    since_date: Optional[str] = None, before_date: Optional[str] = None, extension: Optional[str] = None,
    path_contains: Optional[str] = None, min_size: Optional[int] = None, max_size: Optional[int] = None,
    has_embedding: Optional[bool] = None # NOUVEAU FILTRE
) -> None:
    logger.info(
        f"Listage des fichiers: limite={limit}, tri={sort_by} {order}, verbose={verbose}, "
        f"since={since_date}, before={before_date}, ext={extension}, path_contains={path_contains}, "
        f"min_size={min_size}, max_size={max_size}, has_embedding={has_embedding}" # NOUVEAU
    )

    select_cols_list = ["id", "filepath", "last_processed_utc"]
    # Toujours sélectionner 'embedding' pour pouvoir filtrer dessus, même si non affiché en mode non-verbose
    base_select_cols = "id, filepath, last_processed_utc, checksum, size_bytes, encoding, embedding"

    display_cols = ["id", "filepath", "last_processed_utc"] # Colonnes pour affichage non-verbose
    if verbose:
        # En mode verbose, on veut toutes les colonnes, y compris 'embedding_present'
        display_cols.extend(["checksum", "size_bytes", "encoding", "embedding_present"])

    # Construire la partie SELECT de la requête
    # (embedding IS NOT NULL) as embedding_present est calculé dynamiquement
    query_select_str = f"SELECT {base_select_cols}, (embedding IS NOT NULL) as embedding_present FROM files"

    conditions: List[str] = []
        """TODO: Add docstring."""
    params: List[Any] = []

    def parse_date_flexible(date_str: str, end_of_day: bool = False) -> Optional[str]:
        # ... (fonction parse_date_flexible existante, inchangée) ...
        try:
            if 'T' in date_str:
                dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
            else:
                dt_base = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                if end_of_day:
                    dt = dt_base.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=datetime.timezone.utc)
                else:
                    dt = dt_base.replace(hour=0, minute=0, second=0, tzinfo=datetime.timezone.utc)
            return dt.isoformat()
        except ValueError:
            logger.error(f"Format date invalide pour '{date_str}'. Attendu AAAA-MM-JJ ou format ISO complet.")
            return None

    if since_date:
        parsed_dt = parse_date_flexible(since_date, end_of_day=False)
        if parsed_dt: conditions.append("last_processed_utc >= ?"); params.append(parsed_dt)
        else: format_output({"erreur": f"Date --since invalide: {since_date}"}, output_format); return
    if before_date:
        parsed_dt = parse_date_flexible(before_date, end_of_day=True)
        if parsed_dt: conditions.append("last_processed_utc <= ?"); params.append(parsed_dt)
        else: format_output({"erreur": f"Date --before invalide: {before_date}"}, output_format); return

    if extension:
        ext_to_search = extension.lower() # Comparaison insensible à la casse
        if not ext_to_search.startswith('.'):
            ext_to_search = '.' + ext_to_search
        conditions.append("LOWER(SUBSTR(filepath, INSTR(filepath, '.'))) = ?") # Cherche la dernière extension
        # Alternative plus simple mais moins précise pour les noms avec plusieurs points :
        # conditions.append("LOWER(filepath) LIKE LOWER(?)"); params.append(f"%{ext_to_search}")
        params.append(ext_to_search)
    if path_contains:
        conditions.append("filepath LIKE ?"); params.append(f"%{path_contains}%")
    if min_size is not None:
        conditions.append("size_bytes >= ?"); params.append(min_size)
    if max_size is not None:
        conditions.append("size_bytes <= ?"); params.append(max_size)

    # NOUVEAU FILTRE : has_embedding
    if has_embedding is True:
        conditions.append("embedding IS NOT NULL")
    elif has_embedding is False:
        conditions.append("embedding IS NULL")

    query = query_select_str
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Validation du champ de tri
    # 'embedding_present' n'est pas une vraie colonne pour trier directement,
    # il faudrait trier sur '(embedding IS NOT NULL)'
    allowed_sort_fields = ["id", "filepath", "last_processed_utc", "checksum", "size_bytes", "encoding"]
    sql_sort_by_field = sort_by
    if sort_by == "embedding_present": # Cas spécial pour trier par présence d'embedding
        sql_sort_by_field = "(embedding IS NOT NULL)"
    elif sort_by not in allowed_sort_fields:
        logger.warning(f"Champ de tri '{sort_by}' invalide pour list-files. Utilisation de 'last_processed_utc'. Valides: {', '.join(allowed_sort_fields + ['embedding_present'])}")
        sql_sort_by_field = "last_processed_utc"

    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    query += f" ORDER BY {sql_sort_by_field} {order_sql}, id {order_sql} LIMIT ?;" # Ajout de id pour un tri secondaire stable
    params.append(limit)

    logger.debug(f"Exécution SQL pour list-files: {query} avec params: {params}")
    cursor = conn.cursor()
    try:
        cursor.execute(query, tuple(params))
        files_result_raw = [dict(row) for row in cursor.fetchall()]

        files_to_display = []
        if not files_result_raw:
            format_output("Aucun fichier trouvé avec ces critères.", output_format, title="Liste des Fichiers Analysés")
            return

        for row_data in files_result_raw:
            display_row = {}
            for col in display_cols: # Utiliser les colonnes définies pour l'affichage
                if col == "embedding_present":
                     display_row[col] = 1 if row_data.get('embedding_present') else 0
                elif col == "filepath" and not verbose and output_format == "text":
                    fp_display = row_data.get(col, '')
                    max_fp_len = 70
                    if len(fp_display) > max_fp_len:
                        fp_display = "..." + fp_display[-(max_fp_len-3):]
                    display_row[col] = fp_display
                elif col == "last_processed_utc" and not verbose and output_format == "text":
                    ts_utc = row_data.get(col, '')
                    ts_display = ts_utc
                    try:
                        dt_obj = datetime.datetime.fromisoformat(ts_utc.replace('Z', '+00:00'))
                        ts_display = dt_obj.strftime("%Y-%m-%d %H:%M") # Format plus court
                    except (ValueError, TypeError): pass
                    display_row[col] = ts_display
                else:
                    display_row[col] = row_data.get(col)
            files_to_display.append(display_row)

        format_output(files_to_display, output_format, title="Liste des Fichiers Analysés")

    except sqlite3.Error as e_sql:
        """TODO: Add docstring."""
        logger.error(f"Erreur SQLite lors du listage des fichiers: {e_sql}", exc_info=True)
        format_output({"erreur_sql": str(e_sql)}, output_format)

    def parse_date_flexible(date_str: str, end_of_day: bool = False) -> Optional[str]:
        # ... (même fonction qu'avant) ...
        try:
            if 'T' in date_str: # Format ISO complet
                dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                if dt.tzinfo is None: # S'assurer qu'il est conscient du fuseau horaire
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
            else: # Format AAAA-MM-JJ
                dt_base = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                if end_of_day:
                    dt = dt_base.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=datetime.timezone.utc)
                else:
                    dt = dt_base.replace(hour=0, minute=0, second=0, tzinfo=datetime.timezone.utc)
            return dt.isoformat()
        except ValueError:
            logger.error(f"Format date invalide pour '{date_str}'. Attendu AAAA-MM-JJ ou format ISO complet (ex: 2023-10-26 ou 2023-10-26T14:30:00Z).")
            return None


    if since_date:
        parsed_dt = parse_date_flexible(since_date, end_of_day=False)
        if parsed_dt: conditions.append("last_processed_utc >= ?"); params.append(parsed_dt)
        else: return # Arrêter si la date est invalide
    if before_date:
        parsed_dt = parse_date_flexible(before_date, end_of_day=True)
        if parsed_dt: conditions.append("last_processed_utc <= ?"); params.append(parsed_dt)
        else: return

    if extension:
        ext_to_search = extension if extension.startswith('.') else '.' + extension
        conditions.append("LOWER(filepath) LIKE LOWER(?)"); params.append(f"%{ext_to_search}")
    if path_contains:
        conditions.append("filepath LIKE ?"); params.append(f"%{path_contains}%") # L'utilisateur met les % si besoin de partiel
    if min_size is not None:
        conditions.append("size_bytes >= ?"); params.append(min_size)
    if max_size is not None:
        conditions.append("size_bytes <= ?"); params.append(max_size)

    query = base_query
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    allowed_sort_fields = ["id", "filepath", "last_processed_utc", "checksum", "size_bytes", "encoding"]
    if sort_by not in allowed_sort_fields:
        logger.warning(f"Champ de tri '{sort_by}' invalide. Utilisation de 'last_processed_utc'. Valides: {', '.join(allowed_sort_fields)}")
        sort_by = "last_processed_utc"

    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    query += f" ORDER BY {sort_by} {order_sql} LIMIT ?;"
    params.append(limit)

    logger.debug(f"Exécution SQL pour list-files: {query} avec params: {params}")
    cursor = conn.cursor()
    try:
        cursor.execute(query, tuple(params))
        files_result_raw = [dict(row) for row in cursor.fetchall()]

        # Convertir le booléen embedding_present en int pour affichage si verbose
        if verbose:
            for row in files_result_raw:
                if 'embedding_present' in row:
                    row['embedding_present'] = 1 if row['embedding_present'] else 0

        if not verbose and output_format == "text" and files_result_raw:
            files_display = []
            for f_data_dict in files_result_raw:
                fp_display = f_data_dict['filepath']
                max_fp_len = 70 # Longueur max pour l'affichage du chemin
                if len(fp_display) > max_fp_len:
                    fp_display = "..." + fp_display[-(max_fp_len-3):] # Tronquer au début

                ts_utc = f_data_dict['last_processed_utc']
                ts_display = ts_utc # Par défaut
                try: # Essayer de formater la date de manière plus lisible
                    dt_obj = datetime.datetime.fromisoformat(ts_utc.replace('Z', '+00:00'))
                    ts_display = dt_obj.strftime("%Y-%m-%d %H:%M:%S") # Format local plus court
                except ValueError:
                    pass # Garder le format ISO si le parsing échoue
                files_display.append({"id": f_data_dict['id'], "filepath": fp_display, "last_processed_utc": ts_display})
            format_output(files_display, output_format, title="Liste des Fichiers Analysés")
        else:
            format_output(files_result_raw if files_result_raw else "Aucun fichier trouvé avec ces critères.", output_format, title="Liste des Fichiers Analysés")

    except sqlite3.Error as e_sql:
        logger.error(f"Erreur SQLite lors du listage des fichiers: {e_sql}", exc_info=True)
        format_output({"erreur_sql": str(e_sql)}, output_format)
            """TODO: Add docstring."""


def handle_list_entities(
    conn: sqlite3.Connection, output_format: str, verbose: bool,
    entity_type: Optional[str], min_count: int, sort_by: str, order: str, limit: int,
    output_csv_path: Optional[str]
) -> None:
    # ... (Code de handle_list_entities que nous avions déjà bien avancé, il est probablement correct)
    # ... (Je vais le reprendre de notre version précédente qui était déjà assez complète)
    logger.info(
        f"Listage des entités: type={entity_type or 'tout'}, min_count={min_count}, "
        f"sort_by={sort_by}, order={order}, limit={limit}, csv={output_csv_path}, verbose={verbose}"
    )
    select_fields_map = {
        "norm_entity_text": "LOWER(entity_text) as norm_entity_text",
        "entity_text_display": "entity_text", # Pour afficher le premier texte rencontré pour ce groupe
        "entity_type": "entity_type",
        "frequency": "COUNT(*) as frequency",
        "distinct_documents": "COUNT(DISTINCT file_id) as distinct_documents"
    }
    select_parts_keys = ["entity_text_display", "entity_type", "frequency"]
    if verbose:
        select_parts_keys.append("distinct_documents")

    # S'assurer que norm_entity_text est là pour le GROUP BY
    final_select_parts_sql = [select_fields_map["norm_entity_text"]]
    # Pour entity_text_display, on peut prendre le MAX pour avoir une casse consistante (ou MIN)
    final_select_parts_sql.append("MAX(entity_text) as entity_text_display")
    final_select_parts_sql.append(select_fields_map["entity_type"])
    final_select_parts_sql.append(select_fields_map["frequency"])
    if verbose:
        final_select_parts_sql.append(select_fields_map["distinct_documents"])

    base_query = f"SELECT {', '.join(final_select_parts_sql)} FROM named_entities"
    conditions: List[str] = []
    params: List[Any] = []

    if entity_type:
        conditions.append("LOWER(entity_type) = LOWER(?)") # Comparaison insensible à la casse pour le type
        params.append(entity_type)

    query = base_query
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " GROUP BY norm_entity_text, LOWER(entity_type)" # Grouper par texte normalisé et type normalisé

    if min_count > 0: # min_count=0 ou négatif n'a pas de sens, on filtre si > 0
        query += " HAVING COUNT(*) >= ?"
        params.append(min_count)

    allowed_sort_fields_map = {
        "entity_text": "norm_entity_text",
        "entity_type": "LOWER(entity_type)",
        "frequency": "frequency",
        "distinct_documents": "distinct_documents"
    }
    if sort_by not in allowed_sort_fields_map:
        logger.warning(f"Champ de tri '{sort_by}' invalide pour list-entities. Utilisation de 'frequency'.")
        sort_by = "frequency"
    if sort_by == "distinct_documents" and not verbose:
        logger.warning(f"Tri par 'distinct_documents' non disponible sans --verbose. Utilisation de 'frequency'.")
        sort_by = "frequency"

    sql_sort_field = allowed_sort_fields_map[sort_by]
    order_sql = "DESC" if order.lower() == "desc" else "ASC"
    query += f" ORDER BY {sql_sort_field} {order_sql}, norm_entity_text ASC LIMIT ?;"
    params.append(limit)

    logger.debug(f"Exécution SQL pour list-entities: {query} avec params: {params}")
    cursor = conn.cursor()
    try:
        cursor.execute(query, tuple(params))
        entities_result_raw = [dict(row) for row in cursor.fetchall()]

        entities_result_display = []
        for row_dict_raw in entities_result_raw:
            # On veut afficher entity_text_display, pas norm_entity_text
            row_dict_display = {k: v for k, v in row_dict_raw.items() if k != "norm_entity_text"}
            entities_result_display.append(row_dict_display)

        if output_csv_path:
            if entities_result_display:
                headers_csv = list(entities_result_display[0].keys())
                with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headers_csv)
                    writer.writeheader()
                    writer.writerows(entities_result_display)
                logger.info(f"Résultats exportés en CSV vers : {output_csv_path}")
                if output_format == "text": print(f"Résultats également exportés vers {output_csv_path}")
            else:
                logger.info("Aucune entité à exporter en CSV.")
                if output_format == "text": print("Aucune entité à exporter.")

        if not output_csv_path or output_format == "json" or (output_csv_path and output_format == "text"):
             format_output(entities_result_display if entities_result_display else "Aucune entité trouvée avec ces critères.", output_format, title="Liste des Entités Nommées")
    except sqlite3.Error as e_sql:
        logger.error(f"Erreur SQLite lors du listage des entités: {e_sql}", exc_info=True)
            """TODO: Add docstring."""
        format_output({"erreur_sql": str(e_sql)}, output_format)


def handle_db_summary(conn: sqlite3.Connection, output_format: str) -> None:
    # ... (Code de handle_db_summary que nous avions déjà bien avancé, il est probablement correct)
    # ... (Je vais le reprendre de notre version précédente)
    logger.info("Génération du résumé de la base de données.")
    summary_data: Dict[str, Any] = {}
    cursor = conn.cursor()
    queries = {
        "total_fichiers_analyses": "SELECT COUNT(*) FROM files;",
        "fichiers_avec_embedding": "SELECT COUNT(*) FROM files WHERE embedding IS NOT NULL;", # NOUVEAU
        "total_tokens_linguistiques": "SELECT COUNT(*) FROM linguistic_tokens;",
        "total_tokens_significatifs": "SELECT COUNT(*) FROM linguistic_tokens WHERE is_significant = 1;",
        "total_entites_nommees_occurrences": "SELECT COUNT(*) FROM named_entities;", # Total des occurrences
        "total_entites_nommees_uniques": "SELECT COUNT(DISTINCT LOWER(entity_text) || '_' || LOWER(entity_type)) FROM named_entities;", # Plus précis pour uniques
        "total_types_entites_distincts": "SELECT COUNT(DISTINCT LOWER(entity_type)) FROM named_entities;",
        "total_metadonnees": "SELECT COUNT(*) FROM metadata;",
        "premier_fichier_traite_utc": "SELECT MIN(last_processed_utc) FROM files;",
        "dernier_fichier_traite_utc": "SELECT MAX(last_processed_utc) FROM files;",
    }
    for key, query_str in queries.items(): # Renommé query en query_str
        try:
            cursor.execute(query_str)
            result = cursor.fetchone()
            summary_data[key] = result[0] if result and result[0] is not None else "N/A"
        except sqlite3.Error as e_sql:
            logger.warning(f"Erreur SQL pour la statistique '{key}': {e_sql}")
            summary_data[key] = "Erreur d'accès"

    db_file_path_obj = get_db_path(None)
    if db_file_path_obj and db_file_path_obj.exists():
        try:
            db_size_bytes = db_file_path_obj.stat().st_size
            summary_data["taille_db_mo"] = round(db_size_bytes / (1024 * 1024), 2)
        except Exception as e_stat:
            logger.warning(f"Impossible de lire la taille du fichier DB {db_file_path_obj}: {e_stat}")
            summary_data["taille_db_mo"] = "N/A"
                """TODO: Add docstring."""
    else:
        summary_data["taille_db_mo"] = "N/A (Chemin DB non trouvé)"
    format_output(summary_data, output_format, title="Résumé de la KnowledgeBase")

def main():
    global EXPLORER_APP_CONFIG # Nécessaire car load_cerveau_configuration_for_explorer modifie cette globale

    # 1. Charger la configuration de l'explorateur (qui lit cerveau_config.yaml)
    # Cette fonction met à jour la globale EXPLORER_APP_CONFIG.
    try:
        load_cerveau_configuration_for_explorer()
    except Exception as e_conf_load:
        # Utiliser un logger temporaire ou print si le logger principal n'est pas encore configuré
        temp_logger_main = logging.getLogger(f"{APP_NAME}.MainInit")
        if not temp_logger_main.handlers:
            _ch_temp = logging.StreamHandler(sys.stderr) # Écrire les erreurs critiques sur stderr
            _ch_temp.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s'))
            temp_logger_main.addHandler(_ch_temp)
            temp_logger_main.setLevel(logging.ERROR)
        temp_logger_main.critical(f"ERREUR CRITIQUE lors du chargement de la configuration pour l'explorateur: {e_conf_load}", exc_info=True)
        sys.exit(1)

    # 2. Configuration du parser d'arguments
    parser = argparse.ArgumentParser(
        description="Explorateur CLI pour la KnowledgeBase d'ALMA Cerveau.\n"
                    "Les options globales (ex: -v, --output-format, --db-path) doivent précéder la sous-commande.",
        formatter_class=argparse.RawTextHelpFormatter, # Permet de mieux formater l'aide
        epilog="Exemple: explorateur_kb.py -v --output-format json file-info MonRapport.txt"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="Chemin optionnel vers le fichier cerveau_knowledge.sqlite. Si non fourni, tente de le déduire."
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Format de sortie (défaut: text)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Afficher plus de détails dans la sortie et les logs DEBUG en console."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}" # Assurez-vous que VERSION est définie globalement dans votre script
    )

    subparsers = parser.add_subparsers(dest="command", title="Commandes disponibles", required=False)

    # --- Commande file-info ---
    file_info_parser = subparsers.add_parser("file-info", help="Infos détaillées d'un fichier (ID ou chemin).",
                                             description="Affiche toutes les informations stockées pour un fichier spécifique, identifié par son ID numérique dans la KB ou son chemin (absolu, ou relatif au dossier Connaissance configuré).")
    file_info_parser.add_argument("identifier_or_path", metavar="ID_OU_CHEMIN", type=str, help="ID numérique du fichier ou chemin du fichier.")
    file_info_parser.set_defaults(func_to_call=handle_file_info)

    # --- Commande find-entity ---
    find_entity_parser = subparsers.add_parser("find-entity", help="Trouver fichiers contenant une entité nommée.",
                                               description="Liste tous les fichiers où une entité nommée spécifique a été trouvée, avec options de filtrage.")
    find_entity_parser.add_argument("entity_text", metavar="TEXTE_ENTITE", type=str, help="Texte de l'entité à rechercher (peut utiliser '%%' comme joker SQL).")
    find_entity_parser.add_argument("-t", "--type", dest="entity_type", type=str, help="Filtrer par type d'entité (ex: PER, LOC, ORG). La casse est ignorée pour le type.")
    find_entity_parser.add_argument("-cst", "--case-sensitive-text", action="store_true", help="Rendre la recherche du texte de l'entité sensible à la casse (par défaut, insensible).")
    find_entity_parser.add_argument("-l", "--limit", type=int, default=50, help="Nombre maximum de fichiers à retourner (défaut: 50).")
    find_entity_parser.set_defaults(func_to_call=handle_find_entity)

    # --- Commande list-files ---
    list_files_parser = subparsers.add_parser("list-files", help="Lister les fichiers dans la KB avec options de filtrage et de tri.",
                                              description="Liste les fichiers enregistrés dans la KnowledgeBase. Permet de filtrer par date, extension, contenu du chemin, taille, et présence d'embedding, ainsi que de trier les résultats.")
    list_files_parser.add_argument("-l", "--limit", type=int, default=20, help="Nombre maximum de fichiers à afficher (défaut: 20).")
    list_files_parser.add_argument("-s", "--sort-by", choices=['id', 'filepath', 'last_processed_utc', 'checksum', 'size_bytes', 'encoding', 'embedding_present'], default='last_processed_utc', help="Champ pour le tri (défaut: last_processed_utc). 'date' est un alias pour 'last_processed_utc'.")
    list_files_parser.add_argument("-o", "--order", choices=['asc', 'desc'], default='desc', help="Ordre de tri (défaut: desc pour les dates/ID, asc pour les textes).")
    list_files_parser.add_argument("--since", dest="since_date", type=str, metavar="AAAA-MM-JJ[THH:MM:SS]", help="N'afficher que les fichiers traités depuis cette date/timestamp ISO (inclus).")
    list_files_parser.add_argument("--before", dest="before_date", type=str, metavar="AAAA-MM-JJ[THH:MM:SS]", help="N'afficher que les fichiers traités avant cette date/timestamp ISO (exclus).")
    list_files_parser.add_argument("-e", "--extension", type=str, help="Filtrer par extension de fichier (ex: .txt, .json, sans le point).")
    list_files_parser.add_argument("-pc", "--path-contains", type=str, help="Filtrer les fichiers dont le chemin (relatif à Connaissance/) contient cette chaîne.")
    list_files_parser.add_argument("--min-size", type=str, help="Taille minimale du fichier (ex: 10KB, 1MB, ou en octets si pas d'unité).") # Changé en str pour parser l'unité
    list_files_parser.add_argument("--max-size", type=str, help="Taille maximale du fichier (ex: 100MB, ou en octets).") # Changé en str
    list_files_parser.add_argument("--has-embedding", choices=['true', 'false'], type=str.lower, default=None, help="Filtrer par présence d'embedding ('true' ou 'false').") # Modifié pour accepter 'true'/'false'
    list_files_parser.set_defaults(func_to_call=handle_list_files)

    # --- Commande list-entities ---
    list_entities_parser = subparsers.add_parser("list-entities", help="Lister les entités nommées uniques et leur fréquence.",
                                                 description="Liste toutes les entités nommées uniques trouvées dans la KB, avec leur fréquence d'apparition et le nombre de documents distincts les mentionnant.")
    list_entities_parser.add_argument("-t", "--type", dest="entity_type", type=str, help="Filtrer par type d'entité (ex: PER, LOC, ORG). La casse est ignorée.")
    list_entities_parser.add_argument("-mc", "--min-count", type=int, default=1, help="N'afficher que les entités apparaissant au moins N fois au total (défaut: 1).")
    list_entities_parser.add_argument("-s", "--sort-by", choices=['entity_text', 'entity_type', 'frequency', 'distinct_documents'], default='frequency', help="Champ pour le tri (défaut: frequency).")
    list_entities_parser.add_argument("-o", "--order", choices=['asc', 'desc'], default='desc', help="Ordre de tri (défaut: desc).")
    list_entities_parser.add_argument("-l", "--limit", type=int, default=50, help="Nombre maximum d'entités à afficher (défaut: 50).")
    list_entities_parser.add_argument("-csv", "--output-csv", dest="output_csv_path", type=str, metavar="CHEMIN_FICHIER.csv", help="Chemin optionnel pour sauvegarder les résultats en fichier CSV.")
    list_entities_parser.set_defaults(func_to_call=handle_list_entities)

    # --- Commande db-summary ---
    db_summary_parser = subparsers.add_parser("db-summary", help="Afficher un résumé statistique de la KnowledgeBase.",
                                              description="Affiche des statistiques globales sur la KnowledgeBase (nombre de fichiers, tokens, entités, taille de la base, etc.).")
    db_summary_parser.set_defaults(func_to_call=handle_db_summary)
    # --- Fin Définition des Sous-Parseurs ---

    args = parser.parse_args()

    # 3. Configuration du logger principal du module (après parsing des args pour utiliser -v)
    log_level_console = logging.DEBUG if args.verbose else logging.INFO
    if not logger.handlers: # Configurer seulement si pas déjà fait (ex: si importé)
        ch_main = logging.StreamHandler(sys.stdout) # Utiliser stdout pour les messages normaux
        # Un format plus simple pour la console peut être suffisant
        formatter_main = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s', datefmt="%H:%M:%S")
        ch_main.setFormatter(formatter_main)
        logger.addHandler(ch_main)
    logger.setLevel(log_level_console) # Définit le niveau pour TOUS les handlers du logger

    logger.debug(f"Arguments CLI parsés: {args}")

    # 4. Gérer le cas où aucune sous-commande n'est fournie
    if not args.command:
        parser.print_help()
        logger.info("Aucune sous-commande fournie. Affichage de l'aide.")
        sys.exit(0)

    # 5. Obtenir le chemin de la DB et se connecter
    db_path_to_use = get_db_path(args.db_path) # Utilise la fonction get_db_path corrigée

    if not db_path_to_use:
        # get_db_path logue déjà l'erreur spécifique
        logger.critical("Chemin de la KnowledgeBase non valide ou base de données introuvable. Arrêt de l'explorateur.")
        sys.exit(1)

    conn = None # Initialiser avant le try
    try:
        conn = connect_db(db_path_to_use)
        if not conn:
            # connect_db logue déjà l'erreur si la connexion échoue
            logger.critical(f"Impossible de se connecter à la KnowledgeBase à : {db_path_to_use}. Arrêt.")
            sys.exit(1)

        # 6. Appeler la fonction handler associée à la sous-commande
        # La méthode args.func_to_call(conn, args) est plus propre
        if hasattr(args, 'func_to_call') and callable(args.func_to_call):
            logger.debug(f"Appel de la fonction handler: {args.func_to_call.__name__} pour la commande '{args.command}'")
            args.func_to_call(conn, args) # Passer l'objet args complet
        else:
            # Ce cas ne devrait plus se produire grâce à la gestion de args.command plus haut
            logger.error(f"Logique d'erreur : Aucune fonction handler associée à la commande '{args.command}'.")
            parser.print_help()
            sys.exit(1)

    except sqlite3.Error as e_sql_main:
        logger.critical(f"Erreur SQLite majeure non gérée dans main: {e_sql_main}", exc_info=True)
        sys.exit(1)
    except Exception as e_main_unexpected:
        logger.critical(f"Erreur inattendue majeure non gérée dans main: {e_main_unexpected}", exc_info=True)
        sys.exit(1)
    finally:
        if conn:
            try:
                conn.close()
                logger.info("Connexion à la KnowledgeBase fermée.")
            except Exception as e_close_main:
                logger.error(f"Erreur lors de la fermeture de la connexion DB dans main: {e_close_main}", exc_info=True)

if __name__ == "__main__":
    # Configuration initiale du logger pour les messages AVANT que le logger principal ne soit configuré par main()
    # Ceci est utile si ALMA_BASE_DIR a un problème et que le logger du module n'est pas encore prêt.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s.%(levelname)s - %(message)s (Bootstrap)')

    # Déterminer ALMA_BASE_DIR au niveau du module pour que les autres fonctions puissent l'utiliser
    # (Cette logique est déjà en haut de votre script, c'est bien)
    if not ALMA_BASE_DIR_RESOLVED_EXPLORER: # Utiliser le flag global
        # Message d'erreur si ALMA_BASE_DIR n'a pas pu être résolu (déjà géré par la logique en haut)
        print(f"ERREUR CRITIQUE (Bootstrap __main__): ALMA_BASE_DIR n'a pas pu être déterminé. Vérifiez la structure du projet ou la variable d'environnement.", file=sys.stderr)
        sys.exit(1)

    # Maintenant que le logger principal (logger) est configuré dans main(),
    # on peut l'utiliser pour les messages de démarrage du script.
    # Les messages avant l'appel à main() utiliseront le basicConfig.

    logger_main_script = logging.getLogger(APP_NAME) # Utiliser le même nom que dans main() pour la cohérence
    logger_main_script.info(f"--- Démarrage {APP_NAME} V{VERSION} ---")
    try:
        main()
        logger_main_script.info(f"--- {APP_NAME} V{VERSION} Terminé Normalement ---")
    except SystemExit as e_exit: # Attraper SystemExit pour éviter le traceback complet si on quitte proprement
        if e_exit.code == 0:
             logger_main_script.info(f"--- {APP_NAME} V{VERSION} Terminé avec code de sortie 0 (normal) ---")
        else:
             logger_main_script.error(f"--- {APP_NAME} V{VERSION} Terminé avec code de sortie {e_exit.code} (erreur) ---")
    except Exception as e_script_global:
        logger_main_script.critical(f"Exception non gérée au niveau du script global __main__: {e_script_global}", exc_info=True)
        sys.exit(1) # S'assurer de quitter avec un code d'erreur