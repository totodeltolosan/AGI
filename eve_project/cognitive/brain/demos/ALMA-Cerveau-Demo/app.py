import gradio as gr
import os
import sys
import time
from pathlib import Path
import logging
import json # Pour afficher les résultats
import sqlite3 # Pour la connexion DB du worker simulé
import tempfile # Pour gérer le fichier uploadé par Gradio

# --- Configuration du Logger pour app.py ---
space_logger = logging.getLogger("ALMA.Space.CerveauDemoApp")
space_logger.setLevel(logging.INFO)
if not space_logger.handlers:
    ch_space = logging.StreamHandler(sys.stdout)
    formatter_space = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-7s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    ch_space.setFormatter(formatter_space)
    space_logger.addHandler(ch_space)

space_logger.info("app.py (Gradio Space pour Cerveau ALMA) démarré.")

# --- Variables Globales pour les Composants Cerveau Initialisés ---
SPACE_ROOT_DIR = Path(os.getcwd()) # Racine du dépôt du Space

# Pour que cerveau.py et Core.py s'importent correctement
# cerveau.py est à la racine, Core.py est dans Core/
if str(SPACE_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(SPACE_ROOT_DIR))
    space_logger.info(f"Ajouté '{SPACE_ROOT_DIR}' à sys.path.")

# Alias pour les modules et classes de cerveau.py et Core.py
cerveau_module = None
core_module = None
KnowledgeBase_class = None
FileProcessor_class = None
PipelineStepClasses = {} # ComprehensionStep, AnalysisStep, etc.
TextImprover_class = None
KnowledgeLinker_class = None

# Instances initialisées
APP_CONFIG_SPACE: dict = {}
KB_INSTANCE_SPACE: Optional[Any] = None # Sera KnowledgeBase
TEXT_IMPROVER_INSTANCE_SPACE: Optional[Any] = None
KNOWLEDGE_LINKER_INSTANCE_SPACE: Optional[Any] = None
PIPELINE_STEPS_INSTANCES_SPACE: list = []

CERVEAU_COMPONENTS_READY = False

