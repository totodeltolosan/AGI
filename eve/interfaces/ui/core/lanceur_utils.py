"""
Utilitaires lanceur projet Le Simulateur (Directive 60).
Fonctions support initialisation et maintenance.
"""

import logging
import time
import json
from lanceur_constantes import CONFIG_PATH, LOGS_DIR

logger = logging.getLogger(__name__)


def charger_configuration():
    """Charge la configuration depuis le fichier JSON."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}")
        return {}


def initialiser_logging():
    """Initialise le système de logging."""
    LOGS_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOGS_DIR / "simulateur.log"),
            logging.StreamHandler(),
        ],
    )


def verifier_dependances():
    """Vérifie la disponibilité des dépendances critiques."""
    try:
        import multiprocessing

        return True
    except ImportError as e:
        logger.error(f"Dépendance manquante: {e}")
        return False


def creer_queues_communication():
    """Crée les queues de communication inter-processus."""
    import multiprocessing as mp

    return {
        "gui_vers_ia": mp.Queue(),
        "ia_vers_gui": mp.Queue(),
        "jeu_vers_ia": mp.Queue(),
        "ia_vers_jeu": mp.Queue(),
        "mentor_vers_ia": mp.Queue(),
        "ia_vers_mentor": mp.Queue(),
    }


def attendre_initialisation(processus, timeout):
    """Attend l'initialisation d'un processus avec timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not processus.is_alive():
            return False
        time.sleep(0.1)
    return True


def nettoyer_ressources(queues, processus_list):
    """Nettoie les ressources système."""
    for q in queues.values():
        try:
            while not q.empty():
                q.get_nowait()
        except Exception as e:
            logger.warning(f"Erreur nettoyage queue: {e}")

    for p in processus_list:
        if p.is_alive():
            p.terminate()
            p.join(timeout=5)
