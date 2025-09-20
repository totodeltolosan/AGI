#!/usr/bin/env python3
# parlealma.py

"""
---
name: parlealma.py
version: 0.2.3-beta # NLU slots multiples V2, DM contexte clarification V2
author: Toni & Gemini AI
description: Interface conversationnelle CLI pour ALMA.
role: Interaction en langage naturel avec ALMA
type_execution: cli_interactive
état: en développement actif
last_update: 2025-05-24 # NLU extraction slots multiples V2, DM contexte V2
dossier: ALMA/Interfaces/
tags: [V20, alma, dialogue, cli, nlu, nlg, kb_interaction, contexte, clarification]
dependencies: [spacy, PyYAML (pour config explorateur), sqlite3]
---
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path
import re
from typing import Dict, Any, Optional, List, Tuple
import argparse

# Configuration du logger pour parlealma
logger = logging.getLogger("ALMA.ParleALMA")
if not logger.handlers:
    _ch = logging.StreamHandler(sys.stdout)
    _formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s - %(message)s', datefmt="%H:%M:%S")
    _ch.setFormatter(_formatter)
    logger.addHandler(_ch)
logger.setLevel(logging.DEBUG)

try:
    import yaml
    PYYAML_AVAILABLE = True
except ImportError:
    yaml = None # type: ignore
    PYYAML_AVAILABLE = False

DEFAULT_PATHS_CONFIG_PARLEALMA: Dict[str, str] = {
    "cerveau_dir_suffix": "Cerveau",
    "knowledge_base_filename": "cerveau_knowledge.sqlite",
    "connaissance_dir_suffix": "Connaissance"
}
PARLEALMA_APP_CONFIG: Dict[str, Any] = {"paths": DEFAULT_PATHS_CONFIG_PARLEALMA.copy(), "db_timeout_seconds": 10}

def load_db_config_for_parlealma() -> None:
    """TODO: Add docstring."""
    global PARLEALMA_APP_CONFIG
    logger.debug("load_db_config_for_parlealma: Début chargement config DB.")
    base_alma_dir_str = os.getenv("ALMA_BASE_DIR")
    current_paths_config = DEFAULT_PATHS_CONFIG_PARLEALMA.copy()
    db_timeout = 10

    if base_alma_dir_str:
        base_alma_dir = Path(base_alma_dir_str)
        cerveau_config_path = base_alma_dir / DEFAULT_PATHS_CONFIG_PARLEALMA["cerveau_dir_suffix"] / "cerveau_config.yaml"
        if PYYAML_AVAILABLE and cerveau_config_path.exists():
            try:
                with open(cerveau_config_path, 'r', encoding='utf-8') as f_cfg:
                    loaded_cfg = yaml.safe_load(f_cfg) # type: ignore
                if loaded_cfg and isinstance(loaded_cfg, dict):
                    paths_cfg_from_cerveau = loaded_cfg.get("paths", {})
                    kb_cfg_from_cerveau = loaded_cfg.get("knowledge_base", {})

                    current_paths_config["knowledge_base_filename"] = kb_cfg_from_cerveau.get("db_name", current_paths_config["knowledge_base_filename"])
                    current_paths_config["cerveau_dir_suffix"] = paths_cfg_from_cerveau.get("cerveau_dir_suffix", current_paths_config["cerveau_dir_suffix"])
                    current_paths_config["connaissance_dir_suffix"] = paths_cfg_from_cerveau.get("connaissance_dir_suffix", current_paths_config["connaissance_dir_suffix"])
                    db_timeout = kb_cfg_from_cerveau.get("db_timeout_seconds", db_timeout)
                    logger.info(f"load_db_config_for_parlealma: Config DB MAJ depuis cerveau_config.yaml.")
            except Exception as e: logger.warning(f"load_db_config_for_parlealma: Erreur chargement cerveau_config.yaml: {e}")

    PARLEALMA_APP_CONFIG["paths"] = current_paths_config
    PARLEALMA_APP_CONFIG["db_timeout_seconds"] = db_timeout
    logger.debug(f"load_db_config_for_parlealma: Config finale: {PARLEALMA_APP_CONFIG}")


    """TODO: Add docstring."""
def get_kb_db_path_for_parlealma() -> Optional[Path]:
    logger.debug("get_kb_db_path_for_parlealma: Tentative de récupération du chemin de la KB.")
    base_alma_dir_str = os.getenv("ALMA_BASE_DIR")
    if not base_alma_dir_str:
        logger.error("get_kb_db_path_for_parlealma: ALMA_BASE_DIR non défini.")
        return None
    base_alma_dir = Path(base_alma_dir_str)
    if not PARLEALMA_APP_CONFIG or "paths" not in PARLEALMA_APP_CONFIG: # Vérifier si load_db_config a été appelé
        load_db_config_for_parlealma() # Charger si ce n'est pas déjà fait
        if not PARLEALMA_APP_CONFIG or "paths" not in PARLEALMA_APP_CONFIG: # Revérifier
             logger.error("get_kb_db_path_for_parlealma: PARLEALMA_APP_CONFIG non initialisé même après tentative de chargement.")
             return None

    paths_cfg = PARLEALMA_APP_CONFIG.get("paths", DEFAULT_PATHS_CONFIG_PARLEALMA)
    kb_path = base_alma_dir / paths_cfg["cerveau_dir_suffix"] / paths_cfg["knowledge_base_filename"]

    if kb_path.exists() and kb_path.is_file():
        logger.debug(f"get_kb_db_path_for_parlealma: Chemin KB trouvé: {kb_path}")
        return kb_path
    else:
        logger.error(f"get_kb_db_path_for_parlealma: KnowledgeBase non trouvée à {kb_path.resolve()}")
        return None
            """TODO: Add docstring."""
                """TODO: Add docstring."""

class NLUEngine:
    def __init__(self, spacy_model_name: str = "fr_core_news_sm"):
        self.nlp: Optional[Any] = None
        self.matcher: Optional[Any] = None
        self.spacy_model_name = spacy_model_name
        self.instance_id = id(self)
        self.filename_regex = re.compile(
            r"""
            \b                                # Début de mot
            (?:                               # Groupe non capturant pour préfixes optionnels
                [\w\s()\-.'"]*?               # Caractères possibles avant le nom de fichier réel (non gourmand)
                (?:de|sur|pour|concernant|fichier|document|rapport)\s+
            )?
            (                                 # Groupe capturant 1: le nom de fichier
                [\w\s()\-.'"]+                # Nom du fichier (peut contenir des espaces, etc.)
                \.                            # Le point de l'extension
                (?:txt|md|json|py|sh|xml)     # Les extensions autorisées
            )
            \b                                # Fin de mot
            """,
            re.IGNORECASE | re.VERBOSE
        )
        self.conjunction_regex = re.compile(
            r'\s+(?:et\s+aussi\s+sur|et\s+aussi|ainsi\s+que|et|ou)\s+|,', # Ajout de la virgule comme séparateur
            re.IGNORECASE
        )
        logger.debug(f"NLUEngine __init__ (ID: {self.instance_id}): Tentative d'init avec '{self.spacy_model_name}'.")
        try:
            import spacy
            from spacy.matcher import Matcher
            self.nlp = spacy.load(self.spacy_model_name)
            self.matcher = Matcher(self.nlp.vocab)
            self._add_intent_patterns()
            logger.info(f"NLUEngine: Modèle spaCy '{self.spacy_model_name}' et Matcher initialisés.")
                """TODO: Add docstring."""
        except Exception as e:
            logger.error(f"NLUEngine __init__ (ID: {self.instance_id}): ERREUR init: {e}.", exc_info=True)

    def _add_intent_patterns(self):
        if self.matcher is None: return
        logger.debug(f"NLUEngine _add_intent_patterns (ID: {self.instance_id}): Ajout des patrons...")
        p_auteur = [[{"LOWER": "qui"}, {"LOWER": "est"}, {"LOWER": "l'auteur"}, {"LOWER": "de"}],[{"LEMMA": "auteur"}, {"LOWER": "de"}],[{"LOWER": "par"}, {"LOWER": "qui"}, {"LEMMA": "être", "POS":"AUX"}, {"LEMMA": "écrire"}]]
        self.matcher.add("DEMANDE_AUTEUR", p_auteur)
        p_entites = [[{"LEMMA": "lister"}, {"LOWER": "moi", "OP": "?"}, {"LOWER": "les", "OP": "?"}, {"LEMMA": "entité"}],[{"LEMMA": "quel"}, {"LEMMA": "être"}, {"LOWER": "les", "OP": "?"}, {"LEMMA": "entité"}],[{"LEMMA": "entité"}, {"LOWER": "principale", "OP": "?"}, {"LOWER": "de", "OP": "?"}]]
        self.matcher.add("DEMANDE_ENTITES", p_entites)
        p_info = [[{"LEMMA": "info"}, {"LOWER": "sur"}],[{"LOWER": "parler"}, {"LOWER": "moi"}, {"LOWER": "de"}],[{"LEMMA": "donner"}, {"LOWER": "moi", "OP": "?"}, {"LOWER": "des", "OP": "?"}, {"LEMMA": "info"}, {"LOWER": "sur"}],[{"LEMMA": "quel"}, {"LEMMA": "être"}, {"LOWER": "les", "OP": "?"}, {"LEMMA": "information"}, {"LOWER": "pour", "OP": "?"}, {"LOWER": "concernant", "OP": "?"}]]
        self.matcher.add("DEMANDE_INFO_DOC", p_info)
        p_etat = [[{"LOWER": "comment"}, {"LEMMA": "aller"}],[{"LOWER": "ça"}, {"LOWER": "va"}]]
        self.matcher.add("SMALL_TALK_ETAT_ALMA", p_etat)
        self.matcher.add("SALUTATION", [[{"LOWER": "bonjour"}], [{"LOWER": "salut"}], [{"LOWER": "hello"}]])
        self.matcher.add("QUITTER", [[{"LOWER": "quitter"}], [{"LOWER": "au"}, {"LOWER": "revoir"}], [{"LOWER": "bye"}]])
        logger.debug(f"NLUEngine _add_intent_patterns (ID: {self.instance_id}): Patrons ajoutés.")

    def _extract_filenames_from_segment(self, text_segment: str) -> List[str]:
        """Extrait les noms de fichiers d'un segment de texte donné (Regex puis NER pour confirmer/affiner)."""
        if not text_segment or not self.nlp: return []

        found_filenames_with_pos = {} # stocke filename -> start_pos pour trier

        # 1. Regex sur le segment entier pour trouver tous les noms de fichiers potentiels
        for match in self.filename_regex.finditer(text_segment):
            filename = match.group(1).strip() # Le groupe 1 est le nom de fichier réel
            if '.' in filename and not filename.startswith('.'):
                if filename not in found_filenames_with_pos: # Éviter doublons de la regex
                    found_filenames_with_pos[filename] = match.start(1)
                logger.debug(f"NLUEngine _extract_filenames (ID: {self.instance_id}): Regex sur segment '{text_segment[:20]}...' a trouvé: '{filename}'")

        # 2. Utiliser NER pour potentiellement affiner ou trouver des cas manqués (moins prioritaire ici)
        segment_doc_spacy = self.nlp(text_segment) # type: ignore
        if hasattr(segment_doc_spacy, 'ents'):
            for ent in segment_doc_spacy.ents:
                # Si l'entité elle-même est un nom de fichier complet
                if self.filename_regex.fullmatch(ent.text.strip()):
                    filename = ent.text.strip()
                    if filename not in found_filenames_with_pos: # Ajouter si pas déjà trouvé par regex
                        found_filenames_with_pos[filename] = ent.start_char
                        logger.debug(f"NLUEngine _extract_filenames (ID: {self.instance_id}): NER (match exact) sur segment '{text_segment[:20]}...' a trouvé: '{filename}'")

        # Trier les noms de fichiers trouvés par leur position de début dans le segment
        sorted_filenames = sorted(found_filenames_with_pos.keys(), key=lambda fn: found_filenames_with_pos[fn])
            """TODO: Add docstring."""

        logger.debug(f"NLUEngine _extract_filenames (ID: {self.instance_id}): Candidats uniques pour segment '{text_segment[:30]}...': {sorted_filenames}")
        return sorted_filenames

    def process_input(self, text: str, previous_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Réception: '{text}'")
        if self.nlp is None or self.matcher is None:
            return {"intention": "error_nlu_not_ready", "slots": {}, "texte_original": text, "doc_spacy": None}

        doc = self.nlp(text)
        logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Texte tokenisé ({len(doc)} tokens).")

        matches = self.matcher(doc)
        logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Matcher a trouvé {len(matches)} correspondances.")

        detected_intent_str = "unknown"
        slots: Dict[str, Any] = {}
        document_candidates: List[str] = []

        if matches:
            matches.sort(key=lambda m: m[2] - m[1], reverse=True)
            match_id, start_token_idx, end_token_idx = matches[0]
            detected_intent_str = self.nlp.vocab.strings[match_id]
            matched_segment_text = doc[start_token_idx:end_token_idx].text
            logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Intent Matcher (meilleur): '{detected_intent_str}' pour segment: '{matched_segment_text}'")

            remainder_text = doc[end_token_idx:].text.strip()
            if remainder_text:
                logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Extraction de slot sur reste (après patron): '{remainder_text}'")
                document_candidates = self._extract_filenames_from_text(remainder_text)
        else:
            logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Aucun patron d'intention. Extraction de doc sur texte complet, en segmentant par conjonctions.")
            # Essayer de segmenter par conjonctions pour trouver plusieurs documents
            # Splitter aussi par la virgule, puis nettoyer les segments
            temp_segments = []
            for part in self.conjunction_regex.split(doc.text):
                temp_segments.extend(p.strip() for p in part.split(',') if p.strip())

            segments_to_analyze = [s for s in temp_segments if s]
            logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Segments à analyser après split conj/virgule: {segments_to_analyze}")

            if not segments_to_analyze and doc.text.strip(): # Si aucun split, analyser le texte entier
                segments_to_analyze = [doc.text.strip()]

            for seg in segments_to_analyze:
                document_candidates.extend(self._extract_filenames_from_text(seg))
            # Dédoublonner en gardant l'ordre d'apparition
            seen = set()
            ordered_unique_candidates = []
            for fn in document_candidates:
                if fn not in seen:
                    ordered_unique_candidates.append(fn)
                    seen.add(fn)
            document_candidates = ordered_unique_candidates


        if document_candidates:
            if len(document_candidates) == 1:
                slots["document_nom"] = document_candidates[0]
            else:
                slots["document_nom_candidats"] = document_candidates
                slots["document_nom"] = None
                logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Plusieurs documents candidats trouvés: {document_candidates}")

        intent_needs_doc = detected_intent_str in ["DEMANDE_AUTEUR", "DEMANDE_ENTITES", "DEMANDE_INFO_DOC"]
        is_doc_slot_empty = not slots.get("document_nom") and not slots.get("document_nom_candidats")

        if is_doc_slot_empty and intent_needs_doc:
            if previous_context and previous_context.get("last_mentioned_document"):
                is_possessive = any(token.pos_ == "DET" and token.morph.get("Poss") == ["Yes"] for token in doc)
                is_demonstrative = any(token.lemma_ in ["ce", "cet", "cette"] for token in doc)
                is_pronoun_referring = any(token.lemma_ in ["le", "la", "les", "lui", "en", "y"] and token.dep_ in ["obj", "iobj", "obl"] for token in doc)
                is_short_pronoun_phrase = any(t.tag_ == "PRON" for t in doc) and len(doc) < 4

                if is_possessive or is_demonstrative or is_pronoun_referring or is_short_pronoun_phrase:
                    slots["document_nom"] = previous_context["last_mentioned_document"]
                    logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Coréférence: slot document_nom rempli avec '{slots['document_nom']}'")

        if detected_intent_str == "unknown" and (slots.get("document_nom") or slots.get("document_nom_candidats")):
            detected_intent_str = "DEMANDE_INFO_DOC"
            logger.debug(f"NLUEngine process_input (ID: {self.instance_id}): Doc(s) trouvé(s) sans intent Matcher, fallback sur: {detected_intent_str}")

        final_intent_standardized = detected_intent_str.lower().replace("_", "-")
            """TODO: Add docstring."""

        logger.info(f"NLUEngine process_input (ID: {self.instance_id}): Résultat NLU -> Intention: '{final_intent_standardized}', Slots: {slots}")
            """TODO: Add docstring."""
        return {"intention": final_intent_standardized, "slots": slots, "texte_original": text, "doc_spacy": doc}

class KnowledgeInterface:
    def __init__(self, db_path: Path, db_timeout: int):
        self.db_path = db_path
        self.db_timeout = db_timeout
        self.instance_id = id(self)
        self.base_connaissance_path_str = ""

        base_alma_dir_str = os.getenv("ALMA_BASE_DIR")
        if base_alma_dir_str:
            # S'assurer que PARLEALMA_APP_CONFIG est chargé pour obtenir connaissance_dir_suffix
            if not PARLEALMA_APP_CONFIG or "paths" not in PARLEALMA_APP_CONFIG or \
               "connaissance_dir_suffix" not in PARLEALMA_APP_CONFIG["paths"]:
                load_db_config_for_parlealma() # Assure que la config est chargée

            paths_cfg = PARLEALMA_APP_CONFIG.get("paths", DEFAULT_PATHS_CONFIG_PARLEALMA)
                """TODO: Add docstring."""
            self.base_connaissance_path_str = str(Path(base_alma_dir_str) / paths_cfg["connaissance_dir_suffix"]) + os.sep
        else: # Fallback si ALMA_BASE_DIR n'est pas défini (moins idéal)
            self.base_connaissance_path_str = "Connaissance" + os.sep


        logger.debug(f"KnowledgeInterface __init__ (ID: {self.instance_id}): Initialisée. Base Connaissance: '{self.base_connaissance_path_str}' DB: '{self.db_path}'")

    def _execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        logger.debug(f"KnowledgeInterface _execute_query (ID: {self.instance_id}): Req: '{query[:100]}...' Params: {params}")
        conn = None
        try:
            conn_str = f"file:{self.db_path}?mode=ro&immutable=1"
            conn = sqlite3.connect(conn_str, uri=True, timeout=self.db_timeout)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
                """TODO: Add docstring."""
            logger.debug(f"KnowledgeInterface _execute_query (ID: {self.instance_id}): {len(results)} lignes retournées.")
            return results
        except sqlite3.Error as e:
            logger.error(f"KnowledgeInterface _execute_query (ID: {self.instance_id}): Erreur SQLite: {e}", exc_info=True)
            return []
        finally:
            if conn: conn.close()

    def _get_document_full_path_from_name(self, document_name_fragment: str) -> Optional[str]:
        logger.debug(f"KnowledgeInterface _get_document_full_path_from_name: Recherche pour fragment '{document_name_fragment}'")

        # 1. Tester si le fragment est déjà un chemin absolu existant dans la DB
        query_abs = "SELECT filepath FROM files WHERE filepath = ?"
        results_abs = self._execute_query(query_abs, (document_name_fragment,))
        if results_abs:
            logger.debug(f"KI _get_doc_path: Match exact sur chemin absolu '{document_name_fragment}'")
            return results_abs[0]["filepath"]

        # 2. Tester si c'est un chemin relatif à la base de connaissance
        if self.base_connaissance_path_str:
            potential_full_path = os.path.normpath(os.path.join(self.base_connaissance_path_str, document_name_fragment))
            results_rel_connaissance = self._execute_query(query_abs, (potential_full_path,))
            if results_rel_connaissance:
                logger.debug(f"KI _get_doc_path: Match sur chemin relatif à Connaissance '{potential_full_path}'")
                return results_rel_connaissance[0]["filepath"]

        # 3. Fallback sur LIKE pour les noms de fichiers seuls (plus précis : se terminant par /nom_fichier)
        query_like_suffix = "SELECT filepath FROM files WHERE filepath LIKE ?"
        results_like_suffix = self._execute_query(query_like_suffix, (f"%/{document_name_fragment}",))
        if results_like_suffix:
            if len(results_like_suffix) > 1: logger.warning(f"KI _get_doc_path: Plusieurs fichiers LIKE '%/{document_name_fragment}'. Prise du premier.")
            logger.debug(f"KI _get_doc_path: Match LIKE '%/{document_name_fragment}' -> {results_like_suffix[0]['filepath']}")
            return results_like_suffix[0]["filepath"]

        # 4. Fallback sur LIKE plus large (moins précis)
            """TODO: Add docstring."""
        results_like_broader = self._execute_query(query_like_suffix, (f"%{document_name_fragment}%",))
        if results_like_broader:
            if len(results_like_broader) > 1: logger.warning(f"KI _get_doc_path: Plusieurs fichiers LIKE '%{document_name_fragment}%'. Prise du premier.")
            logger.debug(f"KI _get_doc_path: Match LIKE '%{document_name_fragment}%' -> {results_like_broader[0]['filepath']}")
            return results_like_broader[0]["filepath"]

        logger.debug(f"KnowledgeInterface _get_document_full_path_from_name: Fragment '{document_name_fragment}' non résolu.")
            """TODO: Add docstring."""
        return None

    def get_document_author(self, document_name: str) -> Tuple[Optional[str], bool]:
        exact_filepath = self._get_document_full_path_from_name(document_name)
        if not exact_filepath: return None, False
        query = "SELECT m.meta_value FROM metadata m JOIN files f ON m.file_id = f.id WHERE f.filepath = ? AND m.meta_key = 'author';"
            """TODO: Add docstring."""
        results = self._execute_query(query, (exact_filepath,))
        if results: return results[0]["meta_value"], True
        return None, True

    def get_document_entities(self, document_name: str, limit: int = 10) -> Tuple[Optional[List[Dict[str, Any]]], bool]:
        exact_filepath = self._get_document_full_path_from_name(document_name)
        if not exact_filepath: return None, False
            """TODO: Add docstring."""
        query = "SELECT ne.entity_text, ne.entity_type, COUNT(*) as occurrences FROM named_entities ne JOIN files f ON ne.file_id = f.id WHERE f.filepath = ? GROUP BY LOWER(ne.entity_text), ne.entity_type ORDER BY occurrences DESC, ne.entity_text ASC LIMIT ?;"
        results = self._execute_query(query, (exact_filepath, limit))
        return results if results else [], True

    def get_general_info(self, document_name: str) -> Optional[Dict[str, Any]]:
        exact_filepath = self._get_document_full_path_from_name(document_name)
        if not exact_filepath: return None
        query = "SELECT filepath, checksum, last_processed_utc, size_bytes, encoding FROM files WHERE filepath = ?;"
            """TODO: Add docstring."""
        results = self._execute_query(query, (exact_filepath,))
            """TODO: Add docstring."""
        return results[0] if results else None

class DialogueManager:
    def __init__(self, knowledge_if: KnowledgeInterface):
        self.knowledge_if = knowledge_if
            """TODO: Add docstring."""
        self.session_context: Dict[str, Any] = {
            "last_mentioned_document": None,
            "clarification_pending_for_slot": None,
            "pending_intent_after_clarification": None,
            "clarification_options": []
        }
        self.instance_id = id(self)
        logger.debug(f"DialogueManager __init__ (ID: {self.instance_id}): Initialisé.")

    def _reset_clarification_context(self):
        self.session_context["clarification_pending_for_slot"] = None
        self.session_context["pending_intent_after_clarification"] = None
        self.session_context["clarification_options"] = []
        logger.debug(f"DM Context (ID: {self.instance_id}): Contexte de clarification réinitialisé.")

    def handle_nlu_output(self, nlu_data: Dict[str, Any]) -> Dict[str, Any]:
        intent = nlu_data.get("intention", "unknown")
        slots = nlu_data.get("slots", {})
        texte_original = nlu_data.get("texte_original", "")
        logger.debug(f"DialogueManager handle_nlu_output (ID: {self.instance_id}): NLU -> Intent: '{intent}', Slots: {slots}")

        response_action: Dict[str, Any] = {"action_type": "repondre_texte", "texte_reponse": "Je n'ai pas bien compris. Pouvez-vous reformuler ?"}

        # --- 1. Gestion d'une clarification en attente ---
        is_clarification_handled_this_turn = False
        if self.session_context.get("clarification_pending_for_slot"):
            slot_a_clarifier = self.session_context["clarification_pending_for_slot"]
            clarification_options = self.session_context.get("clarification_options", [])
            pending_intent = self.session_context.get("pending_intent_after_clarification", "demande-info-doc")
            chosen_value_from_clarification: Optional[str] = None

            if texte_original.isdigit() and clarification_options:
                try:
                    choice_idx = int(texte_original) - 1
                    if 0 <= choice_idx < len(clarification_options):
                        chosen_value_from_clarification = clarification_options[choice_idx]
                except ValueError: pass
            elif slots.get("document_nom") and clarification_options and slots["document_nom"] in clarification_options:
                chosen_value_from_clarification = slots["document_nom"]

            if chosen_value_from_clarification:
                logger.debug(f"DM (ID: {self.instance_id}): Clarification reçue pour '{slot_a_clarifier}': '{chosen_value_from_clarification}'")
                slots = {"document_nom": chosen_value_from_clarification}
                intent = pending_intent
                self.session_context["last_mentioned_document"] = chosen_value_from_clarification
                self._reset_clarification_context()
                is_clarification_handled_this_turn = True
                logger.debug(f"DM (ID: {self.instance_id}): Clarification résolue. Reprise intention '{intent}' avec doc: '{chosen_value_from_clarification}'")
            # Si ce n'est pas une réponse directe à la clarification, MAIS que la nouvelle entrée a une intention claire,
            # on abandonne l'ancienne clarification.
            elif intent != "unknown" and intent != "error_nlu_not_ready": # Si la nouvelle entrée a une intention (pas juste "unknown")
                logger.debug(f"DM (ID: {self.instance_id}): Nouvelle intention '{intent}' détectée. Abandon de la clarification précédente pour '{slot_a_clarifier}'.")
                self._reset_clarification_context()
                # Laisser l'intent/slots actuels (de la nouvelle phrase) être traités ci-dessous
            else: # L'utilisateur n'a pas clarifié et n'a pas clairement changé de sujet
                response_action["texte_reponse"] = "Je n'ai pas compris votre choix. Veuillez entrer un numéro ou le nom exact du document parmi les options proposées, ou reformulez votre demande."
                logger.debug(f"DM (ID: {self.instance_id}): Réponse à clarification non comprise, demande de réessayer.")
                return response_action

        # --- 2. Si NLU a retourné plusieurs candidats de documents (et pas en cours de clarification) ---
        document_candidates = slots.get("document_nom_candidats")
        if document_candidates and not is_clarification_handled_this_turn:
            self.session_context["clarification_pending_for_slot"] = "document_nom"
            self.session_context["pending_intent_after_clarification"] = intent if intent not in ["unknown", "error_nlu_not_ready"] else "demande-info-doc"
            self.session_context["clarification_options"] = document_candidates
            response_action = {
                "action_type": "demander_clarification_document",
                "texte_reponse": "J'ai trouvé plusieurs documents qui pourraient correspondre. Lequel vous intéresse ?",
                "document_options": document_candidates
            }
            logger.debug(f"DM Action (ID: {self.instance_id}): Demande clarification pour documents: {document_candidates}")
            return response_action

        # --- 3. Traiter l'intention avec le document_nom (qui est maintenant unique ou None) ---
        doc_name = slots.get("document_nom")
        if doc_name and not self.session_context.get("clarification_pending_for_slot"):
            self.session_context["last_mentioned_document"] = doc_name
            logger.debug(f"DM Context (ID: {self.instance_id}): last_mentioned_document confirmé/MAJ -> '{doc_name}'")

        # --- Logique des Intentions ---
        if intent == "demande-auteur":
            if doc_name:
                author, found = self.knowledge_if.get_document_author(doc_name)
                if found: response_action["texte_reponse"] = f"L'auteur de '{doc_name}' est {author}." if author else f"Je connais le document '{doc_name}', mais son auteur n'est pas spécifié."
                else: response_action["texte_reponse"] = f"Je n'ai pas trouvé d'informations sur un document nommé '{doc_name}'."
            else:
                response_action["texte_reponse"] = "De quel document souhaitez-vous connaître l'auteur ?"
                self.session_context["clarification_pending_for_slot"] = "document_nom"; self.session_context["pending_intent_after_clarification"] = intent
        elif intent == "demande-entites":
            if doc_name:
                entities_dicts, found = self.knowledge_if.get_document_entities(doc_name)
                if found:
                    if entities_dicts: response_action["texte_reponse"] = f"Voici quelques entités pour '{doc_name}': {', '.join([f'{e['entity_text']} ({e['entity_type']})' for e in entities_dicts])}."
                    else: response_action["texte_reponse"] = f"Je connais le document '{doc_name}', mais je n'y ai pas trouvé d'entités notables."
                else: response_action["texte_reponse"] = f"Je n'ai pas trouvé d'informations sur un document nommé '{doc_name}' pour en lister les entités."
            else:
                response_action["texte_reponse"] = "Pour quel document souhaitez-vous lister les entités ?"
                self.session_context["clarification_pending_for_slot"] = "document_nom"; self.session_context["pending_intent_after_clarification"] = intent
        elif intent == "demande-info-doc":
            if doc_name:
                info_dict = self.knowledge_if.get_general_info(doc_name)
                if info_dict:
                    info_parts = [f"Chemin: {info_dict.get('filepath','N/A')}"]
                    if info_dict.get('checksum'): info_parts.append(f"Checksum: {info_dict['checksum'][:16]}...")
                    if info_dict.get('last_processed_utc'): info_parts.append(f"Dernière analyse: {info_dict['last_processed_utc']}")
                    if info_dict.get('size_bytes') is not None: info_parts.append(f"Taille: {info_dict['size_bytes']} octets")
                    response_action["texte_reponse"] = f"Informations pour '{doc_name}': {', '.join(info_parts)}."
                else: response_action["texte_reponse"] = f"Je n'ai pas trouvé d'informations générales pour '{doc_name}'."
            else:
                response_action["texte_reponse"] = "De quel document souhaitez-vous des informations ?"
                self.session_context["clarification_pending_for_slot"] = "document_nom"; self.session_context["pending_intent_after_clarification"] = intent
                    """TODO: Add docstring."""
        elif intent == "small-talk-etat-alma":
            response_action["texte_reponse"] = "Je fonctionne de manière optimale, merci de demander ! Prêt à vous assister."
            if not is_clarification_handled_this_turn: self._reset_clarification_context()
                """TODO: Add docstring."""
        elif intent == "salutation":
            response_action["texte_reponse"] = "Bonjour Toni ! Comment puis-je vous assister aujourd'hui ?"
            if not is_clarification_handled_this_turn: self._reset_clarification_context()
        elif intent == "quitter":
            response_action = {"action_type": "terminer_dialogue", "texte_reponse": "Au revoir Toni !"}
        elif intent == "unknown" and doc_name:
             response_action["texte_reponse"] = f"J'ai noté une référence à '{doc_name}'. Que souhaitez-vous savoir à son sujet ou que puis-je faire ?"
                 """TODO: Add docstring."""

        logger.debug(f"DialogueManager handle_nlu_output (ID: {self.instance_id}): Action finale: {response_action}")
        return response_action

class NLGEngine:
    # ... (inchangé)
    def __init__(self):
        self.instance_id = id(self)
        logger.debug(f"NLGEngine __init__ (ID: {self.instance_id}): Initialisé.")

    def generate_response(self, dm_action: Dict[str, Any]) -> str:
        logger.debug(f"NLGEngine generate_response (ID: {self.instance_id}): Action DM: {dm_action}")
            """TODO: Add docstring."""
        action_type = dm_action.get("action_type", "repondre_texte")
        response_text = dm_action.get("texte_reponse", "Je ne suis pas sûr de savoir comment répondre à cela.")

        if action_type == "terminer_dialogue":
            response_text = dm_action.get("texte_reponse", "Au revoir.")
        elif action_type == "demander_clarification_document":
            options = dm_action.get("document_options", [])
            if options:
                options_text = "\n".join([f"  {i+1}. {doc}" for i, doc in enumerate(options)])
                response_text = f"{dm_action.get('texte_reponse', 'Veuillez préciser parmi les documents suivants :')}\n{options_text}\nEntrez le numéro correspondant ou le nom exact du document."
            else:
                response_text = dm_action.get('texte_reponse', "Je ne suis pas sûr de quel document vous parlez. Pouvez-vous préciser ?")
                    """TODO: Add docstring."""

        logger.debug(f"NLGEngine generate_response (ID: {self.instance_id}): Réponse finale: '{response_text}'")
        return response_text


class ParleALMACLI:
    # ... (inchangé)
    def __init__(self, db_config_path: Optional[str] = None, scenario_file: Optional[str] = None):
        self.scenario_file = scenario_file
        self.instance_id = id(self)
        logger.info(f"ParleALMACLI __init__ (ID Session CLI: {self.instance_id}): Initialisation...")

        load_db_config_for_parlealma()
        kb_path = get_kb_db_path_for_parlealma()
        if not kb_path:
            logger.critical("Impossible de localiser la KnowledgeBase. ParleALMA ne peut pas démarrer.")
            raise FileNotFoundError("KnowledgeBase non trouvée. Vérifiez ALMA_BASE_DIR et la configuration.")
                """TODO: Add docstring."""

        spacy_model_to_use = "fr_core_news_sm"
        try:
            base_alma_dir_str = os.getenv("ALMA_BASE_DIR")
            if base_alma_dir_str and PYYAML_AVAILABLE:
                cerveau_cfg_path = Path(base_alma_dir_str) / PARLEALMA_APP_CONFIG["paths"]["cerveau_dir_suffix"] / "cerveau_config.yaml"
                if cerveau_cfg_path.exists():
                    with open(cerveau_cfg_path, 'r', encoding='utf-8') as f:
                        cfg = yaml.safe_load(f) # type: ignore
                    models_list = cfg.get("nlp", {}).get("spacy_model_names", ["fr_core_news_sm"])
                    if models_list: spacy_model_to_use = models_list[0]
        except Exception as e_cfg_read:
            logger.warning(f"ParleALMACLI: Erreur lecture config spaCy: {e_cfg_read}. Utilisation de '{spacy_model_to_use}'.")

        logger.info(f"ParleALMACLI: Utilisation du modèle spaCy '{spacy_model_to_use}' pour NLUEngine.")
        self.nlu = NLUEngine(spacy_model_name=spacy_model_to_use)
        self.knowledge_if = KnowledgeInterface(kb_path, PARLEALMA_APP_CONFIG["db_timeout_seconds"])
        self.dm = DialogueManager(self.knowledge_if)
        self.nlg = NLGEngine()
        logger.info(f"ParleALMA CLI (ID: {self.instance_id}) initialisée. Mode scénario: {'Activé (' + str(scenario_file) + ')' if scenario_file else 'Désactivé'}")

    def start_dialogue(self):
        print(f"\nBonjour Toni, je suis ALMA Parle (NLU v{self.nlu.spacy_model_name}). Comment puis-je vous assister ? (Tapez 'quitter' pour terminer)")

        if self.scenario_file:
            try:
                with open(self.scenario_file, 'r', encoding='utf-8') as f_scenario:
                    user_inputs = [line.strip() for line in f_scenario if line.strip()]

                for user_input in user_inputs:
                    if user_input.lower() in ["quitter", "exit", "au revoir", "bye"]:
                        print(f"ALMA > Au revoir Toni ! (Fin du scénario)")
                        logger.info(f"ParleALMACLI (ID: {self.instance_id}): Dialogue terminé par scénario.")
                        break

                    print(f"Toni (Scénario)> {user_input}")
                    logger.info(f"ParleALMACLI (ID: {self.instance_id}): Entrée scénario: '{user_input}' (NLU ID: {self.nlu.instance_id})")

                    nlu_result = self.nlu.process_input(user_input, self.dm.session_context)
                    dm_action = self.dm.handle_nlu_output(nlu_result)
                    response = self.nlg.generate_response(dm_action)
                    print(f"ALMA > {response}")
                    logger.info(f"ParleALMACLI (ID: {self.instance_id}): Réponse ALMA: '{response}'")
                    import time; time.sleep(0.5)
            except FileNotFoundError:
                logger.error(f"ParleALMACLI (ID: {self.instance_id}): Fichier scénario '{self.scenario_file}' non trouvé.")
                print(f"ALMA > ERREUR: Fichier scénario '{self.scenario_file}' non trouvé.")
            except Exception as e_scenario:
                logger.error(f"ParleALMACLI (ID: {self.instance_id}): Erreur exécution scénario: {e_scenario}", exc_info=True)
                print(f"ALMA > ERREUR: Problème exécution scénario.")
        else: # Boucle interactive
            while True:
                try:
                    user_input = input("Toni > ").strip()
                    logger.info(f"ParleALMACLI (ID: {self.instance_id}): Entrée utilisateur: '{user_input}' (NLU ID: {self.nlu.instance_id})")
                    if not user_input: continue

                    nlu_result = self.nlu.process_input(user_input, self.dm.session_context)
                    dm_action = self.dm.handle_nlu_output(nlu_result)
                    response_text = self.nlg.generate_response(dm_action)
                    print(f"ALMA > {response_text}")

                    if dm_action.get("action_type") == "terminer_dialogue":
                        logger.info(f"ParleALMACLI (ID: {self.instance_id}): Dialogue terminé par l'utilisateur.")
                        break
                except KeyboardInterrupt:
                    print("\nALMA > Au revoir Toni ! (Interruption clavier)")
                    logger.info(f"ParleALMACLI (ID: {self.instance_id}): Dialogue interrompu par KeyboardInterrupt.")
                    break
                except Exception as e:
                    logger.error(f"ParleALMACLI (ID: {self.instance_id}): Erreur inattendue boucle principale: {e}", exc_info=True)
                    print("ALMA > Oups, j'ai rencontré un problème interne. Veuillez réessayer.")

if __name__ == "__main__":
    if not os.getenv("ALMA_BASE_DIR"):
        script_dir = Path(__file__).resolve().parent
        potential_alma_base_dir = script_dir.parent
        if (potential_alma_base_dir / "Cerveau").exists() and (potential_alma_base_dir / "Connaissance").exists():
            os.environ["ALMA_BASE_DIR"] = str(potential_alma_base_dir)
            logger.info(f"__main__ (ParleALMA): ALMA_BASE_DIR déduit et défini à: {potential_alma_base_dir}")
        else:
            logger.critical("__main__ (ParleALMA): ALMA_BASE_DIR non défini. Veuillez la définir.")
            sys.exit(1)

    parser = argparse.ArgumentParser(description="Interface CLI pour ALMA Parle.")
    parser.add_argument("--scenario", type=str, help="Chemin optionnel vers un fichier scénario.")
    cli_args = parser.parse_args()

    try:
        cli = ParleALMACLI(scenario_file=cli_args.scenario)
        cli.start_dialogue()
    except FileNotFoundError as e_fnf:
        logger.critical(f"__main__ (ParleALMA): Erreur démarrage: {e_fnf}")
        print(f"ALMA > ERREUR CRITIQUE: {e_fnf}. Vérifiez config et KB.")
    except Exception as e_main:
        logger.critical(f"__main__ (ParleALMA): Erreur fatale: {e_main}", exc_info=True)
        print("ALMA > Une erreur fatale est survenue.")