# --- Initialisation des Composants Cerveau ---
def initialize_alma_components_for_space():
    """TODO: Add docstring."""
    global cerveau_module, core_module, KnowledgeBase_class, FileProcessor_class, PipelineStepClasses
    global TextImprover_class, KnowledgeLinker_class
    global APP_CONFIG_SPACE, KB_INSTANCE_SPACE, TEXT_IMPROVER_INSTANCE_SPACE, KNOWLEDGE_LINKER_INSTANCE_SPACE
    global PIPELINE_STEPS_INSTANCES_SPACE, CERVEAU_COMPONENTS_READY

    if CERVEAU_COMPONENTS_READY:
        space_logger.info("Composants ALMA Cerveau déjà initialisés pour le Space.")
        return True

    space_logger.info("Début de l'initialisation des composants ALMA Cerveau pour le Space...")
    try:
        # 1. Importer cerveau.py et Core.py
        # Assurez-vous que cerveau.py et Core/core.py sont à la racine du dépôt du Space
        import cerveau as c_mod
        cerveau_module = c_mod
        from Core import core as cr_mod # Importe Core/core.py
        core_module = cr_mod
        space_logger.info("Modules 'cerveau.py' et 'Core/core.py' importés.")

        # 2. Récupérer les classes nécessaires
        KnowledgeBase_class = getattr(cerveau_module, 'KnowledgeBase', None)
        FileProcessor_class = getattr(cerveau_module, 'FileProcessor', None)
        PipelineStepClasses = {
            name: getattr(cerveau_module, name, None)
            for name in ["ComprehensionStep", "AnalysisStep", "StudyStep",
                         "ImprovementProposalStep", "ActiveImprovementStep"]
        }
        TextImprover_class = getattr(core_module, 'TextImprover', None)
        KnowledgeLinker_class = getattr(core_module, 'KnowledgeLinker', None)

        if not all([KnowledgeBase_class, FileProcessor_class, TextImprover_class, KnowledgeLinker_class] +
                   list(PipelineStepClasses.values())):
            space_logger.error("Une ou plusieurs classes ALMA n'ont pas pu être récupérées des modules.")
            return False

        # 3. Configurer les chemins pour cerveau.py dans l'environnement du Space
        cerveau_module.BASE_ALMA_DIR = SPACE_ROOT_DIR
        cerveau_module.CONFIG_FILE_PATH = SPACE_ROOT_DIR / "Cerveau" / "cerveau_config.yaml"
        cerveau_module.KB_DB_PATH = SPACE_ROOT_DIR / "cerveau_knowledge_test.sqlite" # Doit correspondre à db_name dans config

        # S'assurer que les dossiers par défaut attendus par cerveau.py existent
        # (ceux définis dans DEFAULT_CONFIG de cerveau.py, adaptés par le config du Space)
        # La fonction initialize_paths_and_logging de cerveau.py le fait, mais on peut être proactif.
        (SPACE_ROOT_DIR / "Cerveau").mkdir(parents=True, exist_ok=True)
        (SPACE_ROOT_DIR / "logs_space").mkdir(parents=True, exist_ok=True) # Selon config du Space
        (SPACE_ROOT_DIR / "Connaissance_Space_Input").mkdir(parents=True, exist_ok=True)


        # 4. Charger la configuration du Space pour Cerveau
        APP_CONFIG_SPACE = cerveau_module.load_configuration(
            config_path=cerveau_module.CONFIG_FILE_PATH,
            default_config=cerveau_module.DEFAULT_CONFIG
        )
        cerveau_module.APP_CONFIG = APP_CONFIG_SPACE # Mettre à jour la globale dans cerveau.py
        space_logger.info(f"Configuration Cerveau chargée pour le Space depuis {cerveau_module.CONFIG_FILE_PATH.name}")

        # 5. Initialiser les chemins et le logger de cerveau.py avec cette config
        cerveau_module.initialize_paths_and_logging(APP_CONFIG_SPACE)
        space_logger.info("Chemins et logger de cerveau.py (utilisé par les composants) initialisés pour le Space.")

        # 6. Initialiser KnowledgeBase (charge spaCy, etc.)
        nlp_cfg_space = APP_CONFIG_SPACE.get("nlp", {})
        KB_INSTANCE_SPACE = KnowledgeBase_class(nlp_cfg_space)
        space_logger.info(f"Instance KnowledgeBase créée. spaCy prêt: {KB_INSTANCE_SPACE.is_spacy_ready}")

        # Initialiser le schéma de la DB de test si besoin
        kb_cfg_space = APP_CONFIG_SPACE.get("knowledge_base", {})
        if kb_cfg_space.get("use_sqlite_db") and cerveau_module.KB_DB_PATH:
            schema_file = cerveau_module.CERVEAU_DIR / kb_cfg_space.get("schema_file", "cerveau_kb_schema.sql")
            KnowledgeBase_class.initialize_schema_if_needed(cerveau_module.KB_DB_PATH, schema_file, kb_cfg_space.get("db_timeout_seconds", 5))
            space_logger.info(f"Schéma DB pour '{cerveau_module.KB_DB_PATH.name}' vérifié/initialisé.")

        # 7. Initialiser TextImprover et KnowledgeLinker (instances partagées)
        core_algos_cfg_space = APP_CONFIG_SPACE.get("core_algorithms_config", {})
        nlp_inst_for_core_space = KB_INSTANCE_SPACE.nlp_instance if KB_INSTANCE_SPACE and KB_INSTANCE_SPACE.is_spacy_ready else None

        if TextImprover_class and core_algos_cfg_space.get("text_improver"):
            TEXT_IMPROVER_INSTANCE_SPACE = TextImprover_class(
                core_algos_cfg_space["text_improver"], KB_INSTANCE_SPACE, nlp_inst_for_core_space, space_logger
            )
            space_logger.info("Instance TextImprover créée.")
        if KnowledgeLinker_class and core_algos_cfg_space.get("knowledge_linker"):
            KNOWLEDGE_LINKER_INSTANCE_SPACE = KnowledgeLinker_class(
                core_algos_cfg_space["knowledge_linker"], KB_INSTANCE_SPACE, nlp_inst_for_core_space, space_logger
            )
            space_logger.info("Instance KnowledgeLinker créée.")
            # Peupler FAISS si tout est prêt
            if KNOWLEDGE_LINKER_INSTANCE_SPACE and KNOWLEDGE_LINKER_INSTANCE_SPACE.faiss_index and kb_cfg_space.get("use_sqlite_db") and cerveau_module.KB_DB_PATH:
                temp_conn_faiss_init = sqlite3.connect(f"file:{cerveau_module.KB_DB_PATH}?mode=ro&immutable=1", uri=True, timeout=5)
                temp_conn_faiss_init.row_factory = sqlite3.Row
                KNOWLEDGE_LINKER_INSTANCE_SPACE.populate_faiss_index_from_kb(temp_conn_faiss_init)
                temp_conn_faiss_init.close()
                space_logger.info("Index FAISS peuplé au démarrage du Space.")


        # 8. Initialiser les étapes du pipeline
        pipeline_cfg_yaml_space = APP_CONFIG_SPACE.get("pipeline_steps", {})
        sorted_step_names_space = sorted(pipeline_cfg_yaml_space.keys(), key=lambda k: pipeline_cfg_yaml_space[k].get("priority", 99))
        for step_name_space in sorted_step_names_space:
            step_yaml_cfg_space = pipeline_cfg_yaml_space.get(step_name_space, {})
            if step_yaml_cfg_space.get("enabled", False) and step_name_space in PipelineStepClasses and PipelineStepClasses[step_name_space]:
                StepClass = PipelineStepClasses[step_name_space]
                PIPELINE_STEPS_INSTANCES_SPACE.append(
                    StepClass(step_yaml_cfg_space, APP_CONFIG_SPACE, KB_INSTANCE_SPACE,
                              TEXT_IMPROVER_INSTANCE_SPACE, KNOWLEDGE_LINKER_INSTANCE_SPACE)
                )
        space_logger.info(f"Pipeline pour le Space initialisé avec étapes: {[s.__class__.__name__ for s in PIPELINE_STEPS_INSTANCES_SPACE]}")

        CERVEAU_COMPONENTS_READY = True
        space_logger.info("Tous les composants ALMA Cerveau initialisés avec succès pour le Space.")
        return True

    except Exception as e_init_alma:
        space_logger.critical(f"ÉCHEC CRITIQUE lors de l'initialisation des composants ALMA Cerveau: {e_init_alma}", exc_info=True)
        CERVEAU_COMPONENTS_READY = False
        return False

