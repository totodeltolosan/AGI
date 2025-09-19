# /home/toni/Documents/ALMA/Cerveau/Core/core.py

"""
---
name: core.py
version: 20.1.6 # Intégration parent_logger, initialisation conditionnelle robuste des modèles
author: Toni & Gemini AI
description: Module Core d'ALMA contenant les algorithmes avancés pour TextImprover et KnowledgeLinker.
role: Fournir des capacités d'amélioration de texte et de liaison de connaissances.
type_execution: library
état: en développement actif
last_update: 2025-05-26 # Refactorisation V20.1.6
dossier: Cerveau/Core
tags: [V20, alma, core, nlp, ai, text_improvement, knowledge_linking, sbert, faiss, transformers, languagetool]
dependencies: [sqlite3, typing, logging, re, json, pathlib] # Dépendances de base
optional_dependencies: [requests, transformers, torch, sentence-transformers, faiss-cpu, numpy, spacy]
---
"""

import logging
import re
import sys
import sqlite3 # Import direct pour type hinting de Connection si KnowledgeBase y fait référence
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
import json # Pour les logs ou détails des propositions

# --- Configuration d'un logger de fallback pour ce module s'il est utilisé en isolation ---
# Ce logger sera utilisé par les classes si aucun parent_logger n'est fourni.
_core_default_logger = logging.getLogger("ALMA.Core.DefaultInternal")
if not _core_default_logger.handlers: # S'assurer de ne pas ajouter de handlers multiples si le module est rechargé
    _ch_core_def = logging.StreamHandler(sys.stdout) # Ou sys.stderr
    # Utiliser un format qui identifie clairement que c'est le logger de fallback de Core
    _formatter_core_def = logging.Formatter(
        '%(asctime)s - CORE_FALLBACK_LOGGER - %(name)s - %(levelname)-8s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    _ch_core_def.setFormatter(_formatter_core_def)
    _core_default_logger.addHandler(_ch_core_def)
    _core_default_logger.setLevel(logging.INFO) # Mettre INFO ou DEBUG selon besoin
    _core_default_logger.debug("Logger de fallback pour Core.py initialisé.")
# --- Fin logger de fallback ---


# --- Imports Conditionnels pour les Dépendances Lourdes ---
# Ces flags et alias seront utilisés dans les classes pour activer/désactiver des fonctionnalités.

REQUESTS_AVAILABLE = False
requests_module_alias = None # Pour stocker le module 'requests' importé
try:
    import requests as requests_imported_module
    requests_module_alias = requests_imported_module
    REQUESTS_AVAILABLE = True
    _core_default_logger.debug("Bibliothèque 'requests' importée avec succès pour Core.py.")
except ImportError:
    _core_default_logger.info("Bibliothèque 'requests' non trouvée. LanguageTool via HTTP sera indisponible.")
    pass
requests = requests_module_alias # Alias global pour le reste du fichier, sera None si non importé

TRANSFORMERS_AVAILABLE = False
TORCH_AVAILABLE = False # Ou TENSORFLOW_AVAILABLE si vous préférez
pipeline_alias = None # Pour stocker la fonction 'pipeline' de transformers
torch_alias = None    # Pour stocker le module 'torch' importé
try:
    from transformers import pipeline as hf_pipeline_imported_alias
    pipeline_alias = hf_pipeline_imported_alias
    import torch as torch_imported_module # Ou import tensorflow as tf_imported_module
    torch_alias = torch_imported_module
    TRANSFORMERS_AVAILABLE = True
    TORCH_AVAILABLE = True # Mettre à True si torch est importé
    _core_default_logger.debug("Bibliothèques 'transformers' et 'torch' (ou TF) importées avec succès pour Core.py.")
except ImportError:
    _core_default_logger.info("Bibliothèques 'transformers' ou 'torch' (ou TF) non trouvées. Fonctionnalités basées sur Transformers (ex: résumé abstractif) seront indisponibles.")
    pass
# 'pipeline' (de Hugging Face) et 'torch' seront utilisés via leurs alias globaux

SENTENCE_TRANSFORMERS_AVAILABLE = False
SentenceTransformer_alias = None # Pour stocker la classe 'SentenceTransformer'
try:
    from sentence_transformers import SentenceTransformer as STransformer_imported_alias
    SentenceTransformer_alias = STransformer_imported_alias
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    _core_default_logger.debug("Bibliothèque 'sentence-transformers' importée avec succès pour Core.py.")
except ImportError:
    _core_default_logger.info("Bibliothèque 'sentence-transformers' non trouvée. Similarité SBERT/FAISS sera indisponible.")
    pass
# SentenceTransformer sera utilisé via l'alias global SentenceTransformer_alias

FAISS_AVAILABLE = False
faiss_alias = None # Pour stocker le module 'faiss' importé
try:
    import faiss as faiss_imported_module
    faiss_alias = faiss_imported_module
    FAISS_AVAILABLE = True
    _core_default_logger.debug("Bibliothèque 'faiss' importée avec succès pour Core.py.")
except ImportError:
    _core_default_logger.info("Bibliothèque 'faiss' non trouvée. Indexation FAISS sera indisponible.")
    pass
faiss = faiss_alias # Alias global

NUMPY_AVAILABLE = False
numpy_alias = None # Pour stocker le module 'numpy' importé
try:
    import numpy as np_imported_module
    numpy_alias = np_imported_module
    NUMPY_AVAILABLE = True
    _core_default_logger.debug("Bibliothèque 'numpy' importée avec succès pour Core.py.")
except ImportError:
    _core_default_logger.info("Bibliothèque 'numpy' non trouvée. Manipulation d'embeddings pour FAISS sera indisponible.")
    pass
np = numpy_alias # Alias global pour utiliser np.array, np.frombuffer, etc.

# Pour le typage, si cerveau.py n'est pas directement importable ici
# Cela évite les imports circulaires à l'exécution mais permet aux outils de type hinting de fonctionner.
if TYPE_CHECKING:
    # Ajustez le chemin relatif si votre structure de dossier est différente
    # et si core.py est dans Cerveau/Core/ et cerveau.py dans Cerveau/
    from ..cerveau import KnowledgeBase # Supposant que cerveau.py et KnowledgeBase sont dans le parent
    import spacy # Pour typer nlp_spacy_instance
    from spacy.tokens import Doc as SpacyDoc # Si vous typez des objets Doc spaCy

# --- Fin Imports Conditionnels ---


# --- Fonctions Utilitaires Spécifiques à Core.py (si nécessaire) ---
# La fonction robust_file_read_core que vous aviez est bien ici.
# Elle est utile si Core.py doit lire des fichiers directement,
# ce qui est le cas pour _find_and_propose_semantic_links_spacy_fallback.
def robust_file_read_core(filepath: Path, logger_instance: logging.Logger) -> Tuple[Optional[str], Optional[str]]:
    """
    Lit un fichier texte en essayant plusieurs encodages courants.
    Utilise le logger fourni.
    """
    common_encodings = ['utf-8', 'latin-1', 'cp1252', sys.getfilesystemencoding()]
    for encoding in common_encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read(), encoding
        except UnicodeDecodeError:
            continue
        except IOError as e:
            # Log plus concis pour les erreurs de lecture de fichier dans le fallback
            logger_instance.debug(f"Erreur I/O (core fallback) en lisant {filepath.name} avec {encoding}: {type(e).__name__}")
            return None, None
        except Exception as e_gen:
            logger_instance.warning(f"Erreur inattendue (core fallback) en lisant {filepath.name} avec {encoding}: {type(e_gen).__name__}", exc_info=False)
            return None, None
    logger_instance.warning(f"Impossible de décoder le fichier (core fallback) {filepath.name} avec les encodages testés.")
    return None, None
# --- Fin Fonctions Utilitaires ---

class TextImprover:
    """
    Fournit des fonctionnalités pour améliorer le contenu textuel,
    comme la correction grammaticale et la génération de résumés.
    """
    def __init__(self,
                 config: Dict[str, Any],
                 kb_instance: Optional['KnowledgeBase'], # Forward reference pour type hinting
                 nlp_spacy_instance: Optional[Any],      # Type: spacy.Language, instance spaCy de cerveau.py
                 parent_logger: Optional[logging.Logger] = None
                ):
        self.config = config
        self.kb = kb_instance
        self.nlp_spacy = nlp_spacy_instance # Instance spaCy partagée, peut être None

        if parent_logger:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        else: # Fallback si aucun logger parent n'est fourni (ex: tests unitaires de Core.py)
            self.logger = logging.getLogger(f"ALMA.Core.{self.__class__.__name__}")
            if not self.logger.handlers: # S'assurer qu'il y a au moins un handler
                _ch_ti_fallback = logging.StreamHandler(sys.stdout)
                _formatter_ti_fallback = logging.Formatter('%(asctime)s - CORE_TI_FALLBACK - %(levelname)-8s - %(message)s')
                _ch_ti_fallback.setFormatter(_formatter_ti_fallback)
                self.logger.addHandler(_ch_ti_fallback)
                self.logger.setLevel(logging.INFO) # Mettre INFO ou DEBUG selon besoin

        self.logger.info(f"Initialisation de TextImprover...")
        # Utiliser json.dumps avec default=str pour éviter les erreurs de sérialisation sur des types complexes
        self.logger.debug(f"Config reçue par TextImprover: {json.dumps(self.config, indent=2, default=str)}")

        # Initialisation LanguageTool
        self.lt_config = self.config.get("language_tool_config", {})
        self.lt_url = self.lt_config.get("url")
        self.lt_language_default = self.lt_config.get("language", "fr-FR")
        self.lt_enabled = self.lt_config.get("enabled", False) and bool(self.lt_url) and REQUESTS_AVAILABLE

        if self.lt_enabled and self.lt_url: # Double vérification que lt_url est non-None/non-vide
            self.logger.info(f"LanguageTool est configuré. URL: {self.lt_url}, Langue par défaut: {self.lt_language_default}")
            # Test de connexion initial
            test_conn_url_lt = self.lt_url.replace("/v2/check", "/v2/languages") if "/v2/check" in self.lt_url else self.lt_url
            try:
                if requests: # Vérifier que l'alias `requests` n'est pas None
                    response = requests.get(test_conn_url_lt, timeout=3)
                    response.raise_for_status()
                    self.logger.info(f"Connexion initiale au serveur LanguageTool ({test_conn_url_lt}) réussie (status {response.status_code}). LT activé.")
                else: # Ne devrait pas arriver si REQUESTS_AVAILABLE est True, mais sécurité
                    self.logger.warning("Module 'requests' non disponible globalement dans Core.py alors que REQUESTS_AVAILABLE=True. Test de connexion LanguageTool sauté. LT désactivé.")
                    self.lt_enabled = False
            except requests.exceptions.RequestException as e_lt_conn_init_core:
                self.logger.warning(f"Impossible de joindre le serveur LanguageTool à {test_conn_url_lt} lors de l'initialisation de TextImprover: {e_lt_conn_init_core}. La correction grammaticale via LT sera désactivée.")
                self.lt_enabled = False # Désactiver si non joignable
        else:
            reasons_lt_disabled = []
            if not self.config.get("language_tool_config", {}).get("enabled", False): reasons_lt_disabled.append("non activé dans la config TextImprover")
            if not self.lt_url: reasons_lt_disabled.append("URL LanguageTool non configurée")
            if not REQUESTS_AVAILABLE: reasons_lt_disabled.append("bibliothèque 'requests' non disponible")
            self.logger.info(f"LanguageTool désactivé pour TextImprover. Raisons: {', '.join(reasons_lt_disabled) or 'configuration/dépendance manquante'}")

        # Initialisation du pipeline de résumé abstractif Transformers
        self.summarizer_pipeline_instance: Optional[Any] = None
        self.abstractive_summary_model_name_cfg = self.config.get("abstractive_summary_model")
        # Recommandation: "facebook/barthez-large-french-summarization" ou "airKlizz/barthez-small-summarization"
        # Si vous voulez que je mette un de ceux-là par défaut si abstractive_summary_model_name_cfg est vide, dites-le moi.

        if self.abstractive_summary_model_name_cfg and TRANSFORMERS_AVAILABLE and TORCH_AVAILABLE and pipeline_alias:
            self.logger.info(f"Tentative de chargement du modèle de résumé abstractif: {self.abstractive_summary_model_name_cfg}...")
            try:
                device_to_use_sum = 0 if torch_alias and hasattr(torch_alias, 'cuda') and torch_alias.cuda.is_available() else -1
                self.summarizer_pipeline_instance = pipeline_alias(
                    "summarization",
                    model=self.abstractive_summary_model_name_cfg,
                    tokenizer=self.abstractive_summary_model_name_cfg,
                    device=device_to_use_sum
                )
                self.logger.info(f"Pipeline de résumé abstractif '{self.abstractive_summary_model_name_cfg}' chargé avec succès sur device {device_to_use_sum} ({'GPU' if device_to_use_sum >=0 else 'CPU'}).")
            except Exception as e_load_summarizer_core:
                self.logger.error(
                    f"Impossible de charger le modèle de résumé abstractif '{self.abstractive_summary_model_name_cfg}': {e_load_summarizer_core}. "
                    "Le résumé abstractif sera désactivé.", exc_info=True # Mettre True pour la stacktrace
                )
                self.summarizer_pipeline_instance = None
        else:
            reasons_sum_disabled = []
            if not self.abstractive_summary_model_name_cfg: reasons_sum_disabled.append("nom de modèle non configuré")
            if not TRANSFORMERS_AVAILABLE: reasons_sum_disabled.append("bibliothèque 'transformers' non disponible")
            if not TORCH_AVAILABLE: reasons_sum_disabled.append("bibliothèque 'torch' (ou TF) non disponible")
            if not pipeline_alias: reasons_sum_disabled.append("'pipeline' de transformers non importable")
            self.logger.info(f"Résumé abstractif désactivé pour TextImprover. Raisons: {', '.join(reasons_sum_disabled) or 'dépendance/configuration manquante'}")

        self.default_language = self.config.get("default_language", "fr")
        self.summary_ratio_extractive = float(self.config.get("summary_ratio", 0.15)) # Pour le fallback extractif
        self.logger.info(f"TextImprover finalisé. Langue par défaut: {self.default_language}, Ratio résumé (extractif fallback): {self.summary_ratio_extractive}")

    def correct_grammar_typography(self, text_content: str, language: Optional[str] = None) -> Tuple[str, List[str]]:
        """
        Corrige la grammaire et la typographie d'un texte.
        Utilise LanguageTool si configuré et disponible, sinon des regex basiques.
        """
        logs: List[str] = []
        corrected_text = text_content
        # Utiliser la langue spécifiée, sinon la langue par défaut de LT, sinon la langue par défaut de TextImprover
        lang_to_use_lt = language or self.lt_language_default
        lang_to_use_fallback_regex = language or self.default_language


        if self.lt_enabled and self.lt_url and requests: # Vérifier l'état activé
            self.logger.debug(f"Appel à LanguageTool ({self.lt_url}) pour langue '{lang_to_use_lt}'...")
            try:
                response = requests.post(self.lt_url, data={'language': lang_to_use_lt, 'text': text_content}, timeout=15)
                response.raise_for_status()
                results = response.json()
                matches = results.get('matches', [])

                offset_correction = 0
                num_corrections_applied = 0
                for match in sorted(matches, key=lambda m: m['offset']): # Trier par offset
                    offset = match['offset'] + offset_correction
                    length = match['length']

                    suitable_replacement = ""
                    if match.get('replacements') and match['replacements'][0].get('value'):
                        suitable_replacement = match['replacements'][0]['value']

                    # Appliquer seulement si la suggestion est différente et pas trop disruptive
                    if suitable_replacement and corrected_text[offset : offset + length] != suitable_replacement and len(suitable_replacement) <= length + 30:
                        original_segment = corrected_text[offset : offset + length]
                        corrected_text = corrected_text[:offset] + suitable_replacement + corrected_text[offset + length:]
                        offset_correction += len(suitable_replacement) - length

                        log_msg_lt = f"LT (Règle: {match.get('rule',{}).get('id','N/A')}, Pos {match['offset']}): '{original_segment}' -> '{suitable_replacement}' ({match.get('shortMessage','N/A')})"
                        self.logger.debug(log_msg_lt)
                        logs.append(log_msg_lt)
                        num_corrections_applied +=1
                    elif match.get('replacements') and match['replacements'][0].get('value'):
                        logs.append(f"LT Suggestion (Règle: {match.get('rule',{}).get('id','N/A')}, Pos {match['offset']}): Remplacement jugé trop long/identique ignoré ('{match['replacements'][0]['value']}' pour '{corrected_text[offset : offset + length]}')")

                if num_corrections_applied > 0:
                    logs.insert(0, f"LanguageTool a appliqué {num_corrections_applied} correction(s) pour la langue '{lang_to_use_lt}'.")
                else:
                    logs.append(f"LanguageTool n'a appliqué aucune correction pour la langue '{lang_to_use_lt}'.")
                self.logger.audit(f"LanguageTool: {len(matches)} erreurs détectées, {num_corrections_applied} corrections appliquées pour langue '{lang_to_use_lt}'.")
                return corrected_text.strip(), logs # Retourner le texte corrigé par LT

            except requests.exceptions.Timeout:
                logs.append("Erreur: Timeout lors de la connexion à LanguageTool. Fallback sur correction basique.")
                self.logger.error("Timeout lors de l'appel à LanguageTool.")
            except requests.exceptions.RequestException as e_req_lt:
                logs.append(f"Erreur connexion LanguageTool: {type(e_req_lt).__name__}. Fallback sur correction basique.")
                self.logger.error(f"Erreur de requête vers LanguageTool: {e_req_lt}", exc_info=False)
            except json.JSONDecodeError:
                logs.append("Erreur: Réponse LanguageTool non JSON. Fallback sur correction basique.")
                self.logger.error("Réponse de LanguageTool n'était pas un JSON valide.")
            except Exception as e_lt_generic:
                logs.append(f"Erreur LanguageTool: {type(e_lt_generic).__name__}. Fallback sur correction basique.")
                self.logger.error(f"Erreur inattendue avec LanguageTool: {e_lt_generic}", exc_info=True)

        # Si LT n'est pas activé ou a échoué, on passe au fallback regex
        self.logger.debug(f"Application de la correction basique grammaire/typo (regex) pour langue '{lang_to_use_fallback_regex}'.")
        current_text_fallback = text_content # Commencer avec le texte original pour le fallback
        fallback_corrections_log: List[str] = []

        # 1. Normaliser les espaces multiples (sauf sauts de ligne)
        text_after_spaces = re.sub(r'[ \t]+', ' ', current_text_fallback)
        if text_after_spaces != current_text_fallback:
            fallback_corrections_log.append("Regex: Espaces multiples normalisés.")
        current_text_fallback = text_after_spaces

        # 2. Gérer les espaces autour de la ponctuation française courante (si langue fr)
        if lang_to_use_fallback_regex.startswith("fr"):
            text_before_punct = current_text_fallback
            # Pas d'espace avant , .
            current_text_fallback = re.sub(r'\s*([,.])', r'\1', current_text_fallback)
            # Un espace après , . (sauf si suivi d'une autre ponctuation ou fin de ligne)
            current_text_fallback = re.sub(r'([,.])(?=[^\s,.?!])', r'\1 ', current_text_fallback)
            # Espace insécable avant ; ? ! »
            current_text_fallback = re.sub(r'\s*([;:?!»])', r'\u00A0\1', current_text_fallback)
            # Un espace après ; ? ! (sauf si suivi d'une autre ponctuation ou fin de ligne)
            current_text_fallback = re.sub(r'([;:?!])(?=[^\s,.?!])', r'\1 ', current_text_fallback)
            # Espace insécable après «
            current_text_fallback = re.sub(r'(«)\s*', r'\1\u00A0', current_text_fallback)
            # Nettoyer les doubles espaces potentiels introduits
            current_text_fallback = re.sub(r'\s{2,}', ' ', current_text_fallback)
            if current_text_fallback.strip() != text_before_punct.strip():
                fallback_corrections_log.append("Regex: Espaces de ponctuation française ajustés.")

        # 3. Capitalisation des débuts de phrases
        text_before_caps = current_text_fallback
        # Regex plus robuste pour capturer les phrases, en gardant les délimiteurs pour la reconstruction
        # Elle essaie de gérer les sauts de ligne et les espaces multiples après la ponctuation.
        phrases_avec_delimiteurs = re.split(r'([.?!]\s*|\n\s*\n)', current_text_fallback)
        reconstructed_text_parts = []
        for i, part in enumerate(phrases_avec_delimiteurs):
            stripped_part = part.strip()
            if stripped_part: # Si c'est un segment de phrase
                if not reconstructed_text_parts or (reconstructed_text_parts[-1].strip().endswith(('.', '!', '?'))):
                    # Si c'est la première phrase ou si la précédente se terminait par une ponctuation forte
                    reconstructed_text_parts.append(stripped_part[0].upper() + stripped_part[1:])
                else:
                    reconstructed_text_parts.append(stripped_part) # Garder la casse (ex: après une virgule dans la phrase précédente)
            elif part: # Si c'est un délimiteur (espace, saut de ligne)
                reconstructed_text_parts.append(part) # Conserver les délimiteurs pour la structure

        current_text_fallback = "".join(reconstructed_text_parts)
        if current_text_fallback.strip() != text_before_caps.strip():
             fallback_corrections_log.append("Regex: Capitalisation initiale des phrases appliquée.")

        final_text_fallback = current_text_fallback.strip()
        if not fallback_corrections_log:
            fallback_corrections_log.append("Aucune correction grammaire/typo de base appliquée par regex.")

        # Combiner les logs si LT a été tenté et a échoué
        final_logs = logs + fallback_corrections_log if logs else fallback_corrections_log
        self.logger.audit(f"Corrections (fallback regex ou post-LT échec) appliquées. Log: {'; '.join(final_logs)}")
        return final_text_fallback, final_logs

    def generate_summary(self, text_content: str, language: Optional[str] = None) -> Tuple[str, List[str]]:
        """Génère un résumé du texte. Priorise le résumé abstractif si disponible."""
        logs: List[str] = []
        summary_text = ""
        lang_to_use_fallback_spacy = language or self.default_language

        if not text_content.strip():
            logs.append("Contenu vide, impossible de générer un résumé.")
            self.logger.warning("Tentative de résumé sur contenu vide.")
            return "", logs

        # 1. Tentative de résumé abstractif avec Transformers
        if self.summarizer_pipeline_instance:
            self.logger.debug(f"Tentative de résumé abstractif avec le modèle '{getattr(self.summarizer_pipeline_instance.model.config, '_name_or_path', 'Inconnu')}'.")
            try:
                word_count = len(text_content.split())
                # Ajuster min/max length pour être plus flexible et éviter les erreurs de pipeline
                # Pour barthez-large-french-summarization, min_length doit être > 2 pour certains textes.
                # Et max_length ne doit pas être trop petite par rapport à min_length.
                min_len_summary = max(25, int(word_count * 0.05)) # Au moins 25 mots, ou 5%
                max_len_summary = max(50, int(word_count * 0.25)) # Au moins 50 mots, ou 25%

                # Le pipeline gère la troncature du texte d'entrée si > model_max_length
                # Pour barthez-large-french-summarization, c'est 1024 tokens.
                # On peut limiter la longueur du texte d'entrée pour éviter des traitements trop longs
                # si le texte est massivement plus grand que ce que le modèle peut gérer efficacement.
                # Ex: si texte > 3*model_max_length, on pourrait le tronquer. Pour l'instant, on laisse le pipeline gérer.

                # Assurer que min_length < max_length et que max_length n'est pas trop grande pour le modèle
                # (Bien que le pipeline le gère, on peut être proactif)
                # La plupart des modèles de résumé ont une limite de sortie autour de 150-512 tokens.
                if hasattr(self.summarizer_pipeline_instance.model.config, 'max_position_embeddings'):
                     model_output_limit = self.summarizer_pipeline_instance.model.config.max_position_embeddings // 2 # Heuristique
                     max_len_summary = min(max_len_summary, model_output_limit - 5) # Garder une marge
                else: # Fallback si on ne peut pas lire la limite du modèle
                     max_len_summary = min(max_len_summary, 400)


                if min_len_summary >= max_len_summary:
                    min_len_summary = max(25, max_len_summary // 2)
                    if min_len_summary >= max_len_summary and max_len_summary > 25 : min_len_summary = max_len_summary -1 # Assurer min < max
                    elif min_len_summary >= max_len_summary : # Si max_len_summary est trop petit
                         min_len_summary = 10; max_len_summary = 25 # Valeurs minimales absolues


                self.logger.debug(f"Paramètres résumé abstractif: min_length={min_len_summary}, max_length={max_len_summary}")

                summary_result_list = self.summarizer_pipeline_instance(
                    text_content,
                    min_length=min_len_summary,
                    max_length=max_len_summary,
                    truncation=True, # Important pour les textes longs
                    # num_beams=4, # Peut améliorer la qualité mais plus lent
                    # early_stopping=True
                )
                if summary_result_list and isinstance(summary_result_list, list) and summary_result_list[0].get('summary_text'):
                    summary_text = summary_result_list[0]['summary_text'].strip()
                    logs.append(f"Résumé abstractif généré par Transformers ({len(summary_text.split())} mots).")
                    self.logger.audit(f"Résumé abstractif généré (modèle: {getattr(self.summarizer_pipeline_instance.model.config, '_name_or_path', 'Inconnu')}).")
                    return summary_text, logs # Succès, on retourne
                else:
                    logs.append("Le pipeline de résumé Transformers n'a pas retourné de texte de résumé valide.")
                    self.logger.warning("Pipeline de résumé Transformers n'a pas retourné de texte valide.")
            except Exception as e_summarize_tf:
                logs.append(f"Erreur lors de la génération du résumé abstractif: {type(e_summarize_tf).__name__}. Fallback.")
                self.logger.error(f"Erreur du pipeline de résumé Transformers: {e_summarize_tf}", exc_info=True)
                summary_text = "" # Forcer la chaîne vide pour passer au fallback

        # 2. Fallback sur résumé extractif
        self.logger.info("Résumé abstractif non disponible ou échoué. Utilisation du fallback extractif.")
        logs.append("Fallback sur résumé extractif.")
        sentences: List[str] = []

        if self.nlp_spacy: # Utiliser l'instance spaCy partagée si disponible
            try:
                # Vérifier si un pipe de segmentation est présent ou peut être ajouté
                can_sentencize = False
                if self.nlp_spacy.has_pipe("parser") or self.nlp_spacy.has_pipe("sentencizer"):
                    can_sentencize = True
                elif "sentencizer" not in self.nlp_spacy.pipe_names: # Tenter de l'ajouter s'il manque et pas de parser
                    try:
                        self.nlp_spacy.add_pipe("sentencizer", first=True)
                        self.logger.info("Pipe 'sentencizer' ajouté dynamiquement à l'instance spaCy partagée pour le résumé.")
                        can_sentencize = True
                    except ValueError as e_pipe_val:
                         self.logger.debug(f"Impossible d'ajouter 'sentencizer' à spaCy (ValueError): {e_pipe_val}.")
                    except Exception as e_pipe:
                         self.logger.warning(f"Impossible d'ajouter 'sentencizer' à spaCy: {e_pipe}. Fallback sur regex pour segmentation.")

                if can_sentencize:
                    # Limiter la longueur du texte passé à spaCy pour éviter les OOM sur des textes immenses
                    # même si le modèle de résumé n'est pas utilisé.
                    # Une limite de 1M caractères est déjà dans cerveau.py pour le nlp_instance principal.
                    # Ici, on pourrait être plus conservateur si on est en fallback.
                    max_len_for_spacy_fallback = 500000 # Ex: 500k caractères pour le fallback
                    doc = self.nlp_spacy(text_content[:max_len_for_spacy_fallback])
                    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
                    logs.append(f"Segmentation en phrases via spaCy ({len(sentences)} phrases trouvées).")
                else: # Si on ne peut pas sentencizer avec spaCy
                    self.logger.warning("Aucun pipe de segmentation spaCy ('parser' ou 'sentencizer') disponible. Fallback sur regex.")
                    sentences = [] # Forcer le passage au regex
            except Exception as e_spacy_sum:
                self.logger.warning(f"Erreur lors de la segmentation spaCy pour résumé extractif: {e_spacy_sum}. Fallback sur regex.", exc_info=False)
                sentences = []

        if not sentences: # Si spaCy a échoué ou n'est pas dispo/configuré
            sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+', text_content.strip()) if s.strip()]
            logs.append(f"Segmentation en phrases via regex ({len(sentences)} phrases trouvées).")

        if not sentences:
            logs.append("Aucune phrase trouvée pour le résumé extractif.")
            self.logger.warning("Impossible de segmenter en phrases pour le résumé extractif.")
            # Fallback ultime: prendre le début du texte
            summary_text_fallback = text_content[:max(200, int(len(text_content)*0.05))] # 5% ou 200 chars
            logs.append("Utilisation d'un extrait du début du texte comme résumé extractif (fallback ultime).")
            return summary_text_fallback.strip(), logs

        num_sentences_total = len(sentences)
        num_sentences_in_summary = max(1, int(num_sentences_total * self.summary_ratio_extractive))
        num_sentences_in_summary = min(num_sentences_in_summary, num_sentences_total)

        if num_sentences_total <= 2 or num_sentences_total <= num_sentences_in_summary + 1: # Si très peu de phrases ou ratio proche de 100%
            summary_text_final = " ".join(sentences)
            logs.append(f"Texte court ({num_sentences_total} phrases), utilisé en intégralité ou presque comme résumé extractif.")
        else:
            summary_sentences_final = sentences[:num_sentences_in_summary]
            summary_text_final = " ".join(summary_sentences_final)
            logs.append(f"Résumé extractif (premières {len(summary_sentences_final)} phrases sur {num_sentences_total}) généré.")

        self.logger.audit(f"Résumé extractif (fallback) généré. Log: {'; '.join(logs)}")
        return summary_text_final.strip(), logs

    def restructure_content(self, text_content: str, current_format: str, target_format: str) -> Tuple[str, List[str]]:
        """
        Tente de restructurer le contenu d'un format à un autre.
        Actuellement très basique : TXT vers Markdown (listes, paragraphes).
        """
        self.logger.debug(f"Tentative de restructuration de '{current_format}' vers '{target_format}'.")
        logs: List[str] = []
        restructured_text = text_content # Commencer avec le texte original

        if current_format.lower() == "txt" and target_format.lower() == "markdown_basic":
            self.logger.debug("Restructuration TXT vers Markdown basique...")
            lines = text_content.splitlines()
            md_lines: List[str] = []
            in_list_simple_marker: Optional[str] = None # Peut être '*' ou '-' ou 'numbered'

            for line_idx, line in enumerate(lines):
                stripped_line = line.strip()

                # Détection de listes simples (commençant par '*' ou '-' ou '1.')
                list_match_star = re.match(r'^(\s*)\*\s+(.*)', line)
                list_match_dash = re.match(r'^(\s*)-\s+(.*)', line)
                # Regex plus robuste pour les listes numérotées, capturant le numéro et le point
                numbered_list_match = re.match(r'^(\s*)(\d+)\.\s+(.*)', line)

                current_list_item_marker_used_this_line = None
                item_text = ""
                indent_str = ""

                if list_match_star:
                    current_list_item_marker_used_this_line = "*"
                    indent_str, item_text = list_match_star.groups()
                elif list_match_dash:
                    current_list_item_marker_used_this_line = "-"
                    indent_str, item_text = list_match_dash.groups()
                elif numbered_list_match:
                    current_list_item_marker_used_this_line = "numbered" # Type spécial
                    indent_str, num_part, item_text_num = numbered_list_match.groups()
                    item_text = item_text_num.strip()
                    # Reconstituer l'item de liste numérotée avec son indentation
                    md_lines.append(f"{indent_str}{num_part}. {item_text}")
                    # Si on entre dans une liste numérotée et qu'on n'était pas dans une liste
                    if not in_list_simple_marker:
                        if md_lines and len(md_lines) > 1 and md_lines[-2].strip() != "": # Vérifier md_lines[-2] pour éviter double saut de ligne
                            md_lines.insert(-1, "") # Ajouter une ligne vide avant la liste si nécessaire
                    in_list_simple_marker = "numbered" # Mettre à jour l'état de la liste
                    continue # On a déjà traité et ajouté la ligne numérotée

                # Traitement pour les listes * et -
                if current_list_item_marker_used_this_line in ["*", "-"]:
                    # Si on n'était pas dans une liste (ou un type différent de liste), ajouter un saut de ligne avant
                    if not in_list_simple_marker or in_list_simple_marker != current_list_item_marker_used_this_line :
                        if md_lines and md_lines[-1].strip() != "":
                            md_lines.append("")
                    in_list_simple_marker = current_list_item_marker_used_this_line
                    md_lines.append(f"{indent_str}{current_list_item_marker_used_this_line} {item_text.strip()}")
                else: # Ligne non-liste
                    if in_list_simple_marker: # Si on sort d'une liste
                        md_lines.append("") # Ajouter un saut de ligne après la liste
                    in_list_simple_marker = None # Réinitialiser l'état de la liste

                    if not stripped_line: # Ligne vide
                        # Ajouter une ligne vide seulement si la précédente n'était pas déjà vide (pour éviter les sauts multiples)
                        if not md_lines or md_lines[-1].strip() != "":
                            md_lines.append("")
                    else: # Ligne de texte normale (paragraphe)
                        md_lines.append(line) # Conserver l'indentation originale pour les paragraphes

            restructured_text = "\n".join(md_lines).strip()
            # Normaliser les sauts de ligne multiples (plus de 2 consécutifs -> 2)
            restructured_text = re.sub(r'\n{3,}', '\n\n', restructured_text)

            if restructured_text != text_content.strip(): # Comparer après strip pour être sûr
                logs.append(f"Contenu restructuré de TXT vers Markdown basique (listes, paragraphes).")
                self.logger.audit(f"Restructuration TXT -> Markdown basique appliquée.")
                return restructured_text, logs
            else:
                logs.append("Aucune restructuration TXT -> Markdown basique significative appliquée (contenu déjà similaire ou non géré).")
                return text_content.strip(), logs # Retourner le texte original strippé

        logs.append(f"Restructuration de '{current_format}' vers '{target_format}' non supportée ou non nécessaire.")
        return text_content.strip(), logs # Retourner le texte original strippé

# DANS Cerveau/Core/core.py
# (Assurez-vous que les imports conditionnels et les alias en haut du fichier sont corrects)
# ... (imports SENTENCE_TRANSFORMERS_AVAILABLE, SentenceTransformer_alias, FAISS_AVAILABLE, faiss_alias, NUMPY_AVAILABLE, numpy_alias, etc.)

class KnowledgeLinker:
    """
    Analyse les données pour trouver des liens sémantiques et des incohérences.
    Utilise SBERT/FAISS pour la similarité si disponible, sinon fallback sur spaCy.
    """
    def __init__(self,
                 config: Dict[str, Any],
                 kb_instance: Optional['KnowledgeBase'], # Forward reference pour type hinting
                 nlp_spacy_instance: Optional[Any],      # Type: spacy.Language, instance spaCy de cerveau.py
                 parent_logger: Optional[logging.Logger] = None
                ):
        self.config = config
        self.kb = kb_instance       # Peut être None si la DB est désactivée dans cerveau.py
        self.nlp_spacy = nlp_spacy_instance # Instance spaCy partagée de cerveau.KnowledgeBase, peut être None

        if parent_logger:
            self.logger = parent_logger.getChild(self.__class__.__name__)
        else: # Fallback si aucun logger parent n'est fourni
            self.logger = logging.getLogger(f"ALMA.Core.{self.__class__.__name__}")
            if not self.logger.handlers:
                _ch_kl_fallback = logging.StreamHandler(sys.stdout)
                _formatter_kl_fallback = logging.Formatter('%(asctime)s - CORE_KL_FALLBACK - %(levelname)-8s - %(message)s')
                _ch_kl_fallback.setFormatter(_formatter_kl_fallback)
                self.logger.addHandler(_ch_kl_fallback)
                self.logger.setLevel(logging.INFO)

        self.logger.info(f"Initialisation de KnowledgeLinker...")
        self.logger.debug(f"Config reçue par KnowledgeLinker: {json.dumps(self.config, indent=2, default=str)}")

        # Initialisation SBERT (Sentence-Transformers)
        self.sbert_model_name_cfg = self.config.get("sentence_transformer_model")
        self.sbert_model: Optional[Any] = None # Stocker le modèle SBERT chargé (sera de type SentenceTransformer)

        if self.sbert_model_name_cfg and SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer_alias:
            self.logger.info(f"Tentative de chargement du modèle SentenceTransformer: {self.sbert_model_name_cfg}...")
            try:
                self.sbert_model = SentenceTransformer_alias(self.sbert_model_name_cfg)
                self.logger.info(f"Modèle SentenceTransformer '{self.sbert_model_name_cfg}' chargé avec succès.")
            except Exception as e_load_sbert_core:
                self.logger.error(
                    f"Impossible de charger le modèle SentenceTransformer '{self.sbert_model_name_cfg}': {e_load_sbert_core}. "
                    "La similarité sémantique basée sur SBERT/FAISS sera désactivée.", exc_info=True
                )
                self.sbert_model = None
        else:
            reasons_sbert_disabled = []
            if not self.sbert_model_name_cfg: reasons_sbert_disabled.append("nom de modèle non configuré")
            if not SENTENCE_TRANSFORMERS_AVAILABLE: reasons_sbert_disabled.append("bibliothèque 'sentence-transformers' non disponible")
            if not SentenceTransformer_alias: reasons_sbert_disabled.append("'SentenceTransformer' (classe) non importable")
            self.logger.info(f"Modèle SBERT non chargé pour KnowledgeLinker. Raisons: {', '.join(reasons_sbert_disabled) or 'dépendance/configuration manquante'}")

        # Initialisation FAISS (si SBERT, FAISS, et Numpy sont disponibles)
        self.faiss_index: Optional[Any] = None # Sera de type faiss.Index
        self.doc_id_to_faiss_idx: Dict[int, int] = {} # Mapping file_id (KB) -> index FAISS (0 à N-1)
        self.faiss_idx_to_doc_id: List[int] = []      # Mapping index FAISS (0 à N-1) -> file_id (KB)

        if self.sbert_model and FAISS_AVAILABLE and faiss and NUMPY_AVAILABLE and np: # Vérifier les alias
            try:
                embedding_dim = self.sbert_model.get_sentence_embedding_dimension()
                if embedding_dim and isinstance(embedding_dim, int) and embedding_dim > 0:
                    self.faiss_index = faiss.IndexFlatIP(embedding_dim) # IP pour Inner Product
                    self.logger.info(f"Index FAISS (dim: {embedding_dim}, type: IndexFlatIP) initialisé et prêt à être peuplé.")
                else:
                    self.logger.error(f"Dimension d'embedding SBERT invalide ou nulle ({embedding_dim}). Index FAISS non créé.")
                    self.faiss_index = None
            except AttributeError: # Si get_sentence_embedding_dimension n'existe pas
                self.logger.error("Le modèle SBERT chargé ne semble pas avoir la méthode 'get_sentence_embedding_dimension'. Index FAISS non créé.")
                self.faiss_index = None
            except Exception as e_faiss_init_core:
                self.logger.error(f"Erreur lors de l'initialisation de l'index FAISS: {e_faiss_init_core}", exc_info=True)
                self.faiss_index = None
        else:
            if self.sbert_model: # Si SBERT est là mais pas FAISS/Numpy
                reasons_faiss_disabled = []
                if not FAISS_AVAILABLE: reasons_faiss_disabled.append("'faiss' non disponible")
                if not NUMPY_AVAILABLE: reasons_faiss_disabled.append("'numpy' non disponible")
                if not faiss and FAISS_AVAILABLE: reasons_faiss_disabled.append("alias 'faiss' non défini") # Sécurité
                if not np and NUMPY_AVAILABLE: reasons_faiss_disabled.append("alias 'np' non défini") # Sécurité
                self.logger.info(f"Index FAISS non initialisé pour KnowledgeLinker. Raisons: {', '.join(reasons_faiss_disabled) or 'SBERT non chargé mais autre dépendance manquante'}")
            # Si sbert_model est None, le log a déjà été fait.

        self.min_similarity_for_link = float(self.config.get("min_similarity_for_link", 0.8))
        self.num_semantic_links_to_propose = int(self.config.get("num_semantic_links_to_propose", 5))
        self.logger.info(f"KnowledgeLinker finalisé. Seuil similarité: {self.min_similarity_for_link}, Nb liens à proposer: {self.num_semantic_links_to_propose}")

    def populate_faiss_index_from_kb(self, db_conn: sqlite3.Connection):
        """
        Peuple l'index FAISS en mémoire avec les embeddings stockés dans la KnowledgeBase.
        Cette méthode est typiquement appelée une fois au démarrage de CerveauService.
        """
        if not self.kb:
            self.logger.error("POPULATE_FAISS: Instance KnowledgeBase (self.kb) non disponible.")
            return
        if not self.faiss_index:
            self.logger.warning("POPULATE_FAISS: Index FAISS (self.faiss_index) non initialisé. Impossible de peupler.")
            return
        if not (NUMPY_AVAILABLE and np): # Vérifier que numpy est bien disponible via son alias
            self.logger.error("POPULATE_FAISS: Numpy (np) non disponible. Impossible de manipuler les embeddings pour FAISS.")
            return
        if not self.sbert_model : # Besoin de sbert_model pour la dimension
            self.logger.error("POPULATE_FAISS: Modèle SBERT (self.sbert_model) non disponible. Impossible de valider la dimension des embeddings.")
            return


        self.logger.info("POPULATE_FAISS: Début du peuplement de l'index FAISS depuis la KB...")
        self.faiss_index.reset() # type: ignore # Vider l'index existant
        self.doc_id_to_faiss_idx.clear()
        self.faiss_idx_to_doc_id.clear() # Utiliser une liste simple

        try:
            # get_all_document_embeddings retourne List[Tuple[file_id: int, embedding_blob: Optional[bytes]]]
            all_embeddings_data = self.kb.get_all_document_embeddings(db_conn)
            if not all_embeddings_data:
                self.logger.info("POPULATE_FAISS: Aucune donnée d'embedding retournée par la KB.")
                return

            embeddings_to_add_list: List[np.ndarray] = [] # type: ignore
            file_ids_for_faiss_mapping: List[int] = []

            expected_dim = self.sbert_model.get_sentence_embedding_dimension()

            for file_id, embedding_blob in all_embeddings_data:
                if embedding_blob and isinstance(embedding_blob, bytes) and len(embedding_blob) > 0:
                    try:
                        embedding_np_arr = np.frombuffer(embedding_blob, dtype=np.float32)
                        if embedding_np_arr.shape[0] == expected_dim:
                            # La normalisation L2 est cruciale pour IndexFlatIP et doit être faite
                            # soit ici, soit au moment de la génération de l'embedding.
                            # Supposons qu'elle a été faite dans ComprehensionStep avant stockage.
                            # Si ce n'est pas le cas, il faut la faire ici :
                            # norm = np.linalg.norm(embedding_np_arr)
                            # if norm > 0: embedding_np_arr = embedding_np_arr / norm
                            # else: self.logger.warning(f"POPULATE_FAISS: Embedding pour file_id {file_id} a une norme nulle. Ignoré."); continue
                            embeddings_to_add_list.append(embedding_np_arr)
                            file_ids_for_faiss_mapping.append(file_id)
                        else:
                            self.logger.warning(f"POPULATE_FAISS: Embedding pour file_id {file_id} (shape: {embedding_np_arr.shape}) a une dimension incorrecte (attendu: {expected_dim}). Ignoré.")
                    except Exception as e_conv_pop:
                        self.logger.error(f"POPULATE_FAISS: Erreur de conversion d'embedding pour file_id {file_id}: {e_conv_pop}. Ignoré.", exc_info=False)
                else:
                    self.logger.debug(f"POPULATE_FAISS: Embedding blob manquant ou invalide pour file_id {file_id}. Ignoré.")

            if embeddings_to_add_list:
                embeddings_matrix = np.vstack(embeddings_to_add_list).astype('float32')
                self.faiss_index.add(embeddings_matrix) # type: ignore

                # Construire les mappings
                # L'index FAISS est 0-based et correspond à l'ordre d'ajout.
                self.faiss_idx_to_doc_id = file_ids_for_faiss_mapping
                for faiss_i, kb_file_id in enumerate(file_ids_for_faiss_mapping):
                    self.doc_id_to_faiss_idx[kb_file_id] = faiss_i

                self.logger.info(f"POPULATE_FAISS: Index FAISS peuplé avec {self.faiss_index.ntotal} embeddings de documents. Mappings créés.") # type: ignore
            else:
                self.logger.info("POPULATE_FAISS: Aucun embedding de document valide trouvé dans la KB pour peupler l'index FAISS.")

        except sqlite3.Error as e_sql_pop:
            self.logger.error(f"POPULATE_FAISS: Erreur SQLite lors du peuplement de l'index FAISS: {e_sql_pop}", exc_info=True)
        except AttributeError as e_attr_pop: # Ex: si self.kb est None
            self.logger.error(f"POPULATE_FAISS: Erreur d'attribut (self.kb est-il initialisé?): {e_attr_pop}", exc_info=True)
        except Exception as e_gen_pop:
            self.logger.error(f"POPULATE_FAISS: Erreur générale lors du peuplement de l'index FAISS: {e_gen_pop}", exc_info=True)

    def find_and_propose_semantic_links(self, analysed_data_current_file: Dict[str, Any], db_conn_worker: sqlite3.Connection) -> List[Dict[str, Any]]:
        """
        Trouve des documents sémantiquement similaires en utilisant FAISS si disponible,
        sinon fallback sur la similarité spaCy.
        """
        proposals: List[Dict[str, Any]] = []
        current_file_path_str = analysed_data_current_file.get("filepath_str")
        current_file_id = analysed_data_current_file.get("kb_file_id") # ID du fichier dans la table 'files'
        current_file_embedding_blob = analysed_data_current_file.get("document_embedding_blob")

        if not current_file_path_str or current_file_id is None:
            self.logger.warning("Chemin ou ID du fichier courant manquant pour la recherche de liens.")
            return proposals

        current_file_embedding_np_arr: Optional[np.ndarray] = None # type: ignore
        if current_file_embedding_blob and NUMPY_AVAILABLE and np:
            try:
                embedding_arr = np.frombuffer(current_file_embedding_blob, dtype=np.float32)
                # Vérifier si l'embedding est valide (non vide et bonne dimension si sbert_model est chargé)
                if embedding_arr.size > 0 and (not self.sbert_model or embedding_arr.shape[0] == self.sbert_model.get_sentence_embedding_dimension()):
                    current_file_embedding_np_arr = embedding_arr
                else:
                    self.logger.warning(f"Embedding blob pour {current_file_path_str} invalide (taille 0 ou dim incorrecte).")
            except Exception as e_reconstruct:
                self.logger.error(f"Erreur reconstruction embedding pour {current_file_path_str}: {e_reconstruct}", exc_info=False)

        use_faiss = (
            self.sbert_model is not None and
            self.faiss_index is not None and
            NUMPY_AVAILABLE and np is not None and
            current_file_embedding_np_arr is not None and
            self.faiss_index.ntotal > 0 # type: ignore
        )

        if use_faiss and current_file_embedding_np_arr is not None: # Double check pour mypy
            try:
                self.logger.debug(f"Utilisation de FAISS pour trouver des liens sémantiques pour {Path(current_file_path_str).name}.")
                # L'embedding doit être 2D (1, dim) et float32 pour FAISS search
                current_embedding_faiss_query = current_file_embedding_np_arr.reshape(1, -1).astype(np.float32)

                # +1 car le document lui-même pourrait être dans l'index si déjà traité
                k_neighbors = self.num_semantic_links_to_propose + 1

                # D: distances (scores de similarité), I: indices FAISS des voisins
                distances_faiss, indices_faiss = self.faiss_index.search(current_embedding_faiss_query, k_neighbors) # type: ignore

                num_found_by_faiss = 0
                for faiss_internal_idx, score in zip(indices_faiss[0], distances_faiss[0]):
                    if num_found_by_faiss >= self.num_semantic_links_to_propose: break # Assez de propositions
                    if faiss_internal_idx == -1 or faiss_internal_idx >= len(self.faiss_idx_to_doc_id): continue

                    target_kb_file_id = self.faiss_idx_to_doc_id[faiss_internal_idx] # KB file_id
                    if target_kb_file_id == current_file_id: continue # Exclure soi-même

                    similarity_score = float(score) # Pour IndexFlatIP, D est le produit scalaire (similarité cosinus si normalisé)

                    if similarity_score >= self.min_similarity_for_link:
                        if not self.kb: continue # Sécurité
                        target_file_path_str = self.kb.get_filepath_by_id(db_conn_worker, target_kb_file_id)
                        if target_file_path_str:
                            proposals.append({
                                "type": "semantic_similarity_link",
                                "source_file": current_file_path_str,
                                "target_file": target_file_path_str,
                                "similarity_score": round(similarity_score, 4),
                                "method": "FAISS_SBERT",
                                "suggestion": f"Document sémantiquement similaire (FAISS: {similarity_score:.2f}) à '{Path(target_file_path_str).name}'.",
                                "priority": "high" if similarity_score > 0.90 else ("medium" if similarity_score > 0.80 else "low")
                            })
                            self.logger.audit(f"Lien sémantique FAISS: {Path(current_file_path_str).name} <-> {Path(target_file_path_str).name} (Score: {similarity_score:.2f})")
                            num_found_by_faiss += 1
            except Exception as e_faiss_search:
                self.logger.error(f"Erreur lors de la recherche FAISS pour {current_file_path_str}: {e_faiss_search}", exc_info=True)
                # En cas d'erreur FAISS, on peut explicitement appeler le fallback spaCy
                self.logger.info(f"Erreur FAISS, tentative de fallback sur spaCy pour {current_file_path_str}.")
                proposals.extend(self._find_and_propose_semantic_links_spacy_fallback(analysed_data_current_file, db_conn_worker))
            return proposals # Retourner les propositions FAISS (ou du fallback si erreur FAISS)

        # Si FAISS n'est pas utilisable, passer au fallback spaCy
        self.logger.debug(f"FAISS non utilisable pour {current_file_path_str}. Fallback sur similarité spaCy.")
        return self._find_and_propose_semantic_links_spacy_fallback(analysed_data_current_file, db_conn_worker)

    def _find_and_propose_semantic_links_spacy_fallback(self, analysed_data_current_file: Dict[str, Any], db_conn_worker: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Fallback utilisant spaCy doc.similarity() si SBERT/FAISS ne sont pas disponibles."""
        proposals_fallback: List[Dict[str, Any]] = []
        current_file_path_str = analysed_data_current_file.get("filepath_str")
        current_file_id = analysed_data_current_file.get("kb_file_id")
        current_file_content = analysed_data_current_file.get("file_content")

        if not (self.kb and self.nlp_spacy and current_file_content and current_file_id is not None):
            self.logger.debug("Données insuffisantes pour fallback spaCy (KB, nlp_spacy, contenu ou ID fichier).")
            return proposals_fallback

        # Vérifier si le modèle spaCy chargé a des vecteurs
        has_vectors_spacy = False
        if hasattr(self.nlp_spacy, 'vocab') and hasattr(self.nlp_spacy.vocab, 'vectors_length') and self.nlp_spacy.vocab.vectors_length > 0:
            if 'tok2vec' in self.nlp_spacy.pipe_names or self.nlp_spacy.meta.get("vectors", {}).get("width", 0) > 0:
                has_vectors_spacy = True

        if not has_vectors_spacy:
            self.logger.debug(f"Modèle spaCy '{getattr(self.nlp_spacy.meta, 'name', 'inconnu')}' sans vecteurs. Liens sémantiques (fallback spaCy) désactivés pour {current_file_path_str}.")
            return proposals_fallback

        self.logger.debug(f"Utilisation du fallback spaCy.similarity() pour {Path(current_file_path_str).name if current_file_path_str else 'Inconnu'}")
        try:
            max_len_spacy = getattr(self.nlp_spacy, 'max_length', 1_000_000)
            doc_current = self.nlp_spacy(current_file_content[:max_len_spacy])

            if not doc_current.has_vector or doc_current.vector_norm == 0:
                self.logger.debug(f"Vecteur spaCy nul ou manquant pour le document courant {current_file_path_str}. Similarité spaCy non calculable.")
                return proposals_fallback

            # Récupérer un sous-ensemble d'autres fichiers pour comparaison
            other_files_data = self.kb.get_all_files_summary(db_conn_worker, limit=50, exclude_id=current_file_id)
            num_compared_spacy = 0

            for other_file_info in other_files_data:
                if num_compared_spacy >= self.num_semantic_links_to_propose and len(proposals_fallback) >= self.num_semantic_links_to_propose : break # Limiter le nombre de propositions

                other_file_path_str = other_file_info.get('filepath')
                if not other_file_path_str: continue

                # Lire le contenu du fichier cible (optimisation: on pourrait stocker des résumés ou des embeddings spaCy dans la KB)
                other_content, _ = robust_file_read_core(Path(other_file_path_str), self.logger) # Utiliser la fonction de core.py
                if not other_content:
                    self.logger.debug(f"Contenu illisible pour fichier cible (spaCy fallback): {other_file_path_str}")
                    continue

                doc_other = self.nlp_spacy(other_content[:max_len_spacy])
                similarity = 0.0
                try:
                    if doc_other.has_vector and doc_other.vector_norm > 0:
                        similarity = doc_current.similarity(doc_other)
                    else:
                        self.logger.debug(f"Vecteur spaCy nul ou manquant pour document cible {other_file_path_str}.")
                        continue
                except UserWarning as uw_sim: # spaCy peut lever UserWarning si les modèles ne sont pas idéaux pour la similarité
                    self.logger.debug(f"UserWarning lors du calcul de similarité spaCy ({Path(current_file_path_str).name} <-> {Path(other_file_path_str).name}): {uw_sim}")
                    continue # Passer au suivant
                except Exception as e_sim_spacy:
                    self.logger.error(f"Erreur inattendue lors du calcul de similarité spaCy: {e_sim_spacy}", exc_info=False)
                    continue

                if similarity >= self.min_similarity_for_link:
                    proposals_fallback.append({
                        "type": "semantic_similarity_link",
                        "source_file": current_file_path_str,
                        "target_file": other_file_path_str,
                        "similarity_score": round(similarity, 4),
                        "method": f"spaCy_similarity ({getattr(self.nlp_spacy.meta, 'name', 'N/A')})",
                        "suggestion": f"Document sémantiquement similaire (spaCy: {similarity:.2f}) à '{Path(other_file_path_str).name}'.",
                        "priority": "low" # Marquer comme "low" car c'est un fallback
                    })
                    self.logger.audit(f"Lien sémantique spaCy (fallback): {Path(current_file_path_str).name} <-> {Path(other_file_path_str).name} (Score: {similarity:.2f})")
                    num_compared_spacy +=1 # Compter seulement si un lien est proposé
        except Exception as e_fallback_global:
            self.logger.error(f"Erreur majeure dans _find_and_propose_semantic_links_spacy_fallback pour {current_file_path_str}: {e_fallback_global}", exc_info=True)

        return proposals_fallback

    def detect_contradictions_or_inconsistencies(self, entity_text: str, entity_type: str, db_conn_worker: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Détecte les incohérences pour une entité donnée (ex: statuts, versions)."""
        self.logger.debug(f"Détection d'incohérences pour entité '{entity_text}' (type: {entity_type}).")
        issues: List[Dict[str, Any]] = []
        if not self.kb:
            self.logger.warning("KnowledgeBase (self.kb) non disponible pour detect_contradictions.")
            return issues

        try:
            # get_entity_definitions retourne List[Dict{'filepath':str, 'meta_key':str, 'meta_value':str}]
            definitions = self.kb.get_entity_definitions(db_conn_worker, entity_text)
            if not definitions:
                self.logger.debug(f"Aucune définition (métadonnée 'statut' ou 'version') trouvée pour '{entity_text}'.")
                return issues

            # 1. Vérification des incohérences de statut
            statuses_by_file: Dict[str, List[str]] = {} # filepath -> list of statuses
            for defi in definitions:
                if defi.get('meta_key') == 'statut' and defi.get('meta_value') is not None:
                    statuses_by_file.setdefault(defi['filepath'], []).append(str(defi['meta_value']))

            # Aplatir en une liste de (filepath, status_value) pour trouver les statuts uniques
            all_status_values_with_files: List[Tuple[str,str]] = []
            for fp, status_list in statuses_by_file.items():
                for st_val in status_list:
                     all_status_values_with_files.append( (fp, st_val) )

            unique_status_values = set(st_val for fp, st_val in all_status_values_with_files)

            if len(unique_status_values) > 1:
                conflicting_info_status = [{"file": Path(fp).name, "value": st_val} for fp, st_val in all_status_values_with_files]
                issues.append({
                    "type": "consistency_issue_status",
                    "entity_text": entity_text, "entity_type": entity_type,
                    "issue_description": f"L'entité '{entity_text}' a des statuts ('statut') différents à travers les documents: {', '.join(sorted(list(unique_status_values)))}.",
                    "conflicting_info": conflicting_info_status,
                    "suggestion": "Vérifier et harmoniser le statut de cette entité dans les documents listés.",
                    "priority": "high"
                })
                self.logger.audit(f"Incohérence de statut détectée pour '{entity_text}': {unique_status_values}")

            # 2. Vérification des incohérences de version
            versions_by_file: Dict[str, List[str]] = {}
            for defi in definitions:
                if defi.get('meta_key') == 'version' and defi.get('meta_value') is not None:
                    versions_by_file.setdefault(defi['filepath'], []).append(str(defi['meta_value']))

            all_version_values_with_files: List[Tuple[str,str]] = []
            for fp, version_list in versions_by_file.items():
                for v_val in version_list:
                     all_version_values_with_files.append( (fp, v_val) )

            unique_version_values = set(v_val for fp, v_val in all_version_values_with_files)

            if len(unique_version_values) > 1:
                conflicting_info_version = [{"file": Path(fp).name, "value": v_val} for fp, v_val in all_version_values_with_files]
                issues.append({
                    "type": "consistency_issue_version",
                    "entity_text": entity_text, "entity_type": entity_type,
                    "issue_description": f"L'entité '{entity_text}' a des versions ('version') différentes à travers les documents: {', '.join(sorted(list(unique_version_values)))}.",
                    "conflicting_info": conflicting_info_version,
                    "suggestion": "Vérifier si ces versions sont des évolutions attendues ou des contradictions, et harmoniser si nécessaire.",
                    "priority": "medium"
                })
                self.logger.audit(f"Incohérence de version détectée pour '{entity_text}': {unique_version_values}")

        except sqlite3.Error as e_sql_contradict:
            self.logger.error(f"Erreur SQLite lors de la détection d'incohérences pour '{entity_text}': {e_sql_contradict}", exc_info=True)
        except Exception as e_gen_contradict:
            self.logger.error(f"Erreur générale lors de la détection d'incohérences pour '{entity_text}': {e_gen_contradict}", exc_info=True)

        return issues