# Tenter d'initialiser au démarrage de l'application Gradio
# Cela peut prendre du temps (chargement des modèles spaCy, SBERT).
# Si le démarrage du Space est trop long, il peut y avoir un timeout.
INITIALIZATION_ATTEMPTED = False
if not INITIALIZATION_ATTEMPTED:
    INITIALIZATION_SUCCESS = initialize_alma_components_for_space()
    INITIALIZATION_ATTEMPTED = True


# --- Fonctions pour l'interface Gradio ---
    """TODO: Add docstring."""
def process_uploaded_file(gradio_file_object):
    if not CERVEAU_COMPONENTS_READY or not FileProcessor_class or not cerveau_module or not KB_INSTANCE_SPACE:
        return "Erreur: Composants Cerveau non prêts.", "{}", "{}"

    if gradio_file_object is None:
        return "Aucun fichier fourni.", "{}", "{}"

    # Gradio fournit un objet fichier temporaire. Nous devons le sauvegarder
    # dans un emplacement que FileProcessor peut lire, ou lire son contenu.
    # Pour cette démo, nous allons le sauvegarder temporairement dans le Space.

    # Créer un dossier temporaire pour les uploads dans le Space si ce n'est pas déjà fait
    # (Gradio peut le faire dans /tmp/, mais pour que cerveau.py le voie avec des chemins relatifs
    # à sa CONNAISSANCE_DIR_SPACE_INPUT, on le met là)
    uploads_dir_space = SPACE_ROOT_DIR / APP_CONFIG_SPACE.get("paths", {}).get("connaissance_dir_suffix", "Connaissance_Space_Input")
    uploads_dir_space.mkdir(parents=True, exist_ok=True)

    # Utiliser le nom original du fichier pour le sauvegarder
    original_filename = Path(gradio_file_object.name).name # Obtenir juste le nom du fichier
    temp_filepath_in_space = uploads_dir_space / original_filename

    space_logger.info(f"Traitement du fichier téléversé: {original_filename}, sera sauvegardé temporairement comme {temp_filepath_in_space}")

    # Copier le contenu du fichier téléversé vers notre emplacement temporaire
    with open(gradio_file_object.name, "rb") as f_src, open(temp_filepath_in_space, "wb") as f_dst:
        f_dst.write(f_src.read())

    analysis_summary_text = f"Analyse pour : {original_filename}\n"
    entities_json = "{}"
    proposals_json = "{}" # Pour les propositions futures

    db_conn_gradio = None
    try:
        # Ouvrir une connexion DB pour cette tâche
        db_path_gradio = cerveau_module.KB_DB_PATH # Doit être le chemin vers cerveau_knowledge_test.sqlite
        db_timeout_gradio = APP_CONFIG_SPACE.get("knowledge_base",{}).get("db_timeout_seconds", 5)
        db_conn_gradio = sqlite3.connect(str(db_path_gradio), timeout=db_timeout_gradio)
        db_conn_gradio.row_factory = sqlite3.Row
        db_conn_gradio.execute("PRAGMA journal_mode=WAL;")
        db_conn_gradio.execute("PRAGMA foreign_keys = ON;")
        db_conn_gradio.execute("BEGIN IMMEDIATE TRANSACTION;")
        space_logger.info(f"Connexion DB ouverte pour {original_filename}")

        processor = FileProcessor_class(
            filepath=temp_filepath_in_space, # Le chemin vers le fichier sauvegardé dans le Space
            config=APP_CONFIG_SPACE,
            pipeline_steps=PIPELINE_STEPS_INSTANCES_SPACE,
            kb_instance=KB_INSTANCE_SPACE,
            db_conn_worker=db_conn_gradio
        )

        pipeline_success = processor.run_pipeline() # Exécute le pipeline

        if pipeline_success:
            db_conn_gradio.commit()
            space_logger.info(f"Pipeline réussi et transaction commitée pour {original_filename}.")
            analysis_summary_text += "Pipeline exécuté avec succès.\n"
            analysis_summary_text += f"Checksum: {processor.checksum}\n"
            analysis_summary_text += f"Encodage: {processor.encoding}\n"
            analysis_summary_text += f"ID KB: {processor.processed_data.get('kb_file_id', 'N/A')}\n"

            if processor.processed_data.get('linguistic_features', {}).get('entities'):
                entities_json = json.dumps(processor.processed_data['linguistic_features']['entities'][:10], indent=2, ensure_ascii=False) # Top 10 entités

            # Récupérer les propositions si elles ont été générées (bien que désactivé dans config)
            # proposals_count = processor.processed_data.get("proposals_generated_count", 0)
            # proposals_json = json.dumps({"proposals_count": proposals_count, "message": "Détails non affichés ici"}, indent=2)

        else:
            db_conn_gradio.rollback()
            space_logger.error(f"Échec du pipeline pour {original_filename}. Transaction annulée.")
            analysis_summary_text += "ÉCHEC de l'exécution du pipeline.\nConsultez les logs du Space pour les détails."

    except Exception as e:
        space_logger.error(f"Erreur majeure dans process_uploaded_file pour {original_filename}: {e}", exc_info=True)
        analysis_summary_text = f"ERREUR : {e}"
        if db_conn_gradio:
            try: db_conn_gradio.rollback()
            except Exception: pass
    finally:
        if db_conn_gradio:
            try: db_conn_gradio.close()
            except Exception: pass
        # Nettoyer le fichier temporaire uploadé
        try:
            if temp_filepath_in_space.exists():
                temp_filepath_in_space.unlink()
                space_logger.info(f"Fichier temporaire {temp_filepath_in_space} supprimé.")
        except Exception as e_clean:
            space_logger.warning(f"Impossible de supprimer le fichier temporaire {temp_filepath_in_space}: {e_clean}")

    return analysis_summary_text, entities_json, proposals_json

    """TODO: Add docstring."""

def get_current_kb_summary_for_gradio():
    # Similaire à la fonction get_kb_summary précédente, mais utilise les globales du Space
    if not CERVEAU_COMPONENTS_READY or not cerveau_module:
        return "Composants Cerveau non prêts."

    summary_text = "Résumé KB non disponible."
    kb_cfg = APP_CONFIG_SPACE.get("knowledge_base", {})
    db_path_summary = cerveau_module.KB_DB_PATH

    if kb_cfg.get("use_sqlite_db") and db_path_summary and db_path_summary.exists():
        conn_s = None
        try:
            timeout_s = kb_cfg.get("db_timeout_seconds", 5)
            conn_s = sqlite3.connect(f"file:{db_path_summary}?mode=ro&immutable=1", uri=True, timeout=timeout_s)
            conn_s.row_factory = sqlite3.Row
            cur = conn_s.cursor()
            cur.execute("SELECT COUNT(*) as count FROM files")
            num_docs = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM named_entities")
            num_entities = cur.fetchone()['count']
            summary_text = f"KB Test ('{db_path_summary.name}'): Docs={num_docs}, Entités (occur.)={num_entities}"
        except Exception as e:
            summary_text = f"Erreur résumé KB: {e}"
        finally:
            if conn_s: conn_s.close()
    return summary_text

# --- Définition de l'Interface Gradio ---
with gr.Blocks(title="Démo Cerveau ALMA", theme=gr.themes.Soft()) as demo_interface:
    gr.Markdown("# Démonstration du Module Cerveau d'ALMA")
    gr.Markdown(
        f"Téléversez un fichier texte (.txt, .md) pour le faire analyser par `cerveau.py`.\n"
        f"Utilise la base de connaissances de test : `{KB_TEST_IN_SPACE.name if KB_INSTANCE_SPACE and cerveau_module and cerveau_module.KB_DB_PATH else 'KB non chargée'}`.\n"
        f"Statut Initialisation Cerveau : {'Réussie' if CERVEAU_COMPONENTS_READY else 'Échec (vérifiez les logs du Space)'}"
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_uploader = gr.File(label="Fichier à analyser (.txt, .md)", file_types=[".txt", ".md"])
            analyze_btn = gr.Button("🧠 Analyser avec Cerveau", variant="primary")
        with gr.Column(scale=2):
            output_summary = gr.Textbox(label="Résumé de l'Analyse par Cerveau", lines=12, interactive=False)

    with gr.Row():
        output_entities_json = gr.JSON(label="Entités Nommées (Top 10 extraites)")
        output_proposals_json = gr.JSON(label="Propositions d'Amélioration (Si activé)")

    with gr.Accordion("Résumé Actuel de la KnowledgeBase de Test", open=False):
        kb_summary_display = gr.Textbox(label="Statistiques KB", lines=3, interactive=False)
        refresh_kb_btn = gr.Button("🔄 Rafraîchir Résumé KB")

    # Lier les fonctions aux composants Gradio
    analyze_btn.click(
        fn=process_uploaded_file,
        inputs=[file_uploader],
        outputs=[output_summary, output_entities_json, output_proposals_json]
    )
    refresh_kb_btn.click(fn=get_current_kb_summary_for_gradio, inputs=None, outputs=kb_summary_display)

    # Charger le résumé KB au démarrage de l'interface
    demo_interface.load(fn=get_current_kb_summary_for_gradio, inputs=None, outputs=kb_summary_display)

# Lancer l'interface (nécessaire pour les Spaces Gradio)
if __name__ == "__main__":
    space_logger.info("Lancement de l'interface Gradio demo_interface.launch() depuis __main__...")
    # Pour un Space HF, demo.launch() seul suffit. Pas besoin de share=True.
    # Le port est géré par HF.
    demo_interface.launch()
    space_logger.info("Interface Gradio terminée (si exécuté localement et bloquant).")